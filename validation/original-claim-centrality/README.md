# Original-article claim centrality

**LLM-coded and unvalidated; draft for review.** This documents all 2,050 current published FReD effect rows, coded using the original article’s argument. Several claims per original may be central. No production flag, workbook or live-sheet change is included.

| Classification | Rows |
|---|---:|
| central | 1,488 |
| not_central | 462 |
| unclear centrality | 0 |
| centrality empty | 100 |

Empty rows distinguish 92 ambiguous claims, five claims not located, two unavailable original full texts, and one original-only source restriction. [classifications.csv](classifications.csv) contains one permanent effect_uid per row with the identified claim, rationale, original locators, numerical matching limitations and provenance. These are the unchanged final judgments, not a rerun.

## Source and coding

The source was refreshed on 12 November 2026 at 11:13:58 UTC, using production-default eligibility/cleaning and the reviewed correction overlays from main commit `7a8fad9658e4d339492d92b2c127a0efffbbd638`. [provenance.json](provenance.json) records the source URL/hash, code/overlay hashes and frozen input-frame hash. The frame has 704 original-reference keys, including six literal repository/reference identifiers; they are not all verified DOIs. No retrieval-success or article-effect-count filter was used.

Centrality was coded by **GPT-6.1 Sol medium via Codex subscription sessions**, using [the exact short prompt](centrality-prompt.txt) and [reading instructions](reading-instructions.txt). A numerical mismatch blocks coding only if it makes the substantive claim ambiguous. An identified claim can be coded despite unmatched numbers; incompatible targets stay empty.

Claude Opus 5.5 independently identified 422 statistical reconstruction candidates, with medium effort requested but not independently observable by workers. [identity-checks.csv](identity-checks.csv) retains the final comparisons: 324 compatible substantive identifications and 98 unresolved/access/location/version cases. This is identity checking, not database-wide centrality agreement. Fresh Sol rereads and source matching limitations are retained. No separately billed inference was invoked; billing-route visibility limits are in [summary.json](summary.json).

[source records and hashes](sources.csv) identify the actual PDFs/texts read. Papers were read through targeted title/abstract, framing, conclusions and relevant methods/results within full originals, not every page word for word. Supplements were not universally available. Nineteen earlier outcome-exposed judgments were excluded and replaced by fresh blind readings. Eight earlier non-empty judgments are withheld after incompatible target comparisons. Detailed original logs are privately archived, not duplicated here.

The historical pilot contains 50 rows from 47 originals, drawn using seed 20261111; [pilot-sample.csv](pilot-sample.csv) preserves its permanent UIDs in draw order. Its 49 distinct non-empty claim strings are wording counts, not semantic claim counts. The historical source snapshots, prompt experiments and raw judgments are archived; none was used as a coding input to the full run.

## Claims: clarification, not shortening

**Quote length is not an objective. Clear existing claims stay unchanged.** [claim-review.csv](claim-review.csv) retains the 182 useful source excerpts but distinguishes their purpose:

- 21 candidates fill an absent claim.
- 110 candidates propose adding identification detail to a generic table/model pointer or other insufficient wording. Existing wording and relevant context are retained; the proposal is an addition, not a shorter replacement.
- 51 excerpts are supporting evidence only. No change to an already clear claim is proposed.

All candidates need human review. There is no automatically rewritten claim-text dataset. The quote itself, its locator/hash, current wording and review purpose are kept together; statistics, signs, tests and estimands are unchanged. Direct quotations and faithful labelled table excerpts remain available for review, with omissions marked. None of the historical shortening-only suggestions is presented as a required claim edit.

For example, fe02298 already identifies the logo-shape/attitude null and is evidence-only. fe03699 retains its full wage-spillover context rather than replacing it with a table cell. An empty claim such as fe05300 can be filled from its independently located source excerpt.

Generate the interactive spot-checker:

```bash
python3 validation/original-claim-centrality/build_quote_spotcheck.py
```

Open the generated `quote-spotcheck.html` locally or in T3. It starts with ten different originals with clarification candidates; search covers all 182 excerpts. Mark checks, add notes and export a CSV. Earlier browser notes can be carried over, but decisions reset because the proposal purpose changed. The data-filled HTML is ignored by Git; the small template/generator are tracked. PDFs remain private.

## Verification and audit archive

```bash
python3 validation/original-claim-centrality/verify.py
```

This checks frozen data/prompt hashes, exact UID coverage/counts, source-hash consistency, quote review roles and the absence of shortening proposals. It does not validate the LLM judgments. `rebuild_frame.R` can reconstruct the original-only frame from the private frozen source; it never rebuilds output/FReD.xlsx.

[archive.json](archive.json) identifies the hash-verified private archive of the entire previous run and branch history. Raw worker outputs, frozen input copies, reading logs, checkpoints, old prompt experiments and duplicate views are preserved there. The archived commit and file checksums allow detailed audit without publishing a working-directory dump in this PR. Full papers have their separate private hash-addressed archive. Public results retain provenance needed to locate those records.

The source sheet, per-study author-only reported_success, workbook and production codebook fields are untouched. Review meaning and claim clarifications before any production integration.
