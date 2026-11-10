# Seven SCORE aggregate rows superseded by their individual attempts

All seven entries previously lacking report identifiers have been traced to COS posthoc aggregations, each combining two replication attempts. They are not seven unidentified individual replications. COS explicitly labels them `is_manylabs = posthoc` and `manylabs_type = aggregation` in the [published replication outcomes](https://osf.io/download/2c8gh/).

The imported claim IDs, sample sizes, p-values and converted correlations match those records (absolute tolerance 0.000001). Their scripts explicitly fit fixed-effect meta-analytic models and name **Andrew Tyner** as code author, with June 2024 dates. This identifies the aggregation code author; it does not assign that author to the constituent replication reports.

The seven pooled rows are **superseded**: each is replaced by separate FReD rows for its two individual attempts, and they stay excluded from FReD builds. Releasing them as well would count the same participants twice. The archived source files keep their unmodified values. The supersession does not imply the pooled numerical results are invalid.

| FReD claim | Aggregate ID / project | Component attempts and projects | Aggregation script |
|---|---|---|---|
| `AvOr_single-trace` | [6917o](https://osf.io/pbf7c/) | [92g](https://osf.io/jxd7b/), [24716](https://osf.io/bx4hy/) | [R code](https://osf.io/download/e29wm/) |
| `LyLd_single-trace` | [2kk9o](https://osf.io/5kpaz/) | [944y](https://osf.io/jb9rq/), [10g2](https://osf.io/9u2n4/) | [R code](https://osf.io/download/u5ngq/) |
| `zlm2_single-trace` | [2wgy9](https://osf.io/ksu8x/) | [9977](https://osf.io/qy62r/), [128g6](https://osf.io/s2x3c/) | [R code](https://osf.io/download/6881039645326f729c1f64df/) |
| `plLK_single-trace` | [243yy](https://osf.io/d3ukm/) | [5g9](https://osf.io/fhyzs/), [6ow46](https://osf.io/h7wx8/) | [R code](https://osf.io/download/688104a1af56abfc8324220c/) |
| `EQxa_single-trace` | [2kk4o](https://osf.io/s836p/) | [6738](https://osf.io/wdgns/), [6m396](https://osf.io/7f42k/) | [R code](https://osf.io/download/68810e794f6269d905241f97/) |
| `8wZ0_single-trace` | [6o4o5](https://osf.io/fxcey/) | [276](https://osf.io/tdr6s/), [2y486](https://osf.io/vt6ga/) | [R code](https://osf.io/download/uq37e/) |
| `AgO1_single-trace` | [6o4z5](https://osf.io/hfdxs/) | [895g](https://osf.io/5tk2e/), [23m12](https://osf.io/z9emg/) | [R code](https://osf.io/download/68810ee734519150da84fe65/) |

## Individual attempts that supersede the pooled rows

All fourteen completed results reports have been retrieved and checked; see [the report-status ledger](component_reports.md) for links, bylines, stages and import checks.

- **FReD:** each attempt has its own row in `COS coding` (rows 5484–5497, effect IDs fe05482–fe05495), marked `validated - chosen` by Lukas Wallrich on 10 November 2026. Their statistical, effect-size and outcome fields have not yet been coded.
- **FLoRA:** twelve new rows (4247–4258) and the repaired Hoeppner/Hippel/Nax entry (row 2135) await validation. Schmidt/Clark’s report was already published as `FLORA-002670` (row 598, unchanged).
- `entry_sheet_intake.csv` maps each attempt to its report and rows.

The Hanel, Martončik, Berry and Chen reproduction rows for four of the same original papers are different attempts.

## Why the earlier report matches were insufficient

A match on the original paper alone cannot identify a pooled result. For example, the Alves row combines projects `jxd7b` and `bx4hy`; assigning only the Schmidt/Clark report from `bx4hy` would omit the other attempt. The Ohtsubo, Pastötter and Rodriguez-Lara reproduction reports previously found in FLoRA are different attempts, not references for these aggregates. The supposed FReD/FLoRA coverage discrepancy therefore conflated pooled result rows with individual-report rows. A strict superset still needs an explicit definition at those two levels.

## Source and release mechanism

- [Published outcomes](https://osf.io/download/2c8gh/) connect each FReD claim to the aggregate report ID and supply the `posthoc` / `aggregation` flags and matching numeric values.
- [All replication cases](https://osf.io/download/2k9ht/) confirm the aggregate report IDs. [Project tracking](https://osf.io/download/2e5nk/) maps aggregate and component attempt IDs to their OSF projects. The current aggregate projects contain data and R scripts, rather than standalone authored replication reports.
- [COS’s SCORE page](https://www.cos.io/score) links to the authoritative [data project](https://osf.io/dtzx4/). The [central analysis-code project](https://osf.io/uqegb/) contains the seven scripts. Downloaded scripts were inspected as text; they were not executed.
- `holds_evidence.json` records the primary-source hashes, aggregate and component IDs/links, code headers, script hashes, and the three numeric cross-checks per row. `holds.csv` is the exclusion manifest; all seven rows are `superseded`.
- `R/score_report_holds.R` reads the manifest in the SCORE integration step before binding to FReD. It accepts only `hold`, `superseded` or `released`; `hold` and `superseded` rows are excluded. The raw CSV and prepared workbook remain complete (132 rows); the build imports 125 SCORE rows.
- `Rscript tests/score_report_holds.R` tests both real source files, exact preservation of every retained field, the actual notebook integration chunk, and explicit restoration. `Rscript tests/score_report_references.R` continues to test the 116 corrected references.

Tracking: [issue #168](https://github.com/forrtproject/fred-data/issues/168), [PR #167](https://github.com/forrtproject/fred-data/pull/167). Existing generated exports were not rewritten; the exclusion takes effect on the next pipeline build. API cost: US$0.
