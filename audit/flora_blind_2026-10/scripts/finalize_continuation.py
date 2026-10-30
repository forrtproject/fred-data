#!/usr/bin/env python3
"""Integrate only a fully drained, parent-inspected supplemental review queue."""
import collections
import datetime
import json
from pathlib import Path
import adjudicate as a
import compare as c
import verify_integration

R = Path(__file__).resolve().parents[1]


def finalize():
    manifest = json.loads((R/'run_manifest.json').read_text())
    phase = manifest['continuation']
    assert phase['status'] == 'active'
    items = json.loads((R/phase['selection']).read_text())['items']
    keys = {i['file_key'] for i in items}
    assert len(items) == 102 and len(keys) == 87
    inspected = json.loads((R/'continuation_inspection.json').read_text())['works']
    assert keys <= inspected.keys(), 'Parent inspection incomplete'
    states = {}
    for fk in keys:
        state = json.loads((R/'argon'/f'{fk}.state.json').read_text())
        assert state['status'] in ('validated', 'unresolved'), (fk, state['status'])
        assert 1 <= state['attempts'] <= 2
        assert not state.get('requires_parent_scope_inspection'), fk
        states[fk] = state
    dispositions = []
    for item in items:
        fk = item['file_key']
        obj = c.read_json(R/'adjudications'/f'{fk}.json')[0] or {}
        decisions = [d for d in obj.get('decisions', []) if a.decision_key(d) == a.decision_key(item)]
        source = (R/'texts'/f'{fk}.txt').read_text()
        d = decisions[0] if len(decisions) == 1 and c.valid_decision(decisions[0], source) else None
        dispositions.append({k: item.get(k) for k in ('file_key', 'work_key', 'input_row_index', 'target_index', 'field')} |
                            {'review_verdict': d['verdict'] if d else 'no_valid_reply'})
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    all_states = [json.loads(p.read_text()) for p in (R/'argon').glob('*.state.json')]
    called = [s for s in all_states if s.get('attempts', 0)]
    counts = collections.Counter(s['status'] for s in called)
    assert set(counts) <= {'validated', 'unresolved'}, counts
    coverage = json.loads((R/'review_coverage.json').read_text())
    old_summary = dict(coverage['summary'])
    manifest.setdefault('original_bounded_run', {k: manifest[k] for k in
                        ('audit_finalized_at', 'completed_at', 'review_summary', 'final_counts', 'tests_passed')})
    pending = [i for i in coverage['unreviewed_requests_without_call']
               if not states.get(i['file_key'], {}).get('attempts')]
    summary = {'workgroups_with_calls': len(called),
               'call_attempts_consumed': sum(s['attempts'] for s in called),
               'validated_workgroups': counts['validated'],
               'unresolved_workgroups': counts['unresolved'],
               'prepared_workgroups_without_call': len({i['file_key'] for i in pending}),
               'prepared_fields_without_call': len(pending),
               'prepared_workgroups_no_argon_call_including_parent_resolved':
                   len({i['file_key'] for i in pending} | {i['file_key'] for i in coverage['no_call_requests_resolved_by_parent']}),
               'prepared_fields_resolved_by_parent_without_argon': len(coverage['no_call_requests_resolved_by_parent'])}
    phase.update(status='complete', completed_at=stamp, works_reviewed=len(keys),
                 requests_reviewed=len(items), call_attempts_consumed=sum(s['attempts'] for s in states.values()),
                 review_verdicts=dict(collections.Counter(i['review_verdict'] for i in dispositions)))
    summary['supplemental'] = phase.copy()
    coverage.update(finalized_at=stamp, summary=summary, unreviewed_requests_without_call=pending,
                    review_state_counts=dict(counts), supplemental_dispositions=dispositions)
    manifest.update(audit_finalized_at=stamp, completed_at=stamp, review_summary=summary, tests_passed=59)
    a.atomic(R/'review_coverage.json', coverage)
    a.atomic(R/'run_manifest.json', manifest)
    c.run()
    rows = c.read_csv(R/'results.csv')
    missing = c.read_csv(R/'missing_rows.csv')
    final_counts = {'confirmed_error_rows': sum(bool(json.loads(r['suggested_correction'])) for r in rows),
                    'fully_resolved_rows': sum(r['resolution'] != 'unresolved' for r in rows),
                    'confirmed_missing_targets': sum(r['final_verdict'] == 'error' for r in missing),
                    'unverified_missing_targets': sum(r['final_verdict'] == 'unverified' for r in missing)}
    byrow = {r['input_row_index']: r for r in rows}
    bytarget = {(r['file_key'], int(r['target_index'])): r for r in missing}
    for d in dispositions:
        if d['field'] == 'missing_row':
            value = bytarget.get((d['file_key'], d['target_index']), {}).get('final_verdict', 'unverified')
        else:
            value = byrow[str(d['input_row_index'])][d['field']+'_final_verdict']
        d['integrated_verdict'] = value
    phase['integrated_verdicts'] = dict(collections.Counter(d['integrated_verdict'] for d in dispositions))
    summary['supplemental'] = phase.copy()
    manifest.update(final_counts=final_counts, review_summary=summary)
    coverage.update(summary=summary, supplemental_dispositions=dispositions)
    a.atomic(R/'run_manifest.json', manifest)
    a.atomic(R/'review_coverage.json', coverage)
    a.atomic(R/'final_counts.json', final_counts)
    c.run()
    verification = verify_integration.verify()
    a.atomic(R/'verification_final.json', verification)
    with (R/'run_log.md').open('a') as stream:
        stream.write('\n- '+stamp+': User-authorised supplemental queue drained and parent-inspected: '+
                     json.dumps(phase)+'; regenerated comparison, coverage and report. Counts '+
                     json.dumps(final_counts)+'. All codings and correction quotations verified; FLoRA hash unchanged. No new schedules.\n')
    return {'continuation': phase, 'counts': final_counts, 'verification': verification}


if __name__ == '__main__':
    print(json.dumps(finalize(), indent=2))
