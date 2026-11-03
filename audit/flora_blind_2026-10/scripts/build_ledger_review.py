#!/usr/bin/env python3
"""Turn the field ledger into the review app's public-safe plan. Approves and applies nothing."""
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

B = Path(__file__).resolve().parents[1]
H = B / 'handoff'
T = B / 'independent_recode_20261101'
P = B / 'evidence_followup/private/independent_recode_20261101'
ADVERSARY = P / 'adversarial_20261103'
sys.path.insert(0, str(T))

SOURCE_BLOCKED = {'provider_hold', 'source_order_hold', 'header_only_hold', 'source_gap'}
WITHDRAW = {'withdrawn_source_adjudicated', 'withdraw_both_roles_confirm_frozen'}
CANDIDATE = {'reviewed_export_candidate', 'adversary_supported_candidate', 'agreement_pending_adversarial_review',
             'agreement_needs_authoritative_metadata'}
VIEW_ORDER = ['ready', 'record_exclusion', 'no_edit', 'withdraw', 'rebind', 'pending_read', 'rule', 'source_blocked']
VIEW_TEXT = {
    'ready': ('Ready for a set decision', 'Two independent readings and a source review support the change, and current FLoRA still holds the old value.'),
    'record_exclusion': ('Whole-record exclusions', 'Evidence supports removing the record. These stay apart from field edits.'),
    'no_edit': ('Already right in current FLoRA', 'Current FLoRA already holds the proposed value, so no edit is needed.'),
    'withdraw': ('Proposal should be withdrawn', 'Source review or both readings keep the original value.'),
    'rebind': ('Current FLoRA changed', 'The row now holds a third value, or could not be matched with certainty. These need checking against current data.'),
    'pending_read': ('Awaiting a source review', 'Two readings agree with the proposal, but nobody has yet tried to break it against the source.'),
    'rule': ('Waiting on a rule or a person', 'Readers disagree, are unsure, or a coding rule needs settling.'),
    'source_blocked': ('Blocked by the source', 'The available text cannot settle this.'),
}
STATE_TEXT = {
    'reviewed_export_candidate': 'Two confident readings and a source review support this change.',
    'adversary_supported_candidate': 'Two confident readings and a source review that tried to break it support this change.',
    'record_action_candidate': 'Evidence supports excluding the whole record.',
    'agreement_pending_adversarial_review': 'Two confident readings agree with the proposal; a source review is outstanding.',
    'agreement_needs_authoritative_metadata': 'The source review supports a different original; its reference details still need an authoritative record.',
    'agreement_qualified_comparator': 'The readings agree, but one was checked against a differently extracted copy of the source.',
    'adversary_held': 'The source review did not support an automatic change.',
    'withdraw_both_roles_confirm_frozen': 'Both readings confidently keep the existing value.',
    'withdrawn_source_adjudicated': 'Withdrawn after source review. The proposal no longer stands.',
    'third_value_agreement': 'Both readings agree on a value that is neither existing nor proposed.',
    'disagreement_confident': 'Both readings are confident and disagree.',
    'unconfident': 'At least one reading is unsure about this original.',
    'policy_cannot_be_determined': 'The proposal says the outcome cannot be determined, which is never changed automatically.',
    'individual_policy_hold': 'This case needs an individual decision.',
    'record_level_rule': 'This needs a whole-record decision such as removing, merging or rebinding.',
    'binding_unresolved_document': 'This work holds several reports, and no single report is matched with certainty.',
    'target_not_bound': 'A reading names no original that clearly matches this row.',
    'no_eligible_comparator': 'There is no second reading that meets the evidence checks.',
    'source_gap': 'Only an abstract or incomplete text was available.',
    'provider_hold': 'The AI provider refused to process this source, so it was not read. It stays on hold in this audit.',
    'source_order_hold': 'The source text may be out of order, so it is kept out of comparison.',
    'header_only_hold': 'Only a header was available for this source view.',
}
RELATION_TEXT = {
    'unchanged_from_frozen': 'Current FLoRA still holds the audited value.',
    'already_equal': 'Current FLoRA already holds the proposed value.',
    'third_value': 'Current FLoRA now holds a different value from both.',
    'identity_unresolved': 'This row could not be matched in current FLoRA with certainty.',
    'original_changed_in_current': 'The same report now names another original in current FLoRA.',
    'record_action_not_comparable': 'This is a whole-record action.',
}
SETS = [
    ('outcome_only', 'Outcome corrections', 'Change the outcome and its supporting quote, when two independent full-text readings and a source review agree.',
     lambda f: f == {'outcome'}),
    ('reproduction_axis', 'Reproduction results', 'Change the computation or robustness result and its quote. The other result stays as it is.',
     lambda f: f <= {'outcome_computation', 'outcome_robustness'}),
    ('type_and_outcome', 'Study type with its outcome', 'Change the study type and the outcome together. Neither applies alone.',
     lambda f: 'type' in f),
    ('original_reference', 'Corrected original study', 'Replace the original study and its complete reference, confirmed against an authoritative record.',
     lambda f: 'original' in f),
]
FIELD_LABEL = {'outcome': 'Outcome', 'type': 'Study type', 'original': 'Original study', 'outcome_computation': 'Computation result',
               'outcome_robustness': 'Robustness result'}


def read(path):
    return json.loads(Path(path).read_text())


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def excerpt(text, words=25):
    pieces = list(re.finditer(r'\S+', text or ''))
    if not pieces:
        return ''
    return (text or '')[:pieces[min(words, len(pieces)) - 1].end()].strip() + (' …' if len(pieces) > words else '')


def clean(text):
    return re.sub(r'(?:/home/lukas/|audit/flora_blind_2026-10/)[^\s<>"\']+', '[audit file]', str(text or ''))


def show_value(value):
    if value in (None, '', 'NA'):
        return 'No value'
    if isinstance(value, dict):
        if value.get('action') == 'remove_row':
            return 'Remove this row'
        if 'title' in value:
            who = re.sub(r'\s+', ' ', str(value.get('authors') or ''))[:90]
            return ' '.join(x for x in [who, f"({value['year']})" if value.get('year') else '', value['title']] if x)
        return ', '.join(f'{FIELD_LABEL.get(k, k).lower()}: {show_value(v).lower()}' for k, v in value.items())
    return str(value)


def humanize_flag(label):
    text = re.sub(r'_+', ' ', label or '').strip()
    text = re.sub(r'^(held|genuine|parent validated)\s+', '', text)
    return text[:1].upper() + text[1:] if text else ''


def bundle_view(members):
    """One place per row, so a change and its dependencies are never split."""
    states = {m['state'] for m in members}
    relations = {m['current']['relation'] for m in members}
    if states & SOURCE_BLOCKED:
        return 'source_blocked'
    if states <= WITHDRAW:
        return 'withdraw'
    if states == {'record_action_candidate'}:
        return 'record_exclusion'
    if not states <= CANDIDATE:
        return 'rule'
    if relations == {'already_equal'}:
        return 'no_edit'
    if relations != {'unchanged_from_frozen'}:
        return 'rebind'
    if all(m['ready'] for m in members):
        return 'ready'
    if states & {'agreement_needs_authoritative_metadata'}:
        return 'pending_read'
    return 'pending_read'


def first_author(value):
    value = value or ''
    if value.startswith('['):
        try:
            names = json.loads(value)
            return ', '.join(n.get('family', '') for n in names[:3]) + (' et al.' if len(names) > 3 else '')
        except ValueError:
            pass
    return value[:80]


def adversary_review(row, registry):
    entry = registry.get('bundles', {}).get(f'row:{row}')
    if not entry:
        return None, None
    path = ADVERSARY / entry['request_id'] / 'review.json'
    return entry, read(path) if path.exists() else None


def build():
    ledger = read(T / 'field_ledger.json')
    registry_path = T / 'adversarial_review_registry.json'
    registry = read(registry_path) if registry_path.exists() else {'bundles': {}, 'states': {}}
    export = read(T / 'automatically_verified_proposals.json')
    export_cases = {c['input_row_index']: c for c in export['cases']}
    record_cases = {c['input_row_index']: c for c in export['record_actions']}
    frozen = {b['input_row_index']: b for b in ledger['bundles']}
    import csv
    with Path(ledger['baseline']['path']).open(encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    by_row = defaultdict(list)
    for field in ledger['fields']:
        by_row[field['input_row_index']].append(field)

    bundles = {}
    for row, members in sorted(by_row.items()):
        view = bundle_view(members)
        source = rows[row]
        names = {m['field'] for m in members}
        family = next((key for key, _, _, test in SETS if test(names)), 'other')
        entry, review = adversary_review(row, registry)
        case = export_cases.get(row) or record_cases.get(row)
        provenance, limits, quotes = [], [], []
        states = sorted({m['state'] for m in members})
        for state in states:
            provenance.append(STATE_TEXT[state])
        relation = members[0]['current']['relation']
        if len({m['current']['relation'] for m in members}) == 1:
            provenance.append(RELATION_TEXT[relation])
        else:
            provenance.append('Current FLoRA has changed for part of this row.')
        qualification = next((m['sol']['qualification'] for m in members if m['sol'].get('qualification')), None)
        if qualification:
            limits.append({'normalization_chain': 'The second reading was verified through whitespace and header normalization, not the exact registered text.',
                           'alternate_layout': 'The second reading used a different extraction of the same PDF, so it does not meet the literal-source rule.',
                           'parent_annotation_projection': 'The second reading was verified through an annotated copy of the source.'}[qualification])
        if case and row in export_cases:
            quotes.extend(dict(text=excerpt(e.get('quote', '')), section=clean(e.get('section', ''))) for e in case.get('evidence', [])[:3])
            limits.extend(clean(x) for x in case.get('limits', [])[:4])
        summary = clean(case.get('rationale', '')) if case else ''
        if review:
            summary = clean(review.get('plain_language_summary', '')) or summary
            quotes = [dict(text=excerpt(q.get('quote', '')), section=clean(q.get('section', ''))) for q in (review.get('supporting_quotes') or [])[:2]]
            counter = review.get('strongest_counterevidence') or {}
            if counter.get('quote'):
                quotes.append(dict(text=excerpt(counter['quote']), section=clean(counter.get('section', '')), against=True,
                                   note=clean(counter.get('why_not_decisive', ''))[:300]))
            provenance.append('A source review read the complete text looking for reasons to reject this.')
        flag = next((m['reported_status_label'] for m in members if {'parent_hold_flag', 'parent_scope_flag'} & set(m['reasons'])), None)
        group = next((m['policy_group'] for m in members if m['policy_group']), None)
        if entry and entry.get('policy_group') and group != 'review_confidence':
            group = entry['policy_group']
        bundles[row] = dict(
            id=f'row:{row}', row=row, view=view, family=family, flora_id=members[0]['current'].get('flora_id'),
            title=source['title_r'], original=' '.join(x for x in [first_author(source['author_o']), f"({source['year_o']})", source['title_o']] if x),
            changes=[dict(field=m['field'], label=FIELD_LABEL[m['field']], audited=show_value(m['frozen_value']) if m['field'] != 'original' else show_value(dict(title=source['title_o'], authors=first_author(source['author_o']), year=source['year_o'])),
                          proposed=show_value(m['proposed_value']),
                          current=show_value(m['current']['value']) if m['current']['relation'] not in ('identity_unresolved', 'record_action_not_comparable') else 'Not matched',
                          state=m['state'], relation=m['current']['relation']) for m in members],
            status=VIEW_TEXT[view][0], provenance=provenance, limits=limits, quotes=[q for q in quotes if q['text']],
            summary=summary[:700], scope_question=humanize_flag(flag) if flag and view not in ('ready',) else '',
            policy_group=group if view == 'rule' else None,
            record_action=(record_cases[row]['action'] if row in record_cases else None), operations=(len(case['operations']) if row in export_cases else None))

    def fields_in(rows_):
        return sum(len(by_row[r]) for r in rows_)
    views = defaultdict(list)
    for row, bundle in bundles.items():
        views[bundle['view']].append(row)
    statement = [dict(id=v, label=VIEW_TEXT[v][0], note=VIEW_TEXT[v][1], rows=len(views[v]), fields=fields_in(views[v])) for v in VIEW_ORDER]
    assert sum(s['fields'] for s in statement) == ledger['totals']['fields'] == 562
    assert sum(s['rows'] for s in statement) == ledger['totals']['rows'] == 515

    sets = []
    for key, title, rule, _ in SETS:
        members = [bundles[r] for r in views['ready'] if bundles[r]['family'] == key]
        sets.append(dict(id=key, title=title, rule=rule, rows=len(members), fields=sum(len(b['changes']) for b in members),
                         fingerprint=fingerprint([[b['id'], b['changes']] for b in members]), items=[b['id'] for b in members]))
    groups = []
    for key, question in ledger['policy_questions'].items():
        members = [bundles[r] for r in views['rule'] if bundles[r]['policy_group'] == key]
        if members:
            questions = Counter()
            for row in (b['row'] for b in members):
                _, review = adversary_review(row, registry)
                if review and review.get('policy_question'):
                    questions[clean(review['policy_question'])[:220]] += 1
            groups.append(dict(id=key, question=question, rows=len(members), fields=sum(len(b['changes']) for b in members),
                               items=[b['id'] for b in members], reviewer_questions=[q for q, _ in questions.most_common(3)]))
    ungrouped = [bundles[r] for r in views['rule'] if not bundles[r]['policy_group']]
    if ungrouped:
        groups.append(dict(id='other_individual', question=ledger['policy_questions']['other_individual'], rows=len(ungrouped),
                           fields=sum(len(b['changes']) for b in ungrouped), items=[b['id'] for b in ungrouped], reviewer_questions=[]))
    groups.sort(key=lambda g: -g['rows'])
    blocked_kinds = Counter()
    for row in views['source_blocked']:
        for m in by_row[row]:
            if m['state'] in SOURCE_BLOCKED:
                blocked_kinds[m['state']] += 1
    outside = ledger['outside_proposal_scope']
    reviews = registry.get('states', {})
    result = dict(
        schema_version=1, ledger_sha256=hashlib.sha256((T / 'field_ledger.json').read_bytes()).hexdigest(),
        baseline=dict(sha256=ledger['baseline']['sha256'], rows=ledger['baseline']['rows']),
        current=dict(commit=ledger['current']['commit'], sha256=ledger['current']['sha256'], rows=ledger['current']['rows'], columns=ledger['current']['columns']),
        statement=statement, totals=dict(fields=562, rows=515, works=ledger['totals']['works']),
        sets=sets, set_decisions_open=False,
        set_decision_note='Set decisions are not open yet. Individual review stays the route for any outcome until a named rule is decided.',
        record_exclusions=[f'row:{r}' for r in views['record_exclusion']],
        rule_groups=groups,
        blocked=dict(kinds=dict(blocked_kinds), items=[f'row:{r}' for r in views['source_blocked']],
                     labels={k: STATE_TEXT[k] for k in SOURCE_BLOCKED}),
        no_edit=[f'row:{r}' for r in views['no_edit']], withdraw=[f'row:{r}' for r in views['withdraw']],
        rebind=[f'row:{r}' for r in views['rebind']], pending_read=[f'row:{r}' for r in views['pending_read']],
        outside_scope=dict(confirmed_missing_pairs=outside['pairs']['confirmed_missing_pair'],
                           unresolved_candidates=outside['pairs']['unresolved_missing_candidate']['items'],
                           planned_pairs=outside['pairs']['planned_study_pair']['items'],
                           quote_updates=outside['quote_provenance_updates'],
                           unreviewed_two_reader_targets=outside['new_two_role_target_candidates']['items']),
        adversary=dict(reviews=reviews, verdicts=registry.get('verdicts', {})),
        bundles={b['id']: b for b in bundles.values()},
        canonical_changes_applied=False, user_approval_recorded=False)
    (H / 'ledger_review.json').write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    return result


if __name__ == '__main__':
    built = build()
    print(json.dumps([(s['id'], s['rows'], s['fields']) for s in built['statement']]))
    print(json.dumps([(s['id'], s['rows'], s['fields']) for s in built['sets']]))
    print(json.dumps([(g['id'], g['rows']) for g in built['rule_groups']]))
