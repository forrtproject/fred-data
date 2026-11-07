# Source-grouped completion pass, 31 October 2026

## Current state (7 November 2026)

The pass is closed at the checkpoint in `completion_checkpoint.json`: all 951 assigned source groups and 420 independent-review groups processed, no queued or live work. The checked export (`export_fingerprint.json`, 5 November) has 694 confirmed field errors in 503 rows, 7,720 verified fields, 7,400 unverified and 28 not-comparable fields. All 6,411 baseline decisions are preserved. Unresolved fields remain unverified; no acquisition or restart is authorised.

Audit findings are not the same as corrections applied to FReD. `release_draft/policy_ledger.py` classifies every finding under the application policies agreed on 7 November 2026 (sign relative to the original effect; `reported_success` per study from author statements or project rules only; coherent row sides; individual review of model, sample-role, metric-equivalence and adaptation changes). Human decisions go in `release_draft/manual_decisions.csv`. `release_draft/build_release.py --out release_draft/application_package` builds the draft patch from applied decisions only; `release_draft/review_page.py` builds the private review page with source screenshots outside the repository.

The files directly in `release_draft/` (other than these scripts and the ledger) are the published 1 November snapshot: 635 corrections, 470 rows, 1,207 cell updates. They are kept unchanged.

`CONTINUE.md` is the historical operating log of the pass; its counts and instructions before the final checkpoint are superseded.

## Original brief

Separately authorised by Lukas’s “go” after the source-grouped proposal. Baseline: 493 confirmed errors in 381 rows; 6,411 verified field instances; 112 fully verified rows. Historical deadlines, completion files and source-acquisition passes remain unchanged.

Repair integration/evidence-processing defects first; then run a purposefully mixed 24-source pilot, checking all unfinished fields for the assigned rows together. Preserve previously verified fields, maintain blind extraction, independently adjudicate substantive disagreements, and record specific reasons for unresolved fields. Retain literal evidence validation. No new source acquisition, paid API calls, shipped dataset/pipeline/main checkout/FLoRA edits. Parent owns integration, Git, report and correction exports.
