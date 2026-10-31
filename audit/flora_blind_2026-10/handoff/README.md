# FLoRA audit handoff

The [full audit report](../REPORT.md) and [machine-readable overview](audit_overview.json) present the complete findings. The audit covers 2,818 input rows from 2,344 works. It gives determined field dispositions for 2,516 row reviews, retains specific evidence limits for 294, and identifies 8 coding-policy cases. Determined dispositions include conditional inapplicability after supported identity/type corrections; no dataset changes have been applied.

## Review and downloads

- [Correction proposals](correction_proposals.json): 563 field proposals across 516 rows, with evidence, frozen before-values, full-record hashes, and dependencies. Seven field proposals have a policy or application hold; four row bundles require coordinated application. One superseded removal is explicitly withdrawn.
- [Evidence updates](evidence_provenance_fixes.json): 14 literal primary-report quotation/provenance replacements, distinct from scientific field changes.
- [Confirmed missing pairs](confirmed_missing_pairs.csv): 442 genuinely absent study–original pairs, with no outcome inferred from missing-pair identity alone.
- [Unresolved missing candidates](unresolved_missing_pairs.csv): 124 candidates with remaining source, identity, or finding-correspondence limits.
- [All input rows](audit_rows.csv): one current audit-status record for every input row.
- [Review-required cases](review_required.json): 33 cases covering evidence limits, policy choices, and application dependencies.

The [Cloudflare review app](https://lukas-reports.lukas-wallrich.workers.dev/flora-audit-2026-10/) links the combined downloads and supports searching the evidence, reviewing concrete policy alternatives, and saving/exporting notes. It verifies the complete queue SHA-256. Notes remain in browser storage and never edit FLoRA. The published app contains review records and downloads. Acquired full reports, private source paths, and access details are excluded.

## Interpretation and application

Across the complete audit, 2,516 row reviews have determined field dispositions, 294 retain specific evidence limits, and 8 need coding-policy decisions. The evidence limits include 221 rows with partial or abstract evidence, 52 without usable text, and 21 where saved full text still cannot establish a necessary value. A completed audit does not establish a value the available evidence cannot support.

Every correction proposal has supporting audit evidence. The `decision_required` label marks a known policy or application hold; `evidence_checked_proposal` marks the other proposals. Both remain proposals. Apply a correction only after resolving its dependencies and checking its exact frozen before-record. Preserve both replication attempts when merging the OSC duplicate, retain source history for original replacements, and apply dependent outcomes only to their intended original. The combined files do not change the codebook or silently resolve policy choices.

The original exports, all model/source decisions, and contradictory evidence remain preserved. The combined view removes superseded proposals and reconciles completed decisions without overwriting those records. Detailed verification is in the [completion receipt](../evidence_followup/integration/final_sol_closure_20261031.json), [private-archive receipt](../evidence_followup/integration/final_sol_private_archive_20261031.json), and source decision files linked from the review app.

Rebuild the presentation from the repository root:

```bash
python3 audit/flora_blind_2026-10/scripts/build_review_handoff.py
python3 audit/flora_blind_2026-10/scripts/build_audit_report.py
python3 audit/flora_blind_2026-10/scripts/validate_review_handoff.py
```

Build and publish the public app with the installed `deploy-html` helper:

```bash
flora_site_dir=$(mktemp -d /tmp/flora-audit-site.XXXXXX)
python3 audit/flora_blind_2026-10/scripts/build_public_review.py --output "$flora_site_dir"
/home/lukas/.codex/skills/deploy-html/bin/deploy-doc.sh "$flora_site_dir" --slug flora-audit-2026-10 --no-comments
```

The app supplies its own case-review controls. The [deployment receipt](../publication/cloudflare_deployment.json) records the hosted asset hashes and browser checks.
