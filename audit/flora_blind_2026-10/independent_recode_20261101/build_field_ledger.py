#!/usr/bin/env python3
"""Reconcile frozen proposals, blind codings, reviews and current FLoRA, field by field.

Read-only over every scientific artifact. Writes field_ledger.json and nothing else.
No model call, network request, approval or dataset change happens here.
Article packets of provider-held documents are never opened.
"""
import csv
import difflib
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

T = Path(__file__).resolve().parent
B = T.parent
ROOT = B.parents[1]
P = B / 'evidence_followup/private/independent_recode_20261101'
BASELINE = Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv')
BASELINE_SHA = '6d391186dfb57263bbc6bb504e8561e0d1e25997b36417072c023812efaad9f7'
CURRENT_COMMIT = '1204ec81f21cad9af1c6cddb92bbb718d8c03fe4'
CURRENT_SHA = 'c783e586431ebd6b52a6fdb94caba770bf7fa41333982ca6fc8e9b44a9887228'
OUTPUT = T / 'field_ledger.json'

PROVIDER_HELD = {'document_0366', 'document_0367', 'document_0374', 'document_0375',
                 'document_0463', 'document_0464', 'document_0465'}
SOURCE_ORDER_HELD = {'document_0096'}
HEADER_ONLY = {'document_0656', 'document_0662'}

# Prior readings count only by exact name; nothing qualifies by prefix.
PRIOR_ELIGIBLE = {
    'exact_source_complete_tool_receipt_verified',
    'exact_source_complete_tool_receipt_verified_strict_projection_verified',
    'exact_source_complete_tool_receipt_verified_with_whitespace_only_quote_transcription',
    'exact_source_complete_tool_receipt_verified_registered_normalization',
    'exact_source_complete_before_construction_strict_projection_verified',
}
PRIOR_QUALIFIED = {
    'ordered_complete_source_verified_through_recorded_header_and_whitespace_normalization': 'normalization_chain',
    'abstract_body_and_literal_metadata_receipts_verified_whitespace_only_separator_reconstruction': 'normalization_chain',
    'complete_literal_body_and_unique_whitespace_reference_display_verified': 'normalization_chain',
    'complete_source_display_via_verified_whitespace_serialization_chain_strict_projection_verified': 'normalization_chain',
    'complete_body_and_metadata_visible_with_verified_normalization_chain': 'normalization_chain',
    'same_pdf_complete_alternate_layout_read_verified_registered_view_not_printed': 'alternate_layout',
    'exact_source_complete_tool_receipt_verified_parent_annotation_projection_verified': 'parent_annotation_projection',
}

STATES = {
    'reviewed_export_candidate': 'Protected export: two confident readings and a source review support it',
    'record_action_candidate': 'Protected export: whole-record exclusion, kept apart from field edits',
    'adversary_supported_candidate': 'Two confident readings and a completed adversarial read support it',
    'agreement_pending_adversarial_review': 'Two confident readings agree with the proposal; adversarial read outstanding',
    'agreement_needs_authoritative_metadata': 'Two readings agree on a different original; authoritative bibliography outstanding',
    'close_read_supported_candidate': 'Both readers back the change, and one more read of the paper finds the existing value wrong',
    'close_read_keep_existing': 'One more read of the paper finds the existing value defensible, so it stays',
    'agreement_needs_close_read': 'Both readers back the change, but one is unsure or the check was not confident; one more read decides',
    'no_agreement_keep_existing': 'The readers do not agree on a new value and at least one is unsure, so the existing value stays',
    'adversary_held': 'Adversarial read did not support an automatic correction',
    'withdraw_both_roles_confirm_frozen': 'Both roles confidently keep the frozen value, so the proposal should be withdrawn',
    'withdrawn_source_adjudicated': 'Already withdrawn after source review',
    'third_value_agreement': 'Both roles agree on a value that is neither frozen nor proposed',
    'disagreement_confident': 'Both roles are confident and disagree',
    'policy_cannot_be_determined': 'Proposal is cannot_be_determined, which is never an automatic fix',
    'individual_policy_hold': 'Formal individual-case hold',
    'record_level_rule': 'Needs a whole-record rule: removal, merge, split or rebinding',
    'binding_unresolved_document': 'Multi-report work: no single current report is positively bound',
    'target_not_bound': 'A role names no target positively matching this original',
    'no_eligible_comparator': 'No eligible Sol reading for this source view',
    'source_gap': 'Only abstract-level or incomplete source text',
    'provider_hold': 'Provider-refused source; permanently held in this audit',
    'source_order_hold': 'Source-order continuity hold',
    'header_only_hold': 'Header-only source view',
}
READY_STATES = {'reviewed_export_candidate', 'adversary_supported_candidate', 'close_read_supported_candidate'}
# Parent labels that only record a pending step. All other labels stay visible as flags.
CLEAN_PENDING_LABELS = {
    'missing_sol_completed_scientific_comparison_pending',
    'fresh_comparison_mechanically_validated_scientific_alignment_pending',
    'genuine_prior_complete_source_receipt_verified_comparison_pending',
    'genuine_blind_outcome_agreement_pending_primary_source_review',
    'genuine_blind_target_outcome_agreement_pending_primary_source_review',
    'genuine_blind_central_comparative_failure_agreement_pending_source_review',
}
PRIMARY_REASONS = {
    'provider_hold', 'source_order_hold', 'header_only_hold', 'withdrawn_source_adjudicated',
    'formal_individual_hold', 'reliability_hold', 'record_action_dependency', 'remove_row_proposal',
    'conditional_application_hold', 'document_binding_ambiguous', 'target_unbound_opus',
    'target_unbound_sol', 'target_multibound', 'opus_absent', 'comparator_absent',
    'comparator_ineligible', 'comparator_normalization_chain', 'comparator_alternate_layout',
    'comparator_parent_annotation_projection', 'abstract_level_evidence', 'prospective_status',
    'unconfident_opus', 'unconfident_sol', 'both_confident_on_frozen', 'both_confident_third_value',
    'confident_disagreement', 'cannot_be_determined_value', 'full_text_gap', 'in_protected_export',
    'in_protected_record_actions', 'adversary_pending', 'adversary_supported', 'adversary_not_supported',
    'adversary_quote_failed', 'adversary_below_high_confidence', 'qa_second_read_not_upheld', 'needs_authoritative_bibliography', 'type_change_needs_axes',
    'parent_scope_flag', 'parent_hold_flag', 'literal_recheck_failed', 'validator_unproved_evidence',
    'prior_reading_differs', 'record_exclusion_rule', 'relink_would_duplicate_pair',
    'close_read_correct', 'close_read_keep_existing',
}


def read(path):
    return json.loads(Path(path).read_text())


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def resolve(path):
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def norm(value):
    return re.sub(r'[^\w]', '', (value or '').casefold())


def spaced(text):
    return ' '.join((text or '').split())


def identifier(value):
    value = (value or '').strip().casefold()
    if value in ('', 'na', 'nan', 'null'):
        return ''
    value = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:\s*)', '', value).rstrip('/')
    match = re.fullmatch(r'(?:10\.17605/|https?://)?osf\.io/([a-z0-9]+)', value)
    return 'osf:' + match[1] if match else value


def side_ids(row, side):
    return {v for k in ('doi_' + side, 'alt_identifier_' + side) if (v := identifier(row.get(k, '')))}


def surname(authors):
    authors = authors or ''
    if authors.startswith('['):
        try:
            return json.loads(authors)[0].get('family', '')
        except (ValueError, IndexError, AttributeError):
            pass
    match = re.match(r'\s*([^\s,]+)', authors)
    return match[1] if match else ''


def identity_of_row(row):
    return dict(ids=side_ids(row, 'o'), title=row['title_o'], year=row['year_o'], author=row['author_o'])


def identity_of_proposal(value):
    return dict(ids={v for v in [identifier(value.get('doi', ''))] if v}, title=value.get('title', ''),
                year=str(value.get('year', '')), author=value.get('authors', ''))


def target_binding(target, identity):
    """Positive identity only: printed identifier, or title corroborated by year or author."""
    printed = identifier(target.get('doi', ''))
    if printed and printed in identity['ids']:
        return 'identifier'
    a, b = norm(target.get('title')), norm(identity['title'])
    if not a or not b:
        return None
    if a == b:
        return 'title_exact'
    corroborated = (target.get('year') and target['year'] == identity['year']) or (
        surname(target.get('authors')) and norm(surname(target['authors'])) == norm(surname(identity['author'])))
    if not corroborated:
        return None
    if len(a) >= 25 and len(b) >= 25 and (a in b or b in a):
        return 'title_contained'
    if difflib.SequenceMatcher(None, a, b).ratio() >= 0.93:
        return 'title_close'
    return None


AXES = {'computationally reproducible': ('computation', 'computationally reproducible'),
        'computational issues': ('computation', 'computational issues'),
        'technical failure': ('computation', 'technical failure'),
        'computation not checked': ('computation', 'not checked'),
        'robust': ('robustness', 'robust'),
        'robustness challenges': ('robustness', 'robustness challenges'),
        'robustness not checked': ('robustness', 'not checked')}


def parse_axes(outcome):
    """Frozen outcome strings pack two axes. Current uses 'not checked' for either."""
    parts = [p.strip() for p in (outcome or '').split(',')]
    result = {'outcome_computation': None, 'outcome_robustness': None}
    for index, part in enumerate(parts):
        if part in AXES:
            axis, value = AXES[part]
            result['outcome_' + axis] = value
        elif part == 'not checked':
            result['outcome_computation' if index == 0 else 'outcome_robustness'] = 'not checked'
    return result


def frozen_field_value(field, proposed, before):
    if field == 'type':
        return before['type']
    if field == 'outcome' and isinstance(proposed, dict):
        axes = parse_axes(before['outcome'])
        return {k: axes.get(k) for k in proposed}
    if field == 'outcome':
        return before['outcome']
    if field in ('outcome_computation', 'outcome_robustness'):
        return parse_axes(before['outcome'])[field]
    return None


QUOTE_KEY = {'outcome': 'outcome_quote', 'outcome_computation': 'outcome_computational_quote',
             'outcome_robustness': 'outcome_robustness_quote', 'original': 'evidence_quote'}


def coder_value(field, proposed, coding, target):
    if field == 'type':
        return coding.get('record_type')
    if target is None:
        return None
    if field == 'outcome' and isinstance(proposed, dict):
        return {k: target.get(k) for k in proposed}
    if field in ('outcome', 'outcome_computation', 'outcome_robustness'):
        return target.get(field)
    return None


def literal_in_source(quote, source_text):
    """Whitespace-tolerant check; multi-part quotes must each be literal."""
    parts = [spaced(p) for p in re.split(r'\s*(?:\|\||\[\.\.\.\]|\.\.\.|…)\s*', quote or '') if spaced(p)]
    return bool(parts) and all(p in source_text for p in parts)


def classify_field(f):
    """Assign one closed primary state from gathered facts. Pure, so failures can be planted."""
    reasons = list(f.get('standing_reasons', []))
    def out(state, *more):
        return state, sorted(set(reasons) | set(more))
    if f['provider_held']:
        return out('provider_hold', 'provider_hold')
    if f['source_order_held']:
        return out('source_order_hold', 'source_order_hold')
    if f['header_only']:
        return out('header_only_hold', 'header_only_hold')
    if f['withdrawn']:
        return out('withdrawn_source_adjudicated', 'withdrawn_source_adjudicated')
    if f['formal_hold']:
        return out('individual_policy_hold', 'formal_individual_hold')
    if f['reliability_hold']:
        return out('individual_policy_hold', 'reliability_hold')
    if f['in_record_actions']:
        return out('record_action_candidate', 'in_protected_record_actions')
    if f['in_export']:
        return out('reviewed_export_candidate', 'in_protected_export')
    if f['remove_row']:
        return out('record_level_rule', 'remove_row_proposal')
    if f['record_dependency']:
        return out('record_level_rule', 'record_action_dependency')
    if f['application_hold']:
        return out('record_level_rule', 'conditional_application_hold')
    if f['field'] == 'type' and f['proposed_value'] == 'not_a_replication':
        return out('record_level_rule', 'record_exclusion_rule')
    if f['relink_duplicate']:
        return out('record_level_rule', 'relink_would_duplicate_pair')
    if f['field'] == 'type' and f['proposed_value'] == 'reproduction' and not f['type_has_axis_partner']:
        return out('record_level_rule', 'type_change_needs_axes')
    if f['document_id'] is None:
        return out('binding_unresolved_document', 'document_binding_ambiguous')
    opus, sol = f['opus'], f['sol']
    if not opus['present']:
        return out('no_eligible_comparator', 'opus_absent')
    if not sol['present']:
        return out('no_eligible_comparator', 'comparator_absent')
    if not sol['eligible_for_comparison']:
        return out('no_eligible_comparator', 'comparator_ineligible')
    if opus['evidence_level'] != 'full_text' or sol['evidence_level'] != 'full_text':
        return out('source_gap', 'abstract_level_evidence')
    if f['full_text_gap']:
        return out('source_gap', 'full_text_gap')
    if f['field'] != 'type':
        for role, coder in (('opus', opus), ('sol', sol)):
            if coder['binding_count'] > 1:
                return out('target_not_bound', 'target_multibound')
            if coder['binding_count'] == 0:
                return out('target_not_bound', 'target_unbound_' + role)
    if 'prospective' in (opus['study_status'], sol['study_status']):
        return out('record_level_rule', 'prospective_status')
    if f['proposed_is_cannot_be_determined']:
        return out('policy_cannot_be_determined', 'cannot_be_determined_value')
    relation_opus, relation_sol = opus['relation'], sol['relation']
    close = f.get('close_read')
    if close:
        if close['verdict'] == 'keep_existing':
            return out('close_read_keep_existing', 'close_read_keep_existing')
        assert close['verdict'] == 'correct' and relation_opus == relation_sol == 'proposed', f['field']
        if f['field'] == 'original' and not close.get('authoritative_metadata_verified'):
            return out('agreement_needs_authoritative_metadata', 'needs_authoritative_bibliography')
        return out('close_read_supported_candidate', 'close_read_correct')
    unconfident = [r for r, c in (('opus', opus), ('sol', sol)) if not c['confident']]
    if relation_opus == relation_sol == 'frozen' and not unconfident:
        return out('withdraw_both_roles_confirm_frozen', 'both_confident_on_frozen')
    if unconfident:
        codes = ['unconfident_' + r for r in unconfident]
        if relation_opus == relation_sol == 'proposed':
            return out('agreement_needs_close_read', *codes)
        return out('no_agreement_keep_existing', *codes)
    if relation_opus != relation_sol or (relation_opus == 'other' and not f['coders_agree_exactly']):
        return out('disagreement_confident', 'confident_disagreement')
    if relation_opus == 'other':
        return out('third_value_agreement', 'both_confident_third_value')
    if relation_opus != 'proposed':
        return out('no_agreement_keep_existing')
    # Both confident and exact on the proposed value from here on.
    if not (opus['literal_quote_ok'] and sol['literal_quote_ok']):
        return out('no_eligible_comparator', 'literal_recheck_failed')
    if not (opus['validator_clean'] and sol['validator_clean']):
        return out('no_eligible_comparator', 'validator_unproved_evidence')
    if sol.get('qualification'):
        # Recorded for transparency only: how the text was extracted does not hold back a correction.
        reasons.append('comparator_' + sol['qualification'])
    review = f.get('adversary')
    if review:
        if not review['quote_verified']:
            return out('adversary_held', 'adversary_quote_failed')
        if review['verdict'] != 'supported':
            return out('adversary_held', 'adversary_not_supported')
        if review.get('qa_status') == 'flip':
            return out('adversary_held', 'qa_second_read_not_upheld')
        if review.get('qa_status') in ('softened', 'unusable'):
            return out('agreement_needs_close_read', 'qa_second_read_not_upheld')
        if review.get('confidence') != 'high':
            return out('agreement_needs_close_read', 'adversary_below_high_confidence')
        if f['field'] == 'original' and not review['authoritative_metadata_verified']:
            return out('agreement_needs_authoritative_metadata', 'needs_authoritative_bibliography')
        return out('adversary_supported_candidate', 'adversary_supported')
    return out('agreement_pending_adversarial_review', 'adversary_pending')


def absent_as_none(value):
    return None if value in ('NA', '', None) else value


def current_value(field, proposed, row):
    if field == 'type':
        return row['type']
    if field == 'outcome' and isinstance(proposed, dict):
        return {k: absent_as_none(row.get(k)) for k in proposed}
    if field in ('outcome', 'outcome_computation', 'outcome_robustness'):
        return absent_as_none(row.get(field))
    if field == 'original':
        return dict(doi=row['doi_o'], title=row['title_o'], year=row['year_o'], authors=row['author_o'])
    return None


def current_relation(field, proposed, frozen_value, row, frozen_row=None):
    """Compare proposed, frozen and current. Only exact equality counts."""
    if field == 'original':
        if not isinstance(proposed, dict) or 'title' not in proposed:
            return 'record_action_not_comparable'
        target = current_value(field, proposed, row)
        if target_binding(target, identity_of_proposal(proposed)):
            return 'already_equal'
        return 'unchanged_from_frozen' if target_binding(target, identity_of_row(frozen_row)) else 'third_value'
    value = current_value(field, proposed, row)
    if value == proposed:
        return 'already_equal'
    return 'unchanged_from_frozen' if value == frozen_value else 'third_value'


def build_identity_index(rows):
    pairs, titles = defaultdict(set), defaultdict(set)
    for index, row in enumerate(rows):
        for a in side_ids(row, 'o'):
            for b in side_ids(row, 'r'):
                pairs[(a, b)].add(index)
        if norm(row['title_o']) and norm(row['title_r']):
            titles[(norm(row['title_o']), norm(row['title_r']))].add(index)
    return dict(pairs=pairs, titles=titles, rows=rows)


def pair_candidates(row, index):
    found = set()
    for a in side_ids(row, 'o'):
        for b in side_ids(row, 'r'):
            found |= index['pairs'].get((a, b), set())
    return found


def bind_current(row, frozen_index, current_index, current_rows, relink=None):
    """Bind by both study identifiers with unique reverse lookup, or by both exact titles."""
    candidates = pair_candidates(row, current_index)
    reverse = pair_candidates(row, frozen_index)
    method = None
    if len(candidates) == 1 and len(reverse) == 1:
        current = current_rows[next(iter(candidates))]
        same_titles = norm(current['title_o']) == norm(row['title_o']) and norm(current['title_r']) == norm(row['title_r'])
        close = difflib.SequenceMatcher(None, norm(current['title_o']), norm(row['title_o'])).ratio() >= 0.9 and \
            difflib.SequenceMatcher(None, norm(current['title_r']), norm(row['title_r'])).ratio() >= 0.9
        if same_titles:
            method = 'both_identifiers_and_titles'
        elif close:
            method = 'both_identifiers_titles_close'
        else:
            return None, 'identifiers_match_titles_conflict', sorted(candidates)
        return next(iter(candidates)), method, sorted(candidates)
    if len(candidates) > 1 or len(reverse) > 1:
        return None, 'ambiguous_identifier_pair', sorted(candidates)
    key = (norm(row['title_o']), norm(row['title_r']))
    titles = current_index['titles'].get(key, set())
    if len(titles) == 1 and len(frozen_index['titles'].get(key, set())) == 1:
        candidate = next(iter(titles))
        if current_rows[candidate]['year_r'] == row['year_r']:
            return candidate, 'both_exact_titles_and_year', sorted(titles)
    if len(titles) > 1:
        return None, 'ambiguous_titles', sorted(titles)
    ids_r, ids_o = side_ids(row, 'r'), side_ids(row, 'o')
    if relink is not None:
        # Original may already be corrected: replication identifiers plus the proposed original.
        matches = [i for i, c in enumerate(current_rows) if side_ids(c, 'r') & ids_r and target_binding(
            dict(doi=c['doi_o'], title=c['title_o'], year=c['year_o'], authors=c['author_o']), relink)]
        if len(matches) == 1:
            return matches[0], 'replication_identifiers_and_proposed_original', matches
    if ids_o:
        # Unregistered reports have no identifier: original identifier plus exact report title or URL.
        url = norm(row.get('url_r'))
        matches = [i for i, c in enumerate(current_rows) if side_ids(c, 'o') & ids_o and (
            norm(c['title_r']) == norm(row['title_r']) or (url and url != 'na' and norm(c.get('url_r')) == url))]
        reverse_rows = [r for r in frozen_index['rows'] if side_ids(r, 'o') & ids_o and (
            norm(r['title_r']) == norm(row['title_r']) or (url and url != 'na' and norm(r.get('url_r')) == url))]
        if len(matches) == 1 and len(reverse_rows) == 1:
            return matches[0], 'original_identifier_and_report_title_or_url', matches
        if len(matches) > 1:
            return None, 'ambiguous_report_match', matches[:5]
    if ids_r:
        matches = [i for i, c in enumerate(current_rows) if side_ids(c, 'r') & ids_r]
        if len(matches) == 1:
            return matches[0], 'single_replication_row_original_differs', matches
        if matches:
            return None, 'replication_found_original_differs_several_rows', matches[:5]
    return None, 'no_positive_match', []


def load_current():
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{CURRENT_COMMIT}:output/flora.csv'])
    assert sha_bytes(raw) == CURRENT_SHA, 'Current FLoRA bytes changed'
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))


def clean_for_fields(entry):
    """An unproved list of background references excluded as targets is not outcome evidence."""
    return all(item['path'].startswith('$.excluded_candidates') for item in entry['unproved_evidence_entries'])


def validation_index():
    index = defaultdict(dict)
    for entry in read(T / 'current_validation_index.json')['validations']:
        role = 'opus' if entry['provider'] == 'claudeAgent' else 'sol'
        assert role == 'opus' or entry['model'] == 'gpt-6.1-sol'
        index[entry['document_id']][role] = entry
    return index


def coder_facts(coding, source, field, proposed, frozen_value, identity, frozen_identity, validator_clean=True,
                eligible=True, path=None, kind=None, qualification=None):
    facts = dict(present=coding is not None, eligible_for_comparison=eligible, path=path, kind=kind,
                 qualification=qualification, validator_clean=validator_clean)
    if coding is None:
        facts.update(evidence_level=None, study_status=None, binding_count=0, relation=None, confident=False,
                     literal_quote_ok=False, value=None)
        return facts
    bound = [(i, m) for i, t in enumerate(coding.get('targets', [])) if (m := target_binding(t, identity))]
    target = coding['targets'][bound[0][0]] if len(bound) == 1 else None
    value = coder_value(field, proposed, coding, target)
    if field == 'original':
        frozen_bound = any(target_binding(t, frozen_identity) for t in coding.get('targets', []))
        relation = 'proposed' if len(bound) == 1 else ('frozen' if frozen_bound else 'other')
    elif field == 'type' or target is not None:
        relation = 'proposed' if value == proposed else 'frozen' if value == frozen_value else 'other'
    else:
        relation = None
    if field == 'type':
        quote = coding.get('record_type_quote', '')
    elif target is None:
        quote = ''
    elif field == 'original':
        quote = target.get('evidence_quote', '')
    elif field == 'outcome' and isinstance(proposed, dict):
        quote = target.get('outcome_computational_quote', '') or target.get('outcome_robustness_quote', '')
    else:
        quote = target.get(QUOTE_KEY[field], '')
    if field == 'type':
        targets = coding.get('targets', [])
        confident = bool(targets) and all(t.get('outcome_confident') is True for t in targets) \
            if len(bound) != 1 else target.get('outcome_confident') is True
    elif field == 'original':
        confident = target is not None and target.get('outcome_confident') is True and target.get('identified_by') == 'citation'
    else:
        confident = target is not None and target.get('outcome_confident') is True
    facts.update(evidence_level=coding.get('evidence_level'), study_status=coding.get('study_status'),
                 record_type=coding.get('record_type'), target_count=len(coding.get('targets', [])),
                 binding_count=len(bound), binding=[dict(target_index=i, method=m) for i, m in bound],
                 relation=relation, confident=confident, value=value, identified_by=target.get('identified_by') if target else None,
                 literal_quote_ok=bool(source and literal_in_source(quote, source)),
                 replication_study_numbers=target.get('replication_study_numbers') if target else None)
    return facts


class Artifacts:
    """All inputs, loaded once."""

    def __init__(self):
        assert sha_bytes(BASELINE.read_bytes()) == BASELINE_SHA, 'Frozen baseline changed'
        with BASELINE.open(encoding='utf-8-sig') as f:
            self.frozen = list(csv.DictReader(f))
        self.current = load_current()
        self.proposals = read(B / 'handoff/correction_proposals.json')
        self.reliability = read(B / 'handoff/review_reliability.json')
        self.inventory = read(T / 'source_inventory.json')
        self.queue = read(T / 'comparison_review_queue.json')['documents']
        self.upgrades = read(T / 'source_upgrades.json')['upgrades']
        self.prior = read(T / 'prior_sol_receipt_checks.json')['documents']
        self.completion = read(T / 'sol_completion_20261103.json')
        self.acceptance = read(T / 'parent_acceptance_decisions.json')
        self.held = read(T / 'held_acceptance_decisions.json')['cases']
        self.withdrawn = read(T / 'withdrawn_proposals.json')['cases']
        self.export = read(T / 'automatically_verified_proposals.json')
        self.validations = validation_index()
        self.documents = {d['document_id']: d for d in self.inventory['documents']}
        for upgrade in self.upgrades:
            self.documents[upgrade['document_id']] = upgrade
        self.superseded = {u['supersedes_document_id']: u['document_id'] for u in self.upgrades
                           if u['document_id'] != 'document_0691'}
        for document, entry in self.completion['documents'].items():
            if entry['route'] == 'superseded_source_view':
                self.superseded[document] = entry['resolved_comparison']['document_id']
        self.cache = {}
        registry = T / 'adversarial_review_registry.json'
        self.adversary = read(registry)['bundles'] if registry.exists() else {}
        metadata = T / 'authoritative_original_metadata.json'
        self.authoritative = read(metadata)['rows'] if metadata.exists() else {}
        close = T / 'close_read_20261104.json'
        self.close_read = read(close)['reviews'] if close.exists() else {}
        final = T / 'final_read_decisions.json'
        if final.exists():
            self.close_read = {**self.close_read, **read(final)['reviews']}

    def coding(self, path):
        path = resolve(path)
        if path not in self.cache:
            self.cache[path] = read(path)
        return self.cache[path]

    def source_text(self, document):
        """Whitespace-normalized registered text; held packets are never opened."""
        if document in PROVIDER_HELD:
            return None
        key = 'source:' + document
        if key not in self.cache:
            packet = self.documents.get(document, {}).get('packet_path')
            path = resolve(packet) / 'article.txt' if packet else None
            self.cache[key] = spaced(path.read_text()) if path and path.exists() else None
        return self.cache[key]

    def current_document(self, document):
        while document in self.superseded:
            document = self.superseded[document]
        return document

    def opus(self, document):
        entry = self.validations.get(document, {}).get('opus')
        if entry:
            return Path(entry['validation_path']).parent / 'coding.json', 'validated_opus', clean_for_fields(entry)
        path = self.queue.get(document, {}).get('opus_coding_path')
        return (resolve(path), 'queue_registered_opus', True) if path else (None, None, False)

    def sol(self, document):
        """Return path, kind, eligibility, qualification and validator cleanliness."""
        entry = self.validations.get(document, {}).get('sol')
        if entry:
            eligible = entry.get('scientific_comparison_eligible', True) is not False
            return (Path(entry['validation_path']).parent / 'coding.json', 'fresh_sol', eligible, None,
                    clean_for_fields(entry))
        completion = self.completion['documents'].get(document)
        if completion:
            route = completion['route']
            if route == 'exact_source_alias':
                return (completion['resolved_comparison']['sol_coding_path'], 'exact_source_alias', True, None, True)
            if route == 'same_report_body_reuse_after_0660':
                return (completion['representative_comparison']['sol_coding_path'], 'identical_body_one_pair', True, None, True)
        check = self.prior.get(document)
        if not check:
            return None, None, False, None, False
        queue = self.queue.get(document, {})
        status = check['status']
        path = check.get('prior_coding_path')
        if queue.get('prior_sol_comparator_eligible_for_blind_agreement') is False:
            return path, 'prior_sol', False, None, True
        if status in PRIOR_ELIGIBLE:
            return path, 'prior_sol', True, None, True
        if status in PRIOR_QUALIFIED:
            return path, 'prior_sol', True, PRIOR_QUALIFIED[status], True
        return path, 'prior_sol', False, None, True


def proposal_groups(art):
    by_row = defaultdict(list)
    for change in art.proposals['changes']:
        by_row[change['input_row_index']].append(change)
    return by_row


def bind_document(art, work, identity):
    """Report of a collection is bound by the original's target; never by position."""
    candidates = []
    for document in work['ready_document_ids']:
        document = art.current_document(document)
        if document not in candidates:
            candidates.append(document)
    if len(candidates) == 1:
        return candidates[0], 'single_current_report', candidates
    hits = []
    for document in candidates:
        if document in PROVIDER_HELD:
            continue
        for path in (art.opus(document)[0], art.sol(document)[0]):
            if path and any(target_binding(t, identity) for t in art.coding(path).get('targets', [])):
                hits.append(document)
                break
    if len(hits) == 1:
        return hits[0], 'unique_report_naming_this_original', hits
    return None, 'ambiguous' if hits else 'no_report_names_this_original', hits


def parent_flag(label):
    if label in CLEAN_PENDING_LABELS or label.startswith(('accepted_', 'existing_outcome_proposal_eligible')):
        return None
    return 'parent_hold_flag' if 'held' in label.split('_') or label.startswith('held') else 'parent_scope_flag'


def dimensions(document, opus, sol, queue):
    """Separate answers to separate questions; none of them implies a later one."""
    roles = (opus.get('present'), sol.get('present') and sol.get('eligible_for_comparison'))
    relations = (opus.get('relation'), sol.get('relation'))
    confident = sum(bool(c.get('confident')) for c in (opus, sol))
    value_a, value_b = opus.get('value'), sol.get('value')
    comparable = roles == (True, True) and None not in relations
    return dict(
        coverage='both_roles' if all(roles) else 'opus_only' if roles[0] else 'comparator_only' if roles[1] else 'neither',
        parent_scientific_comparison=bool(queue.get('current_scientific_codes_compared') is True or queue.get('root_comparison_extent')
                                          or queue.get('parent_scientific_comparison')),
        confidence={2: 'both', 1: 'one', 0: 'neither'}[confident] if comparable else 'not_applicable',
        agreement=('agree' if relations[0] == relations[1] and value_a == value_b else 'disagree') if comparable else 'not_applicable',
        relation_to_proposal=relations[0] if comparable and relations[0] == relations[1] else 'mixed' if comparable else 'not_applicable')


POLICY_GROUPS = {
    'verdict_scope': ('When an author verdict covers the main result but specific findings differ, which value applies?',
                      re.compile('verdict|overall|central|focal|main_|key_|partial|whole|primary_vs|scope_policy')),
    'special_verdicts': ('When does a critique make a result "statistically successful but flawed" or "uninformative"?',
                         re.compile('flawed|uninformative|validity|critique|descriptive|inconclusive|method')),
    'which_original': ('When a report has a replication chain or several candidates, which original does the row represent?',
                       re.compile('chain|roster|identity|binding|citation|attribution|target|original_doi|additional')),
    'reproduction_axes': ('When is a reanalysis a reproduction, and what does each computation and robustness value require?',
                          re.compile('reproduction|type|reanalysis|reconstructed|axes|axis|numerical|computation|robust')),
    'version_identity': ('Which version of a work should the record cite when versions differ?',
                         re.compile('version|preprint|working_paper|publication|legacy|historical|duplicate_report')),
    'source_completeness': ('Can agreement on an abstract or an incomplete source support a change?',
                            re.compile('abstract|incomplete|missing|supplement|omitted|source_limit|intrinsic_source')),
    'plan_records': ('How should plans and protocols be represented?', re.compile('prospective|protocol|plan|registered|interim|preliminary')),
    'record_inclusion': ('When should a record be excluded, merged or removed?', re.compile('exclu|merge|remov|not_a_replication|not_replication|eligib')),
    'finding_scope': ('When a verdict covers a narrower test than the original, is it the record outcome?', re.compile('scope|boundary|limit|conceptual|extension|measure')),
}
STATE_POLICY = {
    'record_level_rule': 'record_inclusion', 'source_gap': 'source_completeness',
    'binding_unresolved_document': 'which_original', 'target_not_bound': 'which_original',
    'policy_cannot_be_determined': 'determinability',
}
EXTRA_POLICY_QUESTIONS = {
    'determinability': 'When should a record say the outcome cannot be determined, rather than keep its value?',
}
TERMINAL_STATES = READY_STATES | {'withdrawn_source_adjudicated', 'withdraw_both_roles_confirm_frozen', 'provider_hold',
                                  'source_order_hold', 'header_only_hold', 'record_action_candidate',
                                  'agreement_pending_adversarial_review', 'agreement_needs_authoritative_metadata',
                                  'agreement_needs_close_read', 'close_read_keep_existing', 'no_agreement_keep_existing'}


def policy_group(state, label, reasons):
    """Group recurring open questions so one rule can settle many cases."""
    if state in TERMINAL_STATES:
        return None
    if state in STATE_POLICY:
        return STATE_POLICY[state]
    for key, (_, pattern) in POLICY_GROUPS.items():
        if pattern.search(label or ''):
            return key
    return 'other_individual'


def reconcile_export(art, fields, bundles):
    """Re-derive the protected export and name every difference."""
    families = Counter()
    by_row = defaultdict(list)
    for field in fields:
        by_row[field['input_row_index']].append(field)
    case_rows = []
    for case in art.export['cases']:
        names = set(case['proposal_fields'])
        if names == {'outcome'}:
            family = 'outcome_only'
        elif names == {'original'}:
            family = 'original_reference'
        elif names <= {'outcome_computation', 'outcome_robustness'}:
            family = 'reproduction_axis'
        else:
            assert names == {'type', 'outcome'}, names
            family = 'type_and_outcome'
        families[family] += 1
        rechecks = {f['field']: f['gate_recheck']['state'] for f in by_row[case['input_row_index']] if f['field'] in names}
        case_rows.append(dict(case_id=case['case_id'], family=family, fields=sorted(names), operations=len(case['operations']),
                              gate_recheck=rechecks,
                              current_relations=sorted({f['current']['relation'] for f in by_row[case['input_row_index']] if f['field'] in names})))
    return dict(
        cases=len(art.export['cases']), fields=art.export['automatic_fields_verified'],
        operations=sum(len(c['operations']) for c in art.export['cases']),
        record_actions=[c['input_row_index'] for c in art.export['record_actions']], families=dict(sorted(families.items())),
        case_rows=case_rows,
        gate_differences=[c['case_id'] for c in case_rows if set(c['gate_recheck'].values()) - {'agreement_pending_adversarial_review'}],
        note='Record exclusions recheck as whole-record rules by design; field gates never authorize them.',
        user_approval_recorded=art.export['user_approval_recorded'], canonical_changes_applied=art.export['canonical_changes_applied'])


def csv_rows(name):
    with (B / 'handoff' / name).open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def outside_scope(art, frozen_index, current_index, by_row):
    """Findings the 562 proposed fields do not cover, each counted once."""
    def pair_status(row):
        target_doi, work = identifier(row['doi']), identifier(row['work_key'])
        if target_doi and work and current_index['pairs'].get((target_doi, work)):
            return 'already_in_current'
        titles = [i for i, c in enumerate(art.current) if norm(c['title_o']) == norm(row['title'])
                  and work and work in side_ids(c, 'r')]
        return 'already_in_current' if titles else 'not_in_current'
    pair_sets = {}
    for name, key in (('confirmed_missing_pairs.csv', 'confirmed_missing_pair'),
                      ('unresolved_missing_pairs.csv', 'unresolved_missing_candidate'),
                      ('planned_study_pairs.csv', 'planned_study_pair')):
        rows = csv_rows(name)
        status = Counter(pair_status(r) for r in rows)
        pair_sets[key] = dict(items=len(rows), current=dict(sorted(status.items())))
    known = {(r['file_key'], norm(r['title'])) for n in ('confirmed_missing_pairs.csv', 'unresolved_missing_pairs.csv',
                                                         'planned_study_pairs.csv') for r in csv_rows(n)}
    replication_rows = defaultdict(list)
    for row in art.frozen:
        for key in side_ids(row, 'r'):
            replication_rows[key].append(row)
    proposed_originals = defaultdict(list)
    for row_index, changes in by_row.items():
        for change in changes:
            if change['field'] == 'original' and 'title' in change['proposed_value']:
                proposed_originals[identifier(art.frozen[row_index]['doi_r'])].append(identity_of_proposal(change['proposed_value']))
    omissions = []
    for document, entry in sorted(art.documents.items()):
        if entry.get('active') is False or document in PROVIDER_HELD | SOURCE_ORDER_HELD | HEADER_ONLY or document in art.superseded:
            continue
        opus_path, sol_path = art.opus(document)[0], art.sol(document)[0]
        if not opus_path or not sol_path or not art.sol(document)[2]:
            continue
        opus, sol = art.coding(opus_path), art.coding(sol_path)
        work_rows = replication_rows.get(identifier(entry.get('parent_work_key')), [])
        for target in opus.get('targets', []):
            if not target.get('title') or not target.get('outcome_confident'):
                continue
            identity = identity_of_proposal(target)
            if not any(target_binding(t, identity) and t.get('outcome_confident') for t in sol.get('targets', [])):
                continue
            if any(target_binding(target, identity_of_row(r)) for r in work_rows) or (entry.get('parent_file_key'), norm(target['title'])) in known:
                continue
            if any(target_binding(target, other) for other in proposed_originals.get(identifier(entry.get('parent_work_key')), [])):
                continue
            omissions.append(dict(document_id=document, work_key=entry.get('parent_work_key'), title=target['title'][:200],
                                  doi=target.get('doi', ''), authors=target.get('authors', '')[:120], year=target.get('year', '')))
    return dict(
        pairs=pair_sets,
        new_two_role_target_candidates=dict(
            items=len(omissions), status='not_reviewed_no_row_created', examples=omissions[:400]),
        quote_provenance_updates=len(read(B / 'handoff/evidence_provenance_fixes.json')['changes']),
        record_action_proposals=len(read(B / 'handoff/record_actions.json')['actions']),
        superseded_source_proposals=art.proposals['superseded_source_proposals'],
        earlier_withdrawn_proposals=art.proposals['withdrawn_proposals'],
        collection_reports_outside_frozen_rows=sum(1 for d in art.documents.values() if d.get('role') == 'individual_primary_report'),
        source_gaps=sum(g['kind'] == 'full_report_completeness_limit' for g in art.inventory['source_verification_queue']),
        formal_individual_holds=dict(cases=len(art.held), resolved=sum(c['status'].startswith('resolved_') for c in art.held)))


def build_ledger(art=None):
    art = art or Artifacts()
    changes = art.proposals['changes']
    assert art.proposals['baseline_sha256'] == BASELINE_SHA
    assert len(changes) == 562 and len({c['input_row_index'] for c in changes}) == 515
    field_work = {(m['input_row_index'], m['field']): w for w in art.inventory['works']
                  for m in w['frozen_row_field_mapping']}
    assert len(field_work) == 562 and len(art.inventory['works']) == 469
    by_row = proposal_groups(art)
    export_fields = {(c['input_row_index'], f): c for c in art.acceptance['cases'] for f in c['proposal_fields']}
    assert len(export_fields) == art.export['automatic_fields_verified'] == 42
    record_cases = {c['input_row_index']: c for c in art.acceptance['record_cases']}
    formal = defaultdict(list)
    for case in art.held:
        if case['status'].startswith('resolved_'):
            continue
        rows = case.get('input_row_indices') or [case.get('input_row_index')]
        for row in rows:
            formal[row].append(case)
    withdrawn = {(c['input_row_index'], c['field']) for c in art.withdrawn}
    reliability = {int(k.split(':')[1]) for k in art.reliability.get('holds', {})}
    gap_keys = {g['parent_file_key'] for g in art.inventory['source_verification_queue']
                if g['kind'] == 'full_report_completeness_limit'}
    frozen_index = build_identity_index(art.frozen)
    current_index = build_identity_index(art.current)
    replication_rows = defaultdict(list)
    for other in art.frozen:
        for key in side_ids(other, 'r'):
            replication_rows[key].append(other)
    frozen_by_replication = {r: [o for key in side_ids(art.frozen[r], 'r') for o in replication_rows[key]] for r in by_row}

    fields = []
    for change in changes:
        row_index, field = change['input_row_index'], change['field']
        row = art.frozen[row_index]
        proposed = change['proposed_value']
        assert change['expected_before_full_record_sha256'] == digest(row), f'Proposal row hash {row_index}'
        work = field_work[(row_index, field)]
        relink = next((c['proposed_value'] for c in by_row[row_index] if c['field'] == 'original'
                       and isinstance(c['proposed_value'], dict) and 'title' in c['proposed_value']), None)
        identity = identity_of_proposal(relink) if relink else identity_of_row(row)
        frozen_identity = identity_of_row(row)
        accepted = export_fields.get((row_index, field))
        if accepted:
            document, method, candidates = accepted['document_id'], 'protected_export_decision', [accepted['document_id']]
        elif row_index in record_cases:
            document, method, candidates = record_cases[row_index]['document_id'], 'protected_export_decision', [record_cases[row_index]['document_id']]
        else:
            document, method, candidates = bind_document(art, work, identity)
        frozen_value = frozen_field_value(field, proposed, row)
        standing = []
        label, opus_facts, sol_facts, source_sha = None, None, None, None
        if document:
            queue = art.queue.get(document, {})
            label = queue.get('status')
            flag = parent_flag(label) if label else None
            if flag:
                standing.append(flag)
            source_sha = queue.get('source_sha256') or art.documents.get(document, {}).get('source_sha256')
            source = art.source_text(document)
            opus_path, opus_kind, opus_clean = art.opus(document)
            sol_path, sol_kind, sol_eligible, qualification, sol_clean = art.sol(document)
            load = (lambda p: art.coding(p)) if document not in PROVIDER_HELD else (lambda p: None)
            opus_facts = coder_facts(load(opus_path) if opus_path else None, source, field, proposed, frozen_value,
                                     identity, frozen_identity, opus_clean, True, str(opus_path) if opus_path else None, opus_kind)
            sol_facts = coder_facts(load(sol_path) if sol_path else None, source, field, proposed, frozen_value,
                                    identity, frozen_identity, sol_clean, sol_eligible, str(sol_path) if sol_path else None,
                                    sol_kind, qualification)
            prior = art.prior.get(document)
            if sol_kind == 'fresh_sol' and prior and prior.get('prior_coding_path'):
                prior_facts = coder_facts(art.coding(prior['prior_coding_path']), None, field, proposed, frozen_value,
                                          identity, frozen_identity)
                if prior_facts['value'] is not None and prior_facts['value'] != sol_facts['value']:
                    standing.append('prior_reading_differs')
        empty = dict(present=False, eligible_for_comparison=False, relation=None, confident=False, binding_count=0,
                     evidence_level=None, study_status=None, literal_quote_ok=False, validator_clean=False, value=None)
        opus_facts, sol_facts = opus_facts or empty, sol_facts or empty
        review = art.adversary.get('row:%d' % row_index)
        bundle_review = None
        if review:
            bundle_review = dict(verdict=review['verdict'], quote_verified=review['quote_verified'],
                                 authoritative_metadata_verified=str(row_index) in art.authoritative,
                                 confidence=review.get('confidence'), policy_group=review.get('policy_group'),
                                 qa_status=(review.get('qa') or {}).get('status'))
        partner_fields = {c['field']: c['proposed_value'] for c in by_row[row_index]}
        relink_duplicate = False
        if field == 'original' and relink:
            relink_duplicate = any(
                other != row and side_ids(other, 'r') & side_ids(row, 'r') and target_binding(
                    dict(doi=other['doi_o'], title=other['title_o'], year=other['year_o'], authors=other['author_o']), identity)
                for other in frozen_by_replication[row_index])
        facts = dict(
            field=field, proposed_value=proposed, relink_duplicate=relink_duplicate,
            type_has_axis_partner=isinstance(partner_fields.get('outcome'), dict) or bool(
                {'outcome_computation', 'outcome_robustness'} & set(partner_fields)),
            standing_reasons=standing, document_id=document,
            provider_held=document in PROVIDER_HELD or bool(set(work['ready_document_ids']) & PROVIDER_HELD and not document),
            source_order_held=document in SOURCE_ORDER_HELD, header_only=document in HEADER_ONLY,
            withdrawn=(row_index, field) in withdrawn, formal_hold=bool(formal.get(row_index)),
            reliability_hold=row_index in reliability, in_record_actions=row_index in record_cases,
            in_export=accepted is not None, remove_row=isinstance(proposed, dict) and proposed.get('action') == 'remove_row',
            record_dependency=bool(change.get('record_action_dependency')),
            application_hold=bool(change.get('application_hold') or change.get('application_dependency')),
            full_text_gap=work['parent_file_key'] in gap_keys and document in work['ready_document_ids']
            and len(work['ready_document_ids']) == 1,
            opus=opus_facts, sol=sol_facts,
            coders_agree_exactly=opus_facts.get('value') == sol_facts.get('value') and opus_facts.get('value') is not None,
            proposed_is_cannot_be_determined=proposed == 'cannot_be_determined' or (
                isinstance(proposed, dict) and 'cannot_be_determined' in proposed.values()),
            adversary=bundle_review,
            close_read=(dict(art.close_read[f'row:{row_index}:{field}'], authoritative_metadata_verified=str(row_index) in art.authoritative)
                        if f'row:{row_index}:{field}' in art.close_read else None))
        state, reasons = classify_field(facts)
        assert state in STATES and set(reasons) <= PRIMARY_REASONS, (state, reasons)
        recheck_state, recheck_reasons = classify_field(dict(facts, in_export=False, in_record_actions=False))
        current_index_found, current_method, candidates_current = bind_current(row, frozen_index, current_index, art.current,
                                                                               identity if relink else None)
        current_block = dict(binding_method=current_method, candidate_positions=candidates_current[:5])
        if current_index_found is None:
            current_block.update(flora_id=None, relation='identity_unresolved', value=None)
        else:
            match = art.current[current_index_found]
            relation = current_relation(field, proposed, frozen_value, match, row)
            if current_method == 'single_replication_row_original_differs' and field != 'original':
                # The same report now names another original: this row's verdict may not carry over.
                relation = 'original_changed_in_current'
            current_block.update(flora_id=match['id'], source_record_id=match['source_record_id'],
                                 row_position=current_index_found, relation=relation,
                                 value=current_value(field, proposed, match))
        fields.append(dict(
            field_id=f'row:{row_index}:{field}', input_row_index=row_index, field=field,
            work_key=work['parent_work_key'], parent_file_key=work['parent_file_key'],
            frozen_value=frozen_value, proposed_value=None if field == 'original' and not isinstance(proposed, dict) else proposed,
            frozen_record_sha256=change['expected_before_full_record_sha256'],
            document_id=document, document_binding=method, document_candidates=candidates[:8],
            source_sha256=source_sha, reported_status_label=label,
            opus={k: opus_facts.get(k) for k in ('present', 'kind', 'value', 'relation', 'confident', 'evidence_level', 'study_status', 'binding_count', 'literal_quote_ok', 'path')},
            sol={k: sol_facts.get(k) for k in ('present', 'kind', 'eligible_for_comparison', 'qualification', 'value', 'relation', 'confident', 'evidence_level', 'study_status', 'binding_count', 'literal_quote_ok', 'path')},
            state=state, reasons=reasons, ready=state in READY_STATES,
            gate_recheck=dict(state=recheck_state, reasons=recheck_reasons) if accepted or row_index in record_cases else None,
            dimensions=dimensions(document, opus_facts, sol_facts, art.queue.get(document, {}) if document else {}),
            policy_group=policy_group(state, label, reasons),
            adversarial_review=bundle_review, close_read=facts['close_read'], current=current_block,
            bundle_id=f'row:{row_index}'))

    bundles = []
    for row_index, members in sorted(defaultdict(list, {r: [f for f in fields if f['input_row_index'] == r]
                                                       for r in by_row}).items()):
        states = {m['state'] for m in members}
        export_case = next((c for c in art.export['cases'] if c['input_row_index'] == row_index), None)
        record = next((c for c in art.export['record_actions'] if c['input_row_index'] == row_index), None)
        all_ready = all(m['ready'] for m in members)
        relations = {m['current']['relation'] for m in members}
        bundles.append(dict(
            bundle_id=f'row:{row_index}', input_row_index=row_index, fields=[m['field'] for m in members],
            states=sorted(states), ready=all_ready, title_r=art.frozen[row_index]['title_r'],
            operation_count=len(export_case['operations']) if export_case else None,
            record_action=record['action'] if record else None,
            current_relations=sorted(relations), flora_id=members[0]['current'].get('flora_id')))
    state_counts = Counter(f['state'] for f in fields)
    export_reconciliation = reconcile_export(art, fields, bundles)
    outside = outside_scope(art, frozen_index, current_index, by_row)
    return dict(
        schema_version=1,
        baseline=dict(path=str(BASELINE), sha256=BASELINE_SHA, rows=len(art.frozen), columns=len(art.frozen[0])),
        current=dict(commit=CURRENT_COMMIT, sha256=CURRENT_SHA, rows=len(art.current), columns=len(art.current[0])),
        totals=dict(fields=len(fields), rows=len(by_row), works=len(art.inventory['works']),
                    state_counts=dict(sorted(state_counts.items())),
                    current_relations=dict(sorted(Counter(f['current']['relation'] for f in fields).items()))),
        export_reconciliation=export_reconciliation, outside_proposal_scope=outside,
        policy_questions={**{k: v[0] for k, v in POLICY_GROUPS.items()}, **EXTRA_POLICY_QUESTIONS,
                          'other_individual': 'Case-specific question with no shared rule yet.'},
        fields=fields, bundles=bundles, states=STATES)


if __name__ == '__main__':
    ledger = build_ledger()
    OUTPUT.write_text(json.dumps(ledger, ensure_ascii=False, indent=1) + '\n')
    progress = read(T / 'progress.json')
    progress['field_ledger'] = dict(path=OUTPUT.name, sha256=sha_bytes(OUTPUT.read_bytes()), **ledger['totals'])
    (T / 'progress.json').write_text(json.dumps(progress, indent=2) + '\n')
    print(json.dumps(ledger['totals'], indent=1))
