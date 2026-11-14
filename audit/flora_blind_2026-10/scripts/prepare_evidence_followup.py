#!/usr/bin/env python3
"""Prepare complete, immutable follow-up queues without changing prior verdicts."""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

import adjudicate as a
import compare as c

R = Path(__file__).resolve().parents[1]
F = R / 'evidence_followup'


def prepare():
    if (F / 'state.json').exists():
        raise SystemExit('Existing follow-up must be resumed, not reinitialised')
    for name in ('luna/batches', 'luna/results', 'field_requests', 'argon', 'acquisition',
                 'private/acquisition', 'private/new_texts', 'private/blind_codings',
                 'private/old_texts', 'private/old_codings', 'integration'):
        (F / name).mkdir(parents=True, exist_ok=True)
    rows = c.read_csv(R / 'results.csv')
    originals = [c.adapt_row(x) for x in c.read_csv(c.INPUT)]
    manifest = c.read_csv(R / 'manifest.csv')
    bywork = collections.defaultdict(list)
    for row in rows:
        bywork[row['file_key']].append(row)
    sanitized = {x['file_key']: x for x in json.loads((R / 'work_queue.json').read_text())}
    missing = [x for x in c.read_csv(R / 'missing_rows.csv') if x['final_verdict'] != 'correct']
    candidates = collections.defaultdict(list)
    for item in missing:
        candidates[item['file_key']].append(item)
    packets = []
    acquisition = set()
    for fk, items in sorted(candidates.items()):
        coding = json.loads((R / 'codings' / (fk + '.json')).read_text())
        shipped = []
        for row in bywork[fk]:
            raw = originals[int(row['input_row_index'])]
            shipped.append({'input_row_index': row['input_row_index'], **{
                k: raw.get(k, '') for k in ('doi_o', 'title_o', 'authors_o', 'year_o')}})
        if coding.get('evidence_level') != 'full_text' or not coding.get('text_scope_complete', True):
            acquisition.add(fk)
        for start in range(0, len(items), 6):
            group = items[start:start+6]
            packets.append({'file_key': fk, 'work_key': items[0]['work_key'],
                'text_path': str(R / 'texts' / (fk + '.txt')),
                'coding_path': str(R / 'codings' / (fk + '.json')),
                'codebook_path': str(R / 'codebook.md'),
                'source_instruction': a.source_instruction(fk, R / 'texts' / (fk + '.txt'),
                    (R / 'texts' / (fk + '.txt')).read_text()),
                'evidence_level': coding.get('evidence_level'),
                'shipped_originals': shipped,
                'prior_adjudication_path': str(R / 'adjudications' / (fk + '.json')),
                'candidates': [{'target_index': int(x['target_index']),
                    'previous_final_verdict': x['final_verdict'],
                    'blind_target': json.loads(x['blind_target']),
                    'prior_decision': json.loads(x['evidence'])} for x in group]})
    # Each bounded batch has at most six candidates; retain work-specific context.
    batches, current, size = [], [], 0
    for packet in packets:
        n = len(packet['candidates'])
        if current and size+n > 6:
            batches.append(current); current, size = [], 0
        current.append(packet); size += n
    if current:
        batches.append(current)
    batch_index = []
    for i, works in enumerate(batches):
        bid = f'luna_{i:04d}'
        path = F / 'luna/batches' / (bid + '.input.json')
        a.atomic(path, {'batch_id': bid, 'works': works})
        batch_index.append({'batch_id': bid, 'input_path': str(path),
            'output_path': str(F / 'luna/results' / (bid + '.json')),
            'candidate_count': sum(len(w['candidates']) for w in works), 'status': 'pending'})
    dispositions = c.read_csv(R / 'completion_pass/field_dispositions.csv')
    conditional = {(x['input_row_index'], x['field']) for x in dispositions
                   if x['disposition'] == 'conditionally_inapplicable'}
    fields = collections.defaultdict(list)
    deferred = []
    for item in c.read_csv(R / 'remaining_fields.csv'):
        if (item['input_row_index'], item['field']) in conditional:
            deferred.append(dict(item, followup_status='conditional_inapplicability'))
        elif item['evidence_level'] == 'full_text' and not item['skip_reason']:
            fields[item['file_key']].append(item)
        else:
            acquisition.add(item['file_key'])
            deferred.append(dict(item, followup_status='awaiting_primary_source'))
    requests = []
    # Small requests preserve all earlier call history; no old state is reset.
    for fk, items in sorted(fields.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        full_rows = []
        for row in bywork[fk]:
            raw = originals[int(row['input_row_index'])]
            full_rows.append({'input_row_index': int(row['input_row_index']),
                'paired_target_index': row['blind_target_index'],
                'identity_resolved': row['identity_resolved'],
                **{k: raw.get(k, '') for k in ('doi_o', 'title_o', 'authors_o', 'year_o',
                    'type', 'outcome', 'outcome_computation', 'outcome_robustness', 'outcome_quote')}})
        for start in range(0, len(items), 6):
            rid = f'fields_{fk}_{start//6:03d}'
            path = F / 'field_requests' / (rid + '.json')
            a.atomic(path, {'request_id': rid, 'file_key': fk,
                'work_key': items[0]['work_key'], 'requested_fields': items[start:start+6],
                'source_path': str(R / 'texts' / (fk + '.txt')),
                'source_instruction': a.source_instruction(fk, R / 'texts' / (fk + '.txt'),
                    (R / 'texts' / (fk + '.txt')).read_text()),
                'coding_path': str(R / 'codings' / (fk + '.json')),
                'prior_adjudication_path': str(R / 'adjudications' / (fk + '.json')),
                'prior_state_path': str(R / 'argon' / (fk + '.state.json')),
                'shipped_rows': full_rows})
            requests.append({'request_id': rid, 'input_path': str(path),
                'field_count': len(items[start:start+6]), 'status': 'pending'})
    acquisition_records = [{k: sanitized[fk].get(k, '') for k in
        ('file_key', 'work_key', 'doi_r', 'url_r', 'title_r', 'author_r', 'year_r', 'journal_r')}
        for fk in sorted(acquisition)]
    assert len({(x['file_key'], x['target_index']) for x in missing}) == 716
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    state = {'authorized_at': stamp, 'status': 'active',
        'scope': 'Review every outstanding full-text field, recover primary evidence for remaining rows, triage all candidate omissions and audit all confirmed omissions for true absence.',
        'baseline_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'max_combined_children_and_infrastructure': 10, 'max_parallel_argon': 3,
        'max_parallel_luna': 3, 'max_acquisition_tasks': 1,
        'incremental_api_spend_usd': 0, 'tasks': [],
        'counts_at_start': {'unresolved_full_text_rows': 421, 'unresolved_abstract_rows': 283,
            'unresolved_no_usable_evidence_rows': 53, 'unverified_omission_candidates': 603,
            'confirmed_omissions_to_recheck': 113, 'luna_candidates': 716,
            'luna_batches': len(batches), 'initial_field_requests': len(requests),
            'initial_full_text_fields': sum(x['field_count'] for x in requests),
            'acquisition_works': len(acquisition_records)},
        'prior_primary_result_sha256': hashlib.sha256((R / 'results.csv').read_bytes()).hexdigest(),
        'original_attempt_histories_immutable': True,
        'new_request_attempt_limit': 2,
        'new_review_basis': 'User renewed scope; smaller target-specific requests replace previously oversized work-level requests. Prior reasons/objections must be read.',
    }
    a.atomic(F / 'luna/index.json', batch_index)
    a.atomic(F / 'field_requests/index.json', requests)
    a.atomic(F / 'acquisition/works.json', acquisition_records)
    a.atomic(F / 'deferred_until_source.json', deferred)
    a.atomic(F / 'state.json', state)
    return state['counts_at_start']


if __name__ == '__main__':
    print(json.dumps(prepare(), indent=2))
