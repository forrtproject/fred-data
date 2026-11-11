# Analysis spec — adjudicating the FLoRA / Observatory disagreements

A specification for work nobody has done yet. `disagreements.csv` holds 159 rows where
FLoRA's pipeline and the Metascience Observatory give different answers about the same
replication. **Neither side is ground truth**, and no row here has been checked by a
human. The point of the analysis is to find out which is right, how often, and whether
the pattern says anything about either database that should change.

Read it alongside `screen_discards.csv`, which is the other kind of disagreement: works
the Observatory calls replications that FLoRA's screen rejects outright.

## The four kinds, and why they are different questions

`disagreements.csv` carries a `kind` column. They are not variations of one problem:

| `kind` | Rows | The question |
| --- | ---: | --- |
| `we found no original` | 54 | A recall question about FLoRA's linker. The Observatory names an original; our ladder returned none. |
| `different original` | 50 | A precision question for *both*. Two pipelines, two different papers. At most one is right — possibly neither, and possibly both if the paper targets several. |
| `same original, different outcome` | 47 | The cleanest comparison in the set: same claim, different verdict. Nothing about linking confounds it. |
| `MO names no original DOI` | 8 | Mostly a data-completeness question about the Observatory. |

**Analyse them separately.** Pooling them produces a single "agreement rate" that means
nothing, because the four have different causes and different remedies.

## Research questions

**RQ1 — Who is right, and how often?** For each kind, the share of rows where a human
adjudicator judges FLoRA correct, the Observatory correct, both defensible, or neither.

**RQ2 — Is either side's error predictable?** Do FLoRA's errors concentrate in rows it
already flags (`link_confidence: low`, particular `link_method` values)? Do the
Observatory's concentrate by `source`, `confidence`, `ai_version`, or in rows it
extracted with an LLM versus imported from FReD/Curate Science?

**RQ3 — Is `inconclusive` the same category on both sides?** 28 of the 185 comparable
rows are ours committing to success or failure where the Observatory records
`inconclusive`; 6 are the reverse. This is the largest single disagreement class and may
be a vocabulary difference rather than a factual one.

**RQ4 — Does the multi-original case explain `different original`?** A paper that
re-tests several findings has several valid originals. FLoRA writes one row per original
(`n_originals` records how many it found); the Observatory writes one row per pair. Some
share of the 50 may be two right answers about different targets.

## The data

`disagreements.csv`, one row per FLoRA extraction row:

| Column | Meaning |
| --- | --- |
| `doi_r`, `title_r` | The replication. |
| `kind` | The four classes above. |
| `our_doi_o`, `our_title_o`, `our_outcome` | FLoRA's answer. |
| `mo_doi_o`, `mo_outcome` | The Observatory's answer. |
| `our_link_method`, `our_link_confidence` | Which ladder rung resolved it, and how confident. |
| `our_outcome_quote`, `out_quote_source` | **The sentence the outcome was coded from**, and whether it came from the abstract or the full text. This is what makes adjudication cheap: the coder can check the quote against the paper without re-reading everything. |
| `our_link_evidence` | Why that original was accepted. |
| `mo_replication_type`, `mo_discipline`, `mo_source`, `mo_confidence`, `mo_ai_version` | The Observatory's own metadata, including whether the row was LLM-extracted. |

FLoRA's outcome vocabulary is mapped onto the Observatory's four values for comparison:
`successful`→success, `failed`→failure, `mixed` and
`statistically successful but flawed`→inconclusive. **The mapping is a judgement and
should be revisited** — RQ3 is largely about whether it is right.

## Coding protocol

1. **Sample.** All 47 `same original, different outcome` rows (the cleanest class, and
   small enough to do whole). For `different original` and `we found no original`, a
   random 25 of each is enough for a first estimate; draw with a fixed seed and record
   it. Do not start with the rows that look interesting.
2. **Two independent coders**, blind to which database gave which answer. Present the
   replication, the candidate original(s) and the quote; ask for the correct original
   and the correct outcome in FLoRA's vocabulary.
3. **Blinding matters here.** A coder who knows FLoRA produced an answer is being asked
   to audit their own project. Shuffle the two answers per row and label them A/B.
4. **Record disagreement between coders before resolving it** — Cohen's κ on both the
   original and the outcome. If κ on the outcome is low, RQ1 cannot be answered and the
   finding is that the outcome vocabulary is underspecified, which is itself worth
   knowing.
5. **Resolve by discussion**, and keep the pre-resolution codes.

## Pre-specified analyses

* Per `kind`: proportion FLoRA-correct / Observatory-correct / both / neither, with
  Wilson intervals. n is small; report intervals, not point estimates alone.
* RQ2: FLoRA error rate split by `our_link_confidence` (`low` vs `high`) and by
  `our_link_method`. The pre-registered expectation is that **errors concentrate in
  `low`** — if they do not, `link_confidence` is not carrying information and that is a
  bug worth filing against the extractor.
* RQ2, other side: Observatory error rate split by `mo_source` (LLM-extracted vs FReD /
  Curate Science import) and by `mo_confidence`.
* RQ3: for the 28 ours-decisive / theirs-`inconclusive` rows, the share where the
  adjudicator judges the evidence genuinely indecisive. A high share means FLoRA is
  overconfident; a low share means the two `inconclusive` categories differ and the
  mapping above is wrong.
* RQ4: for `different original`, the share where both named originals are defensible
  targets of the same paper. Cross-check `n_originals` from the extraction.

## What the result should change

State these before coding, so the analysis cannot be read backwards into whatever it
found:

* **FLoRA error rate above ~10% in `low`-confidence links** → those rows should not
  reach validators unflagged; the extractor should gate them.
* **Errors spread evenly across confidence levels** → `link_confidence` is not
  informative and needs re-deriving.
* **RQ3 resolves as a vocabulary difference** → the crosswalk in this directory is wrong
  and any future merge of the two databases must not use it.
* **The Observatory is right materially more often on `different original`** → FLoRA's
  resolution ladder has a systematic bias worth locating (start with `link_method`).
* **Neither side is reliably right** → the honest output is a `needs_human` flag on the
  class, not a merge.

## Scope, separately

`screen_discards.csv` is not an error analysis — it is 265 works FLoRA's screen rejects
because the paper does not state an aim to re-test a specific finding, while the
Observatory counts them because the study functionally re-tests one. That is a
definitional difference between the projects and **cannot be settled by adjudicating
individual rows**.

The decision it poses is: does FLoRA want the functional-replication class at all? If
the project ever says yes, this file is the ready-made evaluation set — 265 works with
the screen's reasoning already attached, grouped by reason, with 53 of them flagged as
judged from a title alone because no abstract could be found (the weakest of the
discards and the first place to look for genuine screen errors).

## Reproducing the inputs

Scripts are in `forrtproject/flora-extractor`, `analysis/mo_observatory/`:
`screen_offline.py` (screen), `extract_offline.py` (link + outcome),
`build_flora_entries.py` (this split), `build_scope_html.py` (the report). They read the
Observatory CSV and the extractor's own caches; every LLM call is content-keyed, so a
re-run with the same prompts and models is free.
