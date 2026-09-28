# Metascience Observatory — candidates FLoRA's pipeline cannot reach

Everything here comes from comparing the [Metascience
Observatory](https://github.com/delton137/metascience-observatory) replications database
(`replications_database_2026_09_04_184008.csv`, 8,892 rows / 4,855 distinct replication
DOIs) against FLoRA's extraction pipeline
([`forrtproject/flora-extractor`](https://github.com/forrtproject/flora-extractor)).

**Why these works are here and not in the pipeline.** FLoRA's Stage 1 builds a survivor
pool by scanning the OpenAlex bulk snapshot and keeping works whose title or abstract
carries a replication stem. 710 of the Observatory's DOIs are not in that pool, so no
Stage 2 filter rule and no Stage 3 extraction can ever reach them — a rule routes rows
that are already in the pool. 573 of the 710 are gate misses that are not already ours.

They were therefore screened and extracted **outside** the pipeline, using the
pipeline's own code and models so the answers are the ones it would give:

* the screen is `classify_replication()` — the shipped prompt, the shipped voter pair
  (`deepseek-v4-flash` + `gpt-5.4-mini`) and `screen_gate()`, unchanged;
* the extraction is `_process_row()` — the real Stage 3 resolution ladder, per-target
  adapter, guards, DOI verification and outcome coding.

Nothing was written to the pool, the routing store or the verdict store. Full method,
counts and caveats: `scope_differences.html` (open it in a browser — self-contained).

## What is in this directory

| File | Rows | What it is |
| --- | ---: | --- |
| `candidates_agreed.csv` | 117 | **Ready for FLoRA.** Both databases independently name the same original DOI *and* the same outcome. In the FLoRA entry sheet's 20 columns and vocabulary. |
| `disagreements.csv` | 159 | The two pipelines differ. The analysis set — see `ANALYSIS_SPEC.md`. |
| `screen_discards.csv` | 265 | Works the Observatory calls replications and FLoRA's screen rejects, each with the reason. The scope difference, itemised. |
| `scope_differences.html` | — | The readable report: every discard grouped by reason, plus the recall gap. |

108 distinct works are covered by `candidates_agreed.csv` (a work with two originals
contributes two rows, which is FLoRA's own convention).

## `candidates_agreed.csv` — what a validator should know

* **Not validated.** `validation_status` is blank deliberately, so these enter the
  normal queue. `Coder` is `AI`, the value the sheet already uses for machine coding.
* **Agreement means the same claim.** The original DOI is matched first, then the
  outcome. Matching outcomes alone would count a row where the pipeline read a
  *different* original and happened to land on the same verdict, which corroborates
  nothing.
* **31 of the 117 carry `link_confidence: low`** in FLoRA's own linker. They are
  included because two pipelines independently naming the same original is stronger
  evidence than one linker's confidence in isolation — but the confidence is written
  into `prep_notes` on every row, so it can be filtered on.
* `outcome` uses the entry sheet's vocabulary, including
  `statistically_successful_but_fundamentally_flawed` (the extractor's schema spells
  this differently).
* `ref_r` is built from OpenAlex metadata via the extractor's `format_apa_reference`.
  `ref_o` comes from the extraction itself. Columns that could not be sourced are left
  **empty rather than guessed** — a blank is a question for a validator; a guess is a
  wrong answer.

## The headline finding, in one table

Of the 573 works screened, the two-voter screen said proceed on 308 and discard on 265.

| | |
| --- | ---: |
| Screened (not already in FLoRA) | 573 |
| → proceed | 308 |
| → discard (scope difference) | 265 |
| Extracted (proceeds with a record type) | 229 works / 276 rows |
| Original resolved | 225 rows |
| Same original as the Observatory | 164 of 215 rows where both name one (**76%**) |
| Same outcome | 146 of 185 (**79%**) |
| Flat contradictions (success vs failure) | **4 (2%)** |

**The scope difference is definitional, not an error on either side.** FLoRA asks what a
paper *says it is doing* — a replication states an aim to check a specific earlier
finding. The Observatory asks what a study *does* — any design that re-tests a reported
effect counts, however the authors frame it. The gap follows: 88% of `conceptual`
replications are discarded against 65% of `direct` ones, and genetic-association studies
(where each new cohort is a replication sample written up as original work) are the
single largest class.

## Not a scope difference: 147 works FLoRA wants and cannot see

Separately from the above, 147 of the 573 have abstracts that say plainly they are
replications — *"we replicate and extend previous work"* — which FLoRA's gate never read
because **OpenAlex holds no abstract for those records**. Europe PMC supplied 303 of the
354 missing abstracts on request.

This is a recall bug in Stage 1, not a question about scope, and it is upstream of the
existing abstract backfill: that backfill runs over the *routing table* (rows already in
the pool with `pending_reason = 'no_text'`), so a work that never entered the pool is
never in its worklist. Tracked in the extractor repo; listed here because it explains
why these works were invisible.

## Provenance

* Source snapshot: `delton137/metascience-observatory`, `replications_database_2026_09_04_184008.csv`, 2026-09-04.
* Screen and extraction: 2026-09-21, `forrtproject/flora-extractor` branch
  `feat/observatory-priority-rule`, scripts under `analysis/mo_observatory/`.
* Every CSV here is written UTF-8 with a BOM, per this repo's `.claude/claude.md`.
