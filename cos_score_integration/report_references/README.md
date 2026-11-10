# SCORE report authors (10 November 2026)

The references credit the named replication teams or reproduction analysts printed in the reports. SCORE staff remain only where the report itself credits them as contributors. No DOI was added or changed.

## Coverage and delivery

- FReD: 116 source corrections prepared; 16 unresolved rows; 0 discovery candidates excluded as unrelated to SCORE.
- FLoRA: 277 source corrections prepared; 12 unresolved rows; 1 discovery candidates excluded as unrelated to SCORE.

FReD corrections are in `cache/manual_references.xlsx`. `R/score_report_references.R`, called after the reference join in `pipelines/fred/prepare_fred.qmd`, overrides cached project metadata only for corrected FReD URLs listed in this audit. `output/FReD.xlsx` and `output/flora.csv` were read only.

FLoRA now uses its own sheet sources (`score_2025`, replications and reproductions) and Python reference pipeline in **forrtproject/flora-validation**. It does not inherit subsequent edits to this workbook. Its own `data/manual_references.xlsx` is a separate seed. The companion PR supplies a reviewed batch and an application script that calls `flora_service.update_record()` → `flora_edits.save()`. The batch has not been applied to the live database. SCORE IDs and existing reference text match both repositories’ exports.

## Evidence and conventions

- `audit.csv` lists every candidate, its permanent row ID, file row number (header is row 1), original study, current reference, corrected reference or unresolved reason. Discovery uses the prepared COS claim IDs, FLoRA SCORE provenance, SCORE staff metadata, and the manual reproduction keys from the earlier repairs. One unrelated reproduction was excluded after checking its report.
- `evidence.json` records public OSF API and report links, report headers/bylines, file hashes, and date evidence. Metadata was retrieved through the free public API, reusing cached responses. Incremental cost: US$0.
- Bracketed titles are supplied descriptive titles identifying the original paper; they replace opaque internal codes. Printed titles remain in the evidence headers. Named author order follows the report, including explicit data-finder/data-analyst credits. Titles are not presented as literal transcriptions.
- Use the date printed in the report header where available; otherwise use the OSF report file deposit year, explicitly labelled in the evidence. Project update dates were not used. Corrected references link the report file; existing dataset DOI and URL columns are preserved.
- A project contributor list that mixes researchers with SCORE administrators cannot by itself establish who wrote an unsigned report. These cases remain unresolved. Do not infer an author from a project code.

## Unresolved rows

**No named authors in report byline (or placeholder only); project contributors do not distinguish report writers from SCORE staff.**

FReD: x0pA_single-trace, FReD: DEqr_single-trace, FReD: eg3p_single-trace, FReD: mxyQ_single-trace, FReD: qXX2_single-trace, FLoRA: FLORA-002648, FLoRA: FLORA-002655, FLoRA: FLORA-002692, FLoRA: FLORA-002841, FLoRA: FLORA-002881, FLoRA: FLORA-002883, FLoRA: FLORA-002891, FLoRA: FLORA-002895

**OSF report GUID returns HTTP 410 (deleted file); cited project storage has no identifiable replacement report.**

FReD: mJDj_single-trace, FReD: G1Lr_single-trace, FReD: Q1dl_single-trace, FReD: YpZZ_single-trace, FLoRA: FLORA-002867, FLoRA: FLORA-002886, FLoRA: FLORA-002893, FLoRA: FLORA-002906

**No report URL or DOI in the FReD export or prepared COS source; original DOI alone does not identify the replication.**

FReD: AvOr_single-trace, FReD: LyLd_single-trace, FReD: zlm2_single-trace, FReD: plLK_single-trace, FReD: EQxa_single-trace, FReD: 8wZ0_single-trace, FReD: AgO1_single-trace

## Ten before/after spot checks

### 1. FReD — e3G7_single-trace

Before: Parsons, E. S., Miske, O., Luis, B., Loomas, Z., Kline Struhl, M., Fox, N. W., … Baskin, E. (2025, November 18). Lammers_JournPerSocPsy_2018_e3G7 - Baskin - New Data Replication - 6o442. Retrieved from osf.io/23ghe

After: Baskin, E. (2021). [Replication report for “Past-focused temporal communication overcomes conservatives’ resistance to liberal political ideas”]. OSF. https://osf.io/36w4c/

Evidence: https://osf.io/36w4c/

### 2. FReD — YWep_single-trace

Before: Bokhove, C., Nast, C., Tyner, A. H., Abatayo, A., Loomas, Z., Miske, O., … Bokhove, C. (2025, November 18). Kim_CompEdu_2014_YWep - Nast/Bokhove - Secondary Data Replication - 75g6. Retrieved from osf.io/u52y3

After: Bokhove, C., Nast, C., & SCORE team (2021). [Replication report for “An analysis of variables affecting the ICT literacy level of Korean elementary school students”]. OSF. https://osf.io/2wfgv/

Evidence: https://osf.io/2wfgv/

### 3. FLoRA — FLORA-001441

Before: Parsons, E. S., Miske, O., Luis, B., Loomas, Z., Fox, N., Tyner, A. H., Hahn, K., Maier, M., Bartoš, F., & Savi, A. O. (2022). Reproduction (with author data): Hansen & Melzner (2014, Journal of Experimental Social Psychology). OSF. https://doi.org/10.17605/osf.io/akubt

After: Bartoš, F., Maier, M., & Savi, A. (2022). [Reproduction report for “What you hear shapes how you think: Sound patterns change level of construal”]. OSF. https://osf.io/39g7q/

Evidence: https://osf.io/39g7q/

### 4. FLoRA — FLORA-001499

Before: Fox, N., Loomas, Z., Miske, O., Luis, B., & Tutor, M. (2020). Reproduction (with author data & code): Wang (2013, American Economic Journal: Applied Economics). OSF. https://doi.org/10.17605/osf.io/ezx2k

After: Tutor, M. (2020). [Reproduction report for “Marriage Networks, Nepotism, and Labor Market Outcomes in China”]. OSF. https://osf.io/2yndk/

Evidence: https://osf.io/2yndk/

### 5. FLoRA — FLORA-001519

Before: Miske, O., Loomas, Z., Luis, B., Tyner, A. H., Fox, N., Struhl, M. K., & Talbert, E. (2020). Reproduction (with author data & code): Chen & van Ours (2018, Demography). OSF. https://doi.org/10.17605/osf.io/kup8x

After: Talbert, E. (2020). [Reproduction report for “Subjective Well-being and Partnership Dynamics: Are Same-Sex Relationships Different?”]. OSF. https://osf.io/u3qpy/

Evidence: https://osf.io/u3qpy/

### 6. FLoRA — FLORA-001523

Before: Huntington-Klein, N., Tyner, A. H., Loomas, Z., Miske, O., Fox, N., & Luis, B. (2020). Reproduction (without author data): Horowitz (2018, American Sociological Review). OSF. https://doi.org/10.17605/osf.io/6ye5m

After: Huntington-Klein, N. (2020). [Reproduction report for “Relative Education and the Advantage of a College Degree”]. OSF. https://osf.io/wrdvs/

Evidence: https://osf.io/wrdvs/

### 7. FLoRA — FLORA-002742

Before: Miske, O., Loomas, Z., Luis, B., Fox, N. W., & Talbert, E. (2026, February 11). Malik_covid_wx5k - Talbert - Reproduction (with author data & code) - 36mz. Retrieved from osf.io/yrnmv

After: Talbert, E. (2020). [Reproduction report for “COVID-19 related social distancing measures and reduction in city mobility”]. OSF. https://osf.io/x7jrb/

Evidence: https://osf.io/x7jrb/

### 8. FReD — d24p_single-trace

Before: Baskin, E., Parsons, E. S., Miske, O., Luis, B., Loomas, Z., Kline Struhl, M., … Hahn, K. (2025, November 18). Ritov_OrgBehavior_2014_d24p - Baskin - New Data Replication - 67z12. Retrieved from osf.io/cwmb5

After: Baskin, E. (2021). [Replication report for “Affirmative action and other group tradeoff policies: Identifiability of those adversely affected”]. OSF. https://osf.io/9hjxc/

Evidence: https://osf.io/9hjxc/

### 9. FReD — 5XEE_single-trace

Before: Parsons, E. S., Miske, O., Luis, B., Loomas, Z., Kline Struhl, M., Fox, N. W., … Baskin, E. (2025, November 18). Kausel_OrgBehavior_2015_5XEE - Baskin - New Data Replication - 21z56. Retrieved from osf.io/n35c2

After: Baskin, E. (2021). [Replication report for “Too arrogant for their own good? Why and when narcissists dismiss advice”]. OSF. https://osf.io/r58ch/

Evidence: https://osf.io/r58ch/

### 10. FReD — N8pB_single-trace

Before: Parsons, E. S., Miske, O., Luis, B., Loomas, Z., Kline Struhl, M., Fox, N. W., … Baskin, E. (2025, November 18). Lu_OrgBehavior_2017_N8pB - Baskin - New Data Replication - 2ggz2. Retrieved from osf.io/ujg2c

After: Baskin, E. (2021). [Replication report for ““Switching On” creativity: Task switching can increase creativity by reducing cognitive fixation”]. OSF. https://osf.io/ahgfx/

Evidence: https://osf.io/ahgfx/

## Verification

- `Rscript tests/score_report_references.R`: all corrected FReD rows override stale references, unresolved rows are preserved, protected values are unchanged, and reruns are identical.
- FLoRA: the batch validates all fields through `flora_edits.clean_value`; tests cover stale-reference rejection before any save, correction-log routing, version checks and safe reruns. The full suite on the updated base passed (2,856 passed, 412 skipped); JavaScript syntax check passed.
- Full FReD regeneration was not run: generated outputs are outside this source correction, and this environment lacks the notebook’s `rcrossref` dependency. The actual overlay was executed against every audited FReD row.
