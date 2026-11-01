# Independent recoding of proposed corrections

This reassessment covers 562 proposed fields across 515 frozen rows and 469 works. It remains in progress.

183 of 677 initial source packets and six additional source views have passed Opus schema, literal-quote and actual reading checks. Twenty-six fresh Sol views pass the same checks. These counts describe text packets, including reports split from collections, rather than unique papers.

The current export contains **26 cases covering 28 proposed fields, plus one whole-record exclusion**. All remain unapproved and unapplied. They are checkpoint proposals for later batch approval. The legacy outcome batches remain suspended.

Agreement between two models is a candidate for correction, not a correctness certificate. A proposal enters `automatically_verified_proposals.json` only after:

- Primary report identity, version, completeness and empirical study status are established.
- Both genuine blind readings cover the complete registered source and pass schema, metadata, hash and literal-evidence checks.
- The same original claim and current test are positively aligned. Attempt language, a shared DOI or an omitted target cannot establish an outcome.
- A separate adversarial source review addresses contrary passages, verdict scope and target/report dependencies.
- Bibliographic metadata, duplicate constraints, supporting quotes and dependent fields agree.
- The export retains the complete frozen record, its hash and every atomic operation required for the remedy.

A reproduction conversion carries its type and both result axes together. An original-identity correction replaces the dependent bibliography and quotes. A registered alias of the same DOI can be canonicalized only with its exact authoritative alias record. Whole-record exclusion requires positive scope evidence, archives the complete pair and removes the row after approval; zero targets alone cannot authorize it.

`parent_acceptance_decisions.json` records the parent's scientific eligibility judgments. The historical counter named `automatic_corrections_accepted` counts eligible proposed fields, not user approvals. `withdrawn_proposals.json` preserves three withdrawn suspicions; disagreements and tested-version provenance remain visible.

The current comparison queue contains unresolved source, target and policy questions. Genuine codebook boundaries remain for the later individual-decision stage. Unconfident results and incomplete sources stay outside the automatic set. Prospective registrations require a joint record remedy; an obsolete plan cannot override a separately verified completed report.

The finite 60-item source-recovery pass recovered one verified full report, whose simulation classification remains unresolved. Fifty-nine completeness gaps remain. Access failures are route limits, not evidence that reports do not exist. No broad third recovery pass is scheduled.

A separate gap in document_0147 is resolved by the complete published PDF registered as document_0688, including the repository cover and article pages 61–74. Both fresh blind roles pass complete reading and literal-evidence checks, agreeing on successful. The source review raises an unresolved objection about the original deliberate-control and measurement claims, so the case stays outside the automatic set. Each role has exhausted its single fresh read across aliases of this PDF. Earlier body-only labels confer no approval. This recovery is outside the finite 60-item queue.

Source reviews support Heinemann's failed outcome (row 912) and Hall's mixed outcome (row 649), with contrary passages and target dependencies retained. The crowd-within case (row 1923) remains a policy boundary; its corrigendum changes planned sample sizes only. The proposed reproduction conversion for row 835 stays held until the author manuscript is verified against the published report. Title and abstract are missing from document_0177, and document_0181 has interleaved column text; both remain outside the automatic set.

Both complete blind readings classify the policy-goals paper (document_0173) as outside replication scope. A separate review is checking positive scope evidence and the whole-record remedy for row 169. Document_0188 cites an apparent review as its target and remains held until the retested empirical finding and target are established.

The parent owns integration, Git and dispatch. Blind Opus children receive only opaque packets, the codebook, schema and primary-source metadata. They receive no dataset values, suspected fixes, earlier codings or selection rationale. Earlier Sol coding is usable only when its exact source version and complete actual reading are verified; otherwise a fresh blind Sol pass is required. Preparers and adjudicators never become blind coders.

At most three model children run concurrently. General attempts are capped at two per role and source, with lower source-specific limits in `source_upgrades.json`. Alternate extractions of one PDF share the limit. Included native usage is used throughout; incremental paid API spend is zero.

Native completion notifications drive continuation. Reconcile exact task IDs in `state.json`; use a new `delegate_task` for each round. Do not restart historical controllers, polling loops, watchers or schedules.

The working files are:

- `progress.json`: current counts, active tasks and next untouched group.
- `comparison_review_queue.json`: scientific comparison and review status.
- `current_validation_index.json` and `prior_sol_receipt_checks.json`: verified source-reading and literal-evidence receipts.
- `source_inventory.json`, `source_upgrades.json` and `packet_input_receipts.json`: immutable initial inputs and separately registered source versions.
- `automatically_verified_proposals.json`: guarded, unapproved operations.
- `../run_log.md`: the chronological audit trail.

`prepare_dispatch.py` checks absolute packet paths, frozen inputs, output ownership, capacity and attempts before returning native arguments. `collect_completed_coding.js`, run through `AsyncFunction(tools, text)`, collects explicitly completed tasks and verifies actual tool returns. Neither tool accepts a scientific correction.

Quotations retain exact Unicode, whitespace and UTF-8 offsets. Boundary whitespace lost in transport is recorded; substantive changes fail validation. Report-boundary descriptions are metadata and never count as quote proofs. Missing evidence remains unproved. Source blocks prevent quotes from crossing separate reports.

The export also checks authoritative DOI/title/author/year correspondence and complete frozen-row preconditions. Verified printed author errors and CSV newline representation differences remain explicit and narrowly bound to their source receipts. Raw codings and reviews are preserved.

Run the 125 validation and dependency controls, then rebuild the guarded export:

```sh
python3 -m unittest discover -s audit/flora_blind_2026-10/independent_recode_20261101 -p 'test_*.py' -v
python3 audit/flora_blind_2026-10/independent_recode_20261101/build_verified_proposals.py
```

When registering another source version, verify all frozen inputs:

```sh
python3 audit/flora_blind_2026-10/independent_recode_20261101/freeze_packet_receipts.py
```

All 683 registered packets currently pass that check. Raw source bodies, native reading receipts and unpublished coding outputs stay under the ignored private workspace. Rebuild the public review app after cohort integration, preserving shared decisions and requiring explicit batch approval before data application.
