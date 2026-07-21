# Focal-effect flags (`focal_effect_flags.csv`)

Per-effect flag marking, for each FReD effect, whether it is the **focal effect** of its
replication pair — the single effect the replication study actually targeted as its primary
replication object. One row per FReD `effect_id` (2164 rows, keyed to `output/FReD.xlsx`).

## Columns

| column | meaning |
|---|---|
| `effect_id` | FReD effect id (join key to `output/FReD.xlsx`) |
| `fred_id` | FReD pair id (original study ↔ replication) |
| `doi_o` | original-study DOI (from FReD; not a unique key — see caveats) |
| `is_focal` | `TRUE` **only** for a pair's single focal effect (`focal_role == focal`); `FALSE` for every other coded effect (non-focal, constituent, target-absent, or a base fragment's effects); empty (NA) for `not_applicable`/`uncoded` effects |
| `focal_role` | the effect's role in its pair: `focal` \| `constituent` \| `none` \| empty (NA). See below |
| `focal_source` | how the focal effect / verdict was identified for that pair (see tiered rule); empty for `not_applicable`/`uncoded` |
| `confidence` | high/medium/low confidence of the determination; empty for `not_applicable`/`uncoded` |
| `needs_review` | `FALSE` for every coded pair (no pair is now open for review); empty for uncoded effects |
| `coverage` | `resolved` \| `constituent_set` \| `target_absent` \| `focal_in_sibling` \| `not_applicable` \| `uncoded` (see below) |
| `proposed_row` | `TRUE` for effects of a `target_absent` pair whose focal effect is a **not-yet-in-FReD row that should be added** (see below); empty otherwise |

`focal_role` values:
- **focal** — this effect is the single focal effect of a focal-resolved pair (`is_focal = TRUE`).
- **constituent** — this effect is one member of an **aggregate replication's constituent set**: the replication targeted a whole set of co-equal effects, and this effect is one of them (no single focal). See "Constituent sets" below.
- **none** — a coded effect that is neither focal nor a constituent: a non-focal effect of a focal-resolved pair, a non-constituent candidate of a constituent-set pair, any candidate of a `target_absent` pair, or any effect of a `focal_in_sibling` base fragment.
- **empty (NA)** — effects of `not_applicable` pairs (Soto) and all `uncoded` effects.

`coverage` classes (one per pair, broadcast to its effects):
- **resolved** — the pair has a single identified focal effect (exactly one `focal_role = focal`, `is_focal = TRUE`).
- **constituent_set** — an aggregate replication with no single focal effect; the verdict is about a set of co-equal constituent effects, flagged `focal_role = constituent`.
- **target_absent** — the effect the replication targeted is **not present among FReD's candidate rows** for the pair; the coded replication verdict exists but attaches to no candidate, so no effect is focal or constituent. 3 pairs; two carry `proposed_row = TRUE` (their focal effect is a specific row that should be added to FReD, staged in `proposed_fred_rows_final.csv`).
- **focal_in_sibling** — the pair is a **fragment**: FReD split one original↔replication pair across several `fred_id`s, and the effect the replication actually targeted lives under a *sibling* `fred_id` (same `doi_o` + `doi_r`) that is itself `resolved`. This base fragment holds only non-targeted effects, so none of its own effects is focal. See "fred_id fragmentation" below.
- **not_applicable** — the "focal effect" concept does not apply: the replication is an **association-matrix bundle** (`Soto`, the LOOPR project — a matrix of personality–outcome associations, not a focal-claim replication).
- **uncoded** — the effect's `fred_id` is outside the 987-pair coded universe (never assessed); all flag fields empty.

Invariant: **exactly one `is_focal=TRUE` per focal-resolved pair** (957 resolved pairs → 957 TRUE rows). Each pair is exactly one of: focal-resolved, a constituent set, target-absent, focal-in-sibling, or not-applicable — and **no pair is `needs_review` any more**.

## Derivation

The coding unit is the **pair** (`fred_id`), not the individual effect, so the focal effect is
determined once per pair and then broadcast to that pair's effects here. A pair's focal effect was
resolved by a tiered rule, cheapest evidence first:

1. **single_effect** — the pair has exactly one effect; it is trivially focal.
2. **abstract match** — LLM semantic match of the coder's abstract-level replication finding to
   one candidate effect's original claim.
3. **outcome_quote match** — same, using the finding-level `outcome_quote` when the abstract was
   too coarse.
4. **replication-report reading** — for pairs the abstract/quote could not disambiguate
   (project-level/bundle abstracts, whole-model aggregate verdicts, or an abstract finding that
   matched no candidate), a human-directed agent read the actual replication report to identify
   the targeted effect, citing the report section/table/statistic as evidence.

The LLM tiers (2–3) used **gemini-flash-lite-latest** in a two-pass semantic-matching setup,
validated against the pooled tier logic and spot-checked. The report tier (4) is human-directed
agent reading of the replication reports with cited evidence. When no single focal claim could be
identified, the focal effect was left empty (**never guessed**) and the pair was classified into
one of the non-focal coverage classes: `constituent_set` (aggregate/whole-model, co-equal
multi-outcome), `target_absent` (candidate set missing the actually-targeted effect), or
`unresolved` (still undetermined).

## Source of the coding

Focal determinations derive from FORRT's abstract-level replication-success coding (the
*"Validating FReD replication success"* sheet), joined to FReD.

The sheet is **double-coded**: each replication was coded independently by more than one coder,
and a `validation` column records which coding was adjudicated authoritative. Only rows marked
`validation == "validated - chosen"` are used here; discarded, on-hold, and unvalidated rows are
excluded.

## Identity-keyed verdict attribution

Coded verdicts (outcomes and their supporting quotes) are attached to each pair by matching
**replication identity**, not original DOI alone. A pair's replication identity is the coalesce of
its DOI and URL on *both* the original and replication side, plus **preprint/deposit-duplicate
equivalences** from `cache/confirmed_preprint_duplicates.csv` (so a preprint, its published
version, and a separate data deposit of the same replication are treated as one replication). A
provenance column records how each pair's verdict was matched — `outcome_match` in the analysis
file, mirrored by the tiers below:

- **exact_key** — matched on the exact (original identity, replication identity) key;
- **url_key** — matched once URLs are coalesced with DOIs;
- **dedup_equiv** — matched via a confirmed preprint/deposit-duplicate equivalence;
- **fred_id_bind** — matched by binding to the pair's own FReD `fred_id` when the sheet's DOI/URL
  were incomplete;
- **doi_o_fallback** — no verdict for this exact replication; the outcome is **pooled from other
  replications of the same original** (3 single-trace pairs, flagged in their rationale);
- **none** — no validated verdict is keyed to this replication at all (2 pairs; outcome blank).

This identity keying supersedes the earlier original-DOI-only keying, which had mis-attributed
verdicts across different replications sharing an original DOI and missed verdicts recorded under a
duplicate deposit.

## DOI join / normalisation

DOIs and URLs were normalised before joining (lowercased, trimmed, `https?://(dx.)?doi.org/` prefix
stripped, `na`/`null`/`n/a`/empty → missing). The pair-level assignment joins to FReD on `fred_id`;
the `doi_o` column is carried for reference.

## Constituent sets (aggregate replications)

Many replications are **aggregate**: they target a whole set of co-equal effects (e.g. a full set
of problems, a path model, a battery of trait–outcome correlations, a multi-ROI confirmatory
replication) with no single primary effect. These pairs get `coverage = constituent_set`,
`is_focal = FALSE` for all their effects, and `focal_role = constituent` on the member effects
(non-member candidates stay `none`). The pair's coded verdict describes the set as a whole. 23 pairs
are constituent sets; 3 are `target_absent` (the targeted effect is not among FReD's candidates),
3 are `focal_in_sibling` fragments, and one (`Soto`) is `not_applicable`. This replaces the previous
`needs_review` bucket — the coding is now positive rather than merely "no single focal", and **no
pair remains open for review**.

## fred_id fragmentation (focal_in_sibling)

FReD sometimes splits **one** original↔replication study pair across several `fred_id`s that share
the *same* `doi_o` **and** `doi_r` (a base id plus `_1`/`_2` siblings). When that happens, the
effect the replication actually targeted can live under a **sibling** `fred_id` while the base
`fred_id` holds only the pair's other, non-targeted effects. Three base fragments are affected —
`OpenMKT7` (target lives in `OpenMKT7_1`, effect 927), `Boyce_etal202319` (`Boyce_etal202319_1`,
effect 520), `Boyce_etal202325` (`Boyce_etal202325_1`, effect 533). They are coded
`coverage = focal_in_sibling`; their sibling's focal effect keeps `is_focal = TRUE` (unchanged),
and the base fragment's own effects stay `focal_role = none`. In `focal_effects.csv` the base rows
carry `sibling_fred_id` / `sibling_focal_effect_id`.

**Consequence for downstream de-duplication:** a replication study is identified by
`doi_o + doi_r`, **not** by `fred_id`. Any pooling or z-curve de-duplication over replications must
key on `doi_o + doi_r` (or the identity keys used for verdict attribution), or these fragment
siblings will be double-counted.

## SCORE single-trace pairs (no local outcome)

Three single-effect pairs (`88xa_single-trace`, `LmBx_single-trace`, `xYbO_single-trace`) originate
from the SCORE programme and **carry no outcome in this abstract-coding sheet**. Their focal effect
is structurally determined (single effect), so they stay `resolved` with `is_focal = TRUE`, but
their `abstract_outcome`/`outcome_quote` are blank and `outcome_match = score_no_local_verdict` (an
earlier `doi_o_fallback` value, pooled from *other* teams' replications of the same original, was
removed as not this replication's verdict).

## Proposed FReD rows (proposed_row)

Two `target_absent` pairs have `proposed_row = TRUE`: their focal effect is a specific
original↔replication result that is **genuinely not yet a row in FReD** and should be added. Both
have verified original coefficients staged in `proposed_fred_rows_final.csv`.
- `curatescience15` — the *ego-depletion* DV (prior self-regulation exertion → worse subsequent
  self-control), Muraven 1998 Study 2; only effortfulness manipulation checks are currently coded.
- `resciencex_01` — three *teacher-credential* effect rows (Croninger 2007 Table 3, standardized
  HLM), including a **sign correction** (school-avg advanced-degrees→math γ=−0.068* is adverse);
  the 8 existing candidates are student/school control covariates, not the credential effects.
See `focal_validation_report.md` §8 for the full proposed original + replication statistics.

## additional_studies94 — FReD claim_text defect (not a missing effect)

`additional_studies94` was briefly `target_absent` but is now **`resolved`, focal = effect 323**.
Effects 323/324 already code the paper's Study-1 *God salience → AI-reliance* DV (323 the direct
replication, 324 the conceptual one), but their `claim_text` fields were **mis-pasted with the
manipulation-check wording** ("thinking about God…") while their statistics are the reliance DV.
This is a claim_text defect in FReD, not a missing row. **Fixed in the FReD source on 2026-07-23**
(the "FReD Validation — USE THIS" workbook, "COS coding" tab, rows 2412 and 2415): `claim_text_orig`
and `claim_text_orig_page` were corrected to the focal reliance-DV claim ("a one-way ANOVA on an
index score…F(1,319)=12.91…f=0.20"), recovered from the parallel discarded coding (rowid 664/665),
with a `notes_validation` entry recording the correction. Effect 323 → `is_focal = TRUE`,
`focal_role = focal`; effect 324 → `focal_role = none`.

## Caveats

- **Coded DOIs with no FReD match (10):** DOIs coded in the sheet but absent from FReD after
  normalisation — never enter the pair universe.
- **Orphan effects (5):** FReD effects (`effect_id` 1834, 1847, 1848, 1939, 1968) whose DOI is
  coded but whose `fred_id` is missing; cannot be assigned to a pair (fall in `uncoded`).
- **fred_ids spanning multiple DOIs:** `FORRT_187_1` (2 DOIs) and `Soto` (25 DOIs) — `doi_o` is
  not a unique key for these; the join is on `fred_id`.
- **Aggregate / whole-model verdicts and bundle replications:** many report-tier pairs replicate
  a whole model or a set of co-equal outcomes; where no single primary effect exists they are
  `constituent_set` (member effects flagged `focal_role = constituent`).
- **Candidate sets missing the targeted effect:** some replications target an effect not present
  among the pair's candidate rows → `target_absent`.
- **Duplicate candidate rows:** where duplicate effect rows encode one and the same finding and
  that finding is focal, the resolution picks the **lowest / fullest `effect_id`** by rule.
- **Verdict/finding mismatches (av_199-style):** in a few report-tier pairs the coded replication
  verdict refers to a different finding than the targeted focal effect; the focal effect is still
  flagged, and under identity keying the replication-level verdict is attached (its rationale notes
  the finding-level caveat).

See `abstract_coding/focal_validation_report.md` (in the analysis repo) for the full coverage
tables, spot-check, the constituent/target-absent lists, and LLM spend.
