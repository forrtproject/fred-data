# Status of the fourteen individual SCORE attempts

All fourteen constituent attempts have publicly accessible reports containing results. Each report was retrieved through the public OSF API and read on 10 November 2026. None of these fourteen is merely a registration awaiting results.

**Entry sheets:** all fourteen attempts are represented in both entry sheets. In FReD (`COS coding`, rows 5484–5497) each attempt has its own row, marked `validated - chosen` by Lukas Wallrich on 10 November 2026, with sample sizes, effect sizes and p-values coded from each report (`component_fred_coding.csv`). Their reported success comes from the authors’ own statements, entered in the replication success sheet (rows 1982–1995). In FLoRA (`replication list`) twelve new rows (4247–4258) and the repaired Hoeppner/Hippel/Nax entry (row 2135) await validation; validated Schmidt/Clark row 598 is unchanged. References use the descriptive title `[Replication report for “…”]`. See `entry_sheet_intake.csv` for report-to-row links and `entry_sheet_intake_verification.json` for verification.

**Before intake:** one report was published in FLoRA, one had an unvalidated registration-based entry and twelve had no matching entry. The table and `component_report_status.csv` below preserve that pre-intake status. None of the new entries has been published by this action.

| Original / attempt | Results report | Authors printed in report | Kind and completion | FLoRA source status before intake |
|---|---|---|---|---|
| AvOr / `92g` | [Report](https://osf.io/4hkyn/) | Ilka Gleibs; Nihan Albayrak-Aydemir | direct; completed | No matching entry found |
| AvOr / `24716` | [Report](https://osf.io/tybxg/) | Kathleen Schmidt; Bruce M. Clark | direct; completed | Published as FLORA-002670 |
| LyLd / `944y` | [Report](https://osf.io/bc2v6/) | Bob Reed; Diem Vo; Jane Duan; James Bailey; Tom Coupe | secondary-data; completed | No matching entry found |
| LyLd / `10g2` | [Report](https://osf.io/2cpf8/) | Bob Reed; Diem Vo; Jianhua Duan; Sanghyun Hong; Tom Coupe; Xindong Xue | secondary-data; completed | No matching entry found |
| zlm2 / `9977` | [Report](https://osf.io/pbw2f/) | No byline; attributed to John E. Edlund | direct; completed | No matching entry found |
| zlm2 / `128g6` | [Report](https://osf.io/zjt47/) | John E. Edlund | generalizability; completed | No matching entry found |
| plLK / `5g9` | [Report](https://osf.io/cdqks/) | Lars Tummers; Robin Bouwman | direct; completed | No matching entry found |
| plLK / `6ow46` | [Report](https://osf.io/r42en/) | Kim Peters | generalizability; completed | No matching entry found |
| EQxa / `6738` | [Report](https://osf.io/xn73j/) | Zachariah Berry | direct; completed | No matching entry found |
| EQxa / `6m396` | [Report](https://osf.io/atwck/) | Zachariah Berry | generalizability; completed | No matching entry found |
| 8wZ0 / `276` | [Report](https://osf.io/fq2vg/) | No byline; attributed to Bence Bago; Balazs Aczel | direct; completed | No matching entry found |
| 8wZ0 / `2y486` | [Report](https://osf.io/52nkw/) | Zachariah Berry | generalizability; completed | No matching entry found |
| AgO1 / `895g` | [Report](https://osf.io/fzkm3/) | Jingnan (Cecilia) Chen | direct; completed | No matching entry found |
| AgO1 / `23m12` | [Report](https://osf.io/34qhg/) | Sven Hoeppner; Svenja Hippel; Heinrich Nax | direct; completed | Existing unvalidated registration entry; update to results report |

## What the status flags mean

- The published COS table marks all fourteen **focal component estimates** `repli_version_of_record = FALSE`; the corresponding pooled estimates are selected versions. This is a selection for the headline analysis. It does not say that a report is unfinished. Some other claims within the same multi-claim report are selected individually.
- `focal_cos_criterion_met` in the ledger copies the published COS criterion for the specific focal claim. It is not a new coding of a report’s overall outcome. In particular, Hoeppner/Hippel/Nax report different simple- and complex-claim outcomes. No dataset outcome or effect-size value was changed.
- Four reports explicitly describe generalizability attempts (`128g6`, `6ow46`, `6m396`, `2y486`). Fox’s two attempts are secondary-data replications (CPS versus SIPP). Preserve these distinctions during curation.

## Checks needed before importing individual rows

- **Use the final/cumulative analysis within an attempt.** Ohtsubo `9977`, McCarter `5g9`, Pastötter `6738` and Trémolière `276` have Stage 1 and cumulative Stage 2 results. Those are not independent replication attempts. Alves `92g` stopped after its successful Stage 1 under its stopping rule.
- **Two reports have no byline; their authors are attributed.** Ohtsubo `9977` is attributed to John E. Edlund: the report file’s author metadata names him, the report is written in the first person singular, and he is the OSF project’s only non-SCORE contributor. Trémolière `276` is attributed to Bence Bago and Balazs Aczel: the OSF file name and PDF author metadata name them, and they are the project’s only non-SCORE contributors. The references note the attribution.
- **Use the later Kim Peters report.** McCarter `6ow46` has an [earlier template with an author placeholder](https://osf.io/kjp9f/) and a [later report naming Kim Peters](https://osf.io/r42en/). The latter supplies the attribution.
- **Repair the existing Hoeppner/Hippel/Nax entry instead of duplicating it.** The replications sheet has source UUID `010218f4-5492-47ae-aa68-8c423d6c2fb4`, row 2135 in the checked CSV, with blank `validation_status`, `outcome = unclear` and DOI `10.17605/osf.io/w3kuz`. The OSF API confirms [w3kuz](https://osf.io/w3kuz/) is a registration of project `z9emg`; the [completed results report](https://osf.io/34qhg/) is already available. The entry now cites the completed report and keeps the registration DOI as `alt_identifier_r`. The report is cited in its current version (v4, 9 October 2023): versions 1–2 (November 2021) were blank SCORE templates, and results were first added in version 3 (18 January 2022).
- **Reconcile the Trémolière sample definition.** The `276` report and published individual record use a final analytic sample of 533, while the aggregation script uses 538. This is an import check, not a change to the archived values.
- **Keep the focal analysis unit.** Chen’s `895g` report describes 55 participants but has 27 observations in the focal regression, which matches the published focal record. Multi-claim reports also need claim/study matching before FReD coding.

## Evidence and boundaries

- `component_report_status.csv`: fourteen attempts, preferred report URLs, bylines or attribution gaps, report kinds, focal published flags, current dataset membership and import notes.
- `component_report_evidence.json`: report metadata endpoints, SHA-256 hashes, byline evidence, focal COS records, source-sheet hashes and the existing pending-entry identifier. The checked public sheets were all enabled sources in flora-validation’s `sources.yml`; matches used project/report GUIDs and normalized original DOIs. No claim is made about unpublished work outside those sheets.
- [COS replication outcomes](https://osf.io/download/2c8gh/) and [project tracking](https://osf.io/download/2e5nk/) provide the claim/report mappings and flags. `holds_evidence.json` pins those source files.
- The [seven pooled rows are superseded](held_aggregates.md) by these individual rows and stay excluded from FReD builds. FLoRA changes use its normal validation and correction-log paths. Generated datasets were not edited. API cost: US$0.
