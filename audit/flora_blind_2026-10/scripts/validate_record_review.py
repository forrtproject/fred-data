#!/usr/bin/env python3
"""Check record-level remedies, source proofs and the plan/results separation."""
import csv
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parents[1]
H = B / 'handoff'
BASELINE = Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASELINE) == '6d391186dfb57263bbc6bb504e8561e0d1e25997b36417072c023812efaad9f7'
rows = list(csv.DictReader(BASELINE.open(encoding='utf-8-sig')))
review = json.loads((B / 'publication/record_scope_review_20261101.json').read_text())
assert review['coverage']['originally_prospective_codings_accounted'] == 6
assert review['coverage']['current_final_decision_rows_screened'] == 109
proof_count = 0

def proofs(value):
    global proof_count
    if isinstance(value, list):
        for v in value:
            proofs(v)
    elif isinstance(value, dict):
        q = value.get('literal_contiguous_quote', value.get('quote'))
        if q and 'source_path' in value and 'character_start' in value and 'sha256' in value:
            p = Path(value['source_path'])
            raw = p.read_bytes()
            assert sha(p) == value['sha256'], p
            assert raw.decode()[value['character_start']:value['character_end']] == q
            assert raw[value['utf8_byte_start']:value['utf8_byte_end']].decode() == q
            proof_count += 1
        for v in value.values():
            proofs(v)

proofs(review)
proofs(json.loads((B / 'publication/completed_report_reviews_20261101.json').read_text()))
proofs(json.loads((H / 'current_source_decisions.json').read_text()))
proofs(json.loads((B / 'publication/gray_additional_target_review_20261101.json').read_text()))
import jsonschema
blind_quotes = 0
for name in ['j9mfn', 'ahcpw', 'w34fb']:
    packet = B / 'evidence_followup/private/record_scope_20261101' / ('blind_' + name)
    coding = json.loads((packet / 'coding.json').read_text())
    metadata = json.loads((packet / 'metadata.json').read_text())
    jsonschema.validate(coding, json.loads((packet / 'schema.json').read_text()))
    assert all(coding[k] == v for k, v in metadata.items())
    text = (packet / 'article.txt').read_text()
    assert sha(packet / 'article.txt') == metadata['text_sha256']
    for record in [coding] + coding['targets']:
        for key, quote in record.items():
            if isinstance(quote, str) and key.endswith('_quote') and quote:
                assert quote in text
                blind_quotes += 1
    validation = json.loads((packet / 'validation.json').read_text())
    assert validation['complete_model_visible_read'] and validation['read_coverage_verified_no_gaps']
    end = 0
    for a, b in sorted(validation['model_visible_read_intervals']):
        assert a <= end
        end = max(end, b)
    assert end == len(text)
actions = json.loads((H / 'record_actions.json').read_text())['actions']
by_row = {a['input_row_index']: a for a in actions}
assert len(by_row) == len(actions) == 21
for i, a in by_row.items():
    expected = hashlib.sha256(json.dumps(rows[i], ensure_ascii=False,
        sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert a['expected_before_full_record_sha256'] == expected
    assert a['canonical_dataset_changes_applied'] is False
# Regression: BU3GM must not be presented as an outcome-only ready fix.
assert by_row[0]['operation'] == 'move_plan_out_of_completed_results_pool'
assert by_row[0]['proposed_changes'][0]['to_pool'] == 'planned_studies'
assert by_row[242]['status'] == 'decision_required'
assert by_row[1698]['operation'] == 'merge_attempt_evidence_then_remove_duplicate'
assert by_row[1698]['retained_row_index'] == 1697
completed = list(csv.DictReader((H / 'confirmed_missing_pairs.csv').open(encoding='utf-8-sig')))
planned = list(csv.DictReader((H / 'planned_study_pairs.csv').open(encoding='utf-8-sig')))
assert len(completed) == 440 and len(planned) == 2
assert all(r['file_key'] == '5746d10c18005a08' for r in planned)
assert all(r['file_key'] != '5746d10c18005a08' for r in completed)
assert sha(H / 'fix_proposals.json') == '0e43a796b260ece0f7e1b8078b3341024131ab456ddbe0f15ffe6c3726e7821e'
assert sha(H / 'sol_review_decisions.json') == 'b67201cf27f9e78f6ea34dd039fce16d68fba5168279775232eb3e99d5435c32'
result = dict(status='passed', record_actions=len(actions), source_scope_proof_checks=proof_count,
              fresh_blind_reports=3, fresh_blind_literal_quotes=blind_quotes,
              completed_report_missing_pairs=440, planned_target_pairs=2,
              baseline_unchanged=True, canonical_changes_applied=False)
print(json.dumps(result, indent=2))
