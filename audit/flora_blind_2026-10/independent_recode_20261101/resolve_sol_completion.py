"""Resolve the 46 apparent Sol gaps without turning coverage into acceptance.

Existing audited comparisons are reused with their exact qualifications. A
superseded view is explicitly distinct from a literal comparison of that view.
No source, original coding, export or acceptance decision is rewritten.
"""
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from project_prior_sol import project
from validate_output import coding_quotes

T = Path(__file__).resolve().parent
P = T.parent / 'evidence_followup/private/independent_recode_20261101'
BASE_COMMIT = 'd64a31fb1'
EXACT = 'exact_source_complete_before_construction_strict_projection_verified'
NORMALIZED = {
    'ordered_complete_source_verified_through_recorded_header_and_whitespace_normalization',
    'abstract_body_and_literal_metadata_receipts_verified_whitespace_only_separator_reconstruction',
    'complete_literal_body_and_unique_whitespace_reference_display_verified',
    'complete_source_display_via_verified_whitespace_serialization_chain_strict_projection_verified',
    'complete_body_and_metadata_visible_with_verified_normalization_chain',
}
ALTERNATE = 'same_pdf_complete_alternate_layout_read_verified_registered_view_not_printed'
PRIOR_STATUSES = {EXACT, ALTERNATE} | NORMALIZED
FRESH = ['document_0011', 'document_0012', 'document_0013', 'document_0384',
         'document_0396', 'document_0470', 'document_0472', 'document_0473',
         'document_0474', 'document_0475', 'document_0476', 'document_0477',
         'document_0660']
ALIASES = {'document_0001': 'document_0691', 'document_0471': 'document_0690',
           'document_0499': 'document_0689'}
SUPERSEDED = {'document_0047': 'document_0686', 'document_0115': 'document_0479'}
RESOLVED_STATUSES = {
    'comparison_available_with_recorded_qualification', 'existing_comparison_reused',
    'superseded_view_resolved_to_current_report', 'new_comparison_parent_validated',
    'comparison_available_from_verified_identical_report_body',
}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bound_references(obj):
    """Hash opaque native wrappers without accessing provider reasoning text."""
    result = []
    for key, value in obj.items():
        if not key.endswith('_path') or not isinstance(value, str):
            continue
        hash_key = key[:-5] + '_sha256'
        if isinstance(obj.get(hash_key), str):
            assert sha(value) == obj[hash_key], key
            result.append({'path': value, 'sha256': obj[hash_key]})
    return result


def qualify_prior(doc, record, queue):
    assert record['status'] in PRIOR_STATUSES, 'Unrecognized prior qualification'
    assert not record.get('fresh_sol_read_needed'), 'Reading is still required'
    assert not record.get('quote_check_failures'), 'Unresolved quote failure'
    packet = P / doc
    assert sha(packet / 'article.txt') == record['source_sha256']
    assert sha(record['prior_coding_path']) == record['prior_coding_sha256']
    codebook = record['original_codebook_prompt_proof']
    if sha(T.parent / 'codebook.md') not in json.dumps(codebook):
        wrapper = read(record['receipt_path'])
        page = wrapper.get('structuredContent', wrapper)
        # Filter by provider item type before accessing its text.
        prompts = [x for x in page['items'] if x['type'] == 'user_message'
                   and x['itemId'] == codebook['itemId']]
        assert len(prompts) == 1 and not prompts[0]['textTruncated'], 'Incomplete codebook prompt'
        prompt = prompts[0]['text']
        assert hashlib.sha256(prompt.encode()).hexdigest() == codebook['prompt_sha256']
        assert (T.parent / 'codebook.md').read_text() in prompt, 'Codebook mismatch'
    assert record['receipt_pagination_complete']
    refs = bound_references(record) + bound_references(queue)
    assert any('receipt' in x['path'] or 'audit' in x['path'] for x in refs)
    cached = (queue.get('derived_prior_sol_projection_path')
              or record.get('derived_projection_path')
              or record.get('derived_literal_projection_path'))
    expected = (queue.get('derived_prior_sol_projection_sha256')
                or record.get('derived_projection_sha256'))
    assert cached and expected and sha(cached) == expected
    projected, ledger = project(packet, read(record['prior_coding_path']))
    assert projected == read(cached), 'Projection drift'
    assert ledger['scientific_labels_modified'] is False
    if record['status'] == EXACT:
        assert record['original_tool_output_contains_entire_exact_source']
        assert record['coverage_gaps'] == []
        kind = 'verified_exact_registered_source_prior_reading'
    elif record['status'] == ALTERNATE:
        assert record['alternate_layout_entire_print_verified']
        assert record['bridge_exact_registered_source_equality']
        assert not record['automatic_export_receipt_rule_satisfied']
        kind = 'verified_same_pdf_alternate_layout_with_explicit_export_limit'
    else:
        assert record.get('projection_passed') and record.get('derived_projection_saved')
        kind = 'verified_complete_content_with_normalization_qualification'
    return {'status': 'comparison_available_with_recorded_qualification',
            'route': 'reuse_existing_prior', 'coverage_class': kind,
            'source_sha256': record['source_sha256'],
            'prior_status': record['status'], 'sol_coding_path': cached,
            'sol_coding_sha256': sha(cached), 'original_prior_coding_path': record['prior_coding_path'],
            'original_prior_coding_sha256': record['prior_coding_sha256'],
            'qualified_input_references': refs,
            'registered_literal_reading_verified': record['status'] == EXACT,
            'source_qualification_requires_field_gate_review': record['status'] != EXACT,
            'scope_limit': record.get('scope_limit', record.get('note', '')),
            'new_model_reading': False, 'scientific_acceptance': False}


def current_comparison(doc, queue, state):
    entry = queue[doc]
    path = entry.get('fresh_sol_coding_path') or entry.get('derived_prior_sol_projection_path')
    assert path and Path(path).exists(), (doc, 'Missing existing comparator')
    result = read(path)
    assert result['text_sha256'] == sha(P / doc / 'article.txt')
    refs = bound_references(entry)
    if doc in state['validated_fresh_sol_documents']:
        pv = Path(path).parent / 'parent_validation.json'
        proof = read(pv)
        assert proof['full_model_visible_reading_receipts_verified']
        assert proof['frozen_packet_inputs_verified']
        assert proof['output_hashes']['coding.json'] == sha(path)
        refs.append({'path': str(pv), 'sha256': sha(pv)})
    else:
        assert refs and entry.get('parent_scope_validation_path')
    return {'document_id': doc, 'sol_coding_path': str(path),
            'sol_coding_sha256': sha(path), 'source_sha256': result['text_sha256'],
            'qualified_input_references': refs}


def build():
    state = read(T / 'state.json')
    queue = read(T / 'comparison_review_queue.json')['documents']
    prior = read(T / 'prior_sol_receipt_checks.json')['documents']
    rel = str(T.relative_to(Path.cwd()) / 'state.json')
    initial = json.loads(subprocess.check_output(['git', 'show', BASE_COMMIT + ':' + rel]))
    active = {d['document_id'] for d in read(T / 'source_inventory.json')['documents'] if d['active']}
    active |= {d['document_id'] for d in read(T / 'source_upgrades.json')['upgrades']}
    opus = set(initial['validated_opus_documents']) | {x['document_id'] for x in initial['parent_metadata_projections']}
    old_sol = set(initial['validated_fresh_sol_documents']) | {
        d for d, p in prior.items() if p['status'].startswith('exact_source_complete_tool_receipt_verified')
        and 'blocked' not in p['status']}
    missing = sorted(active & opus - old_sol)
    assert len(missing) == 46
    reused = {d for d in missing if prior.get(d, {}).get('status') in PRIOR_STATUSES}
    assert len(reused) == 27
    assert set(missing) == reused | set(ALIASES) | set(SUPERSEDED) | set(FRESH) | {'document_0661'}
    entries = {}
    for doc in missing:
        if doc in reused:
            entry = qualify_prior(doc, prior[doc], queue[doc])
        elif doc in ALIASES or doc in SUPERSEDED:
            target = (ALIASES | SUPERSEDED)[doc]
            comparison = current_comparison(target, queue, state)
            same = sha(P / doc / 'article.txt') == comparison['source_sha256']
            assert same == (doc in ALIASES)
            if doc == 'document_0047':
                assert queue[doc]['superseded_by_full_report_document'] == target
            if doc == 'document_0115':
                assert queue[doc]['completed_source_sha256'] == comparison['source_sha256']
            entry = {'status': 'existing_comparison_reused' if same else 'superseded_view_resolved_to_current_report',
                     'route': 'exact_source_alias' if same else 'superseded_source_view',
                     'resolved_comparison': comparison, 'registered_old_view_reading_claimed': same,
                     'new_model_reading': False, 'scientific_acceptance': False,
                     'scope_limit': 'No outcomes may transfer across versions. Bind fields to the correct current report; preserve original source/version and scientific holds.'}
        elif doc == 'document_0661':
            entry = {'status': 'waiting_for_representative_comparison',
                     'route': 'same_report_body_reuse_after_0660',
                     'representative_document_id': 'document_0660',
                     'new_model_reading': False, 'scientific_acceptance': False,
                     'scope_limit': 'One report with two provenance wrappers; never count a second vote or dispatch a duplicate reading.'}
            if 'document_0660' in state['validated_fresh_sol_documents']:
                a, b = (P / 'document_0660/article.txt').read_text(), (P / 'document_0661/article.txt').read_text()
                assert a[185:] == b[185:]
                representative = current_comparison('document_0660', queue, state)
                assert all(quote in a[185:] for _, quote in coding_quotes(read(representative['sol_coding_path'])))
                entry.update(status='comparison_available_from_verified_identical_report_body',
                             representative_comparison=representative,
                             identical_body_sha256=hashlib.sha256(a[185:].encode()).hexdigest(),
                             body_character_start=185, all_scientific_quotes_verified_in_identical_body=True,
                             registered_wrapper_itself_read=False)
        else:
            task = next((t for t in state['tasks'] if t.get('role') == 'blind_comparison_coder'
                         and doc in t.get('packet_ids', [])), None)
            entry = {'status': task['status'] if task else 'pending_fresh_comparison',
                     'route': 'first_eligible_fresh_comparison', 'new_model_reading': True,
                     'scientific_acceptance': False}
            if task:
                entry.update(taskId=task['taskId'], attempt=task['attempt'])
            if doc in state['validated_fresh_sol_documents']:
                entry.update(status='new_comparison_parent_validated',
                             comparison=current_comparison(doc, queue, state))
        entries[doc] = entry
    # A terminal task failure is still a coverage gap. Unknown states fail closed.
    pending = [d for d, x in entries.items() if x['status'] not in RESOLVED_STATUSES]
    return {'schema_version': 1, 'scope': 'User-requested reconciliation of 46 apparent Sol gaps, 2026-11-03',
            'user_instruction': 'fix the 46 missing Sol. then get an opus thread to take over and build the full ledger and updated app',
            'baseline_commit': BASE_COMMIT, 'original_document_ids': missing,
            'route_counts': dict(Counter(x['route'] for x in entries.values())),
            'status_counts': dict(Counter(x['status'] for x in entries.values())),
            'documents': entries, 'pending_document_ids': pending,
            'coverage_work_complete': not pending,
            'all_fields_scientifically_accepted': False, 'canonical_changes_applied': False,
            'important_limits': ['Coverage is not scientific agreement, confidence or acceptance.',
                                 'Two alternate-layout readings retain their explicit strict-export limitation; no rule is silently weakened.',
                                 'Five normalization-qualified readings preserve their technical qualifications.',
                                 'Superseded plans/abstracts are not recoded or presented as exact current-report views.',
                                 'Source, version, identity, confidence and policy holds remain.',
                                 'All seven provider-held sources and exhausted original-four budgets remain untouched.'],
            'handoff': 'Launch Opus takeover only after remaining fresh comparisons are parent-validated and all routes are explicitly accounted for.'}


if __name__ == '__main__':
    result = build()
    path = T / 'sol_completion_20261103.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['route_counts', 'status_counts', 'pending_document_ids', 'coverage_work_complete']}))
