# FLoRA audit

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
