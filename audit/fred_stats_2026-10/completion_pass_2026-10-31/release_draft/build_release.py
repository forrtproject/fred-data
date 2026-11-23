"""Build the FReD correction package from the checked audit export and the decision ledger.

Every confirmed audit finding is listed in confirmed_corrections.csv with its application
status. Only findings whose final decision in application_decisions.csv is "apply" become
physical cell updates in fred_fixes.csv. Nothing here changes FReD, the frozen workbook,
the audit verdicts or the published 635-correction snapshot in this directory.

Run from the repository root:
  python3 audit/fred_stats_2026-10/completion_pass_2026-10-31/release_draft/policy_ledger.py
  python3 audit/fred_stats_2026-10/completion_pass_2026-10-31/release_draft/build_release.py \
      --out audit/fred_stats_2026-10/completion_pass_2026-10-31/release_draft/application_package
"""
import argparse, collections, csv, hashlib, json, re, shutil, subprocess, sys, zipfile
from pathlib import Path

P = Path(__file__).resolve().parent
B = P.parents[1]
sys.path.insert(0, str(B / 'scripts'))
sys.path.insert(0, str(P))
from compare import load_adjudications, combine_obvious, metric, parsed_stat, quote_ok, fresh_test_review, reviewed_correction_value  # noqa: E402
from consistency import p_parts, number, analytic_n, pinterval, stat_interval  # noqa: E402
import policy_ledger  # noqa: E402

KEY = ['entry_id', 'effect_id', 'fred_id']
GUARD = KEY + ['ref_o', 'doi_o', 'study_o', 'ref_r', 'doi_r', 'url_r', 'study_r', 'description', 'es_type_o', 'es_type_r',
               'nested_o', 'nested_r', 'pval_tails_o', 'pval_tails_r']
FIELDS = ['n_o', 'es_value_o', 'pval_value_o', 'n_r', 'es_value_r', 'pval_value_r', 'reported_success']
DOWNLOADS = ['fred_fixes.csv', 'merge_fred_fixes.R', 'row_guard.csv', 'confirmed_corrections.csv', 'application_decisions.csv',
             'coherence_check.csv', 'field_summary.csv', 'field_summary_by_project.csv', 'availability_followups.csv',
             'screen_recheck.csv', 'release_summary.json', 'README.md']
OWNED = set(DOWNLOADS) | {'SHA256SUMS.txt', 'fred_audit_fixes.zip', 'test_merge.R', 'r_validation.json'}
MINUS = str.maketrans({'–': '-', '−': '-'})
QUOTE_GLYPHS = {'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl', '⫽': '=', '⬍': '<', '⬎': '>'}
PROTECTED_GLYPHS = re.compile('[⫽⬍⬎␩ﬁﬂﬀﬃﬄ¼]')


def txt(x):
    return '' if x is None else str(x)


def clean_quote(q):
    """Remove PDF extraction artefacts without changing wording."""
    for a, b in QUOTE_GLYPHS.items():
        q = q.replace(a, b)
    return re.sub(r'(\w)-\s*(?:…|\.\.\.)\s*(\w)', r'\1\2', q)  # word hyphenated across a bridged line break


def write_csv(path, rows, cols=None):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols or list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def project_summary(project_counts, field_counts):
    rows = []
    for prefix, fields in sorted(project_counts.items()):
        for field, c in fields.items():
            e = c.get('error', 0); ev = e + c.get('correct', 0); u = c.get('unverified', 0); nc = c.get('not_comparable', 0); n = ev + u + nc
            rows.append({'fred_id_prefix': prefix, 'field': field, 'errors': e, 'evaluable': ev, 'error_rate_evaluable': e / ev if ev else None,
                         'unverified': u, 'not_comparable': nc, 'total': n, 'lower_all_row_error_bound': e / n if n else None,
                         'upper_all_row_error_bound': (e + u + nc) / n if n else None})
    for field, c in field_counts.items():
        group = [r for r in rows if r['field'] == field]
        for column, want in [('errors', c.get('error', 0)), ('evaluable', c.get('correct', 0) + c.get('error', 0)),
                             ('unverified', c.get('unverified', 0)), ('not_comparable', c.get('not_comparable', 0))]:
            assert sum(r[column] for r in group) == want, (field, column, 'Project totals disagree with overall field totals')
    return rows


def check_ledger():
    """The tracked ledger must equal a fresh classification plus manual decisions."""
    path = P / 'application_decisions.csv'
    assert path.exists(), 'Run policy_ledger.py first'
    tracked = list(csv.DictReader(path.open(encoding='utf-8-sig')))
    fresh = sorted(policy_ledger.build_ledger(), key=lambda r: (r['audit_id'], r['field']))
    assert [{k: str(v) for k, v in r.items()} for r in fresh] == [{k: r[k] for k in policy_ledger.COLUMNS} for r in tracked], \
        'application_decisions.csv is stale; rerun policy_ledger.py'
    return {(int(r['audit_id']), r['field']): r for r in tracked}


def side_check(row, s):
    interval, kind = stat_interval(txt(row['es_value_' + s]).replace('–', '-'), row['es_type_' + s], row['n_' + s],
                                   row['nested_' + s], row['pval_tails_' + s])
    p = pinterval(row['pval_value_' + s], txt(row['pval_type_' + s]).split(' ')[0])
    consistent = None if interval is None or p is None else max(interval[0], float(p[0])) <= min(interval[1], float(p[1]))
    parsed = parsed_stat(txt(row['es_value_' + s]).replace('–', '-'))
    n = analytic_n(row['n_' + s])
    gap = n - parsed[1][-1] if parsed and parsed[0] in ('t', 'f') and parsed[1] and n else None
    return consistent, policy_ledger.subsample_gap(gap, n)


def build(out):
    sys.path.insert(0, str(P.parent))
    from check_yield_ready import scientific_fingerprint
    fingerprint = json.loads((P.parent / 'export_fingerprint.json').read_text())
    assert fingerprint['scientific_inputs_sha256'] == scientific_fingerprint(), 'Recompute the checked export before building downloads'
    assert fingerprint['results_sha256'] == hashlib.sha256((B / 'results.csv').read_bytes()).hexdigest()
    manifest = json.loads((B / 'run_manifest.json').read_text()); progress = json.loads((B / 'progress.json').read_text())
    parent = json.loads((B / 'parent_rows.json').read_text())
    results = {int(r['input_row_index']): r for r in csv.DictReader((B / 'results.csv').open(encoding='utf-8-sig'))}
    assert hashlib.sha256((B.parents[1] / 'output/FReD.xlsx').read_bytes()).hexdigest() == manifest['input_sha256']
    ledger = check_ledger()
    decisions = combine_obvious(load_adjudications(B), json.loads((B / 'obvious_resolutions.json').read_text()))
    preservation = json.loads((P.parent / 'preservation_check.json').read_text())
    assert not preservation['changed_protected_fields'] and not preservation['unscoped_gains']

    errors = progress['confirmed_errors']
    assert set(ledger) == {(e['audit_id'], e['field']) for e in errors} and len(errors) == len(ledger)
    applied = {k for k, r in ledger.items() if r['final_decision'] == 'apply'}
    corrections, patches, seen, guard_ids, bound_inferences, normalised = [], [], set(), set(), [], []

    def patch(row, e, cid, column, new, role, source_url, location):
        old = txt(row[column]); new = txt(new)
        if old.replace('\r\n', '\n').strip() == new.replace('\r\n', '\n').strip():
            return
        key = (row['input_row_index'], column); assert key not in seen, key; seen.add(key)
        patches.append({'correction_id': cid, 'audit_id': row['input_row_index'], **{k: row[k] for k in KEY}, 'audit_field': e['field'],
                        'target_column': column, 'old_value': old, 'new_value': new, 'role': role, 'source_url': source_url,
                        'source_location': location})
        guard_ids.add(row['input_row_index'])

    # Study-level reported_success: one canonical applied correction per study (policy D2).
    groups = collections.defaultdict(list)
    for i, row in enumerate(parent, 1):
        groups[policy_ledger.study_key(row)].append(i)
    canonical = {}
    for e in sorted(errors, key=lambda x: x['audit_id']):
        if e['field'] == 'reported_success' and (e['audit_id'], e['field']) in applied:
            canonical.setdefault(policy_ledger.study_key(parent[e['audit_id'] - 1]), e)

    for e in errors:
        aid, field = e['audit_id'], e['field']; row = parent[aid - 1]; d = decisions[aid, field]; status = ledger[(aid, field)]
        assert results[aid][field + '_final_verdict'] == 'error'
        assert e['correction'] == reviewed_correction_value(d, field)
        assert quote_ok({**d, 'value': d['correct_value'], 'confident': True})
        source_url = 'https://doi.org/' + e['doi'] if e.get('doi') else e.get('primary_source_url') or txt(row['url_r'])
        source_ref = row['ref_o'] if field.endswith('_o') else row['ref_r']
        new = e['correction']; pbound = ''; esmetric = ''; cid = status['correction_id']
        x = json.loads((B / 'extractions' / f'{aid}.json').read_text())
        blind = x['reported_success'] if field == 'reported_success' else x['original' if field.endswith('_o') else 'replication']['n' if field.startswith('n_') else 'es' if field.startswith('es_') else 'p']
        if field.startswith('pval'):
            fallback = d.get('correct_bound'); parts = p_parts(new, fallback)
            if parts is None and fallback is None and d['verdict'] == 'blind_right' and number(new) == number(blind['value']):
                parts = p_parts(new, blind['bound'])
            if parts is None:
                # Two historical both-wrong decisions give an explicit equality in their validated quote.
                assert aid in [900, 902] and field == 'pval_value_r'
                assert re.search(r'p\s*[=  ]+\s*\.?' + ('0004' if aid == 900 else '45'), d['quote'])
                parts = p_parts(new, 'e')
                bound_inferences.append({'audit_id': aid, 'field': field, 'correct_bound': 'e', 'basis': 'Explicit p equality in the already validated primary quote.', 'quote': d['quote']})
            assert parts; new, pbound = str(parts[0]), parts[1]
        elif field.startswith('n_'):
            n = analytic_n(new); assert n and n.is_integer(); new = str(int(n))
        if field.startswith('es_'):
            esmetric = d.get('correct_metric') or ('test statistic' if parsed_stat(new) else None)
            if not esmetric and d['verdict'] == 'blind_right' and number(new) == number(blind['value']):
                esmetric = blind['metric']
            if metric(row['es_type_' + field[-1]]) == 'test statistic' and (parsed_stat(new) or fresh_test_review(d, field, row)):
                esmetric = 'test statistic'
            assert esmetric and metric(esmetric) == metric(row['es_type_' + field[-1]]), (aid, field)
            if new.translate(MINUS) != new:
                normalised.append({'correction_id': cid, 'printed': new}); new = new.translate(MINUS)
        if (aid, field) in applied:
            before = len(patches)
            if field == 'reported_success':
                c = canonical[policy_ledger.study_key(row)]; cd = decisions[c['audit_id'], 'reported_success']
                quote = clean_quote(cd['quote']); qsource = f"{source_url}; {cd['location']}"
                patch(row, e, cid, field, new, 'confirmed_value', source_url, d['location'])
                patch(row, e, cid, 'reported_success_quote', quote, 'associated_author_quote', source_url, cd['location'])
                patch(row, e, cid, 'reported_success_quote_source', qsource, 'associated_author_quote_source', source_url, cd['location'])
                for j in groups[policy_ledger.study_key(row)]:
                    if results[j]['reported_success_final_verdict'] in ('correct', 'error'):
                        continue
                    sibling = parent[j - 1]
                    if txt(sibling['reported_success']) == txt(row['reported_success']) and (j, 'reported_success') not in seen:
                        patch(sibling, e, cid, 'reported_success', new, 'study_level_propagation', source_url, d['location'])
                        patch(sibling, e, cid, 'reported_success_quote', quote, 'study_level_propagation', source_url, cd['location'])
                        patch(sibling, e, cid, 'reported_success_quote_source', qsource, 'study_level_propagation', source_url, cd['location'])
            else:
                patch(row, e, cid, field, new, 'confirmed_value', source_url, d['location'])
                if field.startswith('pval'):
                    patch(row, e, cid, 'pval_type_' + field[-1], {'e': 'e (=)', 'l': 'l (<)', 'g': 'g (>)', 'le': 'le (<=)', 'ge': 'ge (>=)'}[pbound],
                          'associated_p_bound', source_url, d['location'])
                if field.startswith('es_'):
                    patch(row, e, cid, 'es_repr_' + field[-1], f"{source_url}; {d['location']}", 'associated_source_locator', source_url, d['location'])
            assert len(patches) > before, (aid, field, 'No physical change for an applied correction')
        corrections.append({'correction_id': cid, 'audit_id': aid, **{k: row[k] for k in KEY}, 'field': field, 'old_value': txt(row[field]),
                            'new_value': new, 'printed_correction': e['correction'],
                            'requested_metric': txt(row.get('es_type_' + field[-1])) if field.startswith('es_') else '', 'corrected_metric': esmetric,
                            'old_p_bound': txt(row.get('pval_type_' + field[-1])) if field.startswith('pval') else '', 'new_p_bound': pbound,
                            'error_kind': e['error_kind'], 'resolution': results[aid][field + '_resolution'],
                            'application_status': status['final_decision'], 'application_policy': status['policy'],
                            'application_reason': status['manual_note'] or status['auto_reason'],
                            'source_url': source_url, 'source_reference': source_ref, 'source_location': d['location'], 'reason': d['reason']})

    for p in patches:
        if p['role'] in ('confirmed_value', 'associated_p_bound'):
            assert not PROTECTED_GLYPHS.search(p['new_value']), ('Extraction glyph in a value', p['correction_id'], p['new_value'])

    # Coherence of every patched row side, before and after the complete patch (policy D3).
    updated = {i: dict(parent[i - 1]) for i in guard_ids}
    for c in patches:
        updated[c['audit_id']][c['target_column']] = c['new_value']
    coherence = []
    for i in sorted(guard_ids):
        for s in 'or':
            if not any(c['audit_id'] == i and c['target_column'] in (f'n_{s}', f'es_value_{s}', f'pval_value_{s}') for c in patches):
                continue
            (pb, gb), (pa, ga) = side_check(parent[i - 1], s), side_check(updated[i], s)
            newly = (pb is not False and pa is False) or (ga and not gb)
            manual = any(r['manual_decision'] == 'apply' for (a, f), r in ledger.items() if a == i and f.endswith('_' + s))
            coherence.append({'audit_id': i, 'side': s, 'p_consistent_before': pb, 'p_consistent_after': pa, 'n_exceeds_df_before': gb,
                              'n_exceeds_df_after': ga, 'status': 'newly_inconsistent' if newly else 'ok', 'manual_override': manual})
            assert not newly or manual, ('Applied correction makes row side incoherent', i, s)

    screen = []
    for flag_row in csv.DictReader((B / 'consistency.csv').open(encoding='utf-8-sig')):
        aid = int(flag_row['input_row_index']); row = updated.get(aid, parent[aid - 1])
        for flag in filter(None, flag_row['flags'].split(';')):
            side = flag[-1]; ok = None
            if flag.startswith('n_range'):
                n = analytic_n(row['n_' + side]); ok = bool(n and n > 0 and n.is_integer())
            elif flag.startswith('p_range'):
                ok = pinterval(row['pval_value_' + side], row['pval_type_' + side]) is not None
            elif flag.startswith('r_range'):
                v = number(row['es_value_' + side]); ok = v is not None and -1 <= v <= 1
            elif flag.startswith('p_consistency'):
                a, _ = stat_interval(row['es_value_' + side], row['es_type_' + side], row['n_' + side], row['nested_' + side], row['pval_tails_' + side])
                b = pinterval(row['pval_value_' + side], row['pval_type_' + side]); ok = None if a is None or b is None else max(a[0], b[0]) <= min(a[1], b[1])
            screen.append({'audit_id': aid, 'flag': flag, 'status': 'passes_after_applied_patch' if ok is True else 'still_flagged' if ok is False else 'not_recomputable'})

    status_counts = dict(collections.Counter(r['application_status'] for r in corrections))
    policy_counts = dict(collections.Counter(f"{r['application_status']}:{r['application_policy']}" for r in corrections))
    applied_rows = sorted({p['audit_id'] for p in patches})
    write_csv(out / 'confirmed_corrections.csv', corrections)
    write_csv(out / 'fred_fixes.csv', patches, ['correction_id', 'audit_id', *KEY, 'audit_field', 'target_column', 'old_value', 'new_value', 'role', 'source_url', 'source_location'])
    write_csv(out / 'row_guard.csv', [{k: txt(parent[i - 1][k]) for k in GUARD} for i in applied_rows], GUARD)
    shutil.copyfile(P / 'application_decisions.csv', out / 'application_decisions.csv')
    write_csv(out / 'coherence_check.csv', coherence, ['audit_id', 'side', 'p_consistent_before', 'p_consistent_after', 'n_exceeds_df_before', 'n_exceeds_df_after', 'status', 'manual_override'])
    write_csv(out / 'field_summary.csv', [{'field': f, **{k: progress['field_counts'][f].get(k, 0) for k in ['correct', 'error', 'unverified', 'not_comparable']},
                                           'evaluable': progress['field_counts'][f].get('correct', 0) + progress['field_counts'][f].get('error', 0),
                                           'applied_corrections': sum(1 for r in corrections if r['field'] == f and r['application_status'] == 'apply')} for f in FIELDS])
    write_csv(out / 'field_summary_by_project.csv', project_summary(progress['project_counts'], progress['field_counts']))
    write_csv(out / 'availability_followups.csv', [{'audit_id': a['audit_id'], 'side': a['side'], 'reference': a['reference'], 'reference_url': a['url'],
                                                    'coded_work_url': a['coded_work_url'], 'flag': a['flag'], 'status': a['status'], 'requested_action': a['requested_parent_action']}
                                                   for a in json.loads((B / 'safe_source_addendum/availability_followups.json').read_text())])
    write_csv(out / 'screen_recheck.csv', screen, ['audit_id', 'flag', 'status'])
    proposals = json.loads((P.parent / 'proposals.json').read_text())
    summary = {
        'release_status': 'draft application package; not published and not applied to FReD',
        'audit_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, cwd=P).strip(),
        'frozen_workbook_sha256': manifest['input_sha256'], 'snapshot_effects': len(parent),
        'audit_findings': {'confirmed_field_errors': len(corrections), 'affected_effect_rows': len({r['audit_id'] for r in corrections}),
                           'coding_omissions': sum(c['error_kind'] == 'coding omission' for c in corrections), 'field_counts': progress['field_counts'],
                           'coverage': progress['coverage']},
        'application': {'by_status': status_counts, 'by_status_and_policy': policy_counts, 'applied_corrections': status_counts.get('apply', 0),
                        'affected_effect_rows': len(applied_rows), 'physical_cell_updates': len(patches),
                        'patch_roles': dict(collections.Counter(p['role'] for p in patches)),
                        'minus_glyphs_normalised': normalised, 'row_sides_coherence_checked': len(coherence),
                        'policies': 'D1 sign relative to original; D2 reported_success per study from author statement or project rule; '
                                    'D3 coherent row sides; T2 individual review of model, sample-role, metric-equivalence and adaptation changes.'},
        'bound_metadata_recovered_from_validated_equality_quotes': bound_inferences,
        'screen_recheck': dict(collections.Counter(r['status'] for r in screen)),
        'exported_at': progress['updated_at'],
        'completion_pass': {'source_side_groups_assessed': len({r['source_key'] for r in proposals}), 'field_assessments': len(proposals),
                            'additional_verified_fields': len(preservation['new_verified_fields']),
                            'protected_verified_baseline_fields': preservation['protected_baseline_fields'], 'changed_protected_fields': 0,
                            'unscoped_gains': 0, 'incremental_paid_API_spend_USD': 0},
        'all_row_uncertainty_bounds_not_confidence_intervals': True, 'removals_in_patch': 0}
    (out / 'release_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    a = summary['application']
    (out / 'README.md').write_text(f"""# FReD statistics audit: correction package (draft)

Generated by `build_release.py` from audit commit `{summary['audit_commit'][:12]}` and export {summary['exported_at']}.
This package is a draft. It has not been published or applied to FReD.

## Findings versus applied corrections

The audit confirmed {len(corrections)} field discrepancies in {summary['audit_findings']['affected_effect_rows']} effect rows.
Under FReD's coding rules {a['applied_corrections']} are applied here, as {a['physical_cell_updates']} cell updates in {a['affected_effect_rows']} rows.
The others are awaiting individual review, held, or not errors under FReD's coding rules:

{chr(10).join(f'- {k}: {v}' for k, v in sorted(status_counts.items()))}

`confirmed_corrections.csv` lists every finding with its application status and reason.
`application_decisions.csv` records the automatic policy decision and any human decision.
Unverified and not-comparable fields are never patched.

## Policies

- D1: effect sizes are coded relative to the original effect.
- D2: `reported_success` is coded per study, only from an author statement or project coding rule. An applied label, quote and quote source are written to every effect of that study.
- D3: a correction is applied only if its row side (N, effect size, p) stays coherent; `coherence_check.csv` checks every patched side.
- T2: changes of test model, large sample-role changes, metric-equivalence decisions and conceptual adaptations need individual review.

## Applying the patch to the frozen workbook

Use only the frozen FReD workbook whose SHA256 (`{manifest['input_sha256']}`) is checked by the R script.
Install readxl, writexl and digest in R, place the files beside `FReD.xlsx`, then run:

```sh
Rscript merge_fred_fixes.R FReD.xlsx FReD_corrected.xlsx
```

The script checks record identities, expected old values and download hashes, writes a new workbook and a change log,
and never modifies the input. Excel styling is not preserved. Re-applying to the corrected data is a no-op.
Primary PDFs and full texts are excluded.
""")
    code = (P / 'merge_fred_fixes.R').read_text()
    for key, file in [('FIX', 'fred_fixes.csv'), ('GUARD', 'row_guard.csv')]:
        code = re.sub(r'(FRED_' + key + r'_SHA256 <- ")[^"]+(")', lambda m: m[1] + hashlib.sha256((out / file).read_bytes()).hexdigest() + m[2], code)
    (out / 'merge_fred_fixes.R').write_text(code)
    shutil.copyfile(P / 'test_merge.R', out / 'test_merge.R')
    (out / 'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256((out / n).read_bytes()).hexdigest()}  {n}\n' for n in DOWNLOADS))
    with zipfile.ZipFile(out / 'fred_audit_fixes.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for n in [*DOWNLOADS, 'SHA256SUMS.txt']:
            info = zipfile.ZipInfo(n, (2026, 11, 7, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o644 << 16
            z.writestr(info, (out / n).read_bytes())
    print(json.dumps({'findings': len(corrections), 'by_status': status_counts, 'applied_rows': len(applied_rows),
                      'physical_cell_updates': len(patches), 'patch_roles': a['patch_roles'],
                      'newly_inconsistent_sides': sum(c['status'] != 'ok' for c in coherence)}, indent=1))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--out', required=True, help='package directory (not the published snapshot directory)')
    out = Path(parser.parse_args().out).resolve()
    assert out != P, 'Write the package to its own directory; the published snapshot files stay unchanged'
    out.mkdir(parents=True, exist_ok=True)
    unexpected = [p.name for p in out.iterdir() if p.name not in OWNED]
    assert not unexpected, ('Unexpected files in package directory', unexpected)
    build(out)


if __name__ == '__main__':
    main()
