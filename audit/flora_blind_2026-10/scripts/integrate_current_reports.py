#!/usr/bin/env python3
"""Integrate independently agreeing current-report decisions, retaining old reviews."""
import csv
import hashlib
import json
from pathlib import Path
B = Path(__file__).resolve().parents[1]
H = B / 'handoff'
P = B / 'evidence_followup/private/record_scope_20261101'
rows = list(csv.DictReader(Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv').open(encoding='utf-8-sig')))
review = json.loads((B / 'publication/completed_report_reviews_20261101.json').read_text())
keys = {1616: 'j9mfn', 1662: 'ahcpw', 1710: 'w34fb'}
current = []
for item in review['reviews']:
    i = item['input_row_index']
    packet = P / ('blind_' + keys[i])
    blind = json.loads((packet / 'coding.json').read_text())
    target = next(t for t in blind['targets'] if t['doi'].lower() == rows[i]['doi_o'].lower())
    extras = [t for t in blind['targets'] if t is not target]
    if extras:
        gate = json.loads((B / 'publication/gray_additional_target_parent_gate_20261101.json').read_text())
        assert i == 1710 and len(extras) == 1
        assert gate['verdict'] == 'not_target' and gate['export_missing_pair'] is False
        assert extras[0]['doi'].lower() == gate['candidate_doi'].lower()
    assert blind['study_status'] == item['study_status'] == 'completed'
    assert target['outcome'] == item['scientific_recommended'] == rows[i]['outcome']
    q = item['overall_verdict']
    raw = Path(q['source_path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == q['sha256']
    assert raw.decode()[q['character_start']:q['character_end']] == q['literal_contiguous_quote']
    assert raw[q['utf8_byte_start']:q['utf8_byte_end']].decode() == q['literal_contiguous_quote']
    manifest = item['source_read_manifest']
    assert manifest['full_source_read'] is True
    intervals = sorted(manifest['model_visible_character_ranges'])
    end = 0
    for a, b in intervals:
        assert a <= end and b >= a
        end = max(end, b)
    assert end == len(raw.decode())
    proof = {('quote' if k == 'literal_contiguous_quote' else k): v for k, v in q.items()}
    short = {
        1616: 'We found mixed support for the findings by Kozak et al. (2006).',
        1662: 'We found mixed support for the findings by Hsee and Rottenstreich (2004).',
        1710: 'we successfully replicated all the original effects',
    }[i]
    text = raw.decode()
    start = text.index(short)
    proof.update(quote=short, quote_sha256=hashlib.sha256(short.encode()).hexdigest(),
                 character_start=start, character_end=start+len(short),
                 utf8_byte_start=len(text[:start].encode()), utf8_byte_end=len(text[:start+len(short)].encode()),
                 section='discussion' if i == 1710 else 'conclusion')
    current.append(dict(case_id=f'row:{i}', input_row_index=i, file_key=item['file_key'],
        audit_status='current_completed_source_reviewed', decision_reference='current_source_decisions.json',
        application_hold='Use this outcome only with the verified completed report: update report identity, bibliography and quotation provenance together.',
        fields={'outcome': dict(disposition='confirmed_correct', confirmed_value=item['scientific_recommended'],
            proposed_value=None, rationale=item['rationale'], proofs=[proof],
            contrary_evidence=item['strongest_contrary_evidence'])},
        source_read_manifest=manifest, prior_source_decision_reference='sol_review_decisions.json',
        blind_validation_reference=str(packet / 'validation.json'),
        independently_agrees_with_blind_coding=True,
        additional_target_scope_reference='../publication/gray_additional_target_parent_gate_20261101.json' if extras else None,
        canonical_dataset_changes_applied=False))
assert {d['input_row_index'] for d in current} == set(keys)
(H / 'current_source_decisions.json').write_text(json.dumps(dict(
    status='current_report_decisions_conditional_on_record_rebinding', decisions=current,
    earlier_reviews_preserved='sol_review_decisions.json'), ensure_ascii=False, indent=2)+'\n')
print('Three current-report outcomes independently agree; old source-bound judgments preserved.')
