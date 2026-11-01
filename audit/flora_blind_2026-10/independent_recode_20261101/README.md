# Independent recoding of proposed corrections

This reassessment covers 562 proposed fields across 515 frozen rows and 469 works. It remains in progress.

214 of 677 initial source packets and seven additional source views have passed Opus schema, literal-quote and actual reading checks. Twenty-eight fresh Sol views pass the same checks. These counts describe text packets, including reports split from collections, rather than unique papers.

The current export contains **29 cases covering 31 proposed fields, plus two whole-record exclusions**. All remain unapproved and unapplied. They are checkpoint proposals for later batch approval. The legacy outcome batches remain suspended.

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

Wolfers's original-paper mismatch (row 387) is established, but its dependent outcome remains disputed between complete confident blind coders and has only a moderate-confidence source recommendation. The original and outcome stay held together. Breda/Napp's archived SSRN record links to the IZA working paper, whose publication footnote links to the PNAS article: these are versions of the same empirical work. Row 1032 retains its current identity pending an individual representation decision; the different DOI does not establish a wrong target.

The bone-strength case (document_0201, row 1208) is eligible as an unapproved outcome correction to uninformative. The authors explicitly say this attempt cannot support or refute the original microbiota-to-tissue-strength claim, with the verdict repeated in the abstract. The failed-manipulation default applies only without an author verdict. The direct treatment null and post hoc microbiota investigation remain the strongest contrary evidence; the source review's moderate-high confidence is preserved. Exact-source blind agreement supplements the claim-specific source assessment.

The original's frozen 2020 year, literal 2021 citation and conflicting Crossref print-2020/online-2021 fields remain recorded. Exact DOI, title, authoritative full authors, volume, issue, pages and a hashed literal reference establish the same work without changing the year or inferring reliable publication chronology. Document_0205 has interleaved columns and fragment quotes; document_0206 is unconfident; documents_0207 and 0208 have abstract-level evidence. These limits exclude automatic acceptance.

Document_0212 has gaps in the title, Study 2 Discussion and reference list despite its full-text metadata label. Document_0213 is abstract-only; document_0214 has an unresolved replication-chain target question; document_0216 has unconfident Wynn outcomes and uncertain claim attribution. Complete packet reading does not resolve these limits. Document_0215 has a verified complete earlier Sol reading and blind agreement on Schmidt 1998, while frozen row 439 names a 2017 metabolome paper. A separate source review is prepared, not dispatched, to check that original correction together with pooled original/new cohorts, the dependent type and outcome, and the extracted DOI/PMID boundary.

The finite 60-item source-recovery pass recovered one verified full report, whose simulation classification remains unresolved. Fifty-nine completeness gaps remain. Access failures are route limits, not evidence that reports do not exist. No broad third recovery pass is scheduled.

A separate gap in document_0147 is resolved by the complete published PDF registered as document_0688, including the repository cover and article pages 61–74. Both fresh blind roles pass complete reading and literal-evidence checks, agreeing on successful. The source review raises an unresolved objection about the original deliberate-control and measurement claims, so the case stays outside the automatic set. Each role has exhausted its single fresh read across aliases of this PDF. Earlier body-only labels confer no approval. This recovery is outside the finite 60-item queue.

Source reviews support Heinemann's failed outcome (row 912) and Hall's mixed outcome (row 649), with contrary passages and target dependencies retained. The crowd-within case (row 1923) remains a policy boundary; its corrigendum changes planned sample sizes only. The proposed reproduction conversion for row 835 stays held until the author manuscript is verified against the published report. Title and abstract are missing from document_0177, and document_0181 has interleaved column text; both remain outside the automatic set.

Knudsen's successful outcome (row 1865) applies to the 24-month informing task, separate from the paper's failed looking-time tasks. Its 2011 online and 2012 print dates identify the same work; the frozen year stays. Rydell's original-paper correction (row 1161) replaces the complete bibliography with the four-author empirical paper and retains failed. Both pass original-specific source review.

Both complete blind readings and the source review place the policy-goals paper (document_0173) outside replication scope. Positive aim, method and sample evidence supports the whole-record exclusion for row 169. Document_0188 cites an apparent review as its target and remains held until the retested empirical finding and target are established.

The old Young–Saxe Stage 1 view (document_0189) is superseded by a separately registered, complete 99-page report (document_0689). Saved OSF file metadata and the cached PDF hash establish its identity; a new extraction is byte-identical to the saved text. Both fresh blind roles read the full main report and supplementary material and classify a completed replication. Matching successful labels remain outside the automatic set because Opus is unconfident and preserves a mixed alternative. Old simulated results and prior nonblind conclusions confer no outcome approval.

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

Run the 137 validation and dependency controls, then rebuild the guarded export:

```sh
python3 -m unittest discover -s audit/flora_blind_2026-10/independent_recode_20261101 -p 'test_*.py' -v
python3 audit/flora_blind_2026-10/independent_recode_20261101/build_verified_proposals.py
```

When registering another source version, verify all frozen inputs:

```sh
python3 audit/flora_blind_2026-10/independent_recode_20261101/freeze_packet_receipts.py
```

All 684 registered packets currently pass that check. Raw source bodies, native reading receipts and unpublished coding outputs stay under the ignored private workspace. Rebuild the public review app after cohort integration, preserving shared decisions and requiring explicit batch approval before data application.
