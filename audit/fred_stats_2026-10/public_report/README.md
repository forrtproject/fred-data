# FReD statistics audit: correction release

The authorised source checking and review passes are complete. The frozen b48a7d6 workbook contains 2,164 effects in 432 replication works. There are 493 confirmed field errors in 381 rows, with 31 coding omissions included. Unverified fields, incompatible metrics, and availability/inclusion decisions are not fixes.

## Files

- `confirmed_corrections.csv`: 493 audited field decisions, with old/new values, metric/bound context, source references, locations, and reasons.
- `fred_fixes.csv`: 920 physical cell updates for those decisions. These comprise 491 changed value cells, 59 p-bound cells, 87 effect-source locators, 141 outcome quotations, and 142 outcome-quote source cells. Two confirmed p errors change only the inequality. One existing outcome quotation already matches after whitespace normalisation, so it is retained.
- `row_guard.csv`: source/study/description/metric/design guards for the 381 affected records. The key is `entry_id` + `effect_id` + `fred_id`; `fred_id` alone is not an effect key.
- `merge_fred_fixes.R`: checked merger and command-line entry point.
- `field_summary.csv`, `field_summary_by_project.csv`: error and coverage denominators.
- `availability_followups.csv`: four pending availability/inclusion requests, excluded from the patch.
- `screen_recheck.csv`: 185 original diagnostic flags rechecked after the confirmed patch; 19 pass, 165 remain flagged, and one cannot be recomputed. A flag is not proof of a coding error.
- `release_summary.json`, `SHA256SUMS.txt`: release counts and download hashes.

Associated quote updates retain the exact short primary-source evidence accepted in adjudication, including any OCR spelling. Source locators and quote sources include the DOI or primary project URL and page/table location. No PDF, full text, page image, private path, credential, or raw model log is included in the public bundle.

## Apply to the frozen workbook

Put the downloaded files and the audited workbook (named `FReD.xlsx`) in one folder. In R, install `readxl`, `writexl`, and `digest` once if needed. Then run:

```sh
Rscript merge_fred_fixes.R FReD.xlsx FReD_corrected.xlsx
```

The command requires the original workbook SHA256 `59545e3fc0c2979d97507097526319ec8c275aae3ac40c0d1a6d327492079e6b`. It verifies the fix and guard downloads, writes a NEW workbook and a cell-level change log, and refuses to overwrite an existing path. It does not edit the source workbook, repository data, or preparation pipeline. The new workbook exports data values; it does not preserve Excel styling.

From this audit worktree's project root, the equivalent command is:

```sh
Rscript audit/fred_stats_2026-10/public_report/merge_fred_fixes.R output/FReD.xlsx /tmp/FReD_corrected_2026-10.xlsx
```

Choose another new destination if that output already exists.

## Merge with an R object

From the folder containing the downloads:

```r
source("merge_fred_fixes.R")
fred <- readxl::read_xlsx("FReD.xlsx", trim_ws = FALSE)
result <- apply_fred_fixes(fred)
fred_corrected <- result$data
result$summary
head(result$changes)
```

The in-memory function permits reordered rows but requires 2,164 rows, unique composite keys, matching target guards, and expected old or already-patched values for every changed cell. Every target is checked before any changes are made. A second application leaves data unchanged. Changes elsewhere in a newer FReD release are not validated by these guards: do not bypass a conflict or force these fixes onto reassigned identifiers. Rebase conflicting records against the evidence first.

The audited statistical fields are character columns. The merger retains input row order, column order, column types, and every cell outside the explicit patch. It does not recalculate derived variables or rerun the FReD preparation pipeline. Preserve the change log when integrating the accepted corrections upstream.

## Limits and pending decisions

Any field is verified for 1,765/2,164 effects (81.6%); all six numeric fields for 147 (6.8%); all seven fields for 112 (5.2%). The 80% complete-effect goal was not reached. Primary-source coverage is 249/255 initially missing source groups, not 249/255 statistically verified effects. Findings are selected by source availability and target identification; they do not estimate a representative dataset error rate.

Chan & Feldman is flagged for possible removal/inclusion review, not automatically removed. Missing Armon, Yang, and Ku primary replication reports are flagged for the responsible OSF/COS team to provide stable report links. No separate email/Slack message or availability-based statistical verdict change has been made.
