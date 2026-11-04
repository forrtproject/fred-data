# FLoRA audit handoff

The [full audit report](../REPORT.md) and [machine-readable overview](audit_overview.json) present the complete findings. The audit covers 2,818 input rows from 2,344 works. It gives determined field dispositions for 2,518 row reviews, retains specific evidence limits for 292, and identifies 8 coding-policy cases. Determined dispositions include conditional inapplicability after supported identity/type corrections; no dataset changes have been applied.

## Review and downloads

- [Correction proposals](correction_proposals.json): 562 field proposals across 515 rows, with evidence, frozen before-values, full-record hashes, and dependencies. Nineteen field proposals have a policy or application hold; whole-record remedies govern inclusion, source binding and coordinated application. One superseded removal is explicitly withdrawn.
- [Evidence updates](evidence_provenance_fixes.json): 14 literal primary-report quotation/provenance replacements, distinct from scientific field changes.
- [Confirmed missing pairs](confirmed_missing_pairs.csv): 440 genuinely absent study–original pairs for completed reports, with no outcome inferred from missing-pair identity alone.
- [Unresolved missing candidates](unresolved_missing_pairs.csv): 124 candidates with remaining source, identity, or finding-correspondence limits.
- [Record-level remedies](record_actions.json): inclusion and report-binding changes that must be resolved before isolated field edits.
- [Planned-study target pairs](planned_study_pairs.csv): two reference matches from the Bulgarian registration, kept out of completed-report additions.
- [All input rows](audit_rows.csv): one current audit-status record for every input row.
- [Review-required cases](review_required.json): 47 cases covering evidence limits, policy choices, and application dependencies.

The [Cloudflare review app](https://lukas-reports.lukas-wallrich.workers.dev/flora-audit-2026-10/) presents grouped proposals with quotes and reasoning. **Bulk approval of replication and reproduction outcomes is suspended.** An adjudication status did not establish that these corrections were unambiguous. Earlier bulk outcome approvals remain in the shared history but no longer produce ready-to-apply operations; review these changes individually.

**Row 462’s mixed → successful proposal is withheld.** “We replicate” establishes an attempt. The authors explicitly attribute the divergent healthcare-rumor result to Berinsky (2017), while the row binds Berinsky, Huber and Lenz (2012). This distinction needs a target-specific comparison inventory; it warrants neither automatic success nor transferring the 2017 divergence to the 2012 pair. Keep the shipped mixed value pending review. [Current objection and source passages](review_reliability.json) preserve both the challenge and the previous interpretation. Previously downloaded bulk outcome bundles should be replaced with a current export.

Every remaining grouped item can still be inspected through “Quotes & evidence”. Individual choices save to the shared log. Missing-pair identity approvals leave outcomes unassigned.

Next, download the approved implementation bundle, then review the remaining cases individually. The bundle contains exact operations, frozen-baseline and full-record checks, and a decision backup; record actions, policy choices and quote replacements stay separate implementation-review instructions. Downloading does not apply changes. Decisions and notes save to a shared Google-backed change log, visible to everyone using the review link. Enter your name once; attribution is self-reported. The app confirms each save by reading it back from the server. Pending writes survive reloads and retry on reconnection. Conflicting edits are retained for an explicit choice rather than overwriting another reviewer. The current navigation step remains personal to each browser; export/import also provides a backup. Earlier browser-only decisions can be published with the dedicated import button. The app verifies the complete queue SHA-256. Acquired full reports, private source paths, and access details are excluded from publication.

## Interpretation and application

Across the complete audit, 2,518 row reviews have determined field dispositions, 292 retain specific evidence limits, and 8 need coding-policy decisions. The evidence limits include 221 rows with partial or abstract evidence, 52 without usable text, and 19 where saved full text still cannot establish a necessary value. A completed audit does not establish a value the available evidence cannot support.

Record inclusion and report identity come before field edits. A plan without results must be kept outside the completed-results pool, or replaced by a verified linked results report with its metadata and quotations updated together. A proposed “not a replication” classification requires review of the whole record’s inclusion.

Every correction proposal has supporting audit evidence. The `decision_required` label marks a known policy or whole-record application hold; `evidence_checked_proposal` marks the other proposals. Both remain proposals. Apply a correction only after resolving its dependencies and checking its exact frozen before-record. Preserve both replication attempts when merging the OSC duplicate, retain source history for original replacements, and apply dependent outcomes only to their intended original. The combined files do not change the codebook or silently resolve policy choices.

The original exports, all model/source decisions, and contradictory evidence remain preserved. The combined view removes superseded proposals and reconciles completed decisions without overwriting those records. Detailed verification is in the [completion receipt](../evidence_followup/integration/final_sol_closure_20261031.json), [private-archive receipt](../evidence_followup/integration/final_sol_private_archive_20261031.json), and source decision files linked from the review app. [Three current-report reviews](current_source_decisions.json) replace simulated-source judgments only when their report-binding remedies are applied; all earlier judgments remain preserved.

Rebuild the presentation from the repository root:

```bash
python3 audit/flora_blind_2026-10/scripts/integrate_current_reports.py
python3 audit/flora_blind_2026-10/scripts/build_audit_report.py
python3 audit/flora_blind_2026-10/scripts/build_review_handoff.py
python3 audit/flora_blind_2026-10/scripts/build_audit_report.py
python3 audit/flora_blind_2026-10/scripts/validate_review_handoff.py
python3 audit/flora_blind_2026-10/scripts/validate_record_review.py
```

**Final position, 4 November 2026:** of 515 records with proposed changes (562 values), 156 are ready to apply, 4 need a route for changing the study type, 3 should be removed, 139 keep their existing value, 21 are already correct in FLoRA, 129 need a coding decision and 63 are on hold because the text available cannot settle them.

**To apply corrections, start with [`corrections_to_apply.csv`](corrections_to_apply.csv)** (one row per column to change) or [`corrections_to_apply.json`](corrections_to_apply.json) (the same changes per record, plus study-type changes that need a route and record removals). Both are keyed on the permanent FLoRA id and give the expected current value, the new value and the note to log. The [route](../independent_recode_20261101/flora_validation_application_route.json) covers the checks and rollback. Nothing has been applied.

**Handover:** the app and these corrections are being handed to the `flora-validation` maintainer, who is also asked to review the other changes and plan how to address them. The live app and its shared decision log work from any browser. Rebuilding it needs this folder plus the private audit files and the audited FLoRA copy, which exist only on the audit machine. Publishing it uses the audit owner's Cloudflare account.

The review app's status, ready lists, coding questions and source-blocked lists come from `independent_recode_20261101/field_ledger.json`, through [`ledger_review.json`](ledger_review.json). Rebuild the ledger first when any review changes. `batch_review.json` now holds missing-pair identities only: the earlier outcome and reproduction batches were retired, and earlier selections approve nothing. `correction_proposals.json` and the row numbers in this folder describe the frozen snapshot, not current FLoRA.

Build and publish the public app with the installed `deploy-html` helper:

```bash
flora_site_dir=$(mktemp -d /tmp/flora-audit-site.XXXXXX)
python3 audit/flora_blind_2026-10/scripts/build_public_review.py --output "$flora_site_dir"
/home/lukas/.codex/skills/deploy-html/bin/deploy-doc.sh "$flora_site_dir" --slug flora-audit-2026-10 --no-comments
```

The app supplies its own case-review controls. The [deployment receipt](../publication/cloudflare_deployment.json) records the hosted asset hashes and browser checks.
