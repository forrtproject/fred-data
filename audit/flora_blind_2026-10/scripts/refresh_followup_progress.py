#!/usr/bin/env python3
"""Refresh live coverage and newly recovered-source field requests, no verdicts."""
import collections
import datetime
import json
from pathlib import Path

import adjudicate as a
import compare as c

R = Path(__file__).resolve().parents[1]
F = R / 'evidence_followup'


def refresh():
    rows = c.read_csv(R / 'results.csv')
    missing = c.read_csv(R / 'missing_rows.csv')
    fields = []
    for field in c.FIELDS:
        for row in c.applicable_rate_rows(rows, field):
            if row[field + '_final_verdict'] == 'unverified':
                fields.append({k: row[k] for k in ('input_row_index', 'file_key', 'work_key',
                    'evidence_level', 'coding_status', 'skip_reason', 'pairing_flags')} | {'field': field})
    c.write_csv(R / 'remaining_fields.csv', fields, ['input_row_index', 'file_key', 'work_key',
                'field', 'evidence_level', 'coding_status', 'skip_reason', 'pairing_flags'])
    counts = {'confirmed_error_rows': sum(any(r[f + '_final_verdict'] == 'error'
                    for f in ('type', 'original', 'outcome')) for r in rows),
              'fully_resolved_rows': sum(r['resolution'] != 'unresolved' for r in rows),
              'confirmed_missing_targets': sum(r['final_verdict'] == 'error' for r in missing),
              'unverified_missing_targets': sum(r['final_verdict'] == 'unverified' for r in missing),
              'unresolved_rows_by_evidence': dict(collections.Counter(r['evidence_level'] for r in rows
                    if r['resolution'] == 'unresolved')), 'unverified_applicable_fields': len(fields)}
    progress = {'status': 'active', 'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'latest_integrated_counts': counts,
                'warning': 'Provisional. Candidate rechecks, field reviews and primary source checks remain active; model replies await parent inspection.'}
    a.atomic(F / 'integration/progress.json', progress)
    manifest = json.loads((R / 'run_manifest.json').read_text())
    assert manifest['evidence_followup']['status'] == 'active'
    manifest['evidence_followup']['latest_integrated_counts'] = counts
    manifest['evidence_followup']['source_checks'] = {
        'verified_full_text': 19, 'verified_primary_abstract': 1, 'rejected_source_hits': 2,
        'partial_source_assessment_complete': 201}
    a.atomic(R / 'run_manifest.json', manifest)

    promoted = {x['file_key'] for x in json.loads((F / 'integration/source_promotions.json').read_text())['promotions']}
    originals = [c.adapt_row(x) for x in c.read_csv(c.INPUT)]
    conditional = {(x['input_row_index'], x['field']) for x in c.read_csv(R / 'completion_pass/field_dispositions.csv')
                   if x['disposition'] == 'conditionally_inapplicable'}
    bywork = collections.defaultdict(list)
    for item in fields:
        if item['file_key'] in promoted and (item['input_row_index'], item['field']) not in conditional:
            bywork[item['file_key']].append(item)
    outdir = F / 'new_source_field_requests'
    outdir.mkdir(exist_ok=True)
    if (outdir / 'index.json').exists():
        index = json.loads((outdir / 'index.json').read_text())
        return counts | {'new_source_field_requests': len(index),
                         'new_source_fields': sum(x['field_count'] for x in index)}
    index = []
    for fk, items in sorted(bywork.items()):
        sourcepath = R / 'texts' / (fk + '.txt')
        shipped = [{'input_row_index': int(row['input_row_index']),
                    'paired_target_index': row['blind_target_index'], 'identity_resolved': row['identity_resolved'],
                    **{k: originals[int(row['input_row_index'])].get(k, '') for k in ('doi_o', 'title_o', 'authors_o',
                        'year_o', 'type', 'outcome', 'outcome_computation', 'outcome_robustness', 'outcome_quote')}}
                   for row in rows if row['file_key'] == fk]
        for start in range(0, len(items), 6):
            rid = f'new_source_{fk}_{start//6:03d}'
            path = outdir / (rid + '.json')
            payload = {'request_id': rid, 'file_key': fk, 'work_key': items[0]['work_key'],
                       'requested_fields': items[start:start+6], 'source_path': str(sourcepath),
                       'source_instruction': a.source_instruction(fk, sourcepath, sourcepath.read_text()),
                       'coding_path': str(R / 'codings' / (fk + '.json')),
                       'prior_adjudication_path': str(R / 'adjudications' / (fk + '.json')),
                       'prior_state_path': str(R / 'argon' / (fk + '.state.json')), 'shipped_rows': shipped}
            if not path.exists():
                a.atomic(path, payload)
            else:
                assert json.loads(path.read_text()) == payload, 'Active source-review input must not change'
            index.append({'request_id': rid, 'file_key': fk, 'input_path': str(path),
                          'field_count': len(items[start:start+6]), 'status': 'pending'})
    # This queue is distinct from the running immutable 271-request relay.
    indexpath = outdir / 'index.json'
    if not indexpath.exists():
        a.atomic(indexpath, index)
    return counts | {'new_source_field_requests': len(index), 'new_source_fields': sum(x['field_count'] for x in index)}


if __name__ == '__main__':
    print(json.dumps(refresh()))
