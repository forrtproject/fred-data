# FReD statistics audit

**Interim checkpoint — 2026-10-29T09:46:38.490252+00:00.** 13 confirmed field errors have been identified so far. Paper checking is still in progress; the deterministic screen alone is not verification.

The frozen workbook contains 2,164 effects in 432 replication works. Part A screened every effect and flagged 175. 4 flagged effects currently contain a confirmed field error (this includes any error on those effects, not necessarily the flagged field).

Paper checkpoints exist for 187/2164 effects. All three original statistics are evaluable for 26/2164; all three replication statistics for 17/2164. All seven fields, including author-reported success, are checked for 2/2164. Individual-field coverage is below.

Coverage depends on paper access and target identification. These results are not a representative sample of FReD. Bounds below describe remaining identification uncertainty, not binomial sampling intervals. Different metrics remain not comparable unless a documented transformation is reproduced.

| Field | Confirmed errors / evaluable | Unverified | Not comparable | All-row error bounds |
|---|---:|---:|---:|---:|
| n_o | 0/43 (0.0%) | 2120 | 1 | 0.00%–98.01% |
| es_value_o | 0/55 (0.0%) | 2102 | 7 | 0.00%–97.46% |
| pval_value_o | 1/56 (1.8%) | 2108 | 0 | 0.05%–97.46% |
| n_r | 6/76 (7.9%) | 2084 | 4 | 0.28%–96.77% |
| es_value_r | 2/34 (5.9%) | 2081 | 49 | 0.09%–98.52% |
| pval_value_r | 0/76 (0.0%) | 2088 | 0 | 0.00%–96.49% |
| reported_success | 4/75 (5.3%) | 2089 | 0 | 0.18%–96.72% |

Source-project breakdown uses the leading text before an underscore or digit in `fred_id`; `fred_id` is provenance, not an effect key. Each cell shows errors/evaluable; unverified and not-comparable values are shown separately.

| Project prefix | Field | Errors/evaluable | Unverified | Not comparable |
|---|---|---:|---:|---:|
|  | n_o | 0/0 | 23 | 0 |
|  | es_value_o | 0/0 | 23 | 0 |
|  | pval_value_o | 0/0 | 23 | 0 |
|  | n_r | 0/0 | 23 | 0 |
|  | es_value_r | 0/0 | 23 | 0 |
|  | pval_value_r | 0/0 | 23 | 0 |
|  | reported_success | 0/0 | 23 | 0 |
| AOQj | n_o | 0/0 | 1 | 0 |
| AOQj | es_value_o | 0/0 | 1 | 0 |
| AOQj | pval_value_o | 0/0 | 1 | 0 |
| AOQj | n_r | 0/0 | 1 | 0 |
| AOQj | es_value_r | 0/0 | 1 | 0 |
| AOQj | pval_value_r | 0/0 | 1 | 0 |
| AOQj | reported_success | 0/0 | 1 | 0 |
| AYQG | n_o | 0/0 | 1 | 0 |
| AYQG | es_value_o | 0/0 | 1 | 0 |
| AYQG | pval_value_o | 0/0 | 1 | 0 |
| AYQG | n_r | 0/0 | 1 | 0 |
| AYQG | es_value_r | 0/0 | 1 | 0 |
| AYQG | pval_value_r | 0/0 | 1 | 0 |
| AYQG | reported_success | 0/0 | 1 | 0 |
| AgO | n_o | 0/0 | 1 | 0 |
| AgO | es_value_o | 0/0 | 1 | 0 |
| AgO | pval_value_o | 0/0 | 1 | 0 |
| AgO | n_r | 0/0 | 1 | 0 |
| AgO | es_value_r | 0/0 | 1 | 0 |
| AgO | pval_value_r | 0/0 | 1 | 0 |
| AgO | reported_success | 0/0 | 1 | 0 |
| AqDO | n_o | 0/0 | 1 | 0 |
| AqDO | es_value_o | 0/0 | 1 | 0 |
| AqDO | pval_value_o | 0/0 | 1 | 0 |
| AqDO | n_r | 0/0 | 1 | 0 |
| AqDO | es_value_r | 0/0 | 1 | 0 |
| AqDO | pval_value_r | 0/0 | 1 | 0 |
| AqDO | reported_success | 0/0 | 1 | 0 |
| Arb | n_o | 0/0 | 27 | 0 |
| Arb | es_value_o | 0/0 | 27 | 0 |
| Arb | pval_value_o | 0/0 | 27 | 0 |
| Arb | n_r | 0/0 | 27 | 0 |
| Arb | es_value_r | 0/0 | 27 | 0 |
| Arb | pval_value_r | 0/0 | 27 | 0 |
| Arb | reported_success | 0/0 | 27 | 0 |
| Arb  | n_o | 0/0 | 5 | 0 |
| Arb  | es_value_o | 0/0 | 5 | 0 |
| Arb  | pval_value_o | 0/0 | 5 | 0 |
| Arb  | n_r | 0/0 | 5 | 0 |
| Arb  | es_value_r | 0/0 | 5 | 0 |
| Arb  | pval_value_r | 0/0 | 5 | 0 |
| Arb  | reported_success | 0/0 | 5 | 0 |
| AvOr | n_o | 0/0 | 1 | 0 |
| AvOr | es_value_o | 0/0 | 1 | 0 |
| AvOr | pval_value_o | 0/0 | 1 | 0 |
| AvOr | n_r | 0/0 | 1 | 0 |
| AvOr | es_value_r | 0/0 | 1 | 0 |
| AvOr | pval_value_r | 0/0 | 1 | 0 |
| AvOr | reported_success | 0/0 | 1 | 0 |
| Blxd | n_o | 0/0 | 2 | 0 |
| Blxd | es_value_o | 0/0 | 2 | 0 |
| Blxd | pval_value_o | 0/0 | 2 | 0 |
| Blxd | n_r | 0/0 | 2 | 0 |
| Blxd | es_value_r | 0/0 | 2 | 0 |
| Blxd | pval_value_r | 0/0 | 2 | 0 |
| Blxd | reported_success | 0/0 | 2 | 0 |
| Boyce | n_o | 0/14 | 265 | 1 |
| Boyce | es_value_o | 0/13 | 264 | 3 |
| Boyce | pval_value_o | 1/11 | 269 | 0 |
| Boyce | n_r | 4/12 | 268 | 0 |
| Boyce | es_value_r | 2/9 | 266 | 5 |
| Boyce | pval_value_r | 0/11 | 269 | 0 |
| Boyce | reported_success | 4/16 | 264 | 0 |
| Br | n_o | 0/0 | 3 | 0 |
| Br | es_value_o | 0/0 | 3 | 0 |
| Br | pval_value_o | 0/0 | 3 | 0 |
| Br | n_r | 0/0 | 3 | 0 |
| Br | es_value_r | 0/0 | 3 | 0 |
| Br | pval_value_r | 0/0 | 3 | 0 |
| Br | reported_success | 0/0 | 3 | 0 |
| BrGp | n_o | 0/0 | 4 | 0 |
| BrGp | es_value_o | 0/0 | 4 | 0 |
| BrGp | pval_value_o | 0/0 | 4 | 0 |
| BrGp | n_r | 0/0 | 4 | 0 |
| BrGp | es_value_r | 0/0 | 4 | 0 |
| BrGp | pval_value_r | 0/0 | 4 | 0 |
| BrGp | reported_success | 0/0 | 4 | 0 |
| CORE | n_o | 0/9 | 105 | 0 |
| CORE | es_value_o | 0/10 | 104 | 0 |
| CORE | pval_value_o | 0/10 | 104 | 0 |
| CORE | n_r | 0/14 | 99 | 1 |
| CORE | es_value_r | 0/3 | 108 | 3 |
| CORE | pval_value_r | 0/7 | 107 | 0 |
| CORE | reported_success | 0/14 | 100 | 0 |
| Camereretal | n_o | 0/0 | 39 | 0 |
| Camereretal | es_value_o | 0/0 | 39 | 0 |
| Camereretal | pval_value_o | 0/0 | 39 | 0 |
| Camereretal | n_r | 0/0 | 39 | 0 |
| Camereretal | es_value_r | 0/0 | 39 | 0 |
| Camereretal | pval_value_r | 0/0 | 39 | 0 |
| Camereretal | reported_success | 0/0 | 39 | 0 |
| D | n_o | 0/0 | 3 | 0 |
| D | es_value_o | 0/0 | 3 | 0 |
| D | pval_value_o | 0/0 | 3 | 0 |
| D | n_r | 0/0 | 3 | 0 |
| D | es_value_r | 0/0 | 3 | 0 |
| D | pval_value_r | 0/0 | 3 | 0 |
| D | reported_success | 0/0 | 3 | 0 |
| DEqr | n_o | 0/0 | 1 | 0 |
| DEqr | es_value_o | 0/0 | 1 | 0 |
| DEqr | pval_value_o | 0/0 | 1 | 0 |
| DEqr | n_r | 0/0 | 1 | 0 |
| DEqr | es_value_r | 0/0 | 1 | 0 |
| DEqr | pval_value_r | 0/0 | 1 | 0 |
| DEqr | reported_success | 0/0 | 1 | 0 |
| Data (editable) | n_o | 0/0 | 3 | 0 |
| Data (editable) | es_value_o | 0/0 | 3 | 0 |
| Data (editable) | pval_value_o | 0/0 | 3 | 0 |
| Data (editable) | n_r | 0/0 | 3 | 0 |
| Data (editable) | es_value_r | 0/0 | 3 | 0 |
| Data (editable) | pval_value_r | 0/0 | 3 | 0 |
| Data (editable) | reported_success | 0/0 | 3 | 0 |
| E | n_o | 0/0 | 1 | 0 |
| E | es_value_o | 0/0 | 1 | 0 |
| E | pval_value_o | 0/0 | 1 | 0 |
| E | n_r | 0/0 | 1 | 0 |
| E | es_value_r | 0/0 | 1 | 0 |
| E | pval_value_r | 0/0 | 1 | 0 |
| E | reported_success | 0/0 | 1 | 0 |
| EJpm | n_o | 0/0 | 3 | 0 |
| EJpm | es_value_o | 0/0 | 3 | 0 |
| EJpm | pval_value_o | 0/0 | 3 | 0 |
| EJpm | n_r | 0/0 | 3 | 0 |
| EJpm | es_value_r | 0/0 | 3 | 0 |
| EJpm | pval_value_r | 0/0 | 3 | 0 |
| EJpm | reported_success | 0/0 | 3 | 0 |
| EKBZ | n_o | 0/0 | 1 | 0 |
| EKBZ | es_value_o | 0/0 | 1 | 0 |
| EKBZ | pval_value_o | 0/0 | 1 | 0 |
| EKBZ | n_r | 0/0 | 1 | 0 |
| EKBZ | es_value_r | 0/0 | 1 | 0 |
| EKBZ | pval_value_r | 0/0 | 1 | 0 |
| EKBZ | reported_success | 0/0 | 1 | 0 |
| EQxa | n_o | 0/0 | 1 | 0 |
| EQxa | es_value_o | 0/0 | 1 | 0 |
| EQxa | pval_value_o | 0/0 | 1 | 0 |
| EQxa | n_r | 0/0 | 1 | 0 |
| EQxa | es_value_r | 0/0 | 1 | 0 |
| EQxa | pval_value_r | 0/0 | 1 | 0 |
| EQxa | reported_success | 0/0 | 1 | 0 |
| Eb | n_o | 0/0 | 1 | 0 |
| Eb | es_value_o | 0/0 | 1 | 0 |
| Eb | pval_value_o | 0/0 | 1 | 0 |
| Eb | n_r | 0/0 | 1 | 0 |
| Eb | es_value_r | 0/0 | 1 | 0 |
| Eb | pval_value_r | 0/0 | 1 | 0 |
| Eb | reported_success | 0/0 | 1 | 0 |
| FORRT | n_o | 0/0 | 24 | 0 |
| FORRT | es_value_o | 0/0 | 24 | 0 |
| FORRT | pval_value_o | 0/0 | 24 | 0 |
| FORRT | n_r | 0/0 | 24 | 0 |
| FORRT | es_value_r | 0/0 | 24 | 0 |
| FORRT | pval_value_r | 0/0 | 24 | 0 |
| FORRT | reported_success | 0/0 | 24 | 0 |
| G | n_o | 0/0 | 1 | 0 |
| G | es_value_o | 0/0 | 1 | 0 |
| G | pval_value_o | 0/0 | 1 | 0 |
| G | n_r | 0/0 | 1 | 0 |
| G | es_value_r | 0/0 | 1 | 0 |
| G | pval_value_r | 0/0 | 1 | 0 |
| G | reported_success | 0/0 | 1 | 0 |
| GXEW | n_o | 0/0 | 1 | 0 |
| GXEW | es_value_o | 0/0 | 1 | 0 |
| GXEW | pval_value_o | 0/0 | 1 | 0 |
| GXEW | n_r | 0/0 | 1 | 0 |
| GXEW | es_value_r | 0/0 | 1 | 0 |
| GXEW | pval_value_r | 0/0 | 1 | 0 |
| GXEW | reported_success | 0/0 | 1 | 0 |
| Holzmeisteretal | n_o | 0/0 | 26 | 0 |
| Holzmeisteretal | es_value_o | 0/0 | 26 | 0 |
| Holzmeisteretal | pval_value_o | 0/0 | 26 | 0 |
| Holzmeisteretal | n_r | 0/0 | 26 | 0 |
| Holzmeisteretal | es_value_r | 0/0 | 26 | 0 |
| Holzmeisteretal | pval_value_r | 0/0 | 26 | 0 |
| Holzmeisteretal | reported_success | 0/0 | 26 | 0 |
| JRpA | n_o | 0/0 | 2 | 0 |
| JRpA | es_value_o | 0/0 | 2 | 0 |
| JRpA | pval_value_o | 0/0 | 2 | 0 |
| JRpA | n_r | 0/0 | 2 | 0 |
| JRpA | es_value_r | 0/0 | 2 | 0 |
| JRpA | pval_value_r | 0/0 | 2 | 0 |
| JRpA | reported_success | 0/0 | 2 | 0 |
| Keith | n_o | 0/0 | 1 | 0 |
| Keith | es_value_o | 0/0 | 1 | 0 |
| Keith | pval_value_o | 0/0 | 1 | 0 |
| Keith | n_r | 0/0 | 1 | 0 |
| Keith | es_value_r | 0/0 | 1 | 0 |
| Keith | pval_value_r | 0/0 | 1 | 0 |
| Keith | reported_success | 0/0 | 1 | 0 |
| Kybl | n_o | 0/0 | 1 | 0 |
| Kybl | es_value_o | 0/0 | 1 | 0 |
| Kybl | pval_value_o | 0/0 | 1 | 0 |
| Kybl | n_r | 0/0 | 1 | 0 |
| Kybl | es_value_r | 0/0 | 1 | 0 |
| Kybl | pval_value_r | 0/0 | 1 | 0 |
| Kybl | reported_success | 0/0 | 1 | 0 |
| LbEB | n_o | 0/0 | 1 | 0 |
| LbEB | es_value_o | 0/0 | 1 | 0 |
| LbEB | pval_value_o | 0/0 | 1 | 0 |
| LbEB | n_r | 0/0 | 1 | 0 |
| LbEB | es_value_r | 0/0 | 1 | 0 |
| LbEB | pval_value_r | 0/0 | 1 | 0 |
| LbEB | reported_success | 0/0 | 1 | 0 |
| LmBx | n_o | 0/0 | 1 | 0 |
| LmBx | es_value_o | 0/0 | 1 | 0 |
| LmBx | pval_value_o | 0/0 | 1 | 0 |
| LmBx | n_r | 0/0 | 1 | 0 |
| LmBx | es_value_r | 0/0 | 1 | 0 |
| LmBx | pval_value_r | 0/0 | 1 | 0 |
| LmBx | reported_success | 0/0 | 1 | 0 |
| LyLd | n_o | 0/0 | 1 | 0 |
| LyLd | es_value_o | 0/0 | 1 | 0 |
| LyLd | pval_value_o | 0/0 | 1 | 0 |
| LyLd | n_r | 0/0 | 1 | 0 |
| LyLd | es_value_r | 0/0 | 1 | 0 |
| LyLd | pval_value_r | 0/0 | 1 | 0 |
| LyLd | reported_success | 0/0 | 1 | 0 |
| ManyLabs | n_o | 0/9 | 29 | 0 |
| ManyLabs | es_value_o | 0/10 | 28 | 0 |
| ManyLabs | pval_value_o | 0/10 | 28 | 0 |
| ManyLabs | n_r | 0/16 | 20 | 2 |
| ManyLabs | es_value_r | 0/0 | 20 | 18 |
| ManyLabs | pval_value_r | 0/13 | 25 | 0 |
| ManyLabs | reported_success | 0/10 | 28 | 0 |
| Manylabs | n_o | 0/0 | 38 | 0 |
| Manylabs | es_value_o | 0/0 | 38 | 0 |
| Manylabs | pval_value_o | 0/0 | 38 | 0 |
| Manylabs | n_r | 0/0 | 38 | 0 |
| Manylabs | es_value_r | 0/0 | 38 | 0 |
| Manylabs | pval_value_r | 0/0 | 38 | 0 |
| Manylabs | reported_success | 0/0 | 38 | 0 |
| N | n_o | 0/0 | 1 | 0 |
| N | es_value_o | 0/0 | 1 | 0 |
| N | pval_value_o | 0/0 | 1 | 0 |
| N | n_r | 0/0 | 1 | 0 |
| N | es_value_r | 0/0 | 1 | 0 |
| N | pval_value_r | 0/0 | 1 | 0 |
| N | reported_success | 0/0 | 1 | 0 |
| None | n_o | 0/0 | 5 | 0 |
| None | es_value_o | 0/0 | 5 | 0 |
| None | pval_value_o | 0/0 | 5 | 0 |
| None | n_r | 0/0 | 5 | 0 |
| None | es_value_r | 0/0 | 5 | 0 |
| None | pval_value_r | 0/0 | 5 | 0 |
| None | reported_success | 0/0 | 5 | 0 |
| OKRy | n_o | 0/0 | 1 | 0 |
| OKRy | es_value_o | 0/0 | 1 | 0 |
| OKRy | pval_value_o | 0/0 | 1 | 0 |
| OKRy | n_r | 0/0 | 1 | 0 |
| OKRy | es_value_r | 0/0 | 1 | 0 |
| OKRy | pval_value_r | 0/0 | 1 | 0 |
| OKRy | reported_success | 0/0 | 1 | 0 |
| OYX | n_o | 0/0 | 3 | 0 |
| OYX | es_value_o | 0/0 | 3 | 0 |
| OYX | pval_value_o | 0/0 | 3 | 0 |
| OYX | n_r | 0/0 | 3 | 0 |
| OYX | es_value_r | 0/0 | 3 | 0 |
| OYX | pval_value_r | 0/0 | 3 | 0 |
| OYX | reported_success | 0/0 | 3 | 0 |
| OeGv | n_o | 0/0 | 3 | 0 |
| OeGv | es_value_o | 0/0 | 3 | 0 |
| OeGv | pval_value_o | 0/0 | 3 | 0 |
| OeGv | n_r | 0/0 | 3 | 0 |
| OeGv | es_value_r | 0/0 | 3 | 0 |
| OeGv | pval_value_r | 0/0 | 3 | 0 |
| OeGv | reported_success | 0/0 | 3 | 0 |
| OpenMKT | n_o | 0/0 | 102 | 0 |
| OpenMKT | es_value_o | 0/7 | 95 | 0 |
| OpenMKT | pval_value_o | 0/7 | 95 | 0 |
| OpenMKT | n_r | 0/13 | 89 | 0 |
| OpenMKT | es_value_r | 0/2 | 87 | 13 |
| OpenMKT | pval_value_r | 0/15 | 87 | 0 |
| OpenMKT | reported_success | 0/13 | 89 | 0 |
| Ovkm | n_o | 0/0 | 1 | 0 |
| Ovkm | es_value_o | 0/0 | 1 | 0 |
| Ovkm | pval_value_o | 0/0 | 1 | 0 |
| Ovkm | n_r | 0/0 | 1 | 0 |
| Ovkm | es_value_r | 0/0 | 1 | 0 |
| Ovkm | pval_value_r | 0/0 | 1 | 0 |
| Ovkm | reported_success | 0/0 | 1 | 0 |
| Ow | n_o | 0/0 | 1 | 0 |
| Ow | es_value_o | 0/0 | 1 | 0 |
| Ow | pval_value_o | 0/0 | 1 | 0 |
| Ow | n_r | 0/0 | 1 | 0 |
| Ow | es_value_r | 0/0 | 1 | 0 |
| Ow | pval_value_r | 0/0 | 1 | 0 |
| Ow | reported_success | 0/0 | 1 | 0 |
| Q | n_o | 0/0 | 1 | 0 |
| Q | es_value_o | 0/0 | 1 | 0 |
| Q | pval_value_o | 0/0 | 1 | 0 |
| Q | n_r | 0/0 | 1 | 0 |
| Q | es_value_r | 0/0 | 1 | 0 |
| Q | pval_value_r | 0/0 | 1 | 0 |
| Q | reported_success | 0/0 | 1 | 0 |
| QllV | n_o | 0/0 | 1 | 0 |
| QllV | es_value_o | 0/0 | 1 | 0 |
| QllV | pval_value_o | 0/0 | 1 | 0 |
| QllV | n_r | 0/0 | 1 | 0 |
| QllV | es_value_r | 0/0 | 1 | 0 |
| QllV | pval_value_r | 0/0 | 1 | 0 |
| QllV | reported_success | 0/0 | 1 | 0 |
| R | n_o | 0/0 | 2 | 0 |
| R | es_value_o | 0/0 | 2 | 0 |
| R | pval_value_o | 0/0 | 2 | 0 |
| R | n_r | 0/0 | 2 | 0 |
| R | es_value_r | 0/0 | 2 | 0 |
| R | pval_value_r | 0/0 | 2 | 0 |
| R | reported_success | 0/0 | 2 | 0 |
| RRR | n_o | 0/0 | 31 | 0 |
| RRR | es_value_o | 0/0 | 31 | 0 |
| RRR | pval_value_o | 0/0 | 31 | 0 |
| RRR | n_r | 0/0 | 31 | 0 |
| RRR | es_value_r | 0/0 | 31 | 0 |
| RRR | pval_value_r | 0/0 | 31 | 0 |
| RRR | reported_success | 0/0 | 31 | 0 |
| RYKv | n_o | 0/0 | 3 | 0 |
| RYKv | es_value_o | 0/0 | 3 | 0 |
| RYKv | pval_value_o | 0/0 | 3 | 0 |
| RYKv | n_r | 0/0 | 3 | 0 |
| RYKv | es_value_r | 0/0 | 3 | 0 |
| RYKv | pval_value_r | 0/0 | 3 | 0 |
| RYKv | reported_success | 0/0 | 3 | 0 |
| RrOb | n_o | 0/0 | 1 | 0 |
| RrOb | es_value_o | 0/0 | 1 | 0 |
| RrOb | pval_value_o | 0/0 | 1 | 0 |
| RrOb | n_r | 0/0 | 1 | 0 |
| RrOb | es_value_r | 0/0 | 1 | 0 |
| RrOb | pval_value_r | 0/0 | 1 | 0 |
| RrOb | reported_success | 0/0 | 1 | 0 |
| Soto | n_o | 0/0 | 60 | 0 |
| Soto | es_value_o | 0/0 | 60 | 0 |
| Soto | pval_value_o | 0/0 | 60 | 0 |
| Soto | n_r | 0/0 | 60 | 0 |
| Soto | es_value_r | 0/0 | 60 | 0 |
| Soto | pval_value_r | 0/0 | 60 | 0 |
| Soto | reported_success | 0/0 | 60 | 0 |
| VB | n_o | 0/0 | 1 | 0 |
| VB | es_value_o | 0/0 | 1 | 0 |
| VB | pval_value_o | 0/0 | 1 | 0 |
| VB | n_r | 0/0 | 1 | 0 |
| VB | es_value_r | 0/0 | 1 | 0 |
| VB | pval_value_r | 0/0 | 1 | 0 |
| VB | reported_success | 0/0 | 1 | 0 |
| Vj | n_o | 0/0 | 3 | 0 |
| Vj | es_value_o | 0/0 | 3 | 0 |
| Vj | pval_value_o | 0/0 | 3 | 0 |
| Vj | n_r | 0/0 | 3 | 0 |
| Vj | es_value_r | 0/0 | 3 | 0 |
| Vj | pval_value_r | 0/0 | 3 | 0 |
| Vj | reported_success | 0/0 | 3 | 0 |
| VvZX | n_o | 0/0 | 1 | 0 |
| VvZX | es_value_o | 0/0 | 1 | 0 |
| VvZX | pval_value_o | 0/0 | 1 | 0 |
| VvZX | n_r | 0/0 | 1 | 0 |
| VvZX | es_value_r | 0/0 | 1 | 0 |
| VvZX | pval_value_r | 0/0 | 1 | 0 |
| VvZX | reported_success | 0/0 | 1 | 0 |
| WLpV | n_o | 0/0 | 1 | 0 |
| WLpV | es_value_o | 0/0 | 1 | 0 |
| WLpV | pval_value_o | 0/0 | 1 | 0 |
| WLpV | n_r | 0/0 | 1 | 0 |
| WLpV | es_value_r | 0/0 | 1 | 0 |
| WLpV | pval_value_r | 0/0 | 1 | 0 |
| WLpV | reported_success | 0/0 | 1 | 0 |
| Wre | n_o | 0/0 | 1 | 0 |
| Wre | es_value_o | 0/0 | 1 | 0 |
| Wre | pval_value_o | 0/0 | 1 | 0 |
| Wre | n_r | 0/0 | 1 | 0 |
| Wre | es_value_r | 0/0 | 1 | 0 |
| Wre | pval_value_r | 0/0 | 1 | 0 |
| Wre | reported_success | 0/0 | 1 | 0 |
| XPHI | n_o | 0/0 | 69 | 0 |
| XPHI | es_value_o | 0/0 | 69 | 0 |
| XPHI | pval_value_o | 0/0 | 69 | 0 |
| XPHI | n_r | 0/0 | 69 | 0 |
| XPHI | es_value_r | 0/0 | 69 | 0 |
| XPHI | pval_value_r | 0/0 | 69 | 0 |
| XPHI | reported_success | 0/0 | 69 | 0 |
| YWep | n_o | 0/0 | 1 | 0 |
| YWep | es_value_o | 0/0 | 1 | 0 |
| YWep | pval_value_o | 0/0 | 1 | 0 |
| YWep | n_r | 0/0 | 1 | 0 |
| YWep | es_value_r | 0/0 | 1 | 0 |
| YWep | pval_value_r | 0/0 | 1 | 0 |
| YWep | reported_success | 0/0 | 1 | 0 |
| YpZZ | n_o | 0/0 | 1 | 0 |
| YpZZ | es_value_o | 0/0 | 1 | 0 |
| YpZZ | pval_value_o | 0/0 | 1 | 0 |
| YpZZ | n_r | 0/0 | 1 | 0 |
| YpZZ | es_value_r | 0/0 | 1 | 0 |
| YpZZ | pval_value_r | 0/0 | 1 | 0 |
| YpZZ | reported_success | 0/0 | 1 | 0 |
| aYyR | n_o | 0/0 | 1 | 0 |
| aYyR | es_value_o | 0/0 | 1 | 0 |
| aYyR | pval_value_o | 0/0 | 1 | 0 |
| aYyR | n_r | 0/0 | 1 | 0 |
| aYyR | es_value_r | 0/0 | 1 | 0 |
| aYyR | pval_value_r | 0/0 | 1 | 0 |
| aYyR | reported_success | 0/0 | 1 | 0 |
| aag | n_o | 0/0 | 1 | 0 |
| aag | es_value_o | 0/0 | 1 | 0 |
| aag | pval_value_o | 0/0 | 1 | 0 |
| aag | n_r | 0/0 | 1 | 0 |
| aag | es_value_r | 0/0 | 1 | 0 |
| aag | pval_value_r | 0/0 | 1 | 0 |
| aag | reported_success | 0/0 | 1 | 0 |
| acykd | n_o | 0/0 | 1 | 0 |
| acykd | es_value_o | 0/0 | 1 | 0 |
| acykd | pval_value_o | 0/0 | 1 | 0 |
| acykd | n_r | 0/0 | 1 | 0 |
| acykd | es_value_r | 0/0 | 1 | 0 |
| acykd | pval_value_r | 0/0 | 1 | 0 |
| acykd | reported_success | 0/0 | 1 | 0 |
| add | n_o | 0/0 | 164 | 0 |
| add | es_value_o | 0/0 | 164 | 0 |
| add | pval_value_o | 0/0 | 164 | 0 |
| add | n_r | 0/0 | 164 | 0 |
| add | es_value_r | 0/0 | 164 | 0 |
| add | pval_value_r | 0/0 | 164 | 0 |
| add | reported_success | 0/0 | 164 | 0 |
| additional | n_o | 0/11 | 340 | 0 |
| additional | es_value_o | 0/14 | 333 | 4 |
| additional | pval_value_o | 0/17 | 334 | 0 |
| additional | n_r | 2/12 | 338 | 1 |
| additional | es_value_r | 0/10 | 331 | 10 |
| additional | pval_value_r | 0/19 | 332 | 0 |
| additional | reported_success | 0/12 | 339 | 0 |
| av | n_o | 0/0 | 166 | 0 |
| av | es_value_o | 0/0 | 166 | 0 |
| av | pval_value_o | 0/0 | 166 | 0 |
| av | n_r | 0/0 | 166 | 0 |
| av | es_value_r | 0/0 | 166 | 0 |
| av | pval_value_r | 0/0 | 166 | 0 |
| av | reported_success | 0/3 | 163 | 0 |
| bY | n_o | 0/0 | 1 | 0 |
| bY | es_value_o | 0/0 | 1 | 0 |
| bY | pval_value_o | 0/0 | 1 | 0 |
| bY | n_r | 0/0 | 1 | 0 |
| bY | es_value_r | 0/0 | 1 | 0 |
| bY | pval_value_r | 0/0 | 1 | 0 |
| bY | reported_success | 0/0 | 1 | 0 |
| bth | n_o | 0/0 | 1 | 0 |
| bth | es_value_o | 0/0 | 1 | 0 |
| bth | pval_value_o | 0/0 | 1 | 0 |
| bth | n_r | 0/0 | 1 | 0 |
| bth | es_value_r | 0/0 | 1 | 0 |
| bth | pval_value_r | 0/0 | 1 | 0 |
| bth | reported_success | 0/0 | 1 | 0 |
| curatescience | n_o | 0/0 | 97 | 0 |
| curatescience | es_value_o | 0/0 | 97 | 0 |
| curatescience | pval_value_o | 0/0 | 97 | 0 |
| curatescience | n_r | 0/6 | 91 | 0 |
| curatescience | es_value_r | 0/6 | 91 | 0 |
| curatescience | pval_value_r | 0/6 | 91 | 0 |
| curatescience | reported_success | 0/4 | 93 | 0 |
| d | n_o | 0/0 | 1 | 0 |
| d | es_value_o | 0/0 | 1 | 0 |
| d | pval_value_o | 0/0 | 1 | 0 |
| d | n_r | 0/0 | 1 | 0 |
| d | es_value_r | 0/0 | 1 | 0 |
| d | pval_value_r | 0/0 | 1 | 0 |
| d | reported_success | 0/0 | 1 | 0 |
| datareplicada | n_o | 0/0 | 17 | 0 |
| datareplicada | es_value_o | 0/0 | 17 | 0 |
| datareplicada | pval_value_o | 0/0 | 17 | 0 |
| datareplicada | n_r | 0/0 | 17 | 0 |
| datareplicada | es_value_r | 0/0 | 17 | 0 |
| datareplicada | pval_value_r | 0/0 | 17 | 0 |
| datareplicada | reported_success | 0/0 | 17 | 0 |
| dqv | n_o | 0/0 | 3 | 0 |
| dqv | es_value_o | 0/0 | 3 | 0 |
| dqv | pval_value_o | 0/0 | 3 | 0 |
| dqv | n_r | 0/0 | 3 | 0 |
| dqv | es_value_r | 0/0 | 3 | 0 |
| dqv | pval_value_r | 0/0 | 3 | 0 |
| dqv | reported_success | 0/0 | 3 | 0 |
| e | n_o | 0/0 | 15 | 0 |
| e | es_value_o | 0/0 | 15 | 0 |
| e | pval_value_o | 0/0 | 15 | 0 |
| e | n_r | 0/0 | 15 | 0 |
| e | es_value_r | 0/0 | 15 | 0 |
| e | pval_value_r | 0/0 | 15 | 0 |
| e | reported_success | 0/0 | 15 | 0 |
| eOQm | n_o | 0/0 | 1 | 0 |
| eOQm | es_value_o | 0/0 | 1 | 0 |
| eOQm | pval_value_o | 0/0 | 1 | 0 |
| eOQm | n_r | 0/0 | 1 | 0 |
| eOQm | es_value_r | 0/0 | 1 | 0 |
| eOQm | pval_value_r | 0/0 | 1 | 0 |
| eOQm | reported_success | 0/0 | 1 | 0 |
| eg | n_o | 0/0 | 2 | 0 |
| eg | es_value_o | 0/0 | 2 | 0 |
| eg | pval_value_o | 0/0 | 2 | 0 |
| eg | n_r | 0/0 | 2 | 0 |
| eg | es_value_r | 0/0 | 2 | 0 |
| eg | pval_value_r | 0/0 | 2 | 0 |
| eg | reported_success | 0/0 | 2 | 0 |
| exd | n_o | 0/0 | 1 | 0 |
| exd | es_value_o | 0/0 | 1 | 0 |
| exd | pval_value_o | 0/0 | 1 | 0 |
| exd | n_r | 0/0 | 1 | 0 |
| exd | es_value_r | 0/0 | 1 | 0 |
| exd | pval_value_r | 0/0 | 1 | 0 |
| exd | reported_success | 0/0 | 1 | 0 |
| fmd | n_o | 0/0 | 1 | 0 |
| fmd | es_value_o | 0/0 | 1 | 0 |
| fmd | pval_value_o | 0/0 | 1 | 0 |
| fmd | n_r | 0/0 | 1 | 0 |
| fmd | es_value_r | 0/0 | 1 | 0 |
| fmd | pval_value_r | 0/0 | 1 | 0 |
| fmd | reported_success | 0/0 | 1 | 0 |
| gRWz | n_o | 0/0 | 1 | 0 |
| gRWz | es_value_o | 0/0 | 1 | 0 |
| gRWz | pval_value_o | 0/0 | 1 | 0 |
| gRWz | n_r | 0/0 | 1 | 0 |
| gRWz | es_value_r | 0/0 | 1 | 0 |
| gRWz | pval_value_r | 0/0 | 1 | 0 |
| gRWz | reported_success | 0/0 | 1 | 0 |
| gea | n_o | 0/0 | 1 | 0 |
| gea | es_value_o | 0/0 | 1 | 0 |
| gea | pval_value_o | 0/0 | 1 | 0 |
| gea | n_r | 0/0 | 1 | 0 |
| gea | es_value_r | 0/0 | 1 | 0 |
| gea | pval_value_r | 0/0 | 1 | 0 |
| gea | reported_success | 0/0 | 1 | 0 |
| gh | n_o | 0/0 | 3 | 0 |
| gh | es_value_o | 0/0 | 3 | 0 |
| gh | pval_value_o | 0/0 | 3 | 0 |
| gh | n_r | 0/0 | 3 | 0 |
| gh | es_value_r | 0/0 | 3 | 0 |
| gh | pval_value_r | 0/0 | 3 | 0 |
| gh | reported_success | 0/0 | 3 | 0 |
| is | n_o | 0/0 | 3 | 0 |
| is | es_value_o | 0/0 | 3 | 0 |
| is | pval_value_o | 0/0 | 3 | 0 |
| is | n_r | 0/0 | 3 | 0 |
| is | es_value_r | 0/0 | 3 | 0 |
| is | pval_value_r | 0/0 | 3 | 0 |
| is | reported_success | 0/0 | 3 | 0 |
| j | n_o | 0/0 | 8 | 0 |
| j | es_value_o | 0/0 | 8 | 0 |
| j | pval_value_o | 0/0 | 8 | 0 |
| j | n_r | 0/0 | 8 | 0 |
| j | es_value_r | 0/0 | 8 | 0 |
| j | pval_value_r | 0/0 | 8 | 0 |
| j | reported_success | 0/0 | 8 | 0 |
| jLr | n_o | 0/0 | 1 | 0 |
| jLr | es_value_o | 0/0 | 1 | 0 |
| jLr | pval_value_o | 0/0 | 1 | 0 |
| jLr | n_r | 0/0 | 1 | 0 |
| jLr | es_value_r | 0/0 | 1 | 0 |
| jLr | pval_value_r | 0/0 | 1 | 0 |
| jLr | reported_success | 0/0 | 1 | 0 |
| jcre | n_o | 0/0 | 71 | 0 |
| jcre | es_value_o | 0/0 | 71 | 0 |
| jcre | pval_value_o | 0/0 | 71 | 0 |
| jcre | n_r | 0/0 | 71 | 0 |
| jcre | es_value_r | 0/0 | 71 | 0 |
| jcre | pval_value_r | 0/0 | 71 | 0 |
| jcre | reported_success | 0/0 | 71 | 0 |
| kXp | n_o | 0/0 | 1 | 0 |
| kXp | es_value_o | 0/0 | 1 | 0 |
| kXp | pval_value_o | 0/0 | 1 | 0 |
| kXp | n_r | 0/0 | 1 | 0 |
| kXp | es_value_r | 0/0 | 1 | 0 |
| kXp | pval_value_r | 0/0 | 1 | 0 |
| kXp | reported_success | 0/0 | 1 | 0 |
| lJ | n_o | 0/0 | 1 | 0 |
| lJ | es_value_o | 0/0 | 1 | 0 |
| lJ | pval_value_o | 0/0 | 1 | 0 |
| lJ | n_r | 0/0 | 1 | 0 |
| lJ | es_value_r | 0/0 | 1 | 0 |
| lJ | pval_value_r | 0/0 | 1 | 0 |
| lJ | reported_success | 0/0 | 1 | 0 |
| mBL | n_o | 0/0 | 1 | 0 |
| mBL | es_value_o | 0/0 | 1 | 0 |
| mBL | pval_value_o | 0/0 | 1 | 0 |
| mBL | n_r | 0/0 | 1 | 0 |
| mBL | es_value_r | 0/0 | 1 | 0 |
| mBL | pval_value_r | 0/0 | 1 | 0 |
| mBL | reported_success | 0/0 | 1 | 0 |
| mJDj | n_o | 0/0 | 1 | 0 |
| mJDj | es_value_o | 0/0 | 1 | 0 |
| mJDj | pval_value_o | 0/0 | 1 | 0 |
| mJDj | n_r | 0/0 | 1 | 0 |
| mJDj | es_value_r | 0/0 | 1 | 0 |
| mJDj | pval_value_r | 0/0 | 1 | 0 |
| mJDj | reported_success | 0/0 | 1 | 0 |
| mxyQ | n_o | 0/0 | 1 | 0 |
| mxyQ | es_value_o | 0/0 | 1 | 0 |
| mxyQ | pval_value_o | 0/0 | 1 | 0 |
| mxyQ | n_r | 0/0 | 1 | 0 |
| mxyQ | es_value_r | 0/0 | 1 | 0 |
| mxyQ | pval_value_r | 0/0 | 1 | 0 |
| mxyQ | reported_success | 0/0 | 1 | 0 |
| odonnell | n_o | 0/0 | 6 | 0 |
| odonnell | es_value_o | 0/0 | 6 | 0 |
| odonnell | pval_value_o | 0/0 | 6 | 0 |
| odonnell | n_r | 0/0 | 6 | 0 |
| odonnell | es_value_r | 0/0 | 6 | 0 |
| odonnell | pval_value_r | 0/0 | 6 | 0 |
| odonnell | reported_success | 0/0 | 6 | 0 |
| osc | n_o | 0/0 | 99 | 0 |
| osc | es_value_o | 0/0 | 99 | 0 |
| osc | pval_value_o | 0/0 | 99 | 0 |
| osc | n_r | 0/0 | 99 | 0 |
| osc | es_value_r | 0/0 | 99 | 0 |
| osc | pval_value_r | 0/1 | 98 | 0 |
| osc | reported_success | 0/1 | 98 | 0 |
| plLK | n_o | 0/0 | 1 | 0 |
| plLK | es_value_o | 0/0 | 1 | 0 |
| plLK | pval_value_o | 0/0 | 1 | 0 |
| plLK | n_r | 0/0 | 1 | 0 |
| plLK | es_value_r | 0/0 | 1 | 0 |
| plLK | pval_value_r | 0/0 | 1 | 0 |
| plLK | reported_success | 0/0 | 1 | 0 |
| q | n_o | 0/0 | 5 | 0 |
| q | es_value_o | 0/0 | 5 | 0 |
| q | pval_value_o | 0/0 | 5 | 0 |
| q | n_r | 0/0 | 5 | 0 |
| q | es_value_r | 0/0 | 5 | 0 |
| q | pval_value_r | 0/0 | 5 | 0 |
| q | reported_success | 0/0 | 5 | 0 |
| qXX | n_o | 0/0 | 1 | 0 |
| qXX | es_value_o | 0/0 | 1 | 0 |
| qXX | pval_value_o | 0/0 | 1 | 0 |
| qXX | n_r | 0/0 | 1 | 0 |
| qXX | es_value_r | 0/0 | 1 | 0 |
| qXX | pval_value_r | 0/0 | 1 | 0 |
| qXX | reported_success | 0/0 | 1 | 0 |
| qYr | n_o | 0/0 | 3 | 0 |
| qYr | es_value_o | 0/0 | 3 | 0 |
| qYr | pval_value_o | 0/0 | 3 | 0 |
| qYr | n_r | 0/0 | 3 | 0 |
| qYr | es_value_r | 0/0 | 3 | 0 |
| qYr | pval_value_r | 0/0 | 3 | 0 |
| qYr | reported_success | 0/0 | 3 | 0 |
| qgWj | n_o | 0/0 | 4 | 0 |
| qgWj | es_value_o | 0/0 | 4 | 0 |
| qgWj | pval_value_o | 0/0 | 4 | 0 |
| qgWj | n_r | 0/0 | 4 | 0 |
| qgWj | es_value_r | 0/0 | 4 | 0 |
| qgWj | pval_value_r | 0/0 | 4 | 0 |
| qgWj | reported_success | 0/0 | 4 | 0 |
| resciencex | n_o | 0/0 | 8 | 0 |
| resciencex | es_value_o | 0/0 | 8 | 0 |
| resciencex | pval_value_o | 0/0 | 8 | 0 |
| resciencex | n_r | 0/0 | 8 | 0 |
| resciencex | es_value_r | 0/0 | 8 | 0 |
| resciencex | pval_value_r | 0/0 | 8 | 0 |
| resciencex | reported_success | 0/0 | 8 | 0 |
| rpq | n_o | 0/0 | 1 | 0 |
| rpq | es_value_o | 0/0 | 1 | 0 |
| rpq | pval_value_o | 0/0 | 1 | 0 |
| rpq | n_r | 0/0 | 1 | 0 |
| rpq | es_value_r | 0/0 | 1 | 0 |
| rpq | pval_value_r | 0/0 | 1 | 0 |
| rpq | reported_success | 0/0 | 1 | 0 |
| rtn | n_o | 0/0 | 1 | 0 |
| rtn | es_value_o | 0/0 | 1 | 0 |
| rtn | pval_value_o | 0/0 | 1 | 0 |
| rtn | n_r | 0/0 | 1 | 0 |
| rtn | es_value_r | 0/0 | 1 | 0 |
| rtn | pval_value_r | 0/0 | 1 | 0 |
| rtn | reported_success | 0/0 | 1 | 0 |
| shah | n_o | 0/0 | 13 | 0 |
| shah | es_value_o | 0/1 | 12 | 0 |
| shah | pval_value_o | 0/1 | 12 | 0 |
| shah | n_r | 0/2 | 11 | 0 |
| shah | es_value_r | 0/1 | 12 | 0 |
| shah | pval_value_r | 0/1 | 12 | 0 |
| shah | reported_success | 0/1 | 12 | 0 |
| soscisubmission | n_o | 0/0 | 129 | 0 |
| soscisubmission | es_value_o | 0/0 | 129 | 0 |
| soscisubmission | pval_value_o | 0/0 | 129 | 0 |
| soscisubmission | n_r | 0/1 | 128 | 0 |
| soscisubmission | es_value_r | 0/3 | 126 | 0 |
| soscisubmission | pval_value_r | 0/3 | 126 | 0 |
| soscisubmission | reported_success | 0/1 | 128 | 0 |
| svodevelopment | n_o | 0/0 | 7 | 0 |
| svodevelopment | es_value_o | 0/0 | 7 | 0 |
| svodevelopment | pval_value_o | 0/0 | 7 | 0 |
| svodevelopment | n_r | 0/0 | 7 | 0 |
| svodevelopment | es_value_r | 0/0 | 7 | 0 |
| svodevelopment | pval_value_r | 0/0 | 7 | 0 |
| svodevelopment | reported_success | 0/0 | 7 | 0 |
| uxajg | n_o | 0/0 | 1 | 0 |
| uxajg | es_value_o | 0/0 | 1 | 0 |
| uxajg | pval_value_o | 0/0 | 1 | 0 |
| uxajg | n_r | 0/0 | 1 | 0 |
| uxajg | es_value_r | 0/0 | 1 | 0 |
| uxajg | pval_value_r | 0/0 | 1 | 0 |
| uxajg | reported_success | 0/0 | 1 | 0 |
| vGqL | n_o | 0/0 | 1 | 0 |
| vGqL | es_value_o | 0/0 | 1 | 0 |
| vGqL | pval_value_o | 0/0 | 1 | 0 |
| vGqL | n_r | 0/0 | 1 | 0 |
| vGqL | es_value_r | 0/0 | 1 | 0 |
| vGqL | pval_value_r | 0/0 | 1 | 0 |
| vGqL | reported_success | 0/0 | 1 | 0 |
| w | n_o | 0/0 | 2 | 0 |
| w | es_value_o | 0/0 | 2 | 0 |
| w | pval_value_o | 0/0 | 2 | 0 |
| w | n_r | 0/0 | 2 | 0 |
| w | es_value_r | 0/0 | 2 | 0 |
| w | pval_value_r | 0/0 | 2 | 0 |
| w | reported_success | 0/0 | 2 | 0 |
| wRvv | n_o | 0/0 | 2 | 0 |
| wRvv | es_value_o | 0/0 | 2 | 0 |
| wRvv | pval_value_o | 0/0 | 2 | 0 |
| wRvv | n_r | 0/0 | 2 | 0 |
| wRvv | es_value_r | 0/0 | 2 | 0 |
| wRvv | pval_value_r | 0/0 | 2 | 0 |
| wRvv | reported_success | 0/0 | 2 | 0 |
| x | n_o | 0/0 | 2 | 0 |
| x | es_value_o | 0/0 | 2 | 0 |
| x | pval_value_o | 0/0 | 2 | 0 |
| x | n_r | 0/0 | 2 | 0 |
| x | es_value_r | 0/0 | 2 | 0 |
| x | pval_value_r | 0/0 | 2 | 0 |
| x | reported_success | 0/0 | 2 | 0 |
| xYbO | n_o | 0/0 | 1 | 0 |
| xYbO | es_value_o | 0/0 | 1 | 0 |
| xYbO | pval_value_o | 0/0 | 1 | 0 |
| xYbO | n_r | 0/0 | 1 | 0 |
| xYbO | es_value_r | 0/0 | 1 | 0 |
| xYbO | pval_value_r | 0/0 | 1 | 0 |
| xYbO | reported_success | 0/0 | 1 | 0 |
| xszk | n_o | 0/0 | 2 | 0 |
| xszk | es_value_o | 0/0 | 2 | 0 |
| xszk | pval_value_o | 0/0 | 2 | 0 |
| xszk | n_r | 0/0 | 2 | 0 |
| xszk | es_value_r | 0/0 | 2 | 0 |
| xszk | pval_value_r | 0/0 | 2 | 0 |
| xszk | reported_success | 0/0 | 2 | 0 |
| yAPR | n_o | 0/0 | 1 | 0 |
| yAPR | es_value_o | 0/0 | 1 | 0 |
| yAPR | pval_value_o | 0/0 | 1 | 0 |
| yAPR | n_r | 0/0 | 1 | 0 |
| yAPR | es_value_r | 0/0 | 1 | 0 |
| yAPR | pval_value_r | 0/0 | 1 | 0 |
| yAPR | reported_success | 0/0 | 1 | 0 |
| yypJ | n_o | 0/0 | 1 | 0 |
| yypJ | es_value_o | 0/0 | 1 | 0 |
| yypJ | pval_value_o | 0/0 | 1 | 0 |
| yypJ | n_r | 0/0 | 1 | 0 |
| yypJ | es_value_r | 0/0 | 1 | 0 |
| yypJ | pval_value_r | 0/0 | 1 | 0 |
| yypJ | reported_success | 0/0 | 1 | 0 |
| zK | n_o | 0/0 | 1 | 0 |
| zK | es_value_o | 0/0 | 1 | 0 |
| zK | pval_value_o | 0/0 | 1 | 0 |
| zK | n_r | 0/0 | 1 | 0 |
| zK | es_value_r | 0/0 | 1 | 0 |
| zK | pval_value_r | 0/0 | 1 | 0 |
| zK | reported_success | 0/0 | 1 | 0 |
| zNEm | n_o | 0/0 | 1 | 0 |
| zNEm | es_value_o | 0/0 | 1 | 0 |
| zNEm | pval_value_o | 0/0 | 1 | 0 |
| zNEm | n_r | 0/0 | 1 | 0 |
| zNEm | es_value_r | 0/0 | 1 | 0 |
| zNEm | pval_value_r | 0/0 | 1 | 0 |
| zNEm | reported_success | 0/0 | 1 | 0 |
| zb | n_o | 0/0 | 4 | 0 |
| zb | es_value_o | 0/0 | 4 | 0 |
| zb | pval_value_o | 0/0 | 4 | 0 |
| zb | n_r | 0/0 | 4 | 0 |
| zb | es_value_r | 0/0 | 4 | 0 |
| zb | pval_value_r | 0/0 | 4 | 0 |
| zb | reported_success | 0/0 | 4 | 0 |
| zlBL | n_o | 0/0 | 3 | 0 |
| zlBL | es_value_o | 0/0 | 3 | 0 |
| zlBL | pval_value_o | 0/0 | 3 | 0 |
| zlBL | n_r | 0/0 | 3 | 0 |
| zlBL | es_value_r | 0/0 | 3 | 0 |
| zlBL | pval_value_r | 0/0 | 3 | 0 |
| zlBL | reported_success | 0/0 | 3 | 0 |
| zlm | n_o | 0/0 | 1 | 0 |
| zlm | es_value_o | 0/0 | 1 | 0 |
| zlm | pval_value_o | 0/0 | 1 | 0 |
| zlm | n_r | 0/0 | 1 | 0 |
| zlm | es_value_r | 0/0 | 1 | 0 |
| zlm | pval_value_r | 0/0 | 1 | 0 |
| zlm | reported_success | 0/0 | 1 | 0 |
| zmYY | n_o | 0/0 | 1 | 0 |
| zmYY | es_value_o | 0/0 | 1 | 0 |
| zmYY | pval_value_o | 0/0 | 1 | 0 |
| zmYY | n_r | 0/0 | 1 | 0 |
| zmYY | es_value_r | 0/0 | 1 | 0 |
| zmYY | pval_value_r | 0/0 | 1 | 0 |
| zmYY | reported_success | 0/0 | 1 | 0 |

## Confirmed errors

- Effect row 100, `n_r`: `229` → `16`. Results, Correlation between MA and the misinformation effect change at the item level, p. 22, Footnote 9. The target effect is an item-level correlation (r = -.385, p = .07, one-tailed) between misinformation availability and net change in the misinformation effect (misinformation endorsement operationalization). Footnote 9 explicitly states that the correlation is computed across 16 item-by-condition data points (8 critical items across 2 MA conditions, df = 14), whereas the shipped value (229) is the total participant count before aggregation to the item level. [Paper](https://doi.org/10.1002/acp.4202).
- Effect row 101, `n_r`: `229` → `16`. Results, Correlation between MA and the misinformation effect change at the item level, p. 22, Footnote 9. The target effect is an item-level correlation (r = -.57, p = .01, one-tailed) between misinformation availability and net change in the misinformation effect (accuracy operationalization). Footnote 9 explicitly states that the correlation is based on 16 item-by-condition data points (8 critical items across 2 MA conditions, df = 14), whereas the shipped value (229) is the total number of participants in the experiment rather than the sample size of the correlation. [Paper](https://doi.org/10.1002/acp.4202).
- Effect row 380, `n_r`: `64` → `4`. Pilot Samples; Results, Transforming data from JSON format to dataframe; Discussion, Summary of Replication Attempt. The target RPubs replication report analyzes 4 pilot participants (length(unique(d.raw$workerid)) = 4). The shipped value of 64 confuses the number of participants (4) with the total number of trait-rating observations across the 16 traits (4 participants x 16 traits = 64 observations; 'Number of obs: 64, groups: workerid, 4'). [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 380, `es_value_r`: `F(1, 56) = 57.800` → `F(1, 2) = 57.800`. Confirmatory analysis, Main Data analysis: Mixed model ANOVA (lines 294-309). In the mixed-model ANOVA table under the 'Error: workerid:traitType' stratum, the main effect of traitType has numerator df = 1, denominator (Residuals) df = 2, and F = 57.800 (also reported in the text at line 309 as 'F(1,2)=57.80'). Shipped erroneously took df2 = 56 from the 'Error: Within' residual stratum below. [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 381, `pval_value_o`: `0.84` → `.084`. p. 1754, Study 1 Results. Visible decimal transcription slip: Study 1 condition × trait-type interaction is printed F(1,78)=3.05, p=.084, partial eta-squared=.04; shipped effect .04 matches but p=.84 omits a zero. [Paper](https://doi.org/10.1177/0956797615598739).
- Effect row 381, `n_r`: `64` → `4`. Pilot Samples; Results, Transforming data from JSON format to dataframe; Discussion, Summary of Replication Attempt. The mixed-model ANOVA testing the traitType:condition interaction was conducted on 4 pilot participants (length(unique(d.raw$workerid)) = 4). The shipped value of 64 is the total number of trait-rating observations (4 participants x 16 traits = 64 observations; 'Number of obs: 64, groups: workerid, 4'). [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 381, `es_value_r`: `F(1, 56) = 0.022` → `F(1, 2) = 0.022`. Confirmatory analysis, Main Data analysis: Mixed model ANOVA (lines 294-298). In the mixed-model ANOVA table under the 'Error: workerid:traitType' stratum, the traitType:condition interaction has numerator df = 1, denominator (Residuals) df = 2, and F = 0.022 (p = 0.8952). Shipped erroneously took df2 = 56 from the 'Error: Within' residual stratum below. [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 381, `reported_success`: `successful` → `failed`. Confirmatory analysis; Discussion, Summary of Replication Attempt. For the interaction between trait type and thinking condition (F(1, 2) = 0.022, p = 0.8952), the author explicitly reports that unlike the original study, there was no marginal interaction effect and changing the definition of creativity did not attenuate the gender bias. [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 382, `reported_success`: `successful` → `descriptive only`. Confirmatory analysis, Follow up data analyses; Discussion, Summary of Replication Attempt. For the within-condition comparison of masculine versus feminine traits in the divergent-thinking condition (F(1, 2) = 69.44, p = 0.076, d = 0.73), the author states that the direction of the data aligned with the original study descriptively, but unlike the original study, the difference did not reach statistical significance. [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 383, `reported_success`: `successful` → `descriptive only`. Confirmatory analysis, Follow up data analyses; Discussion, Summary of Replication Attempt. For the within-condition comparison of masculine versus feminine traits in the convergent-thinking condition (F(1, 2) = 18.78, p = 0.144, d = 0.97), the author states that the descriptive direction aligned with the original study, but unlike the original study, the difference did not reach statistical significance. [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 384, `n_r`: `64` → `4`. Pilot Samples; Results, Transforming data from JSON format to dataframe; Discussion, Summary of Replication Attempt. The study sample comprises 4 pilot participants (32 masculine trait ratings across the 4 participants x 8 masculine traits in fitMasculine). The shipped value of 64 is the total number of trait-rating observations across all 16 traits ('Number of obs: 64, groups: workerid, 4'). [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 384, `reported_success`: `successful` → `failed`. Confirmatory analysis, Follow up data analyses: trait type rating between conditions. The author explicitly states that unlike the original study, thinking condition (divergent vs. convergent) had no effect on the perceived centrality of masculine traits to creativity. [Paper](https://doi.org/10.1098/rsos.231240).
- Effect row 385, `n_r`: `64` → `4`. Pilot Samples; Results, Transforming data from JSON format to dataframe; Discussion, Summary of Replication Attempt. The study sample comprises 4 pilot participants (32 feminine trait ratings across the 4 participants x 8 feminine traits in fitFeminine). The shipped value of 64 is the total number of trait-rating observations across all 16 traits ('Number of obs: 64, groups: workerid, 4'). [Paper](https://doi.org/10.1098/rsos.231240).

## Unverified and skipped work

1977 effects have no paper checkpoint yet. A checkpoint with unavailable or insufficient fields is not a verified effect.

- original: done: 143 sides.
- original: locator_insufficient: 33 sides.
- original: paper_unavailable: 35 sides.
- replication: done: 151 sides.
- replication: locator_insufficient: 49 sides.
- replication: paper_unavailable: 11 sides.

Detailed access/target reasons are retained in the per-effect JSON checkpoints. Frequent reasons at this checkpoint:

- 12 sides: Primary original paper not obtained through permitted open-access routes. Locator names p. 7, Table 2 but gives no row, column, outcome, sample, or test identifier.
- 12 sides: Verified Haller, Flaherty and Balsvik (2023), DOI 10.18718/81781.29. Printed p. 24, Table A3 contains log annual wage regressions by high/low unionisation and skill intensity for Brazil, two Irish periods and Norway. PDF page 24 instead is printed p. 23, Table A2 with four specifications and those country/period panels. Neither interpretation selects one target test.
- 7 sides: Original paper reference supplied, but study, outcome, sample and test are unspecified; no neutral description or locator supplied.
- 7 sides: No replication reference, DOI, URL, study identifier, description or locator supplied.
- 6 sides: Full paper not acquired; the supplied general description and p.4 locator do not independently identify a specific test. No test-level values extracted from previews or abstracts.
- 6 sides: Experiment 2 focus: first shot of each level, very first shot of game, and points per shot among nonborrowers are distinct candidate tests.
- 3 sides: Original Study 1 full paper could not be acquired through permitted open-access routes.
- 3 sides: Movement onset and object contact each have movement-direction/object analyses; description does not uniquely identify the response-time phase and test.
- 3 sides: p. 5 contains distinct stimulus-by-direction tests for movement onset and contact; supplied description does not distinguish them.
- 3 sides: Matching original-paper bibliographic title verified; full paper could not be acquired within acquisition allowance.
- 3 sides: Original full paper not acquired within the per-paper acquisition window.
- 3 sides: Verified Castro, Hur, and Berenbaum (2022), p. 5, section 4.2 and Table 3: five worry/rumination/reflection models and three nested chi-square comparisons, all for the extension analysis. The assigned description and p. 5 locator do not identify which model or model-comparison test belongs to this audit_id. All three assigned entries have identical study identifiers, descriptions and locators; no mapping can be established independently. No model row or comparison was assigned by input order.
- 3 sides: Liu, Wright, Cole, and Warren (2024), title verified using publisher metadata, Unpaywall and OpenAlex. Full paper could not be acquired through permitted open-access routes within the per-paper acquisition limit. Publisher exposes an article preview and section snippets, not complete p. 3 or Table 1; no target-test extraction from snippets.
- 2 sides: Experiment 1 job-choice decoy effect. Section 2.2.1 reports separate exact-binomial tests for Control and Regret-Salient participants, plus a between-condition Fisher exact test. The supplied description and page locator do not select one of these tests.
- 2 sides: Study 2 replication of Connolly et al. Experiment 1. Confirmatory analysis reports separate exact-binomial tests against .5 for Control and Regret-Salient conditions; a separate Fisher exact test compares these conditions. The supplied locator does not identify which condition/test is assigned. The author final preprint has different pagination: its p.18 belongs to Study 1, whereas Study 2 decoy results are pp.35–38.

## Method and limits

Extraction workers received references, studies, neutral descriptions, requested metric labels, and sanitized page/table/primary-source URLs, with no shipped n, estimates, p-values or success verdicts. The first 20 sanitized descriptions and later batch samples were inspected. Original and replication statistics were extracted separately, with printed metric and bound type. Comparisons require confident matching targets and validated source quotes. Non-obvious disagreements go to Gemini 4 Argon (High); obvious decisions retain a reason and evidence location.

The screen checks positive-integer n, p and r ranges, recognized F/t/chi-square/z reports, and non-nested Pearson r with coded analytic n. Missing tails are labelled as an assumed two-sided screen. The codebook does not enumerate every allowed metric, so unfamiliar labels are not declared invalid. No source-project success rule has been established for automatic significance/direction checks. Rounding intervals use stored cell strings; XLSX may already have lost printed precision.

Frozen input SHA256: `59545e3fc0c2979d97507097526319ec8c275aae3ac40c0d1a6d327492079e6b`. No dataset changes are made. Full texts are excluded from Git. See `run_log.md`, `consistency.csv`, `results.csv` and `extractions/` for decisions, diagnostics and short evidence quotes.
