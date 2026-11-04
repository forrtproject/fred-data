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
KEEP = {'withdrawn_source_adjudicated', 'withdraw_both_roles_confirm_frozen', 'close_read_keep_existing', 'no_agreement_keep_existing'}
CANDIDATE = {'reviewed_export_candidate', 'adversary_supported_candidate', 'close_read_supported_candidate', 'agreement_pending_adversarial_review',
             'agreement_needs_authoritative_metadata', 'agreement_needs_close_read'}
VIEW_ORDER = ['ready', 'record_exclusion', 'pending_read', 'needs_reference', 'rule', 'rebind', 'source_blocked', 'withdraw', 'no_edit']
VIEW_TEXT = {
    'ready': ('Ready to apply', 'AI readers and a final check of the paper support the change, and current FLoRA still holds the old value.'),
    'record_exclusion': ('Remove the whole record', 'The paper does not re-test an earlier published finding, so it should not be in FLoRA.'),
    'pending_read': ('Waiting for one more read', 'Both AI readers back the change, but one was unsure or the final check was not confident. One more read of the paper will decide.'),
    'needs_reference': ('Right study, no verified reference', 'The AI readers name a different original study, but no authoritative reference could be confirmed for it.'),
    'rule': ('Needs a coding decision', 'The AI readers disagree, or the case turns on how FLoRA should code it. Not ready to apply.'),
    'rebind': ('Changed in FLoRA since the audit', 'The record now holds a value the audit did not see, or could not be matched for certain. Check by hand before editing.'),
    'source_blocked': ('Cannot be settled from the text we have', 'Only an abstract or incomplete text was available, or the source could not be processed.'),
    'withdraw': ('Keep the existing value', 'The evidence does not show the existing value is wrong, so the proposal is dropped.'),
    'no_edit': ('Already correct in FLoRA', 'Current FLoRA already holds the proposed value. Nothing to do.'),
}
STATE_TEXT = {
    'reviewed_export_candidate': 'Two AI readers agree, and a final check of the paper supports the change.',
    'adversary_supported_candidate': 'Two AI readers agree, and a final check that looked for reasons to reject the change found none.',
    'close_read_supported_candidate': 'Two AI readers back the change, and one more read of the paper finds the existing value wrong.',
    'close_read_keep_existing': 'One more read of the paper finds the existing value defensible, so it stays.',
    'agreement_needs_close_read': 'Both AI readers back the change, but one was unsure or the final check was not confident.',
    'no_agreement_keep_existing': 'The AI readers do not agree on a new value and at least one was unsure, so the existing value stays.',
    'record_action_candidate': 'The evidence supports removing the whole record.',
    'agreement_pending_adversarial_review': 'Two AI readers agree with the proposal. The final check has not been run.',
    'agreement_needs_authoritative_metadata': 'The evidence supports a different original study, but its reference could not be confirmed in an authoritative record.',
    'adversary_held': 'The final check of the paper did not support the change.',
    'withdraw_both_roles_confirm_frozen': 'Both AI readers confidently keep the existing value.',
    'withdrawn_source_adjudicated': 'Withdrawn after an earlier check of the paper.',
    'third_value_agreement': 'Both AI readers agree on a value that is neither the existing nor the proposed one.',
    'disagreement_confident': 'Both AI readers are confident, and they disagree.',
    'policy_cannot_be_determined': 'The proposal says the outcome cannot be determined. That is never changed automatically.',
    'individual_policy_hold': 'This case needs an individual decision.',
    'record_level_rule': 'This needs a decision about the whole record, such as removing, merging or relinking it.',
    'binding_unresolved_document': 'This work has several reports, and we cannot say for certain which one this record means.',
    'target_not_bound': 'An AI reader did not clearly name the original study on this record.',
    'no_eligible_comparator': 'There is no second reading that meets the evidence checks.',
    'source_gap': 'Only an abstract or incomplete text was available.',
    'provider_hold': 'The AI provider refused to process this source, so it was not read. It stays on hold in this audit.',
    'source_order_hold': 'The source text may be out of order, so it was not used.',
    'header_only_hold': 'Only the header of this source was available.',
}
RELATION_TEXT = {
    'unchanged_from_frozen': 'Current FLoRA still holds the value the audit read.',
    'already_equal': 'Current FLoRA already holds the proposed value.',
    'third_value': 'Current FLoRA now holds a different value from both.',
    'identity_unresolved': 'This record could not be matched in current FLoRA for certain.',
    'original_changed_in_current': 'The same report now names another original in current FLoRA.',
    'record_action_not_comparable': 'This is a decision about the whole record.',
}
SETS = [
    ('outcome_only', 'Outcome corrections', 'Change the outcome and its supporting quote.',
     lambda f: f == {'outcome'}),
    ('reproduction_axis', 'Reproduction results', 'Change the computation or robustness result and its quote. Leave the other result as it is.',
     lambda f: f <= {'outcome_computation', 'outcome_robustness'}),
    ('type_and_outcome', 'Study type changes', 'Change the study type and the outcome together. Neither applies alone.',
     lambda f: 'type' in f),
    ('original_reference', 'Wrong original study', 'Replace the original study with its full reference, confirmed in Crossref.',
     lambda f: 'original' in f),
]
PLAIN_QUESTIONS = {
    'which_original': 'Which original study does this record belong to? The report re-tests several studies, or is part of a chain of replications.',
    'record_inclusion': 'Should this record be kept, merged, relinked or removed?',
    'verdict_scope': 'The authors give a verdict on the main result, but specific findings came out differently. Which outcome goes in the record?',
    'finding_scope': 'The verdict is about a narrower test than the original finding. Does it count as the outcome of the record?',
    'special_verdicts': 'When does a critique of the method make a result "statistically successful but flawed" or "uninformative"?',
    'reproduction_axes': 'Is this reanalysis a reproduction, and which computation and robustness results apply?',
    'version_identity': 'Several versions of this work exist. Which one should the record cite?',
    'source_completeness': 'Can agreement based on an abstract or incomplete text support a change?',
    'plan_records': 'How should study plans with no results be recorded?',
    'determinability': 'When should a record say the outcome cannot be determined, rather than keep its value?',
    'other_individual': 'Other cases that each need their own decision.',
}
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


PLAIN = [
    (r'[Ff]resh independent blind readings', 'two independent AI readings'),
    (r'\b[Bb]oth fresh\b', 'Both'), (r'\bcomplete blind roles\b', 'AI readers'), (r'\bblind roles\b', 'AI readers'),
    (r'\bindependent blind (readings|coding)\b', r'independent AI readings'), (r'\bblind (reading|readings|coding)\b', r'AI \1'),
    (r'\b(both|two) roles\b', r'\1 AI readers'), (r'\b[Pp]rimary[- ]source review\b', 'final check of the paper'),
    (r'\b[Ss]eparate original-specific source review\b', 'a final check of the paper'), (r'\b[Ss]ource review\b', 'final check'),
    (r'\b[Aa]dversarial (read|review)\b', 'final check'), (r'\bfrozen\b', 'existing'), (r'\bFrozen\b', 'Existing'),
    (r'\bparent\b(?= (?:review|validation|comparison|decision))', 'lead'), (r'\bpositively bind(s)?\b', r'link\1'), (r'\bbound\b', 'linked'),
    (r'\b[Bb]oth (?:independent )?blind coders\b', 'Both AI readers'), (r'\b[Ii]ndependent blind coders\b', 'Independent AI readers'),
    (r'\bblind coders\b', 'AI readers'), (r'\bprimary review\b', 'the final check'), (r'\bparent\b', 'lead reviewer'), (r'\bcoder(s)?\b', r'AI reader\1'),
    (r'\brule 1\b', 'the codebook rule on overall verdicts'), (r'\brule 2\b', 'the codebook rule on comparisons'),
]


# Notes about how the audit ran say nothing about the evidence, so they stay in the ledger and off the page.
PROCESS_NOTE = re.compile(r'packet|parser|attempt|receipt|\brole|redact|current\d|normali[sz]ation|layout extraction|hashed', re.I)


PROCESS_SENTENCE = re.compile(r'\b(blind|frozen|adversar\w*|comparator|packet|parent|lead reviewer|narrative attribution)\b', re.I)


def plain(text):
    """Audit shorthand reads badly on a public page; say the same thing in ordinary words."""
    text = clean(text)
    for pattern, replacement in PLAIN:
        text = re.sub(pattern, replacement, text)
    # Sentences about how the audit ran say nothing about the evidence.
    kept = [s for s in re.split(r'(?<=[.;])\s+', text) if not PROCESS_SENTENCE.search(s)]
    return ' '.join(kept)


def sentences(text, limit):
    """Shorten at a sentence or word boundary so a note never ends mid-word."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    stop = max(cut.rfind('. '), cut.rfind('; '))
    return cut[:stop + 1] if stop > limit // 2 else cut[:cut.rfind(' ')] + ' …'


def show_value(value):
    if value in (None, '', 'NA'):
        return 'No value'
    if isinstance(value, dict):
        if value.get('action') == 'remove_row':
            return 'Remove this row'
        if 'title' in value:
            who = re.sub(r'\s+', ' ', first_author(str(value.get('authors') or '')))[:90]
            return ' '.join(x for x in [who, f"({value['year']})" if value.get('year') else '', value['title']] if x)
        return ', '.join(f'{FIELD_LABEL.get(k, k).lower()}: {show_value(v).lower()}' for k, v in value.items())
    return str(value)


def edits_of(members):
    """The fields a row still needs changed: not those kept as they are or already right in current FLoRA."""
    return [m for m in members if m['state'] not in KEEP and m['current']['relation'] != 'already_equal']


def bundle_view(members):
    """One place per row, so a change and its dependencies are never split."""
    states = {m['state'] for m in members}
    if states & SOURCE_BLOCKED:
        return 'source_blocked'
    if states <= KEEP:
        return 'withdraw'
    active = {m['state'] for m in members if m['state'] not in KEEP}
    if active == {'record_action_candidate'}:
        return 'record_exclusion'
    if not active <= CANDIDATE:
        return 'rule'
    edits = edits_of(members)
    if not edits:
        return 'no_edit'
    if {m['current']['relation'] for m in edits} != {'unchanged_from_frozen'}:
        return 'rebind'
    if all(m['ready'] for m in edits):
        return 'ready'
    pending = {m['state'] for m in edits} & {'agreement_pending_adversarial_review', 'agreement_needs_close_read'}
    return 'pending_read' if pending else 'needs_reference'


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
        names = {m['field'] for m in edits_of(members)} or {m['field'] for m in members}
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
        if case and row in export_cases:
            quotes.extend(dict(text=excerpt(e.get('quote', '')), section=clean(e.get('section', ''))) for e in case.get('evidence', [])[:3])
            limits.extend(x for x in (plain(y) for y in case.get('limits', [])[:4] if not PROCESS_NOTE.search(y)) if x)
        summary = plain(case.get('rationale', '')) if case else ''
        close_reasons = [m['close_read']['reason'] for m in members if m.get('close_read') and m['field'] != 'original' or (m.get('close_read') and len(members) == 1)]
        if close_reasons:
            summary = ' '.join(close_reasons)
            provenance.append('One more read of the paper settled this.')
            review = None
        if review:
            summary = plain(review.get('plain_language_summary', '')) or summary
            quotes = [dict(text=excerpt(q.get('quote', '')), section=clean(q.get('section', ''))) for q in (review.get('supporting_quotes') or [])[:2]]
            counter = review.get('strongest_counterevidence') or {}
            if counter.get('quote'):
                quotes.append(dict(text=excerpt(counter['quote']), section=clean(counter.get('section', '')), against=True,
                                   note=sentences(plain(counter.get('why_not_decisive', '')), 320)))
        group = next((m['policy_group'] for m in members if m['policy_group']), None)
        if entry and entry.get('policy_group') and 'agreement_needs_close_read' not in states:
            group = entry['policy_group']
        edits = {m['field'] for m in edits_of(members)}
        bundles[row] = dict(
            id=f'row:{row}', row=row, view=view, family=family, flora_id=members[0]['current'].get('flora_id'),
            title=source['title_r'], original=' '.join(x for x in [first_author(source['author_o']), f"({source['year_o']})", source['title_o']] if x),
            changes=[dict(field=m['field'], label=FIELD_LABEL[m['field']], audited=show_value(m['frozen_value']) if m['field'] != 'original' else show_value(dict(title=source['title_o'], authors=first_author(source['author_o']), year=source['year_o'])),
                          proposed=show_value(m['proposed_value']),
                          current=show_value(m['current']['value']) if m['current']['relation'] not in ('identity_unresolved', 'record_action_not_comparable') else 'Not matched',
                          state=m['state'], relation=m['current']['relation']) for m in members if m['state'] not in KEEP or view == 'withdraw'],
            status=VIEW_TEXT[view][0], provenance=provenance, limits=limits, quotes=[q for q in quotes if q['text']],
            summary=sentences(summary, 700),
            kept=[FIELD_LABEL[m['field']] for m in members if m['state'] in KEEP and view != 'withdraw'],
            to_change=sorted(edits),
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

    route_status = read(T / 'flora_validation_application_route.json')['families']
    sets = []
    for key, title, rule, _ in SETS:
        members = [bundles[r] for r in views['ready'] if bundles[r]['family'] == key]
        route = route_status.get(key, {})
        sets.append(dict(id=key, title=title, rule=rule, route_blocked=route.get('status') == 'blocked_no_route',
                         route_note=route.get('note', '') if route.get('status') == 'blocked_no_route' else '', rows=len(members), fields=sum(len(b['to_change']) for b in members),
                         fingerprint=fingerprint([[b['id'], b['changes']] for b in members]), items=[b['id'] for b in members]))
    for row in views['rule']:
        bundles[row]['policy_group'] = bundles[row]['policy_group'] or 'other_individual'
    groups = []
    for key, question in {**ledger['policy_questions'], **PLAIN_QUESTIONS}.items():
        members = [bundles[r] for r in views['rule'] if bundles[r]['policy_group'] == key]
        if members:
            questions = Counter()
            for row in (b['row'] for b in members):
                _, review = adversary_review(row, registry)
                if review and review.get('policy_question'):
                    questions[sentences(clean(review['policy_question']), 260)] += 1
            groups.append(dict(id=key, question=question, rows=len(members), fields=sum(len(b['changes']) for b in members),
                               items=[b['id'] for b in members], reviewer_questions=[plain(q) for q, _ in questions.most_common(3)]))
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
        set_decision_note='These have been checked by AI, not by a person row by row. Whether they go in as a group is decided outside this page, and nothing has been applied.',
        record_exclusions=[f'row:{r}' for r in views['record_exclusion']],
        rule_groups=groups,
        blocked=dict(kinds=dict(blocked_kinds), items=[f'row:{r}' for r in views['source_blocked']],
                     labels={k: STATE_TEXT[k] for k in SOURCE_BLOCKED}),
        no_edit=[f'row:{r}' for r in views['no_edit']], withdraw=[f'row:{r}' for r in views['withdraw']],
        close_read=dict((lambda c: (('sample', c['sample']), ('decisions', c['decisions'])))(read(T / 'close_read_20261104.json'))),
        rebind=[f'row:{r}' for r in views['rebind']], needs_reference=[f'row:{r}' for r in views['needs_reference']], pending_read=[f'row:{r}' for r in views['pending_read']],
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
