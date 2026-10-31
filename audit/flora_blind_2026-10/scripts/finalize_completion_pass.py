#!/usr/bin/env python3
"""Integrate parent-inspected omission decisions and document deferred work."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

import adjudicate as a
import compare as c
import verify_integration

R = Path(__file__).resolve().parents[1]
P = R / 'completion_pass'


def finalize():
    state = json.loads((P / 'state.json').read_text())
    inspection = json.loads((P / 'parent_inspection.json').read_text())
    records = inspection['records']
    assert len(records) == 9 and len({(x['file_key'], x['target_index']) for x in records}) == 9
    tasks = [json.loads(p.read_text()) for p in sorted((P / 'luna').glob('*.task.json'))]
    assert len(tasks) == 3
    assert all(t['status'] == 'completed' and not t['hasPendingChildRuns']
               and not t['hasPendingQuestion'] and not t['pendingApproval'] for t in tasks)
    assert all(t['providerInstanceId'] == 'codex' and t['model'] == 'gpt-6-luna' for t in tasks)
    baseline_results = hashlib.sha256((R / 'results.csv').read_bytes()).hexdigest()
    for item in records:
        source = (R / 'texts' / (item['file_key'] + '.txt')).read_text()
        assert c.quote_present(item['luna_quote'], source), item['file_key']
        if item['parent_disposition'] != 'confirmed_omission':
            continue
        decision = item['decision']
        assert decision['method'] == 'obvious' and c.valid_decision(decision, source)
        assert decision['target_index'] == item['target_index']
        path = R / 'adjudications' / (item['file_key'] + '.json')
        obj = c.read_json(path)[0] or {'decisions': []}
        existing = [d for d in obj['decisions'] if a.decision_key(d) == a.decision_key(decision)]
        assert not existing or existing == [decision], 'Existing decision must not be overwritten'
        if not existing:
            obj['decisions'].append(decision)
            obj['completion_pass_inspection'] = 'completion_pass/parent_inspection.json'
            a.atomic(path, obj)
    manifest = json.loads((R / 'run_manifest.json').read_text())
    stamp = state.get('completed_at') or datetime.datetime.now(datetime.timezone.utc).isoformat()
    phase = {
        'authorized_at': state['authorized_at'], 'completed_at': stamp, 'status': 'complete_with_deferrals',
        'pilot_tasks': 3, 'pilot_candidates': len(records),
        'literal_quotes_verified': len(records),
        'confirmed_additional_omissions': sum(x['parent_disposition'] == 'confirmed_omission' for x in records),
        'pilot_candidates_deferred': sum(x['parent_disposition'] == 'deferred' for x in records),
        'luna_classification_overturned': 1,
        'reported_luna_worker_seconds': inspection['reported_luna_worker_seconds'],
        'additional_argon_calls': 0, 'incremental_api_spend_usd': 0,
        'wider_candidate_triage': 'deferred: parent source and publication-level identity review still required',
        'large_source_reviews': 'deferred: exhausted replies on two 1.9–2.2 million-character collections; renewed target-level extraction/review exceeds this cheap closure pass',
        'owned_tasks_active': 0, 'owned_schedules_remaining': 0,
        'inspection': 'completion_pass/parent_inspection.json',
    }
    manifest.update(audit_finalized_at=stamp, completed_at=stamp, completion_pass=phase)
    manifest['review_summary']['completion_pass'] = phase.copy()
    a.atomic(R / 'run_manifest.json', manifest)
    c.run()
    assert baseline_results == hashlib.sha256((R / 'results.csv').read_bytes()).hexdigest(), 'Input-row results changed'
    rows = c.read_csv(R / 'results.csv')
    missing = c.read_csv(R / 'missing_rows.csv')
    counts = {
        'confirmed_error_rows': sum(bool(json.loads(x['suggested_correction'])) for x in rows),
        'fully_resolved_rows': sum(x['resolution'] != 'unresolved' for x in rows),
        'confirmed_missing_targets': sum(x['final_verdict'] == 'error' for x in missing),
        'unverified_missing_targets': sum(x['final_verdict'] == 'unverified' for x in missing),
    }
    assert counts == dict(state['baseline_counts'], confirmed_missing_targets=113, unverified_missing_targets=603)
    byrow = {x['input_row_index']: x for x in rows}
    field_dispositions = []
    for field in c.read_csv(R / 'remaining_fields.csv'):
        row = byrow[field['input_row_index']]
        correction = json.loads(row['suggested_correction'])
        if (correction.get('original') == {'action': 'remove_row'}
                or (correction.get('type') == 'not_a_replication' and field['field'] in ('original', 'outcome'))
                or (correction.get('type') == 'reproduction' and field['field'] == 'outcome')):
            disposition = 'conditionally_inapplicable'
            reason = 'If the source-checked proposed row/type correction is accepted, this shipped-type field does not apply; primary verdict and shipped-type denominator remain unchanged.'
        elif field['skip_reason']:
            disposition = 'deferred_source_or_identity'
            reason = field['skip_reason'] + '; needs eligible primary evidence and fresh validation before a substantive verdict.'
        elif field['evidence_level'] != 'full_text':
            disposition = 'deferred_primary_evidence'
            reason = 'Available abstract/partial evidence does not settle this field; needs original-specific primary results.'
        else:
            disposition = 'deferred_source_review'
            reason = 'Saved text has not yielded a supported integrated verdict; needs target-specific source/identity/quotation review, with Argon for a non-obvious disagreement. No new field review in the cheap omission pilot.'
        field_dispositions.append(dict(field, disposition=disposition, reason=reason))
    c.write_csv(P / 'field_dispositions.csv', field_dispositions,
                list(field_dispositions[0]))
    pilot = {(x['file_key'], x['target_index']): x for x in records}
    target_dispositions = []
    for target in missing:
        if target['final_verdict'] != 'unverified':
            continue
        inspected = pilot.get((target['file_key'], int(target['target_index'])))
        target_dispositions.append({
            'file_key': target['file_key'], 'work_key': target['work_key'],
            'target_index': target['target_index'], 'evidence_level': target['evidence_level'],
            'title': target['title'], 'disposition': 'deferred',
            'pilot_inspected': bool(inspected),
            'reason': inspected['parent_reason'] if inspected else
                'Not individually reviewed in the cheap pilot. Confirming a paper-level omission requires source-backed retesting and deduplication; Luna labels alone are insufficient.',
        })
    assert len(target_dispositions) == counts['unverified_missing_targets']
    c.write_csv(P / 'candidate_dispositions.csv', target_dispositions, list(target_dispositions[0]))
    disposition_counts = dict(collections.Counter(x['disposition'] for x in field_dispositions))
    phase.update(remaining_candidate_targets=len(target_dispositions),
                 remaining_shipped_scope_fields=len(field_dispositions),
                 field_dispositions=disposition_counts)
    state.update(status='complete_with_deferrals', completed_at=stamp, tasks=tasks,
                 outcome=phase, final_counts=counts)
    manifest.update(final_counts=counts, completion_pass=phase)
    manifest['review_summary']['completion_pass'] = phase.copy()
    coverage = json.loads((R / 'review_coverage.json').read_text())
    coverage['summary']['completion_pass'] = phase.copy()
    backlog = json.loads((R / 'remaining_backlog.json').read_text())
    backlog.update(unverified_candidate_targets=len(target_dispositions),
                   shipped_scope_field_dispositions=disposition_counts,
                   completion_status='deferred with explicit evidence requirements',
                   disposition_files=['completion_pass/field_dispositions.csv', 'completion_pass/candidate_dispositions.csv'])
    a.atomic(P / 'state.json', state)
    a.atomic(R / 'run_manifest.json', manifest)
    a.atomic(R / 'review_coverage.json', coverage)
    a.atomic(R / 'remaining_backlog.json', backlog)
    a.atomic(R / 'final_counts.json', counts)
    c.run()
    verification = verify_integration.verify()
    a.atomic(R / 'verification_final.json', verification)
    a.atomic(P / 'verification.json', dict(verification, pilot_quotes=9,
             primary_input_results_preserved=True, field_dispositions=len(field_dispositions),
             candidate_dispositions=len(target_dispositions)))
    return {'counts': counts, 'completion_pass': phase, 'verification': verification}


if __name__ == '__main__':
    print(json.dumps(finalize(), indent=2))
