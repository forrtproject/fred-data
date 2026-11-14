"""Classify every confirmed audit finding under the agreed FReD application policies.

Audit findings (results.csv / progress.json) are never changed here. This script decides
which findings may be applied to FReD, which are held, and which are not errors under
FReD's coding rules. Policies agreed by Lukas Wallrich on 7 November 2026:

D1  Effect sizes are coded relative to the original effect. A correction that leaves the
    original and replication effects pointing in opposite directions needs review.
D2  reported_success is coded per study (the success-sheet join key doi_o/id_r/study_o/
    study_r) and only from an author statement or project coding rule. Effect-level
    disagreements within one study are not applicable.
D3  A correction applies only if its row side (N, effect size, p) stays coherent. When a
    sibling field on that side is unverified, the correction is held if it changes the
    test kind, changes N by 10% or more, is explained as replacing a value taken from
    another test/row/model, or makes N, statistic and p contradict each other.
T2  Changes of test model, large changes of sample role, metric-equivalence decisions
    and conceptual adaptations are reviewed individually.

Human decisions in manual_decisions.csv override the automatic decision. Only rows whose
final decision is "apply" reach the FReD patch.
"""
import argparse, collections, csv, json, math, random, re, sys
from pathlib import Path

P = Path(__file__).resolve().parent
B = P.parents[1]
sys.path.insert(0, str(B / 'scripts'))
from compare import load_adjudications, combine_obvious, metric, parsed_stat  # noqa: E402
from consistency import number, analytic_n, p_parts, pinterval, stat_interval  # noqa: E402

NUMERIC = ['n', 'es_value', 'pval_value']
DECISIONS = {'apply', 'review', 'hold', 'not_applicable', 'reject'}
SAMPLE_SIZE, SAMPLE_SEED = 30, 20261107
# Text in a review's reason that says the shipped value belongs to another test/analysis.
SWITCH = re.compile(
    r'(?i)(comes from|came from|taken from|was taken|(recorded|extracted|copied|took) .{0,60}from (the|a|an) '
    r'(different|separate|secondary|follow-up|exploratory|omnibus|pairwise|subsequent|full|total|other|interaction)|'
    r'misaligned|wrong (row|test|column|model|table)|different (test|analysis|model|outcome|sample|study|row|condition))')
ADAPTATION = re.compile(r'(?i)conceptual (replication|adaptation)|adapted (target|test|replication)|composite|proxy')
UNSIGNED = {'f', 'chi2', 'x2', 'etasq', 'etasq (partial)', 'r-squared', "cohen's f^2", "cohen's f",
            'omega squared', 'proportion', 'bayes factor', 'w', 'cramer\'s v', "cramér's v", 'kendall\'s w'}
RATIO = {'or', 'rr', 'irr', 'hr', 'odds ratio', 'risk ratio', 'hazard ratio'}


def txt(x):
    return '' if x is None else str(x)


def study_key(row):
    """The key prepare_fred.qmd uses to join the study-level success sheet."""
    doi_r = re.sub(r'\s', '', txt(row.get('doi_r')).lower())
    return (re.sub(r'\s', '', txt(row.get('doi_o')).lower()), txt(row.get('url_r')) or doi_r,
            txt(row.get('study_o')), txt(row.get('study_r')))


def stat_value(value):
    parsed = parsed_stat(txt(value).replace('–', '-'))
    return (parsed[0], number(parsed[2])) if parsed else (None, number(value))


def direction(value, es_type):
    """+1/-1 for a signed effect, None when the metric carries no direction."""
    kind, v = stat_value(value)
    if v is None or v == 0:
        return None
    if kind:
        return (1 if v > 0 else -1) if kind in ('t', 'z') else None
    m = metric(es_type)
    if m in RATIO:
        return None if v == 1 else (1 if v > 1 else -1)
    if m in UNSIGNED or m == 'test statistic':
        return None
    return 1 if v > 0 else -1


def side_state(row, s):
    """Return (p-vs-statistic consistent?, N minus error df) for one row side."""
    interval, _ = stat_interval(txt(row['es_value_' + s]).replace('–', '-'), row['es_type_' + s],
                                row['n_' + s], row['nested_' + s], row['pval_tails_' + s])
    p = pinterval(row['pval_value_' + s], row['pval_type_' + s])
    consistent = None if interval is None or p is None else max(interval[0], float(p[0])) <= min(interval[1], float(p[1]))
    parsed = parsed_stat(txt(row['es_value_' + s]).replace('–', '-'))
    n = analytic_n(row['n_' + s])
    gap = n - parsed[1][-1] if parsed and parsed[0] in ('t', 'f') and parsed[1] and n else None
    return consistent, gap


def subsample_gap(gap, n):
    """N far above the test's error df suggests the test used a subsample of the coded N."""
    return gap is not None and n and gap > max(12, 0.1 * n)


def patched(row, corrections, decisions):
    out = dict(row)
    for e in corrections:
        f = e['field']
        if f.startswith('pval'):
            d = decisions[(e['audit_id'], f)]
            # A bare printed number without an operator is an equality (as build_release.py records it).
            parts = p_parts(e['correction'], d.get('correct_bound')) or p_parts(e['correction'], 'e')
            if parts:
                out[f] = str(parts[0])
                out['pval_type_' + f[-1]] = parts[1]
                continue
        out[f] = e['correction']
    return out


def load():
    progress = json.loads((B / 'progress.json').read_text())
    parent = json.loads((B / 'parent_rows.json').read_text())
    results = {int(r['input_row_index']): r for r in csv.DictReader((B / 'results.csv').open(encoding='utf-8-sig'))}
    decisions = combine_obvious(load_adjudications(B), json.loads((B / 'obvious_resolutions.json').read_text()))
    field_overrides = {(a['audit_id'], a['field']) for a in json.loads((B / 'target_overrides.json').read_text()) if a.get('field')}
    metric_rules = {(a['audit_id'], a['field']) for a in json.loads((B / 'metric_equivalences.json').read_text())}
    return progress['confirmed_errors'], parent, results, decisions, field_overrides, metric_rules


def verified(results, aid, field):
    return results[aid][field + '_final_verdict'] in ('correct', 'error')


def classify(errors, parent, results, decisions, field_overrides, metric_rules):
    by_row = collections.defaultdict(list)
    for e in errors:
        by_row[e['audit_id']].append(e)
    groups = collections.defaultdict(list)
    for i, row in enumerate(parent, 1):
        groups[study_key(row)].append(i)
    ledger = []
    for e in errors:
        aid, field = e['audit_id'], e['field']
        row = parent[aid - 1]
        d = decisions[(aid, field)]
        tags, outcome = [], []  # outcome: (rank, decision, policy, reason)
        if field == 'reported_success':
            members = groups[study_key(row)]
            labels, unverified = set(), []
            for j in members:
                verdict = results[j]['reported_success_final_verdict']
                if verdict == 'correct':
                    labels.add(txt(parent[j - 1]['reported_success']))
                elif verdict == 'error':
                    labels.add(txt(results[j]['reported_success_suggested_correction']))
                else:
                    unverified.append(j)
            tags.append(f'study_effects={len(members)}')
            if len(labels) > 1:
                outcome.append((4, 'not_applicable', 'D2-effect-level',
                                f'Effects of this study carry different verified labels ({", ".join(sorted(labels))}); '
                                'reported_success is coded per study.'))
            else:
                note = ('Confirm an explicit author statement or project coding rule for the study-level label.'
                        if not unverified else
                        f'Confirm an explicit study-level author statement; applying relabels {len(unverified)} unverified effect(s) of the same study.')
                outcome.append((2, 'review', 'D2-author-basis', note))
                if unverified:
                    tags.append('unverified_study_siblings=' + ';'.join(map(str, unverified)))
            quote = txt(d.get('quote')).rstrip()
            if quote.endswith((',', '[', '(')) or quote.count('[') > quote.count(']'):
                tags.append('quote_truncated')
        else:
            s = field[-1]
            siblings = [f + '_' + s for f in NUMERIC]
            side_errors = [x for x in by_row[aid] if x['field'] in siblings]
            full = all(verified(results, aid, f) for f in siblings)
            before = side_state(row, s)
            after_row = patched(row, side_errors, decisions)
            after = side_state(after_row, s)
            n_after = analytic_n(after_row['n_' + s])
            newly_inconsistent = before[0] is not False and after[0] is False
            new_gap = subsample_gap(after[1], n_after) and not subsample_gap(before[1], analytic_n(row['n_' + s]))
            old_kind, _ = stat_value(e['shipped'])
            new_kind, _ = stat_value(e['correction'])
            kind_change = field.startswith('es_') and (old_kind or new_kind) and old_kind != new_kind
            n_shift = False
            if field.startswith('n_'):
                a, b = analytic_n(e['shipped']), analytic_n(e['correction'])
                n_shift = bool(a and b and max(a, b) / min(a, b) >= 1.1)
            language = bool(SWITCH.search(txt(d.get('reason'))))
            switch = kind_change or n_shift or language
            if kind_change:
                tags.append(f'test_kind:{old_kind or "scalar"}->{new_kind or "scalar"}')
            if n_shift:
                tags.append('n_shift>=10%')
            if language:
                tags.append('reason_names_other_test')
            if not full:
                tags.append('unverified_siblings=' + ';'.join(f for f in siblings if not verified(results, aid, f)))
            if newly_inconsistent:
                tags.append('p_vs_statistic_newly_inconsistent')
            if new_gap:
                tags.append('n_exceeds_test_df')
            if not full and (switch or newly_inconsistent or new_gap):
                outcome.append((3, 'hold', 'D3-partial-side',
                                'Sibling field(s) stay unverified while this correction moves the side to another test '
                                'or makes N, statistic and p contradict each other.'))
            elif newly_inconsistent or new_gap:
                outcome.append((2, 'review', 'D3-coherence', 'All side fields are verified, but the corrected values contradict each other.'))
            if field.startswith('es_'):
                o_row = patched(row, by_row[aid], decisions)
                dir_before = (direction(row['es_value_o'], row['es_type_o']), direction(row['es_value_r'], row['es_type_r']))
                dir_after = (direction(o_row['es_value_o'], o_row['es_type_o']), direction(o_row['es_value_r'], o_row['es_type_r']))
                own_before, own_after = direction(e['shipped'], row['es_type_' + s]), direction(e['correction'], row['es_type_' + s])
                if own_before and own_after and own_before != own_after:
                    tags.append('sign_flip')
                    if None not in dir_after and dir_after[0] != dir_after[1]:
                        outcome.append((2, 'review', 'D1-direction',
                                       'After correction the original and replication effects point in opposite directions; '
                                       'confirm a genuine reversal rather than reversed predictor/outcome coding.'))
                    elif None not in dir_before and dir_before[0] != dir_before[1]:
                        tags.append('sign_alignment_restored')
                if kind_change:
                    outcome.append((1, 'review', 'T2-model-change', 'The correction replaces the coded test with a different test.'))
                if (aid, field) in metric_rules:
                    outcome.append((1, 'review', 'T2-metric-equivalence', 'The verdict relies on a field-specific metric-equivalence rule.'))
            if field.startswith('n_'):
                a, b = analytic_n(e['shipped']), analytic_n(e['correction'])
                if a and b and max(a, b) / min(a, b) >= 1.9:
                    tags.append(f'n_ratio={max(a, b) / min(a, b):.1f}')
                    outcome.append((1, 'review', 'T2-sample-role', 'N changes by a factor of 1.9 or more (sample role, unit or subgroup).'))
            basis = txt(results[aid][field + '_target_basis']) + ' ' + txt(d.get('reason'))
            if ADAPTATION.search(basis):
                tags.append('conceptual_adaptation')
                outcome.append((1, 'review', 'T2-adaptation', 'The confirmed target is a conceptual adaptation of the original test.'))
        if (aid, field) in field_overrides:
            tags.append('field_target_override')
        if 'quote_truncated' in tags:
            outcome.append((1, 'review', 'quote', 'The replacement author quote appears truncated.'))
        if outcome:
            rank, decision, policy, reason = max(outcome, key=lambda x: x[0])
            policies = sorted({o[2] for o in outcome})
        else:
            decision, policy, reason, policies = 'apply', 'T1', 'Same-target correction on a coherent row side.', ['T1']
        ledger.append({
            'correction_id': f'FRED202610-{aid:04d}-{field}', 'audit_id': aid, 'effect_id': txt(row['effect_id']),
            'fred_id': txt(row['fred_id']), 'field': field, 'old_value': txt(e['shipped']), 'new_value': txt(e['correction']),
            'auto_decision': decision, 'policy': policy, 'all_policies': ';'.join(policies), 'auto_reason': reason,
            'tags': ';'.join(tags), 'sample_check': ''})
    return ledger


def merge_manual(ledger, path):
    manual = {}
    if path.exists():
        for m in csv.DictReader(path.open(encoding='utf-8-sig')):
            assert m['decision'] in {'apply', 'reject', 'hold'}, m
            assert m['correction_id'] not in manual, ('Duplicate manual decision', m['correction_id'])
            manual[m['correction_id']] = m
    known = {r['correction_id'] for r in ledger}
    unknown = set(manual) - known
    assert not unknown, ('Manual decisions for unknown corrections', sorted(unknown))
    for r in ledger:
        m = manual.get(r['correction_id'], {})
        r['manual_decision'] = m.get('decision', '')
        r['manual_reviewer'] = m.get('reviewer', '')
        r['manual_date'] = m.get('date', '')
        r['manual_note'] = m.get('note', '')
        r['final_decision'] = r['manual_decision'] or r['auto_decision']
        assert r['final_decision'] in DECISIONS
    return ledger


COLUMNS = ['correction_id', 'audit_id', 'effect_id', 'fred_id', 'field', 'old_value', 'new_value', 'auto_decision',
           'policy', 'all_policies', 'auto_reason', 'tags', 'sample_check', 'manual_decision', 'manual_reviewer',
           'manual_date', 'manual_note', 'final_decision']


def enforce_side_coherence(ledger, errors, parent, decisions):
    """D3 on the applied set: a correction coherent only together with an unapplied sibling waits for it."""
    by_side = collections.defaultdict(list)
    for e in errors:
        if e['field'] != 'reported_success':
            by_side[(e['audit_id'], e['field'][-1])].append(e)
    rows = {(r['audit_id'], r['field']): r for r in ledger}
    changed = True
    while changed:
        changed = False
        for (aid, s), side_errors in by_side.items():
            applied = [e for e in side_errors if rows[(aid, e['field'])]['final_decision'] == 'apply']
            if not applied or any(rows[(aid, e['field'])]['manual_decision'] == 'apply' for e in applied):
                continue
            row = parent[aid - 1]
            before, after = side_state(row, s), side_state(patched(row, applied, decisions), s)
            n_before, n_after = analytic_n(row['n_' + s]), analytic_n(patched(row, applied, decisions)['n_' + s])
            if (before[0] is not False and after[0] is False) or (subsample_gap(after[1], n_after) and not subsample_gap(before[1], n_before)):
                waiting = [e['field'] for e in side_errors if e not in applied]
                for e in applied:
                    r = rows[(aid, e['field'])]
                    r.update(auto_decision='hold', final_decision='hold', policy='D3-paired',
                             all_policies=';'.join(sorted(set(r['all_policies'].split(';')) - {'T1'} | {'D3-paired'})),
                             auto_reason='Coherent only together with sibling correction(s) not yet applied: ' + (', '.join(waiting) or 'none') + '.')
                changed = True
    return ledger


def build_ledger():
    data = load()
    errors, parent, results, decisions = data[:4]
    ledger = merge_manual(classify(*data), P / 'manual_decisions.csv')
    ledger = enforce_side_coherence(ledger, errors, parent, decisions)
    applied = sorted((r for r in ledger if r['auto_decision'] == 'apply'), key=lambda r: r['correction_id'])
    for r in random.Random(SAMPLE_SEED).sample(applied, min(SAMPLE_SIZE, len(applied))):
        r['sample_check'] = 'T1-random-30'
    return ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--out', default=str(P / 'application_decisions.csv'))
    args = parser.parse_args()
    ledger = build_ledger()
    with open(args.out, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator='\n')
        w.writeheader()
        w.writerows(sorted(ledger, key=lambda r: (r['audit_id'], r['field'])))
    print(json.dumps({'findings': len(ledger),
                      'final': dict(collections.Counter(r['final_decision'] for r in ledger)),
                      'policy': dict(collections.Counter(r['policy'] for r in ledger)),
                      'sample_check': sum(bool(r['sample_check']) for r in ledger)}, indent=1))


if __name__ == '__main__':
    main()
