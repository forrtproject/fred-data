# Outputs

**`flora.csv` is not produced by this repository.** It is a copy of the FLoRA release published by [flora-validation](https://github.com/forrtproject/flora-validation/blob/main/output/flora.csv), refreshed daily by [`.github/workflows/sync-flora.yml`](../.github/workflows/sync-flora.yml). The FLoRA pipeline in `pipelines/flora/` is superseded and is not run. For FLoRA's preparation, column definitions and release notes, see flora-validation.

Derived from that copy here:

- `flora_filtered.csv`, `flora_filter_log.csv` — `flora.csv` filtered for the DynamoDB-backed API by `R/filter_flora.R`
- `flora_history.png` — dataset size over time, shown in the main README

`flora_export_log.csv`, `dup_outcome_conflicts.csv` and `preprint_dedup_candidates.csv` are left over from the superseded pipeline and are no longer updated.

`FReD.xlsx` (effect-level FReD) is still produced here by `pipelines/fred/`.
