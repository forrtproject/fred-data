#!/usr/bin/env python3
"""Present all completed audit evidence as one current report; never edit FLoRA."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

B = Path(__file__).resolve().parents[1]
O = B / 'handoff'

def read_json(path):
    return json.loads(path.read_text())

def read_csv(path):
    # Match the existing handoff's CSV field parsing, including embedded newlines.
    with path.open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def save_json(name, value):
    (O / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def save_csv(name, rows, columns):
    with (O / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, columns, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

base_rows = read_csv(B / 'results.csv')
final = read_json(O / 'sol_review_decisions.json')['decisions']
by_row = {d['input_row_index']: d for d in final}
assert len(base_rows) == 2818 and len(by_row) == 109
row_view = []
for r in base_rows:
    i = int(r['input_row_index'])
    d = by_row.get(i)
    if d:
        kinds = {v['disposition'] for v in d['fields'].values()}
        status = ('policy_decision' if 'policy_decision_required' in kinds else
                  'evidence_limit' if kinds & {'reviewed_unknown', 'source_needed'} else
                  'determined')
    else:
        status = 'evidence_limit' if r['resolution'] == 'unresolved' else 'determined'
    row_view.append(dict(input_row_index=i, work_key=r['work_key'], file_key=r['file_key'],
                         audit_status=status, source_level=r['evidence_level'],
                         application_dependency=d.get('application_hold', '') if d else '',
                         decision_reference='sol_review_decisions.json' if d else '../results.csv'))
counts = Counter(r['audit_status'] for r in row_view)
assert counts == {'determined': 2516, 'evidence_limit': 294, 'policy_decision': 8}
save_csv('audit_rows.csv', row_view, list(row_view[0]))

initial = read_json(O / 'fix_proposals.json')
baseline_path = Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv')
assert hashlib.sha256(baseline_path.read_bytes()).hexdigest() == initial['baseline_sha256']
frozen = read_csv(baseline_path)
proposals = {}
withdrawn = []
for item in initial['existing_rows']:
    i = item['input_row_index']
    assert item['expected_before'] == frozen[i]
    d = by_row.get(i, {})
    for field, value in item['proposed_changes'].items():
        if field in d.get('withdraw_earlier_proposals', {}):
            withdrawn.append(dict(input_row_index=i, field=field, proposed_value=value,
                                  reason='Superseded by the complete source review; retain the original pair.'))
            continue
        proposals[(i, field)] = dict(input_row_index=i, field=field, proposed_value=value,
                                    expected_before=item['expected_before'], evidence=item['evidence'].get(field),
                                    status='source_adjudicated_proposal', decision_reference='../results.csv')
for d in final:
    for field, value in d['fields'].items():
        if value['disposition'] != 'correction_supported':
            continue
        i = d['input_row_index']
        assert (i, field) not in proposals
        approved = field in d.get('approved_for_application_fields', [])
        proposals[(i, field)] = dict(input_row_index=i, field=field,
                                    proposed_value=value['proposed_value'],
                                    expected_before=frozen[i],
                                    status='source_approved_not_applied' if approved else 'conditional_review_required',
                                    evidence=value, decision_reference='sol_review_decisions.json',
                                    application_dependency=d.get('application_hold'))
for (i, field), item in proposals.items():
    d = by_row.get(i, {})
    policy = any(v['disposition'] == 'policy_decision_required' for v in d.get('fields', {}).values())
    if policy:
        item['application_hold'] = 'Resolve this row’s coding-policy choice before applying its correction bundle.'
    elif d.get('application_hold'):
        item['application_hold'] = d['application_hold']
    before = item['expected_before']
    item['expected_before_full_record_sha256'] = hashlib.sha256(
        json.dumps(before, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    private_fields = [k for k, v in before.items() if any(token in v for token in
                      ['view_only=', 'access_token=', 'api_key=', 'Authorization: Bearer '])]
    if private_fields:
        item['expected_before'] = {k: v for k, v in before.items() if k not in private_fields}
        item['expected_before_omitted_private_fields'] = private_fields
        item['baseline_precondition'] = 'Validate the frozen file SHA256 and canonical full-record hash; private link fields are omitted from this presentation.'
assert len(proposals) == 563 and len({i for i, field in proposals}) == 516
assert len(withdrawn) == 1 and withdrawn[0]['input_row_index'] == 462
save_json('correction_proposals.json', dict(baseline_sha256=initial['baseline_sha256'],
          status='proposal_only_no_dataset_changes', field_count=len(proposals),
          row_count=len({i for i, field in proposals}),
          changes=[proposals[k] for k in sorted(proposals)], withdrawn_proposals=withdrawn))

missing = read_csv(B / 'confirmed_missing_references.csv')
columns = list(missing[0])
additions = read_json(O / 'confirmed_missing_pairs_addendum.json')['pairs']
for a in additions:
    r = {k: '' for k in columns}
    r.update(work_key=a['work_key'], file_key=a['file_key'],
             target_index=a['id'].rsplit(':', 1)[1], **a['original'])
    r = {k: v for k, v in r.items() if k in columns}
    if 'evidence' in r:
        r['evidence'] = json.dumps(dict(reason=a['rationale'],
                                      source_proof_locators=a['source_proof_locators']), ensure_ascii=False)
    missing.append(r)
pair_keys = {(r['work_key'].lower(), r['doi'].lower()) for r in missing if r['doi']}
assert len(missing) == 442
assert len(pair_keys) == sum(bool(r['doi']) for r in missing)
save_csv('confirmed_missing_pairs.csv', missing, columns)
unresolved = read_csv(B / 'unresolved_missing_candidates.csv')
missing_decisions = {d['case_id']: d for d in read_json(O / 'missing_pair_review_decisions.json')['decisions']}
unresolved = [r for r in unresolved if missing_decisions.get(
    f"missing:{r['file_key']}:{r['target_index']}", {}).get('verdict', 'reviewed_unknown') == 'reviewed_unknown']
assert len(unresolved) == 124
save_csv('unresolved_missing_pairs.csv', unresolved, list(unresolved[0]))

summary = dict(status='complete_audit_with_documented_limits', input_rows=2818,
               input_works=2344, determined_row_reviews=2516, evidence_limit_rows=294,
               policy_decision_rows=8, correction_proposal_fields=563, correction_proposal_rows=516,
               conditional_correction_fields=sum(bool(x.get('application_hold')) or x['status']=='conditional_review_required' for x in proposals.values()),
               explicitly_source_approved_fields=14,
               evidence_provenance_updates=14, review_required_rows=33,
               application_dependency_rows=4, confirmed_missing_pairs=442,
               unresolved_missing_candidates=124, all_assigned_fulltext_reviews_complete=True,
               baseline_sha256=initial['baseline_sha256'], canonical_dataset_changes_applied=False)
summary['input_sha256'] = {str(p.relative_to(B)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [B/'results.csv', O/'fix_proposals.json', O/'sol_review_decisions.json',
                                    B/'confirmed_missing_references.csv', O/'confirmed_missing_pairs_addendum.json',
                                    B/'unresolved_missing_candidates.csv', O/'missing_pair_review_decisions.json']}
save_json('audit_overview.json', summary)

report = '''# FLoRA audit

We audited the frozen FLoRA snapshot of **2,818 rows representing 2,344 works** using blind GPT-6.1 Sol coding, primary-source checks, and independent adjudication. The audit identifies incorrect original-study links, duplicate pairs, outcome miscoding, unsupported evidence quotations, and omitted study–original pairs. Corrections remain proposals; the shipped dataset and downstream pipelines are unchanged.

## Findings

| Result | Count |
| --- | ---: |
| Row reviews with determined field dispositions | 2,516 |
| Rows retaining a specific evidence limit | 294 |
| Rows requiring a coding-policy decision | 8 |
| Proposed field corrections | 563 across 516 rows |
| Source-confirmed missing study–original pairs | 442 |
| Unresolved possible missing pairs | 124 |

The row categories sum to all 2,818 input rows. “Determined” includes fields that become inapplicable when a source-supported removal or type correction is applied; it does not mean the proposed dataset changes have been applied. Seven field proposals have a policy or application hold. Four row bundles require coordination of identity changes, duplicate removal, or retained-attempt evidence. Fourteen fields carry explicit source-approval for application, and 14 primary-report quotation/provenance replacements are supplied separately. All proposals retain their evidence, approval state, and application dependencies.

The principal problems were incorrect allocation of findings to originals and incorrect interpretation of outcomes. For example, a results-blind ManyLabs5 manuscript had concealed an available completed report supporting a successful replication. Several student records used collection ratings or quotations from another project instead of the actual individual report. Checks also prevented unnecessary corrections: a title variant in a reference list was a miscitation, and online versus print publication years did not establish a different original.

Missing pairs were confirmed against the complete shipped counterpart set, corrected identities, and alternate or preliminary reports. A different DOI, title, or year alone did not establish an omission. The DeWitt science-capital comparison, for example, qualified because a distinct empirical sample and its finding were actually retested; shared data with an earlier article were retained in the reasoning. Missing-pair confirmation does not imply a separately verified replication outcome.

## Method

Fresh blind coders received only sanitised source metadata, the current report, and the codebook/schema. They did not see shipped values or prior verdicts. Independent informed reviewers compared findings with the shipped records, examined original-specific objections and necessary original reports or supplements, and checked literal evidence. GPT-6.1 Sol performed blind coding and source review; Gemini 4 Argon adjudicated non-obvious disagreements. Luna assisted source acquisition and candidate triage, with positive and negative labels independently checked against source identity and empirical content.

Source recovery covered the finite acquisition and omission inventories, including rechecking earlier omission confirmations. Available saved-full-text cases received complete scoped source reading. New primary reports were independently identified and checked for completeness before fresh blind coding and a separate informed comparison. All earlier attempts, source versions, rejected quotations, and contrary findings remain preserved in the audit records. No study analyses or dataset downloads were used to manufacture missing results.

## Remaining limits and decisions

Of the 294 rows with evidence limits, 221 have partial or abstract evidence, 52 lack usable text, and 21 have saved full text that still does not establish a necessary value. Complete reports can omit the required comparison, identify only a review rather than the claimed empirical original, or leave a particular project narrative unavailable. These are documented evidence limits, not unfinished reading.

The eight policy cases concern claim selection, hybrid replication/reproduction workflows, published anecdotal findings, inconclusive author verdicts, or discovery-inclusive pooled support. Concrete alternatives and their consequences appear in the review app. A complete source and agreement between models cannot settle an unspecified coding rule.

This is a completed audit within the documented source and codebook limits. It is not a claim that every scientific value is known or that every proposed change is ready to apply. Source access and review prioritisation also prevent treating observed error frequencies as representative estimates for other datasets. The most useful next work is to resolve the review cases, apply agreed changes with their exact baseline preconditions, and pursue specific missing reports when their findings matter.

## Review and downloads

- [Review app](http://100.121.34.85:8876/review.html): correction proposals, evidence, policy alternatives, and notes/export without dataset mutation.
- [Audit overview](handoff/audit_overview.json) and [all input-row dispositions](handoff/audit_rows.csv).
- [Combined correction proposals](handoff/correction_proposals.json), [explicitly source-approved fields](handoff/approved_fixes.json), and [primary evidence replacements](handoff/evidence_provenance_fixes.json).
- [Confirmed missing pairs](handoff/confirmed_missing_pairs.csv) and [unresolved candidates](handoff/unresolved_missing_pairs.csv).
- [Cases requiring review](handoff/review_required.json) and [field-level source decisions](handoff/sol_review_decisions.json).

The source exports and execution ledgers remain available for provenance. The [detailed comparison tables](evidence_followup/historical_integrated_report.md) retain their original denominators; the figures above reconcile all completed review decisions into one current audit view. Proposed changes are never automatically applied to FLoRA.

## Validation

Validation passed 88 regression tests, 533 raw handoff quotation checks, fresh-source schema and metadata checks, source hashes, baseline preconditions, and pair deduplication. All 109 saved-full-text review cases are complete. The 24 fresh-source packets contain 25 targets and 71 nonempty literal quote fields. The frozen FLoRA SHA-256 is `6d391186dfb57263bbc6bb504e8561e0d1e25997b36417072c023812efaad9f7`.

All owned model tasks are terminal; no audit workers or recovery schedule remain active. The private review server is retained for the user. Full acquired reports and private access details remain outside Git. Verification and preservation receipts are linked from the [audit handoff](handoff/README.md).
'''
(B / 'REPORT.md').write_text(report)
print(json.dumps(summary, indent=2))
