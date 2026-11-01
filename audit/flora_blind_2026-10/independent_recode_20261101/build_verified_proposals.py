#!/usr/bin/env python3
"""Export only parent-adjudicated cases passing independent evidence gates."""
import csv
import hashlib
import json
import re
from pathlib import Path

from prepare_packets import B, OUT, PACKETS
from project_prior_sol import project

BASELINE = Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv')
BASELINE_SHA = '6d391186dfb57263bbc6bb504e8561e0d1e25997b36417072c023812efaad9f7'


def read(path):
    return json.loads(path.read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def norm(value):
    return re.sub(r'[^\w]', '', value.casefold())


def identifier(value):
    value = value.strip().casefold()
    if value in ('', 'na', 'nan', 'null'):
        return ''
    value = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:\s*)', '', value).rstrip('/')
    match = re.fullmatch(r'(?:10\.17605/|https?://)?osf\.io/([a-z0-9]+)', value)
    return 'osf:' + match[1] if match else value


def ids(row, role):
    return {v for k in ('doi_' + role, 'alt_identifier_' + role)
            if (v := identifier(row.get(k, '')))}


def original_alignment(row, target, year_receipt=None):
    assert norm(row['title_o']) == norm(target['title']), 'Original title is not positively aligned'
    if row['year_o'] != target['year']:
        assert year_receipt, 'Original year/version needs separate adjudication'
        path = Path(year_receipt['path'])
        assert sha(path.read_bytes()) == year_receipt['sha256']
        metadata = read(path)['message']
        assert identifier(metadata['DOI']) in ids(row, 'o')
        assert norm(metadata['title'][0]) == norm(target['title'])
        assert row['year_o'] == str(metadata['published-online']['date-parts'][0][0])
        assert target['year'] == str(metadata['published-print']['date-parts'][0][0])
        assert metadata['volume'] == row['volume_o'] and metadata['issue'] == row['issue_o']
        assert norm(metadata['page']) == norm(row['pages_o'])
    authors = json.loads(row['author_o'])
    assert authors and all(norm(a['family']) in norm(target['authors']) for a in authors), 'Original authors differ'
    if target.get('doi'):
        assert identifier(target['doi']) in ids(row, 'o'), 'Original DOI differs'


def proof(packet, quote):
    raw = (packet / 'article.txt').read_bytes()
    text = raw.decode()
    assert quote and quote in text
    start = text.index(quote)
    end = start + len(quote)
    return dict(quote=quote, source_path=str(packet / 'article.txt'), source_sha256=sha(raw),
                character_start=start, character_end=end, utf8_start=len(text[:start].encode()),
                utf8_end=len(text[:end].encode()), quote_sha256=sha(quote.encode()))


def checked_replacements(row, result, target, decision):
    replacements = decision['replacement_fields'].copy()
    assert set(replacements) == set(decision['proposal_fields']) <= {'type', 'outcome'}, 'Unvalidated field replacement'
    if 'type' in replacements:
        assert replacements['type'] == result['record_type']
    else:
        assert row['type'] == result['record_type'], 'Record type requires a joint remedy'
    if 'outcome' in replacements:
        expected = (target['outcome'] if result['record_type'] == 'replication' else
                    ', '.join(target[k] for k in ('outcome_computation', 'outcome_robustness') if target.get(k)))
        assert replacements['outcome'] == expected, 'Replacement differs from independently coded value'
    return replacements


def build():
    assert sha(BASELINE.read_bytes()) == BASELINE_SHA, 'Frozen baseline changed'
    with BASELINE.open(encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    proposals = read(B / 'handoff/correction_proposals.json')['changes']
    holds = read(B / 'handoff/review_reliability.json').get('holds', {})
    inventory = read(OUT / 'source_inventory.json')
    prior_checks = read(OUT / 'prior_sol_receipt_checks.json')['documents']
    decisions = read(OUT / 'parent_acceptance_decisions.json')['cases']
    result = []
    for decision in decisions:
        row_index, doc = decision['input_row_index'], decision['document_id']
        row, packet = rows[row_index], PACKETS / doc
        assert decision['disposition'] == 'accepted_for_automatic_proposal'
        assert decision['positive_claim_alignment_parent_verified'] is True
        assert decision['counterevidence_parent_adjudicated'] is True
        assert decision['dependent_fields_parent_verified'] is True
        assert 'row:' + str(row_index) not in holds, 'Live scientific hold'
        source = next(d for d in inventory['documents'] if d['document_id'] == doc)
        assert identifier(source['parent_work_key']) in ids(row, 'r'), 'Current work is not aligned'
        opus_dir = Path(decision['opus_output'])
        opus = read(opus_dir / 'coding.json')
        opus_valid = read(opus_dir / 'parent_validation.json')
        assert opus_valid['output_hashes']['coding.json'] == sha((opus_dir / 'coding.json').read_bytes()), 'Opus coding changed after validation'
        assert opus['evidence_level'] == 'full_text', 'Abstracts cannot establish this set'
        assert opus_valid['full_model_visible_reading_receipts_verified'] is True
        assert opus_valid['frozen_packet_inputs_verified'] is True
        if decision['sol_kind'] == 'prior':
            check = prior_checks[doc]
            assert check['status'].startswith('exact_source_complete_tool_receipt_verified')
            assert sha(Path(check['prior_coding_path']).read_bytes()) == check['prior_coding_sha256']
            sol, transcription = project(packet, read(Path(check['prior_coding_path'])))
            assert transcription['scientific_labels_modified'] is False
            sol_path = check['prior_coding_path']
        else:
            sol_dir = Path(decision['sol_output'])
            sol, sol_valid = read(sol_dir / 'coding.json'), read(sol_dir / 'parent_validation.json')
            assert sol_valid['output_hashes']['coding.json'] == sha((sol_dir / 'coding.json').read_bytes()), 'Sol coding changed after validation'
            assert sol_valid['full_model_visible_reading_receipts_verified'] is True
            assert sol_valid['frozen_packet_inputs_verified'] is True
            sol_path = str(sol_dir / 'coding.json')
        assert opus['text_sha256'] == sol['text_sha256'] == sha((packet / 'article.txt').read_bytes())
        oi, si = decision['opus_target_index'], decision['sol_target_index']
        ot, st = opus['targets'][oi], sol['targets'][si]
        original_alignment(row, ot, decision.get('original_year_metadata_receipt'))
        original_alignment(row, st, decision.get('original_year_metadata_receipt'))
        assert ot['outcome_confident'] is True and st['outcome_confident'] is True
        for key, expected in decision['agreed_target_values'].items():
            assert ot[key] == st[key] == expected, 'Independent target labels disagree: ' + key
        assert opus['record_type'] == sol['record_type'] == decision['agreed_record_type']
        reviewer = Path(decision['review_dir'])
        review, validation = read(reviewer / 'review.json'), read(reviewer / 'parent_validation.json')
        for name, expected in decision['accepted_review_file_hashes'].items():
            assert sha((reviewer / name).read_bytes()) == expected, 'Reviewed evidence changed: ' + name
        assert validation['proof_count_verified'] > 0
        for field in decision['proposal_fields']:
            matches = [x for x in review['reviews'] if x.get('row_index', x.get('row_id', x.get('row'))) == row_index
                       and x.get('field', x.get('field_reviewed')) == field
                       and x.get('status', x.get('disposition')) == 'supported_correction']
            assert len(matches) == 1, 'Missing independent adversarial support'
            prop = next(p for p in proposals if int(p['input_row_index']) == row_index and p['field'] == field)
            assert prop['expected_before_full_record_sha256'] == digest(row)
            assert not prop.get('application_hold'), 'Unresolved proposal dependency'
        duplicate_rows = [i for i, other in enumerate(rows) if i != row_index
                          and ids(other, 'r') & ids(row, 'r') and ids(other, 'o') & ids(row, 'o')]
        assert not duplicate_rows, 'Existing pair duplicate requires a joint remedy: ' + str(duplicate_rows)
        replacements = checked_replacements(row, opus, ot, decision)
        quote = ot[decision['replacement_quote_field']]
        replacements['outcome_quote'] = quote
        replacements['outcome_quote_source'] = decision['replacement_quote_section']
        assert set(replacements).issubset(row), 'Unknown CSV columns'
        evidence = [proof(packet, quote)]
        for key in decision['supporting_quote_fields']:
            evidence.append(proof(packet, opus[key] if key == 'record_type_quote' else ot[key]))
        operations = [dict(operation='set_field', field=field, expected_before={field: row[field]},
                           proposed_value=value, input_row_index=row_index,
                           expected_before_full_record_sha256=digest(row), atomic_group='row:' + str(row_index))
                      for field, value in replacements.items() if value != row[field]]
        result.append(dict(case_id='row:' + str(row_index), input_row_index=row_index,
                           status='ready_for_batch_approval', proposal_fields=decision['proposal_fields'],
                           expected_before_full_record_sha256=digest(row), expected_before=row,
                           replacements=replacements, operations=operations,
                           apply_all_fields_atomically=True, original_pair_duplicate_rows=duplicate_rows,
                           evidence=evidence, rationale=decision['rationale'], limits=decision['limits'],
                           independent_inputs=dict(opus=str(opus_dir / 'coding.json'), sol=sol_path,
                                                   reviewer=str(reviewer / 'review.json'))))
    output = dict(schema_version=1, status='incremental_verified_proposals_cohort_in_progress',
                  baseline_sha256=BASELINE_SHA, canonical_changes_applied=False, user_approval_recorded=False,
                  automatic_fields_verified=sum(len(c['proposal_fields']) for c in result),
                  case_count=len(result), cases=result,
                  implementation_rules=['Obtain batch approval before implementation; this file records verified proposals, not approvals.',
                                        'Verify the frozen file and complete row hash; apply all fields of each case atomically.',
                                        'Keep prior decisions and source histories. No original identity is changed by these cases.',
                                        'Do not re-enable other outcome proposals from this incremental file.'])
    (OUT / 'automatically_verified_proposals.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ('case_count', 'automatic_fields_verified', 'canonical_changes_applied')}))
    return output


if __name__ == '__main__':
    build()
