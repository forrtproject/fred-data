# FReD statistics audit

**Drive follow-up completed — 2026-10-30T19:15:42.671196+00:00.** Current integrated results contain 493 confirmed field errors. Retrieval alone is not verification.

The original bounded audit finished on 2026-10-29T18:41:45.057314+00:00 with 408 confirmed field errors across 315 rows, 1593 effects with at least one verified field and 81 with all seven. A separately authorised source-acquisition follow-up is recorded in [source_followup/README.md](source_followup/README.md). Current counts below include only integrated, evidence-validated follow-up results; the original deadlines and completion record are unchanged. A further separately authorised Mac recovery pass starts from 416 confirmed errors across 322 rows and 1,605 effects with any verified field. Its acquisition receipts, protected blind validation batches and independent reviews are in [mac_source_followup/README.md](mac_source_followup/README.md). The completed Linux follow-up and original audit deadlines remain historical; neither schedule was restarted. The Mac pass recovered 58 full articles; its integrated checks added 244 verified field instances, including 17 confirmed errors, relative to the pre-Mac checkpoint. See [Mac recovery findings](mac_source_followup/REPORT.md). A separately authorised Mac continuation starts from 433 confirmed errors. Its received 43 primary texts added 126 verified field instances, including 8 confirmed errors. Acquisition status is complete; acquisition ended at 12:40:14 UTC on 30 October 2026 after all 137 remaining groups were assessed (43 recovered, 94 unrecovered). See [continuation findings](mac_continuation_followup/REPORT.md). The separately authorised Drive check supplied 129 further complete primary sources, bringing exact source coverage to 248/255 initially missing source groups. Its latest comparison adds 594 verified field instances and 52 confirmed errors relative to the 441-error pre-Drive baseline. Targeted validation remains complete. See [Drive follow-up findings](drive_source_followup/REPORT.md).

Complete verification of all six numeric fields covers 147/2164 effects (6.8%); all seven fields cover 112/2164 (5.2%). Complete-effect verification remains below the 80% goal. Any-field coverage counts an effect when only one of its fields has been verified.

Confirmed errors affect 381 effect rows. Counts refer to field instances; an original statistic repeated across replication rows can contribute more than once.

The frozen workbook contains 2,164 effects in 432 replication works. Part A screened every effect and flagged 174. 19/185 individual flags are resolved when source-confirmed corrections are applied in memory, affecting 19/174 flagged effects (see `flag_confirmation.csv`). This includes corrected test statistics or analytic n as well as p-values. Separately, 55 flagged effects contain any confirmed field error.

Paper checkpoints exist for 2164/2164 effects. All three original statistics are evaluable for 334/2164; all three replication statistics for 498/2164. All seven fields, including author-reported success, are checked for 112/2164. At least one original statistic is evaluable for 1237/2164, at least one replication statistic for 1346/2164, and any of the seven fields for 1765/2164. Individual-field coverage is below.

**Decision to review:** reported success is evaluated for the identified study/outcome. A broad paper-level verdict without a defensible mapping to an individual row remains unverified; the original narrative observation is retained. This conservative scope rule avoids assigning a mixed article outcome to every unidentified component effect.

Confirmed errors include coding omissions only when adjudication establishes the requested statistic from the matching primary source; their count is reported separately. Coverage depends on paper access and target identification. These results are not a representative sample of FReD. Bounds below describe remaining identification uncertainty, not binomial sampling intervals. Different metrics remain not comparable unless a documented transformation is reproduced.

| Field | Confirmed errors / evaluable | Unverified | Not comparable | All-row error bounds |
|---|---:|---:|---:|---:|
| n_o | 57/708 (8.1%) | 1386 | 70 | 2.63%–69.92% |
| es_value_o | 49/705 (7.0%) | 1075 | 384 | 2.26%–69.69% |
| pval_value_o | 36/1005 (3.6%) | 1152 | 7 | 1.66%–55.22% |
| n_r | 92/1010 (9.1%) | 1082 | 72 | 4.25%–57.58% |
| es_value_r | 38/793 (4.8%) | 1034 | 337 | 1.76%–65.11% |
| pval_value_r | 79/1067 (7.4%) | 1087 | 10 | 3.65%–54.34% |
| reported_success | 142/1123 (12.6%) | 1041 | 0 | 6.56%–54.67% |

Provenance-prefix breakdown uses text before the first underscore in `fred_id` (preserving project years); legacy codes without underscores use leading letters, with literal ManyLabs1–6 preserved; `fred_id` is provenance, not an effect key. Each cell gives **errors/evaluable (unverified; not comparable)**. The complete machine-readable rates, denominators and uncertainty bounds are in [field_summary_by_project.csv](field_summary_by_project.csv).

| Project prefix | Original n | Original ES | Original p | Replication n | Replication ES | Replication p | Success |
|---|---|---|---|---|---|---|---|
| (missing) | 0/1 (4; 0) | 0/0 (4; 1) | 0/0 (4; 1) | 0/0 (5; 0) | 0/0 (4; 1) | 1/1 (4; 0) | 0/1 (4; 0) |
| (unprefixed) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) |
| 0qar | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| 1X9W | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| 2GKO | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| 2lb5 | 0/0 (1; 0) | 0/0 (0; 1) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| 5JE | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| 5Kgq | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| 5KrD | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| 5XEE | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| 7RR2 | 0/0 (8; 0) | 0/1 (7; 0) | 0/1 (7; 0) | 0/0 (8; 0) | 0/0 (7; 1) | 0/1 (7; 0) | 0/1 (7; 0) |
| 7X54 | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| 88xa | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) |
| 8w97 | 0/0 (0; 1) | 0/0 (1; 0) | 1/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| 8wZ0 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| 9OK1 | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) |
| AOQj | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) |
| AYQG | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| AgO1 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| AqDO | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| Arb | 0/5 (27; 0) | 0/16 (13; 3) | 0/9 (23; 0) | 0/6 (22; 4) | 0/3 (27; 2) | 0/6 (26; 0) | 0/19 (13; 0) |
| AvOr | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| Blxd | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) |
| Boyce | 7/112 (162; 6) | 3/120 (119; 41) | 6/157 (123; 0) | 24/186 (94; 0) | 8/131 (108; 41) | 13/163 (117; 0) | 31/156 (124; 0) |
| Br0x | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| BrGp | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) |
| CORE | 3/45 (66; 3) | 3/29 (73; 12) | 4/53 (61; 0) | 7/62 (42; 10) | 6/50 (48; 16) | 12/69 (45; 0) | 8/75 (39; 0) |
| Camereretal2016 | 0/0 (18; 0) | 0/0 (18; 0) | 0/0 (18; 0) | 0/0 (18; 0) | 0/2 (3; 13) | 0/15 (3; 0) | 0/0 (18; 0) |
| Camereretal2018 | 0/2 (15; 4) | 1/4 (11; 6) | 0/9 (12; 0) | 1/21 (0; 0) | 0/17 (0; 4) | 1/21 (0; 0) | 0/6 (15; 0) |
| D2LY | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| DEqr | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| Data (editable) | 0/0 (3; 0) | 0/1 (1; 1) | 1/1 (2; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| E5qr | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| EJpm | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| EKBZ | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/0 (1; 0) |
| EQxa | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| Eb2N | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| FORRT | 0/20 (4; 0) | 0/18 (6; 0) | 0/20 (4; 0) | 0/4 (5; 15) | 0/17 (5; 2) | 0/4 (20; 0) | 0/6 (18; 0) |
| G1Lr | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| GXEW | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| Holzmeisteretal2024 | 1/10 (16; 0) | 0/8 (14; 4) | 1/14 (11; 1) | 0/26 (0; 0) | 0/26 (0; 0) | 1/26 (0; 0) | 0/26 (0; 0) |
| JRpA | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) |
| Keith | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) |
| Kybl | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| LbEB | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| LmBx | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) |
| LyLd | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| ManyLabs4 | 0/0 (15; 3) | 0/0 (18; 0) | 0/0 (18; 0) | 0/1 (14; 3) | 0/18 (0; 0) | 0/18 (0; 0) | 0/4 (14; 0) |
| ManyLabs5 | 0/10 (10; 0) | 0/12 (7; 1) | 0/13 (7; 0) | 0/20 (0; 0) | 0/20 (0; 0) | 0/14 (6; 0) | 0/10 (10; 0) |
| Manylabs2 | 1/20 (12; 6) | 1/24 (7; 7) | 0/31 (7; 0) | 2/29 (9; 0) | 0/38 (0; 0) | 1/31 (7; 0) | 5/28 (10; 0) |
| N8pB | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| OKRy | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| OYX0 | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| OeGv | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| OpenMKT | 2/47 (54; 0) | 2/51 (29; 21) | 2/67 (34; 0) | 0/71 (30; 0) | 0/61 (20; 20) | 2/78 (23; 0) | 7/48 (53; 0) |
| OpenMKT7 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| Ovkm | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) |
| Ow0 | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) |
| Q1dl | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| QllV | 0/0 (1; 0) | 0/0 (0; 1) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| R8RN | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| R9dv | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| RRR | 0/11 (16; 4) | 0/9 (21; 1) | 1/19 (12; 0) | 5/13 (11; 7) | 1/18 (11; 2) | 1/20 (11; 0) | 0/7 (24; 0) |
| RYKv | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/1 (2; 0) |
| RrOb | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| Soto | 0/20 (37; 3) | 0/21 (25; 14) | 2/31 (29; 0) | 0/42 (18; 0) | 6/11 (28; 21) | 11/35 (25; 0) | 0/0 (60; 0) |
| VB9K | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| Vj0p | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| VvZX | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| WLpV | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 1/1 (0; 0) | 0/0 (1; 0) |
| Wre | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| XPHI | 0/22 (44; 3) | 1/22 (45; 2) | 0/25 (44; 0) | 2/33 (34; 2) | 0/28 (32; 9) | 0/39 (30; 0) | 1/53 (16; 0) |
| YWep | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| YpZZ | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| aYyR | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| aag9 | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| acykd | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| add | 3/70 (86; 8) | 4/72 (10; 82) | 1/88 (73; 3) | 3/40 (112; 12) | 2/40 (108; 16) | 1/56 (108; 0) | 20/67 (97; 0) |
| additional | 21/99 (252; 0) | 23/95 (193; 63) | 9/161 (189; 1) | 13/137 (214; 0) | 5/77 (213; 61) | 12/152 (199; 0) | 35/208 (143; 0) |
| av | 2/45 (105; 16) | 4/58 (99; 9) | 3/71 (94; 1) | 6/44 (111; 11) | 0/51 (107; 8) | 0/59 (98; 9) | 10/78 (88; 0) |
| bY2A | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| bth | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) |
| curatescience | 2/14 (56; 7) | 0/14 (49; 14) | 2/30 (47; 0) | 7/28 (49; 0) | 2/31 (37; 9) | 8/40 (37; 0) | 2/26 (51; 0) |
| curatescience241 | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience244 | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience283 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience320 | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 1/1 (0; 0) | 1/1 (0; 0) | 1/1 (0; 0) | 0/1 (0; 0) |
| curatescience365 | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) |
| curatescience395 | 4/4 (0; 0) | 0/0 (0; 4) | 0/0 (4; 0) | 0/4 (0; 0) | 0/4 (0; 0) | 0/4 (0; 0) | 0/4 (0; 0) |
| curatescience46 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| curatescience533 | 1/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 1/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience537 | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience558 | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 1/1 (0; 0) |
| curatescience599 | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience600 | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience620 | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience641 | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience7 | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| curatescience73 | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 1/1 (0; 0) | 0/1 (0; 0) | 1/1 (0; 0) | 0/0 (1; 0) |
| curatescience75 | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 1/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| d24p | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| datareplicada | 0/6 (11; 0) | 3/13 (2; 2) | 0/14 (3; 0) | 0/5 (12; 0) | 1/10 (5; 2) | 1/6 (11; 0) | 2/17 (0; 0) |
| dqv | 0/0 (3; 0) | 0/2 (1; 0) | 0/3 (0; 0) | 0/0 (0; 3) | 0/3 (0; 0) | 3/3 (0; 0) | 0/3 (0; 0) |
| e | 0/0 (13; 0) | 0/0 (13; 0) | 0/0 (13; 0) | 0/0 (13; 0) | 0/13 (0; 0) | 0/13 (0; 0) | 2/13 (0; 0) |
| e227 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) |
| e3G7 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| eOQm | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| eg1q | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| eg3p | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| exd7 | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| fmd | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 1/1 (0; 0) | 1/1 (0; 0) | 1/1 (0; 0) | 0/0 (1; 0) |
| gRWz | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| gea | 1/1 (0; 0) | 1/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) |
| gh | 0/3 (0; 0) | 0/1 (1; 1) | 0/2 (1; 0) | 0/3 (0; 0) | 0/3 (0; 0) | 0/3 (0; 0) | 0/3 (0; 0) |
| is | 0/3 (0; 0) | 0/1 (0; 2) | 0/3 (0; 0) | 0/1 (2; 0) | 0/1 (2; 0) | 0/1 (2; 0) | 0/3 (0; 0) |
| j2yd | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/0 (1; 0) | 0/1 (0; 0) |
| j8a4p | 0/7 (0; 0) | 0/7 (0; 0) | 0/7 (0; 0) | 0/7 (0; 0) | 0/1 (0; 6) | 0/7 (0; 0) | 0/7 (0; 0) |
| jLr | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| jcre | 0/0 (71; 0) | 0/0 (35; 36) | 0/25 (46; 0) | 0/54 (17; 0) | 0/6 (17; 48) | 0/6 (65; 0) | 0/45 (26; 0) |
| kXp8 | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| lJ0w | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| mBL1 | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/0 (1; 0) |
| mJDj | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| mxyQ | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) |
| odonnell | 0/2 (4; 0) | 0/3 (2; 1) | 0/4 (2; 0) | 0/5 (1; 0) | 0/4 (1; 1) | 0/5 (1; 0) | 0/4 (2; 0) |
| osc | 4/37 (60; 2) | 1/34 (54; 11) | 1/34 (65; 0) | 0/25 (73; 1) | 0/15 (80; 4) | 1/21 (78; 0) | 1/50 (49; 0) |
| plLK | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| q | 0/1 (1; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 2/2 (0; 0) | 2/2 (0; 0) | 1/2 (0; 0) | 0/2 (0; 0) |
| q8xv | 0/1 (2; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/1 (2; 0) | 0/0 (2; 1) | 0/1 (2; 0) | 0/1 (2; 0) |
| qXX2 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| qYr7 | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| qgWj | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) |
| resciencex | 0/0 (8; 0) | 0/0 (8; 0) | 0/0 (8; 0) | 0/0 (8; 0) | 0/0 (8; 0) | 0/0 (8; 0) | 0/0 (8; 0) |
| rpq | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| rtn | 1/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 1/1 (0; 0) |
| shah | 0/0 (13; 0) | 0/1 (12; 0) | 0/1 (12; 0) | 0/2 (11; 0) | 0/1 (12; 0) | 0/1 (12; 0) | 2/3 (10; 0) |
| soscisubmission | 4/57 (54; 4) | 0/38 (53; 24) | 2/51 (64; 0) | 14/60 (51; 4) | 3/47 (53; 15) | 5/62 (53; 0) | 13/66 (49; 0) |
| soscisubmission1 | 0/0 (4; 0) | 0/4 (0; 0) | 0/4 (0; 0) | 0/2 (2; 0) | 0/1 (3; 0) | 0/1 (3; 0) | 0/0 (4; 0) |
| soscisubmission2 | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) |
| soscisubmission3 | 0/4 (0; 0) | 0/4 (0; 0) | 0/4 (0; 0) | 0/1 (3; 0) | 0/1 (3; 0) | 0/0 (4; 0) | 0/0 (4; 0) |
| soscisubmission34 | 0/0 (2; 0) | 0/0 (2; 0) | 0/1 (1; 0) | 1/1 (1; 0) | 0/1 (1; 0) | 0/2 (0; 0) | 1/1 (1; 0) |
| soscisubmission38 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| soscisubmission7 | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| soscisubmission8 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| svodevelopment | 0/0 (4; 0) | 0/3 (1; 0) | 0/3 (1; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/4 (0; 0) | 0/0 (4; 0) |
| svodevelopment2 | 0/1 (2; 0) | 2/3 (0; 0) | 0/3 (0; 0) | 0/0 (3; 0) | 0/1 (2; 0) | 0/1 (2; 0) | 0/0 (3; 0) |
| uxajg | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) |
| vGqL | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| w | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/2 (0; 0) |
| wRvv | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/1 (1; 0) | 0/0 (1; 1) | 0/1 (1; 0) | 0/2 (0; 0) |
| x0pA | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| x3KP | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| xYbO | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| xszk | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/0 (2; 0) | 0/2 (0; 0) |
| yAPR | 0/1 (0; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) |
| yypJ | 0/1 (0; 0) | 0/0 (0; 1) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| zK2 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| zNEm | 0/0 (1; 0) | 0/0 (1; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) | 0/1 (0; 0) |
| zb3Y | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) | 0/0 (4; 0) |
| zlBL | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) | 0/0 (3; 0) |
| zlm2 | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |
| zmYY | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) | 0/0 (1; 0) |

## Confirmed errors

31 confirmed errors are blank coded fields for which the primary source supplies the requested statistic. Each entry below gives the proposed correction and source location; full reasons and retained blind observations are in [results.csv](results.csv).

- Row 9, `es_value_o`: `0.13` → `0.20`. p. 418 (PDF p. 11), Table 1, Physically attractive (good looks) | Men, Ranked criteria; Gender Empowerment Measure. [Paper](https://doi.org/10.1037/0003-066x.54.6.408).
- Row 22, `reported_success`: `failed` → `successful`. p. 44 (article p. 9), Section 3 Results; p. 51 (article p. 16), Section 4 Discussion. [Paper](https://doi.org/10.1017/s1930297500008299).
- Row 29, `es_value_o`: `-0.12` → `0.28`. p. 418 (PDF p. 11), Table 1, Physically attractive (good looks) | Men, Ranked criteria; Gender-Related Development Index. [Paper](https://doi.org/10.1037/0003-066x.54.6.408).
- Row 44, `es_value_o`: `0.2` → `-0.33`. p. 418 (PDF p. 11), Table 1, Physically attractive (good looks) | Men, Rated criteria; Gender Empowerment Measure. [Paper](https://doi.org/10.1037/0003-066x.54.6.408).
- Row 44, `pval_value_o`: `0.1` → `< 0.10`. p. 418 (PDF p. 11), Table 1, Physically attractive (good looks) | Men, Rated criteria; Gender Empowerment Measure; significance footnote. [Paper](https://doi.org/10.1037/0003-066x.54.6.408).
- Row 45, `pval_value_o`: `None` → `< .01`. Printed p. 94 (PDF p. 16), Problem 11 results. [Paper](https://doi.org/10.1006/cogp.1998.0708).
- Row 48, `es_value_o`: `0.18` → `-0.14`. p. 418 (PDF p. 11), Table 1, Physically attractive (good looks) | Men, Rated criteria; Gender-Related Development Index. [Paper](https://doi.org/10.1037/0003-066x.54.6.408).
- Row 49, `n_o`: `18` → `33`. p. 32, Table 7; p. 40, Note 2. [Paper](https://doi.org/10.1111/lang.12161).
- Row 50, `n_o`: `18` → `33`. p. 32, Table 7. [Paper](https://doi.org/10.1111/lang.12161).
- Row 51, `n_o`: `18` → `33`. p. 32, Table 7. [Paper](https://doi.org/10.1111/lang.12161).
- Row 52, `es_value_o`: `0.23` → `0.57`. Printed p. 11 (PDF p. 13), Structural Equation Model; Printed p. 12 (PDF p. 14), Table 2. [Paper](https://doi.org/10.4148/1944-9771.1299).
- Row 53, `es_value_o`: `0.23` → `0.57`. Printed p. 11 (PDF p. 13), Structural Equation Model; Printed p. 12 (PDF p. 14), Table 2. [Paper](https://doi.org/10.4148/1944-9771.1299).
- Row 54, `es_value_o`: `0.07` → `-0.27`. Printed p. 11 (PDF p. 13), Structural Equation Model; Printed p. 12 (PDF p. 14), Table 2. [Paper](https://doi.org/10.4148/1944-9771.1299).
- Row 55, `es_value_o`: `0.07` → `-0.27`. Printed p. 11 (PDF p. 13), Structural Equation Model; Printed p. 12 (PDF p. 14), Table 2. [Paper](https://doi.org/10.4148/1944-9771.1299).
- Row 57, `es_value_r`: `t(91) = 0.85` → `t(69) = –0.34`. p. 41, Results; p. 45, Appendix D, Figure 1. [Paper](https://doi.org/10.26443/msurj.v19i1.231). [Locator URL](https://www.socscistatistics.com/effectsize/default3.aspx).
- Row 57, `pval_value_r`: `0.397` → `0.438`. p. 41, Results; p. 45, Appendix D, Figure 1 caption. [Paper](https://doi.org/10.26443/msurj.v19i1.231). [Locator URL](https://www.socscistatistics.com/effectsize/default3.aspx).
- Row 58, `es_value_r`: `t(82) = 0.5` → `t(69) = –0.34`. p. 41, Results; p. 45, Appendix D, Figure 1. [Paper](https://doi.org/10.26443/msurj.v19i1.231).
- Row 58, `pval_value_r`: `0.618` → `0.438`. p. 41, Results; p. 45, Appendix D, Figure 1. [Paper](https://doi.org/10.26443/msurj.v19i1.231).
- Row 60, `reported_success`: `successful` → `failed`. p. 872 (PDF p. 4), section 3.2.2 Posteromedial and posterolateral directions. [Paper](https://doi.org/10.1016/j.jsams.2024.07.018).
- Row 68, `reported_success`: `mixed` → `successful`. Online-first p. 8, Discussion. [Paper](https://doi.org/10.1177/07419325241240067).
- Row 69, `pval_value_o`: `0.41` → `0.47`. OnlineFirst p. 7, Table 3, Subgroup Analyses, Sample size row, χ²(1), p column. [Paper](https://doi.org/10.3102/0013189x13507104).
- Row 69, `reported_success`: `mixed` → `successful`. Online-first p. 8, Discussion. [Paper](https://doi.org/10.1177/07419325241240067).
- Row 70, `reported_success`: `mixed` → `successful`. Online-first p. 8, Discussion. [Paper](https://doi.org/10.1177/07419325241240067).
- Row 71, `reported_success`: `mixed` → `failed`. Online-first p. 8, Discussion. [Paper](https://doi.org/10.1177/07419325241240067).
- Row 80, `reported_success`: `mixed` → `failed`. Results (Effect of L-DOPA administration post extinction on extinction memory retrieval, p. 4) and Discussion. [Paper](https://doi.org/10.1038/s41467-024-46936-y).
- Row 81, `n_o`: `40` → `35`. Results, The effect of l-DOPA on extinction memory retrieval can be explained by its effect on vmPFC reactivations (p. 5); Fig. 2g (p. 4). [Paper](https://doi.org/10.1038/s41467-018-06785-y).
- Row 81, `pval_value_o`: `0.02` → `0.007`. Results, The effect of l-DOPA on extinction memory retrieval can be explained by its effect on vmPFC reactivations (p. 5); Fig. 2g (p. 4). [Paper](https://doi.org/10.1038/s41467-018-06785-y).
- Row 81, `reported_success`: `mixed` → `failed`. Abstract, Results (Effect of L-DOPA administration post extinction on vmPFC reactivations, p. 5), and Discussion. [Paper](https://doi.org/10.1038/s41467-024-46936-y).
- Row 86, `n_o`: `125` → `97`. Table 2, Sample Size row, CRP column (and Section 2.1 / Table 1). [Paper](https://doi.org/10.1016/j.drugalcdep.2021.108610).
- Row 86, `pval_value_r`: `0.001` → `0.002`. Abstract; Section 3.3, Regression Analyses in Females. [Paper](https://doi.org/10.1016/j.drugalcdep.2024.111323).
- Row 87, `n_o`: `125` → `97`. Table 2, Sample Size row, CRP column (and Section 2.1 / Table 1). [Paper](https://doi.org/10.1016/j.drugalcdep.2021.108610).
- Row 87, `pval_value_r`: `0.002` → `< 0.001`. Abstract; Section 3.3, Regression Analyses in Females. [Paper](https://doi.org/10.1016/j.drugalcdep.2024.111323).
- Row 100, `n_r`: `229` → `16`. Results, Correlation between MA and the misinformation effect change at the item level, p. 22, Footnote 9. [Paper](https://doi.org/10.1002/acp.4202).
- Row 101, `n_r`: `229` → `16`. Results, Correlation between MA and the misinformation effect change at the item level, p. 22, Footnote 9. [Paper](https://doi.org/10.1002/acp.4202).
- Row 136, `reported_success`: `statistically successful but flawed` → `mixed`. p. 1450 (PDF p. 12), Table 2; Discussion and Conclusion, paragraphs 1-2. [Paper](https://doi.org/10.1017/s0272263124000342).
- Row 137, `reported_success`: `statistically successful but flawed` → `mixed`. p. 1450 (PDF p. 12), Table 2; Discussion and Conclusion, paragraphs 1-2. [Paper](https://doi.org/10.1017/s0272263124000342).
- Row 138, `reported_success`: `statistically successful but flawed` → `mixed`. p. 1450 (PDF p. 12), Table 2; Discussion and Conclusion, paragraphs 1-2. [Paper](https://doi.org/10.1017/s0272263124000342).
- Row 139, `reported_success`: `statistically successful but flawed` → `mixed`. p. 1450 (PDF p. 12), Table 2; Discussion and Conclusion, paragraphs 1-2. [Paper](https://doi.org/10.1017/s0272263124000342).
- Row 140, `reported_success`: `statistically successful but flawed` → `mixed`. p. 1450 (PDF p. 12), Table 2; Discussion and Conclusion, paragraphs 1-2. [Paper](https://doi.org/10.1017/s0272263124000342).
- Row 141, `reported_success`: `statistically successful but flawed` → `mixed`. p. 1450 (PDF p. 12), Table 2; Discussion and Conclusion, paragraphs 1-2. [Paper](https://doi.org/10.1017/s0272263124000342).
- Row 146, `pval_value_o`: `None` → `< .001`. p. 149, §8.2 Results and discussion. [Paper](https://doi.org/10.1016/j.obhdp.2018.10.004).
- Row 147, `es_value_o`: `0.79` → `0.66`. Results, Subscale/Syndrome Comparisons, p. 52 (PDF p. 53); Table 5, p. 57 (PDF p. 58). [Paper](https://doi.org/thekeep.eiu.edu/theses/4783).
- Row 147, `es_value_r`: `0.76` → `0.62`. Results, BASC TRS-C Subscale/ASCA Syndrome Comparisons, p. 62 (PDF p. 64); Table 6, p. 67; Table 8, p. 76. [Locator URL](https://thekeep.eiu.edu/theses/5025).
- Row 158, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 160, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 162, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 164, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 166, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 168, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 169, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 170, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 171, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note and caption. [Paper](https://doi.org/10.1002/pam.21702).
- Row 172, `n_o`: `908` → `905`. Published p. 606 (PDF p. 10), Figure 6 note. [Paper](https://doi.org/10.1002/pam.21702).
- Row 179, `n_o`: `1110` → `1106`. printed p. 165 (PDF p. 180), Appendix P. [Paper](https://doi.org/scholars.indianastate.eduetds--2136).
- Row 179, `n_r`: `None` → `343`. printed p. 24; PDF p. 29. [Paper](https://doi.org/digitalcommons.memphis.edu--etd--3538). [Locator URL](https://digitalcommons.memphis.edu/etd/3538/).
- Row 179, `reported_success`: `mixed` → `successful`. printed p. 31; PDF p. 36. [Paper](https://doi.org/digitalcommons.memphis.edu--etd--3538). [Locator URL](https://digitalcommons.memphis.edu/etd/3538/).
- Row 180, `es_value_o`: `X2(1, N = 40) = 22.77` → `X2(1, N = 85) = 22.771`. Accepted manuscript p. 19, footnote 8 & footnote 9; p. 20, section 4.2. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 181, `es_value_o`: `X2(1, N = 40) = 0.03` → `X2(1, N = 69) = 0.027`. Accepted manuscript p. 19, section 4.1 & footnote 9. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 181, `pval_value_o`: `0.05` → `> 0.05`. Accepted manuscript p. 19, section 4.1. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 182, `es_value_o`: `X2(1, N = 40) = 11.59` → `X2(1, N = 154) = 11.587`. Accepted manuscript p. 19, footnote 8 & footnote 9. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 183, `es_value_o`: `X2(1, N = 40) = 24.44` → `X2(1, N = 88) = 24.444`. Accepted manuscript p. 19, footnote 8 & footnote 9. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 184, `es_value_o`: `X2(1, N = 40) = 23.46` → `X2(1, N = 826) = 23.456`. Accepted manuscript p. 19, footnote 8 & footnote 9; p. 23, section 4.4. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 185, `es_value_o`: `X2(1, N = 40) = 37.43` → `X2(1, N = 221) = 37.429`. Accepted manuscript p. 19, footnote 8 & footnote 9; p. 25, section 4.6. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 186, `es_value_o`: `X2(1, N = 40) = 42.12` → `X2(1, N = 221) = 42.119`. Accepted manuscript p. 19, footnote 8 & footnote 9; p. 26, section 4.6. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 187, `es_value_o`: `X2(1, N = 40) = 1.4` → `X2(1, N = 14) = 1.400`. Accepted manuscript p. 19, section 4.1 & footnote 9; pp. 24–25, section 4.5. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 187, `pval_value_o`: `0.05` → `> 0.05`. Accepted manuscript p. 19, section 4.1. [Paper](https://doi.org/10.1075/resla.17019.loz).
- Row 203, `pval_value_o`: `0.05` → `< 0.01`. p. 424, Results, Allocation of Resources, paragraph 2. [Paper](https://doi.org/10.1037/0021-9010.77.4.419).
- Row 210, `pval_value_o`: `0.01` → `0.72`. PDF p. 6 / journal p. 79; §4.2. [Paper](https://doi.org/10.1016/j.learninstruc.2014.08.004).
- Row 221, `n_o`: `240` → `239`. Journal p. 34, Summary of Treatment Groups; Journal p. 37 (article page 11), Table 5. [Paper](https://doi.org/10.1016/0030-5073%2876%2990005-2).
- Row 221, `reported_success`: `failed` → `successful`. Published p. 200, General Discussion (and p. 195, Experiment 1, First Reinvestment Decision). [Paper](https://doi.org/10.1037/xap0000366).
- Row 222, `n_o`: `240` → `239`. Journal p. 34, Summary of Treatment Groups; Journal p. 37 (article page 11), Table 5. [Paper](https://doi.org/10.1016/0030-5073%2876%2990005-2).
- Row 222, `pval_value_r`: `0.003` → `0.010`. Published p. 198, Experiment 2, First Reinvestment Decision. [Paper](https://doi.org/10.1037/xap0000366).
- Row 222, `reported_success`: `mixed` → `successful`. Published p. 200, General Discussion (and p. 198, Experiment 2, First Reinvestment Decision). [Paper](https://doi.org/10.1037/xap0000366).
- Row 224, `n_r`: `754` → `582`. p. 3, Participants; p. 7, Table 4. [Paper](https://doi.org/10.1037/emo0001389).
- Row 226, `n_r`: `754` → `582`. p. 3, Participants; p. 9, Table 7. [Paper](https://doi.org/10.1037/emo0001389).
- Row 233, `pval_value_o`: `None` → `0.003`. Printed p. 7 (PDF p. 8), Section 7, Method chains and comments. [Paper](https://doi.org/10.1109/tse.2016.2527791).
- Row 233, `n_r`: `106` → `66`. PDF p. 8, Section 4.2.7; p. 11, Section 5.2; p. 12, Table 18. [Paper](https://doi.org/10.1109/iccq60895.2024.10576941).
- Row 234, `n_r`: `106` → `66`. PDF p. 8, Section 4.2.7; p. 11, Section 5.2; p. 12, Table 22. [Paper](https://doi.org/10.1109/iccq60895.2024.10576941).
- Row 235, `n_r`: `106` → `54`. PDF p. 8, Section 4.2.7; p. 9, Section 5.1; p. 10, Table 6. [Paper](https://doi.org/10.1109/iccq60895.2024.10576941).
- Row 235, `reported_success`: `failed` → `successful`. PDF p. 14, Section 5.3, Table 27; p. 16, Section 7. [Paper](https://doi.org/10.1109/iccq60895.2024.10576941).
- Row 239, `es_value_o`: `F(1, 64) = 2.36` → `F(1, 64) = 42.32`. p. 1040 (PDF p. 8), Results, Manipulation Checks. [Paper](https://doi.org/10.1086/648381).
- Row 239, `pval_value_o`: `0.12` → `< .001`. p. 1040 (PDF p. 8), Results, Manipulation Checks. [Paper](https://doi.org/10.1086/648381).
- Row 239, `reported_success`: `failed` → `successful`. p. 7, Section 7.1, Manipulation checks. [Paper](https://doi.org/10.1016/j.jesp.2024.104619).
- Row 255, `reported_success`: `descriptive only` → `successful`. Thesis chapter 7, p. 161, section 7.6 Discussion. [Paper](https://doi.org/10.1080/15614263.2022.2102494).
- Row 256, `reported_success`: `descriptive only` → `successful`. Thesis chapter 7, p. 161, section 7.6 Discussion. [Paper](https://doi.org/10.1080/15614263.2022.2102494).
- Row 267, `reported_success`: `failed` → `statistically successful but flawed`. PDF p. 6, Table 2 (H6); PDF pp. 8–10, How should the Mediation Analysis results be understood?. [Paper](https://doi.org/10.31234/osf.io/xjaty).
- Row 269, `reported_success`: `failed` → `successful`. p. r9, General Discussion (see also p. r3, Experiment 1, Results). [Paper](https://doi.org/10.20982/tqmp.20.1.r001).
- Row 275, `es_value_r`: `F(1, 20) = 1.048` → `F(1, 20) = 0.072`. p. r7, Experiment 4, Results. [Paper](https://doi.org/10.20982/tqmp.20.1.r001).
- Row 287, `reported_success`: `mixed` → `failed`. p. 15, Section 3.1; p. 16, Section 3.2; p. 20, Section 4. [Paper](https://doi.org/10.31234/osf.io/xr6bn).
- Row 288, `reported_success`: `mixed` → `successful`. p. 15, Section 3.1; p. 16, Section 3.2; p. 20, Section 4. [Paper](https://doi.org/10.31234/osf.io/xr6bn).
- Row 291, `es_value_o`: `F(3, 78) = 5.93` → `F(1, 26) = 5.93`. Section 1.1.1, p. 2; Table 1, p. 5 (RT to arrows column; Proximity effect 1/4, 1/3, 1/2, 1/1). [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 292, `es_value_o`: `F(2, 52) = 4.00` → `F(1, 26) = 4.00`. Section 1.1.1, p. 2; Table 1, p. 5 (Motivation column; Proximity effect 2/4, 2/3, 2/2). [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 293, `es_value_o`: `F(2, 52) = 6.12` → `F(1, 26) = 6.12`. Section 1.1.1, p. 2; Table 1, p. 5 (RT to arrows column; Proximity effect 2/4, 2/3, 2/2). [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 295, `es_value_o`: `F(2, 52) = 5.16` → `F(1, 26) = 5.16`. Section 1.1.1, p. 2; Section 1.1.4, p. 3; Table 1, p. 5 (RT to arrows column; Proximity effect 3/4, 3/3). [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 298, `es_value_o`: `F(3, 23) = 16.69` → `F(1, 26) = 16.69`. Section 1.1.1, p. 2; Table 1, p. 5 (Motivation column; Expended effort effect 4/4, 3/3, 2/2, 1/1). [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 299, `es_value_o`: `F(3, 78) = 2.34` → `F(1, 26) = 2.34`. Section 1.1.1, p. 2; Table 1, p. 5 (RT to arrows column; Expended effort effect 4/4, 3/3, 2/2, 1/1). [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 300, `es_value_o`: `F(2, 52) = 27.5` → `F(1, 26) = 27.50`. Section 1.1.1, p. 2; Table 1, p. 5 (Motivation column; Expended effort effect 3/4, 2/3, 1/2). [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 301, `es_value_o`: `F(2, 52) = 9.26` → `F(1, 26) = 9.26`. Section 1.1.1, p. 2; Table 1, p. 5 (RT to arrows column; Expended effort effect 3/4, 2/3, 1/2). [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 314, `reported_success`: `successful` → `failed`. Results, Original analyses - Stouffer's p, Table 1; Discussion, paragraphs 2-3. [Paper](https://doi.org/10.12688/openreseurope.17749.1).
- Row 315, `reported_success`: `successful` → `failed`. Results, Original analyses - Stouffer's p, Table 1; Discussion, paragraphs 2-3. [Paper](https://doi.org/10.12688/openreseurope.17749.1).
- Row 316, `reported_success`: `successful` → `failed`. Results, Original analyses - Stouffer's p, Table 1; Discussion, paragraphs 2-3. [Paper](https://doi.org/10.12688/openreseurope.17749.1).
- Row 317, `reported_success`: `successful` → `failed`. Results, Original analyses - Stouffer's p, Table 1; Discussion, paragraphs 2-3. [Paper](https://doi.org/10.12688/openreseurope.17749.1).
- Row 322, `es_value_o`: `F(3, 78) = 10.76` → `F(1, 26) = 10.76`. Proof p. 5, Table 1, Proximity effect, 1/4, 1/3, 1/2, 1/1 row, Motivation column. [Paper](https://doi.org/10.1016/j.cortex.2014.02.013).
- Row 322, `es_value_r`: `F(3, 28) = 27.62` → `F(3, 93) = 27.62`. Table 1, Proximity effect, 1/4, 1/3, 1/2, 1/1 row, Motivation column. [Paper](https://doi.org/10.12688/openreseurope.17749.1).
- Row 326, `n_r`: `1036` → `1032`. p. 12, Participants; p. 13, Results. [Paper](https://doi.org/10.1073/pnas.2402315121).
- Row 331, `n_r`: `58` → `55`. Methods Addendum (Post Data Collection) - Actual Sample; Confirmatory analysis (Table 3). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rstudio-pubs-static.s3.amazonaws.com/333287_a1f6ccb88f36405e802c143a248a2206.html).
- Row 341, `n_r`: `81` → `42`. Methods Addendum, Actual Sample; Results, T-tests. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/okan2018.html).
- Row 342, `n_r`: `81` → `39`. Methods Addendum, Actual Sample; Results, T-tests. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/okan2018.html).
- Row 349, `n_r`: `25` → `21`. Methods Addendum, Actual Sample (PDF p. 5). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 349, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt and Commentary (PDF pp. 11–12). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 350, `pval_value_o`: `0.307` → `0.031`. Results, Experiment 1, Table 2. [Paper](https://doi.org/10.1162/jocn_a_00709).
- Row 350, `n_r`: `25` → `21`. Methods Addendum, Actual Sample (PDF p. 5). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 350, `reported_success`: `successful` → `mixed`. Discussion, Commentary (PDF pp. 11–12). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 351, `n_r`: `25` → `21`. Methods Addendum, Actual Sample (PDF p. 5). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 351, `reported_success`: `successful` → `mixed`. Discussion, Commentary (PDF pp. 11–12). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 352, `n_r`: `25` → `21`. Methods Addendum, Actual Sample (PDF p. 5). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 352, `reported_success`: `successful` → `mixed`. Discussion, Commentary (PDF pp. 11–12). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 353, `n_r`: `25` → `21`. Methods Addendum, Actual Sample (PDF p. 5). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 353, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt and Commentary (PDF pp. 11–12). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 354, `n_r`: `25` → `21`. Methods Addendum, Actual Sample (PDF p. 5). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 354, `reported_success`: `successful` → `mixed`. Discussion, Commentary (PDF pp. 11–12). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/otto2014.pdf).
- Row 355, `n_o`: `124` → `261`. p. 207, Studies 5A and 5B, Method—Participants and Design; p. 208, Results—Attitudes. [Paper](https://doi.org/10.1037/0022-3514.94.2.94.2.196).
- Row 356, `n_r`: `82` → `78`. Confirmatory analysis, condition_counts & crt_first_r; Summary of Rescue Results. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rstudio-pubs-static.s3.amazonaws.com/1178341_5e2ac8c976274f5fb6532dee0d9982c6.html).
- Row 356, `pval_value_r`: `0.2637` → `0.0346`. Confirmatory analysis, crt_first_r. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rstudio-pubs-static.s3.amazonaws.com/1178341_5e2ac8c976274f5fb6532dee0d9982c6.html).
- Row 356, `reported_success`: `failed` → `mixed`. Summary of Rescue Results, Numeric score of replication closeness. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rstudio-pubs-static.s3.amazonaws.com/1178341_5e2ac8c976274f5fb6532dee0d9982c6.html).
- Row 357, `n_r`: `82` → `160`. Confirmatory analysis, Fisher r to z test; Summary of Rescue Results. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rstudio-pubs-static.s3.amazonaws.com/1178341_5e2ac8c976274f5fb6532dee0d9982c6.html).
- Row 357, `reported_success`: `failed` → `mixed`. Summary of Rescue Results, Numeric score of replication closeness. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rstudio-pubs-static.s3.amazonaws.com/1178341_5e2ac8c976274f5fb6532dee0d9982c6.html).
- Row 365, `n_o`: `600` → `594`. Accepted manuscript p. 6 (Method) and p. 10 (Figure 1). [Paper](https://doi.org/10.1177/0956797617728270).
- Row 365, `es_value_o`: `0.34` → `0.58`. Accepted manuscript p. 10 (Results). [Paper](https://doi.org/10.1177/0956797617728270).
- Row 365, `pval_value_o`: `0.007` → `< .001`. Accepted manuscript p. 10 (Results). [Paper](https://doi.org/10.1177/0956797617728270).
- Row 367, `pval_value_o`: `0.58` → `< 0.01`. p. 4088 (paper p. 3), Study 7 results. [Paper](https://doi.org/10.1073/pnas.1118373109).
- Row 380, `n_r`: `64` → `4`. Pilot Samples; Results, Transforming data from JSON format to dataframe; Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ShimaSalehi/155989).
- Row 380, `es_value_r`: `F(1, 56) = 57.800` → `F(1, 2) = 57.800`. Confirmatory analysis, Main Data analysis: Mixed model ANOVA (lines 294-309). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ShimaSalehi/155989).
- Row 381, `pval_value_o`: `0.84` → `.084`. p. 1754, Study 1 Results. [Paper](https://doi.org/10.1177/0956797615598739).
- Row 381, `n_r`: `64` → `4`. Pilot Samples; Results, Transforming data from JSON format to dataframe; Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ShimaSalehi/155989).
- Row 381, `es_value_r`: `F(1, 56) = 0.022` → `F(1, 2) = 0.022`. Confirmatory analysis, Main Data analysis: Mixed model ANOVA (lines 294-298). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ShimaSalehi/155989).
- Row 381, `reported_success`: `successful` → `failed`. Confirmatory analysis; Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ShimaSalehi/155989).
- Row 384, `n_r`: `64` → `4`. Pilot Samples; Results, Transforming data from JSON format to dataframe; Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ShimaSalehi/155989).
- Row 384, `reported_success`: `successful` → `failed`. Confirmatory analysis, Follow up data analyses: trait type rating between conditions. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ShimaSalehi/155989).
- Row 385, `n_r`: `64` → `4`. Pilot Samples; Results, Transforming data from JSON format to dataframe; Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ShimaSalehi/155989).
- Row 392, `pval_value_o`: `0.003` → `0.001`. p. 29, Section 8.2. [Paper](https://doi.org/10.1016/j.jesp.2018.05.006).
- Row 398, `es_value_r`: `-0.9943` → `0.8721`. Confirmatory analysis, Ratings of the Ethicality of the Buyer’s Answer, Honest reference, Coefficients. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/kagood/final-project-report).
- Row 399, `es_value_r`: `0.04378` → `-0.4226`. Confirmatory analysis, Ratings of the Ethicality of the Buyer’s Answer, Lie reference, Coefficients. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/kagood/final-project-report).
- Row 400, `es_value_r`: `0.9505` → `1.2947`. Confirmatory analysis, Ratings of the Ethicality of the Buyer’s Answer, Honest reference, Coefficients. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/kagood/final-project-report).
- Row 401, `es_value_r`: `-0.04378` → `0.04378`. Confirmatory analysis, Buyer Ethicality Ratings, Lie reference, Coefficients. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/kagood/final-project-report).
- Row 408, `reported_success`: `mixed` → `successful`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/cceballos-stanford/544019).
- Row 409, `reported_success`: `mixed` → `successful`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/cceballos-stanford/544019).
- Row 410, `reported_success`: `mixed` → `successful`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/cceballos-stanford/544019).
- Row 433, `n_o`: `577` → `578`. Studies 1b–1d Results, p. 405 (article p. 4). [Paper](https://doi.org/10.1177/0956797614563958).
- Row 434, `n_o`: `577` → `578`. Studies 1b–1d Results, p. 405 (article p. 4). [Paper](https://doi.org/10.1177/0956797614563958).
- Row 435, `n_r`: `90` → `77`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240).
- Row 442, `n_r`: `17` → `16`. Results, Final replication results, Confirmatory analysis, summary(model_replication). [Paper](https://doi.org/10.1098/rsos.231240).
- Row 446, `pval_value_r`: `0.001` → `3.625e-05`. Results, Planned Comparisons; paired t-test output for public_noncok vs. public_cok. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/hrlarry/YUIMU-final).
- Row 460, `es_value_r`: `0.25` → `0.01`. Confirmatory Analysis 3: Mixed Design ANOVA for File B Performance (replication main analysis). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/mkmartykeil/replicationfinal).
- Row 460, `pval_value_r`: `0.001` → `0.65`. Confirmatory Analysis 3: Mixed Design ANOVA for File B Performance (replication main analysis). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/mkmartykeil/replicationfinal).
- Row 471, `pval_value_r`: `0.00001654` → `2.832e-05`. Results, Differences between items of different prototypicality status for each adjective (lines 211-225). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/StanfordPsych254/Tribushinina2011/blob/master/writeup/Replication-Report.html).
- Row 475, `n_r`: `56` → `60`. Confirmatory analysis, summary(model1). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ayl888/695975).
- Row 476, `n_r`: `56` → `60`. Confirmatory analysis, summary(model1). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ayl888/695975).
- Row 478, `n_r`: `56` → `60`. Confirmatory analysis, summary(model1). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/ayl888/695975).
- Row 491, `reported_success`: `mixed` → `failed`. Analysis > Main Analysis; Conclusions. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rstudio-pubs-static.s3.amazonaws.com/155174_48b1633681bb4024b4098ed433d5a80a.html).
- Row 492, `reported_success`: `mixed` → `failed`. Analysis > Secondary analyses > Accuracy-based analysis; Conclusions. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rstudio-pubs-static.s3.amazonaws.com/155174_48b1633681bb4024b4098ed433d5a80a.html).
- Row 493, `pval_value_r`: `3.20E-04` → `3.254853668646976e-4`. Primary authors processed_data.csv, line 178 (data row 175), yang2018, column rep_p_calc. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/data/processed_data.csv).
- Row 501, `es_value_o`: `0.987` → `0.989`. Published article p. 117 (PDF p. 8), Table 4, model (2), row Case-specific variables: Care by family members, ISEI. [Paper](https://doi.org/10.1016/j.ecresq.2019.10.004).
- Row 502, `reported_success`: `mixed` → `successful`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/rcatapano/Zaval_replication_report).
- Row 503, `reported_success`: `mixed` → `successful`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/rcatapano/Zaval_replication_report).
- Row 504, `reported_success`: `mixed` → `failed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/rcatapano/Zaval_replication_report).
- Row 505, `reported_success`: `mixed` → `successful`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/rcatapano/Zaval_replication_report).
- Row 506, `reported_success`: `mixed` → `successful`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/rcatapano/Zaval_replication_report).
- Row 507, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 508, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 509, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 510, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 511, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 512, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 513, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 514, `es_value_o`: `0.56` → `0.67`. p. 216 (article p. 4), Experiment 1a, Results. [Paper](https://doi.org/10.1177/0956797615617779).
- Row 514, `es_value_r`: `F(1, 13) = 9.312` → `F(1, 13) = 21.804`. Confirmatory analysis, Both tasks combined, Overall ANOVA, congruency row. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 514, `pval_value_r`: `0.009` → `0.000`. Confirmatory analysis, Both tasks combined, Overall ANOVA, congruency row. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 514, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 515, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 516, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 517, `reported_success`: `successful` → `mixed`. Discussion, Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/zhao2016.html).
- Row 534, `pval_value_r`: `0.41435` → `0.10256`. Exploratory analyses, glm(hire_rec ~ manipulation + candidate_name + participant_sex + participant_parent) coefficients. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/dmetaxak/correll2007).
- Row 551, `pval_value_r`: `None` → `8.75e-06`. Results, Confirmatory analysis, Fixed effects output. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/franke2016.html).
- Row 552, `pval_value_r`: `None` → `0.0352`. Results, Confirmatory analysis, Fixed effects output. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/franke2016.html).
- Row 555, `pval_value_r`: `0.2886814205` → `0.58`. Discussion, Summary of Replication Attempt (final sample, N = 118). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/garciacastro2020.html).
- Row 557, `pval_value_o`: `0.01548195` → `< 0.01`. p. 26, Experiment 5, Results and Discussion; Table 7A. [Paper](https://doi.org/10.1016/0010-0285%2883%2990002-6).
- Row 557, `pval_value_r`: `None` → `0.0001934`. Results, Confirmatory analysis, GTest(contingency_table). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://rpubs.com/Greses88/449388).
- Row 558, `n_r`: `90` → `72`. Results, Confirmatory Analysis, Main analysis: AUC values (lines 268-272). [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/gong2019.html).
- Row 559, `n_o`: `29` → `25`. pp. 518–519, §7.1.1 Participants. [Paper](https://doi.org/10.1111/j.1551-6709.2010.01161.x).
- Row 568, `pval_value_r`: `None` → `0.376`. Results, Confirmatory analysis, rating model table, condition1. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/hopkins2016.html).
- Row 569, `n_o`: `29` → `28`. Study 3, Method (Participants) and Results and discussion, pp. 2484–2485. [Paper](https://doi.org/10.1177/0956797613494853).
- Row 569, `n_r`: `60` → `58`. Discussion, Summary of Replication Attempt; Results, Statistical Tests. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/hughes2013.html).
- Row 577, `n_o`: `457` → `452`. p. 8, Study 4, Method, Subjects. [Paper](https://doi.org/10.1177/0956797616685771).
- Row 585, `pval_value_r`: `5.75E-04` → `< .0005`. Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/kouchaki2018.html).
- Row 598, `n_r`: `27` → `25`. Discussion — Summary of Replication Attempt. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/reports/lloyd2017.html).
- Row 634, `pval_value_r`: `0.0092` → `< 0.001`. Supplementary Table 3, p. 52 (PDF p. 54), Morewedge et al. (2010) row. [Paper](https://doi.org/10.1038/s41562-018-0399-z). [Locator URL](https://osf.io/k2teb).
- Row 644, `es_value_o`: `X2(1, N = 366) = 16.3` → `X2(1, N = 51) = 16.3`. p. 389, Results (Fig. 1c) and p. 391, Methods. [Paper](https://doi.org/10.1038/nature12774).
- Row 644, `n_r`: `482` → `65`. Supplementary Table 3, p. 52 (PDF p. 54), Derex et al. (2013) row. [Paper](https://doi.org/10.1038/s41562-018-0399-z). [Locator URL](https://osf.io/kchf9).
- Row 650, `n_r`: `214` → `90`. PDF p. 4, Actual Sample and Differences from pre-data collection methods plan. [Locator URL](https://drive.google.com/file/d/1DDCuEgQah24QordxkRGO0EIt6Q681jyL/view).
- Row 650, `es_value_r`: `F(1, 88) = 2.93` → `F(1, 88) = 0.20`. PDF p. 5, Confirmatory analysis, Moral ratings. [Locator URL](https://drive.google.com/file/d/1DDCuEgQah24QordxkRGO0EIt6Q681jyL/view).
- Row 650, `pval_value_r`: `0.09` → `> .10`. PDF p. 5, Confirmatory analysis, Moral ratings. [Locator URL](https://drive.google.com/file/d/1DDCuEgQah24QordxkRGO0EIt6Q681jyL/view).
- Row 651, `n_r`: `440` → `214`. Study 1, Material and Methods, Participants; Table 1. [Paper](https://doi.org/10.3389/fpsyg.2014.01276).
- Row 651, `pval_value_r`: `None` → `0.23`. Study 1, Results, paragraph 1; Table 1. [Paper](https://doi.org/10.3389/fpsyg.2014.01276).
- Row 651, `reported_success`: `successful` → `failed`. Study 1, Results, paragraph 1. [Paper](https://doi.org/10.3389/fpsyg.2014.01276).
- Row 653, `n_o`: `31` → `37`. p. 224, Table 2 title; p. 223, Study 1 Method, Participants. [Paper](https://doi.org/10.1037/0022-3514.77.2.221).
- Row 664, `n_r`: `28` → `31`. Published p. 408 (PDF p. 3), Method, Participants, Study 1a; p. 409 (PDF p. 4), Results, Study 1a. [Paper](https://doi.org/10.1037/0022-3514.83.2.406).
- Row 665, `es_value_r`: `F(1, 36) = 6.77` → `F(1, 36) = 2.95`. Published p. 409 (PDF p. 4), Results, Study 1b. [Paper](https://doi.org/10.1037/0022-3514.83.2.406).
- Row 665, `pval_value_r`: `0.01` → `0.09`. Published p. 409 (PDF p. 4), Results, Study 1b. [Paper](https://doi.org/10.1037/0022-3514.83.2.406).
- Row 671, `pval_value_r`: `None` → `.177`. p. 698 (PDF p. 3), Table 1, Current studies, Sample 1 row. [Paper](https://doi.org/10.3758/s13423-013-0549-2).
- Row 672, `pval_value_r`: `None` → `.139`. p. 698 (PDF p. 3), Table 1, Current studies, Sample 2 row. [Paper](https://doi.org/10.3758/s13423-013-0549-2).
- Row 678, `n_r`: `5979` → `5942`. Accepted manuscript pp. 24–25, Table 2, Retrospective gambler fallacy row. [Paper](https://doi.org/10.1027/1864-9335/a000178). [Locator URL](https://osf.io/y36m8).
- Row 678, `es_value_r`: `0.02` → `0.61`. Accepted manuscript pp. 24–25, Table 2, Retrospective gambler fallacy row. [Paper](https://doi.org/10.1027/1864-9335/a000178). [Locator URL](https://osf.io/y36m8).
- Row 678, `pval_value_r`: `0.27` → `<.001`. Accepted manuscript pp. 24–25, Table 2, Retrospective gambler fallacy row. [Paper](https://doi.org/10.1027/1864-9335/a000178). [Locator URL](https://osf.io/y36m8).
- Row 686, `n_o`: `104` → `103`. p. 1162 (PDF p. 2), Method; p. 1163 (PDF p. 3), Results and Discussion. [Paper](https://doi.org/10.1177/01461672952111004).
- Row 687, `n_o`: `104` → `103`. p. 1162 (PDF p. 2), Method; p. 1163 (PDF p. 3), Results and Discussion. [Paper](https://doi.org/10.1177/01461672952111004).
- Row 688, `n_o`: `104` → `103`. p. 1162 (PDF p. 2), Method; p. 1163 (PDF p. 3), Results and Discussion. [Paper](https://doi.org/10.1177/01461672952111004).
- Row 689, `n_o`: `104` → `103`. p. 1162 (PDF p. 2), Method; p. 1163 (PDF p. 3), Results and Discussion. [Paper](https://doi.org/10.1177/01461672952111004).
- Row 693, `pval_value_o`: `0.025` → `0.047`. p. 1452, Study 4 results, middle column. [Paper](https://doi.org/10.1126/science.1130726).
- Row 693, `pval_value_r`: `0.22` → `0.93`. p. 26 (PDF p. 6), Study 2, Results and Discussion. [Locator URL](https://www.jasnh.com/pdf/Vol6-No2.pdf).
- Row 696, `n_r`: `57` → `58`. Published p. 225 (PDF p. 2), Method > Participants; p. 226 (PDF p. 3), Results. [Paper](https://doi.org/10.1177/2167702613485565).
- Row 701, `n_r`: `None` → `100`. Main text, p. 636; Online Supplement, p. 2. [Paper](https://doi.org/10.1177/1745691612463078).
- Row 703, `n_o`: `80` → `86`. Sciencexpress PDF p. 1, Experiment 1; p. 6, Table 1, Exp. 1 RMET. [Paper](https://doi.org/10.1126/science.1239918).
- Row 704, `pval_value_o`: `0.3` → `0.04`. Sciencexpress PDF p. 6, Table 1, Exp. 5 RMET, Condition row. [Paper](https://doi.org/10.1126/science.1239918).
- Row 705, `n_o`: `80` → `86`. Sciencexpress PDF p. 1, Experiment 1; p. 6, Table 1, Exp. 1 RMET. [Paper](https://doi.org/10.1126/science.1239918).
- Row 706, `n_o`: `51` → `50`. p. 1171 (PDF page 3), Study 2, Method, Participants. [Paper](https://doi.org/10.1111/j.1467-9280.2009.02426.x).
- Row 706, `n_r`: `2374` → `2285`. manuscript pp. 25–26, section 6. [Paper](https://doi.org/10.1016/j.jesp.2015.10.012). [Locator URL](https://osf.io/ct89g/).
- Row 711, `reported_success`: `mixed` → `failed`. manuscript p. 28, section 8; p. 44. [Paper](https://doi.org/10.1016/j.jesp.2015.10.012). [Locator URL](https://osf.io/ct89g/).
- Row 715, `pval_value_r`: `0.079` → `0.004`. p. 62 (PDF p. 3), Table 1, Replication 1 row, Interaction effect p column. [Paper](https://doi.org/10.1016/j.jesp.2015.08.005).
- Row 716, `pval_value_r`: `0.494` → `0.046`. p. 62 (PDF p. 3), Table 2, Replication 1 row, Interaction effect p column. [Paper](https://doi.org/10.1016/j.jesp.2015.08.005).
- Row 717, `reported_success`: `mixed` → `failed`. manuscript p. 30, section 9; p. 44. [Paper](https://doi.org/10.1016/j.jesp.2015.10.012). [Locator URL](https://osf.io/ct89g/).
- Row 723, `n_r`: `105` → `219`. p. 2129 (PDF p. 2), Table 1, Current studies / Sample 1 row. [Paper](https://doi.org/10.1177/0956797613486983).
- Row 725, `n_r`: `6340` → `6333`. Accepted manuscript pp. 24–25, Table 2, Currency Priming row. [Paper](https://doi.org/10.1027/1864-9335/a000178). [Locator URL](https://osf.io/y36m8).
- Row 725, `pval_value_r`: `0.44` → `0.83`. Accepted manuscript pp. 24–25, Table 2, Currency Priming row. [Paper](https://doi.org/10.1027/1864-9335/a000178). [Locator URL](https://osf.io/y36m8).
- Row 726, `n_r`: `6335` → `6336`. Accepted manuscript pp. 24–25, Table 2, Imagined contact row. [Paper](https://doi.org/10.1027/1864-9335/a000178). [Locator URL](https://osf.io/y36m8).
- Row 732, `reported_success`: `successful` → `failed`. Results, paragraph 2 (line 83) and paragraph 6 (line 91). [Locator URL](https://datacolada.org/83).
- Row 737, `pval_value_r`: `None` → `.864`. SPSS_output.docx, Independent Samples Test, attractiveness_avg, Equal variances assumed, Sig. (2-tailed). [Paper](https://doi.org/10.1525/collabra.177). [Locator URL](https://osf.io/dqv9y).
- Row 738, `pval_value_r`: `None` → `.481`. SPSS_output.docx, Independent Samples Test, sex_attraction_avg, Equal variances assumed, Sig. (2-tailed). [Paper](https://doi.org/10.1525/collabra.177). [Locator URL](https://osf.io/dqv9y).
- Row 739, `pval_value_r`: `None` → `.755`. SPSS_output.docx, Independent Samples Test, likeability_avg, Equal variances assumed, Sig. (2-tailed). [Paper](https://doi.org/10.1525/collabra.177). [Locator URL](https://osf.io/dqv9y).
- Row 746, `reported_success`: `successful` → `failed`. Table 1, P. Intent to kill row, Replicated? column. [Paper](https://doi.org/10.17605/osf.io/e9d3k).
- Row 748, `reported_success`: `successful` → `failed`. Conclusions, p. 5; Table 1, Causal locus row, Replicated? column. [Paper](https://doi.org/10.17605/osf.io/e9d3k).
- Row 753, `n_r`: `300` → `303`. p. 10, section 4.2.1; p. 11, section 4.2.3. [Paper](https://doi.org/10.18718/81781.38).
- Row 753, `es_value_r`: `-0.017` → `0.050`. p. 11, section 4.2.3 Hypothesis Tests. [Paper](https://doi.org/10.18718/81781.38).
- Row 753, `pval_value_r`: `0.383` → `0.809`. p. 11, section 4.2.3 Hypothesis Tests. [Paper](https://doi.org/10.18718/81781.38).
- Row 759, `n_o`: `735` → `737`. Results, Uncalculating Cooperation Is Used as a Signal; Fig. 2B, p. 8660. [Paper](https://doi.org/10.1073/pnas.1601280113).
- Row 759, `pval_value_o`: `0.002` → `0.014`. Results, Uncalculating Cooperation Is Used as a Signal; Fig. 2B, p. 8660. [Paper](https://doi.org/10.1073/pnas.1601280113).
- Row 764, `pval_value_r`: `0.904` → `0.799`. Post-replication report p. 2, Replication results. [Paper](https://doi.org/10.1038/s41562-024-02062-9). [Locator URL](https://osf.io/sejyp).
- Row 854, `es_value_o`: `F(1, 78) = 17.27` → `F(1, 78) = 17.7`. p. 283, Table 1, Supermarket story row. [Paper](https://doi.org/10.1016/0022-1031%2877%2990049-x).
- Row 856, `pval_value_r`: `0` → `< 3.32e-285`. p. 464, Effect 22, Replication. [Paper](https://doi.org/10.1177/2515245918810225).
- Row 856, `reported_success`: `mixed` → `successful`. p. 464, Effect 22, Replication. [Paper](https://doi.org/10.1177/2515245918810225).
- Row 863, `reported_success`: `mixed` → `successful`. p. 461, Effect 17, Replication. [Paper](https://doi.org/10.1177/2515245918810225).
- Row 864, `reported_success`: `mixed` → `successful`. p. 461, Effect 18, Replication. [Paper](https://doi.org/10.1177/2515245918810225).
- Row 865, `reported_success`: `mixed` → `successful`. p. 456, Effect 6, Replication. [Paper](https://doi.org/10.1177/2515245918810225).
- Row 870, `n_o`: `207` → `201`. p. 245, Study 2, Participants and design. [Paper](https://doi.org/10.1002/bdm.586).
- Row 872, `n_r`: `3582` → `3549`. p. 467, Section 28. [Paper](https://doi.org/10.1177/2515245918810225).
- Row 885, `reported_success`: `successful` → `failed`. Results, Klink (2000), marketing letters, p. 6; Table 2. [Paper](https://doi.org/10.3389/fcomm.2022.1048896).
- Row 895, `reported_success`: `successful` → `failed`. Results, Klink (2000), marketing letters, p. 6; Table 2. [Paper](https://doi.org/10.3389/fcomm.2022.1048896).
- Row 900, `pval_value_r`: `0.004` → `0.0004`. SI Appendix p. 67 (Tully Study 5 Replication Write Up), Results, paragraph 2. [Paper](https://doi.org/10.1073/pnas.2103313118).
- Row 902, `pval_value_r`: `0.56` → `0.45`. Results without careless responses, paragraph 1. [Paper](https://doi.org/10.1073/pnas.2103313118).
- Row 902, `reported_success`: `mixed` → `failed`. Discussion, paragraph 2. [Paper](https://doi.org/10.1073/pnas.2103313118).
- Row 903, `reported_success`: `mixed` → `failed`. Discussion, paragraph 2. [Paper](https://doi.org/10.1073/pnas.2103313118).
- Row 904, `reported_success`: `mixed` → `failed`. Discussion, paragraph 2. [Paper](https://doi.org/10.1073/pnas.2103313118).
- Row 905, `reported_success`: `mixed` → `failed`. Discussion, paragraph 2. [Paper](https://doi.org/10.1073/pnas.2103313118).
- Row 926, `es_value_o`: `F(1, 76) = 3.20` → `F(1, 76) = 4.87`. Published article p. 998 (PDF p. 11), Study 4, Results. [Paper](https://doi.org/10.1086/661531).
- Row 926, `pval_value_o`: `0.08` → `< 0.05`. Published article p. 998 (PDF p. 11), Study 4, Results. [Paper](https://doi.org/10.1086/661531).
- Row 929, `es_value_o`: `0.85` → `0.085`. PDF p. 6, Experiment 1, Results. [Paper](https://doi.org/10.1093/jcr/ucv049).
- Row 931, `n_o`: `194` → `179`. p. 229 (PDF p. 7), Study 2, Results and Discussion, first paragraph. [Paper](https://doi.org/10.1086/669476).
- Row 932, `n_o`: `194` → `179`. p. 229 (PDF p. 7), Study 2, Results and Discussion, first paragraph. [Paper](https://doi.org/10.1086/669476).
- Row 938, `n_o`: `24` → `14`. p. 362 (PDF p. 10), Experiment 3, Method. [Paper](https://doi.org/10.1037/0278-7393.34.2.353).
- Row 944, `es_value_o`: `0.26` → `0.326`. Results, paragraph 2. [Paper](https://doi.org/10.1111/j.1467-9280.2008.02092.x).
- Row 952, `n_o`: `115` → `120`. p. 257 (PDF p. 3), Method—Participants; p. 258 (PDF p. 4), Results—Apartment Choice and Table 1. [Paper](https://doi.org/10.1111/j.1467-9280.2008.02077.x).
- Row 960, `reported_success`: `successful` → `statistically successful but flawed`. Summary of Replication Attempt, line 62; Commentary, line 67. [Paper](https://doi.org/10.1126/science.aac4716). [Locator URL](https://osf.io/gxvd3).
- Row 970, `pval_value_o`: `0.001` → `0.010`. p. 408 (PDF p. 4), Results, top of right column. [Paper](https://doi.org/10.1111/j.1467-9280.2008.02100.x).
- Row 987, `n_o`: `18` → `33`. Published pp. 308–309 (PDF pp. 7–8), Experiment 3, Method—Participants and Results. [Paper](https://doi.org/10.1037/0278-7393.34.2.302).
- Row 988, `n_o`: `154` → `153`. Experiment 1, Results, Latencies, p. 347 (PDF p. 5); Table 4 and interaction test, p. 348 (PDF p. 6). [Paper](https://doi.org/10.1037/0278-7393.34.2.343).
- Row 1026, `pval_value_r`: `0.19` → `0.22`. p. 4, Confirmatory analysis. [Paper](https://doi.org/10.1126/science.aac4716). [Locator URL](https://osf.io/79dey).
- Row 1037, `n_r`: `182` → `183`. p. 17, sections 5.2.1 and 5.2.3. [Paper](https://doi.org/10.18718/81781.38). [Locator URL](https://doi.org/10.31234/osf.io/bgp3m).
- Row 1037, `es_value_r`: `0.215` → `0.198`. p. 17, section 5.2.3 Hypothesis Tests. [Paper](https://doi.org/10.18718/81781.38). [Locator URL](https://doi.org/10.31234/osf.io/bgp3m).
- Row 1037, `pval_value_r`: `0.925` → `0.908`. p. 17, section 5.2.3 Hypothesis Tests. [Paper](https://doi.org/10.18718/81781.38). [Locator URL](https://doi.org/10.31234/osf.io/bgp3m).
- Row 1038, `n_r`: `182` → `183`. p. 17, sections 5.2.1 and 5.2.3. [Paper](https://doi.org/10.18718/81781.38). [Locator URL](https://doi.org/10.31234/osf.io/bgp3m).
- Row 1038, `es_value_r`: `0.001` → `0.006`. p. 17, section 5.2.3 Hypothesis Tests. [Paper](https://doi.org/10.18718/81781.38). [Locator URL](https://doi.org/10.31234/osf.io/bgp3m).
- Row 1039, `n_o`: `51` → `50`. p. 1171 (PDF page 3), Study 2, Method, Participants. [Paper](https://doi.org/10.1111/j.1467-9280.2009.02426.x).
- Row 1039, `reported_success`: `mixed` → `failed`. p. 8, Results. [Paper](https://doi.org/10.2139/ssrn.2586261).
- Row 1042, `reported_success`: `uninformative` → `failed`. General discussion, paragraph 1 (line 938). [Paper](https://doi.org/10.1007/s00213-019-05314-z).
- Row 1054, `reported_success`: `mixed` → `successful`. Results, Replication, lines 374-390 (PDF pp. 12-13). [Paper](https://doi.org/10.1027/1864-1105/a000334).
- Row 1057, `reported_success`: `mixed` → `successful`. Results, Replication, lines 374-390 (PDF pp. 12-13). [Paper](https://doi.org/10.1027/1864-1105/a000334).
- Row 1064, `n_r`: `954` → `303`. p. 3, Methods, Materials; p. 6, Results, Hypothesis 14. [Paper](https://doi.org/10.1525/collabra.68054).
- Row 1064, `reported_success`: `successful` → `failed`. p. 6, Results, Hypothesis 14. [Paper](https://doi.org/10.1525/collabra.68054).
- Row 1070, `n_o`: `34` → `36`. Experiment 2, Method, Participants; Results and discussion (p. 6). [Paper](https://doi.org/10.3758/s13414-020-02150-8).
- Row 1072, `pval_value_o`: `0.12` → `0.93`. p. 3, Results, No Age Differences in Empathy and Positive Age Differences in Compassion. [Paper](https://doi.org/10.1038/s41598-017-10669-4).
- Row 1072, `pval_value_r`: `0.145` → `0.780`. p. 7, Results, Social affect: empathy and compassion. [Paper](https://doi.org/10.1098/rsos.210641).
- Row 1075, `es_value_r`: `-0.03` → `-0.05`. p. 5, Section 5.2 Results, paragraph 2 (also Abstract, p. 1, and Table 1, p. 3). [Paper](https://doi.org/10.1016/j.intell.2020.101471).
- Row 1075, `pval_value_r`: `0.592` → `0.345`. p. 5, Section 5.2 Results, paragraph 2 (also Abstract, p. 1, and Table 1, p. 3). [Paper](https://doi.org/10.1016/j.intell.2020.101471).
- Row 1079, `es_value_o`: `F(1, 444) = 4.88` → `F(1, 444) = 4.63`. Printed p. 737 (PDF page 5), Study 1, Results and Discussion. [Paper](https://doi.org/10.1037/0022-3514.73.4.733).
- Row 1083, `es_value_o`: `X2(3, N = 1593) = 166.88` → `X2(6, N = 1593) = 62.25`. Printed p. 741 (PDF page 9), Study 4, Results and Discussion. [Paper](https://doi.org/10.1037/0022-3514.73.4.733).
- Row 1097, `es_value_o`: `t(3411) = 21.5` → `t(3410) = 30.2`. Author manuscript pp. 28–29, Section 9, footnote 10. [Paper](https://doi.org/10.5840/jphil20091061128).
- Row 1111, `n_r`: `316` → `318`. Results, paragraphs 3-4. [Paper](https://doi.org/10.1007/s13164-018-0400-9). [Locator URL](https://osf.io/4ewkh).
- Row 1137, `n_r`: `127.00` → `129`. PDF p. 2; Results, Data analysis - Target effect. [Paper](https://doi.org/10.1007/s13164-018-0400-9). [Locator URL](https://osf.io/juxpq).
- Row 1172, `pval_value_r`: `1.33E-42` → `1.32505878875791e-56`. Author primary workbook, Results sheet, row 5, column AU. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1173, `pval_value_r`: `3.20E-31` → `3.199850522144975e-45`. Author primary workbook, Results sheet, row 6, column AU. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1174, `es_value_r`: `0.57` → `0.4790435067040672`. Author primary workbook, Results sheet, row 4, column AQ. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1174, `pval_value_r`: `9.89E-76` → `9.891336164105786e-90`. Author primary workbook, Results sheet, row 4, column AU. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1177, `pval_value_r`: `6.46E-18` → `6.464814723748534e-18`. Author primary workbook, Results sheet, row 39, column AU. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1187, `pval_value_o`: `None` → `< .01`. Table 5 and note, p. 945 (L1592-L1593, L1648). [Paper](https://doi.org/10.1111/1467-6494.05028).
- Row 1188, `pval_value_o`: `None` → `< .01`. Table 5 and note, p. 945 (L1592-L1593, L1648). [Paper](https://doi.org/10.1111/1467-6494.05028).
- Row 1215, `reported_success`: `successful` → `mixed`. Published p. 171 (PDF p. 1), abstract; p. 176-177 (PDF p. 6-7), Results—Replication Analyses; p. 179 (PDF p. 9), Discussion.. [Paper](https://doi.org/10.1037/ebs0000279).
- Row 1216, `es_value_r`: `F(1, 94) = 0.017` → `F(1, 94) = 0.155`. Section 4 Results, L441, first ANOVA paragraph. [Paper](https://doi.org/10.1111/desc.13244).
- Row 1216, `pval_value_r`: `0.896` → `0.695`. Section 4 Results, L441, first ANOVA paragraph. [Paper](https://doi.org/10.1111/desc.13244).
- Row 1249, `reported_success`: `mixed` → `failed`. SI Appendix, p. 49. [Paper](https://doi.org/10.1073/pnas.2103313118).
- Row 1254, `pval_value_o`: `0.32` → `0.032`. accepted manuscript p. 36, Results, Dependent Variable. [Paper](https://doi.org/10.1093/jcr/ucw056).
- Row 1271, `reported_success`: `mixed` → `successful`. p. 5, Study 1 Results, Replication. [Paper](https://doi.org/10.1525/collabra.32572).
- Row 1272, `es_value_r`: `1.38` → `1.67`. Results, Part 1: Replication of Johnson and Goldstein (2003), paragraph 1 and Table 6. [Paper](https://doi.org/10.15626/mp.2022.3108).
- Row 1272, `pval_value_r`: `0.021` → `<.001`. Results, Part 1: Replication of Johnson and Goldstein (2003), paragraph 1 and Table 6. [Paper](https://doi.org/10.15626/mp.2022.3108).
- Row 1278, `es_value_r`: `1.7` → `-0.89`. preprint p. 17, Table 4, Low-High row. [Paper](https://doi.org/10.1017/s026144482000021x).
- Row 1278, `pval_value_r`: `0.001` → `0.003`. preprint p. 17, Table 4, Low-High row. [Paper](https://doi.org/10.1017/s026144482000021x).
- Row 1280, `n_o`: `80` → `30`. p. 688 (PDF p. 9), The Chinese EIT; pp. 693–694 (PDF pp. 14–15), Features of the Items Influencing Outcomes of the EIT. [Paper](https://doi.org/10.1111/flan.12063).
- Row 1280, `n_r`: `65` → `30`. preprint p. 11, Section 5.2.2; pp. 21–23, Section 7.4. [Paper](https://doi.org/10.1017/s026144482000021x).
- Row 1282, `pval_value_o`: `0.09` → `0.009`. Printed p.1577 (PDF p.3), Results, Body sway, first sentence.. [Paper](https://doi.org/10.1177/0956797610384746).
- Row 1287, `pval_value_r`: `None` → `4.889658369986202e-47`. OSF Results sheet (https://osf.io/mc3z7), row 21 (ResultsOrder 20), column ReplicationPValue. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1288, `pval_value_r`: `None` → `1.3222161668157884e-150`. OSF Results sheet (https://osf.io/mc3z7), row 22 (ResultsOrder 21), column ReplicationPValue. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1300, `es_value_r`: `0.25` → `0.22848043525041464`. OSF Results sheet (https://osf.io/mc3z7), row 19 (ResultsOrder 18), column ReplicationEffect (cf. Table 1, p. 13: .23/.25). [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1300, `pval_value_r`: `None` → `8.331911727997158e-20`. OSF Results sheet (https://osf.io/mc3z7), row 19 (ResultsOrder 18), column ReplicationPValue. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1301, `es_value_r`: `-0.35` → `-0.33316177089309484`. OSF Results sheet (https://osf.io/mc3z7), row 20 (ResultsOrder 19), column ReplicationEffect (cf. Table 1, p. 13: .33/.35). [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1301, `pval_value_r`: `None` → `1.7111944756903308e-41`. OSF Results sheet (https://osf.io/mc3z7), row 20 (ResultsOrder 19), column ReplicationPValue. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1302, `es_value_r`: `-0.57` → `-0.47492850576184314`. OSF Results sheet (https://osf.io/mc3z7), row 9 (ResultsOrder 8), column ReplicationEffect (cf. Table 1, p. 13: .47/.57). [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1302, `pval_value_r`: `None` → `2.111214410676517e-50`. OSF Results sheet (https://osf.io/mc3z7), row 9 (ResultsOrder 8), column ReplicationPValue. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1303, `es_value_r`: `0.25` → `0.20933245700763436`. OSF Results sheet (https://osf.io/mc3z7), row 10 (ResultsOrder 9), column ReplicationEffect (cf. Table 1, p. 13: .21/.25). [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1303, `pval_value_r`: `None` → `1.6522558004419532e-12`. OSF Results sheet (https://osf.io/mc3z7), row 10 (ResultsOrder 9), column ReplicationPValue. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1307, `es_value_r`: `-0.19` → `-0.17261233227624778`. OSF Results sheet (https://osf.io/mc3z7), row 52 (ResultsOrder 51), column ReplicationEffect (cf. Table 1, p. 13: .17/.19). [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1307, `pval_value_r`: `None` → `1.1305169117438363e-07`. OSF Results sheet (https://osf.io/mc3z7), row 52 (ResultsOrder 51), column ReplicationPValue. [Paper](https://doi.org/10.1177/0956797619831612).
- Row 1309, `n_r`: `301` → `303`. p. 10, section 4.2.1; p. 11, section 4.2.3. [Paper](https://doi.org/10.18718/81781.38).
- Row 1310, `es_value_o`: `t(2) = 4.59` → `t = 4.59`. p. 12 (PDF p. 8), Experiment 2, Section 3.2 Results. [Paper](https://doi.org/10.1023/a%3A1015044207315).
- Row 1314, `es_value_r`: `0.19` → `0.45`. p. 1014 (PDF p. 10), Table 6 (and p. 1013, Table 5, Model 2). [Paper](https://doi.org/10.1177/1948550620948973).
- Row 1317, `n_r`: `2697` → `1479`. p. 19, Participants. [Paper](https://doi.org/10.31219/osf.io/q56rk).
- Row 1317, `es_value_r`: `1.5` → `1.75`. p. 22, Confirmatory Analysis. [Paper](https://doi.org/10.31219/osf.io/q56rk).
- Row 1318, `n_r`: `2697` → `1479`. p. 19, Participants; p. 21, Confirmatory Analysis. [Paper](https://doi.org/10.31219/osf.io/q56rk).
- Row 1319, `n_r`: `2697` → `1479`. p. 19, Participants; p. 21, Confirmatory Analysis. [Paper](https://doi.org/10.31219/osf.io/q56rk).
- Row 1326, `n_r`: `270` → `286`. Supplementary Document II, Pre-Study 2, Results and discussion, paragraph 1. [Paper](https://doi.org/10.31219/osf.io/q56rk).
- Row 1327, `n_r`: `270` → `286`. Supplementary Document II, Pre-Study 2, Results and discussion, paragraph 1. [Paper](https://doi.org/10.31219/osf.io/q56rk).
- Row 1332, `pval_value_r`: `0.001` → `0.002`. Supplementary Document II, Table S2-2, Extended, GM vs FM. [Paper](https://doi.org/10.31219/osf.io/q56rk).
- Row 1347, `reported_success`: `failed` → `successful`. p. 5, Perceived Competence. [Paper](https://doi.org/10.1525/collabra.90195). [Locator URL](https://drive.google.com/file/d/1zJ3IIX26CyEcHOzgjGdLzzyONBKjM3Eo/view).
- Row 1351, `reported_success`: `mixed` → `successful`. PDF p. 9, Discussion, first paragraph. [Paper](https://doi.org/10.31234/osf.io/dca65).
- Row 1356, `n_r`: `40` → `38`. pp. 598–600, §§2.1, 3 (PDF pp. 4–6). [Paper](https://doi.org/10.1016/s0005-7967%2898%2900158-2).
- Row 1362, `n_r`: `98` → `100`. Study 2, Method—Participants; Table 1; Table 3. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1363, `n_r`: `98` → `100`. Study 2, Method—Participants; Table 3. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1364, `n_r`: `98` → `100`. Study 2, Method—Participants; Table 3. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1365, `n_r`: `98` → `100`. Study 2, Method—Participants; Replication of the American-Independent Conditions of Study 2. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1366, `n_r`: `100` → `101`. Study 3, Method—Participants; Table 1; Table 5. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1367, `n_r`: `100` → `101`. Study 3, Method—Participants; Table 5. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1368, `n_r`: `100` → `101`. Study 3, Method—Participants; Table 5. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1369, `n_r`: `100` → `101`. Study 3, Method—Participants; Replication of the American-Independent Conditions of Study 3. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1369, `pval_value_r`: `0.06` → `0.030`. Replication of the American-Independent Conditions of Study 3, Conducted March 2022. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1370, `n_r`: `100` → `101`. Study 3, Method—Participants; Replication of the American-Independent Conditions of Study 3. [Paper](https://doi.org/10.31234/osf.io/fmdqe).
- Row 1382, `pval_value_o`: `None` → `< .01`. p. 467, Experiment 2. [Paper](https://doi.org/10.1177/0261927x01020004004).
- Row 1398, `n_r`: `1203` → `387`. p. 5, Table 3, Panel C. [Paper](https://doi.org/10.15626/mp.2021.2932).
- Row 1401, `n_r`: `835` → `817`. p. 2, section 3.2.2; p. 4, Table 2. [Paper](https://doi.org/10.1016/j.jesp.2022.104372).
- Row 1407, `n_o`: `219` → `12`. p. 11, Results, Exhibit 6. [Paper](https://doi.org/10.1002/%28sici%291099-0771%28200001/03%2913%3A1%3C1%3A%3Aaid-bdm333%3E3.0.co%3B2-s).
- Row 1409, `pval_value_r`: `0.501` → `0.395`. manuscript p. 14 (PDF p. 16), Study 2a, Key Results: Pricing. [Paper](https://doi.org/10.1016/j.jesp.2020.103972).
- Row 1410, `pval_value_r`: `0.016` → `< 0.001`. manuscript p. 21 (PDF p. 23), Study 3a, Results. [Paper](https://doi.org/10.1016/j.jesp.2020.103972).
- Row 1414, `n_o`: `40` → `43`. pp. 1220–1221 (PDF pp. 2–3), Experiment 2 Method (Participants) and Table 2. [Paper](https://doi.org/10.1111/j.1467-9280.2008.02227.x).
- Row 1414, `es_value_o`: `0.09` → `0.16`. p. 1221 (PDF p. 3), Experiment 2 Results and Discussion, Moral Judgments. [Paper](https://doi.org/10.1111/j.1467-9280.2008.02227.x).
- Row 1416, `pval_value_o`: `0.003` → `0.035`. Accepted manuscript p. 7 (cached PDF p. 8), Results. [Paper](https://doi.org/10.1111/j.1467-9280.2007.01944.x).
- Row 1420, `reported_success`: `successful` → `failed`. Discussion, paragraph 3 (and Results, Region 1 section; Table I). [Paper](https://doi.org/10.1002/pros.21320).
- Row 1421, `reported_success`: `successful` → `failed`. Discussion, paragraph 3 (and Results, Region 1 section; Table I). [Paper](https://doi.org/10.1002/pros.21320).
- Row 1422, `reported_success`: `successful` → `failed`. Discussion, paragraph 3 (and Results, Region 1 section; Table I). [Paper](https://doi.org/10.1002/pros.21320).
- Row 1501, `n_o`: `63` → `48`. p. 140 (PDF p. 8), Section 7.2 (Differences by country); p. 137 (PDF p. 5), Fig. 3. [Paper](https://doi.org/10.1016/s0272-6963%2897%2900033-8).
- Row 1502, `es_value_r`: `0.02` → `0.19`. Manuscript p. 16 (PDF p. 17), Results. [Paper](https://doi.org/10.1037/h0101833).
- Row 1502, `pval_value_r`: `0.365` → `< 0.001`. Manuscript p. 16 (PDF p. 17), Results. [Paper](https://doi.org/10.1037/h0101833).
- Row 1509, `n_o`: `94` → `369`. Section 3.2, pp. 175–176 (PDF pp. 14–15). [Paper](https://doi.org/10.1075/arcl.7.07gri).
- Row 1510, `n_o`: `94` → `369`. Section 3.2, pp. 175–176 (PDF pp. 14–15). [Paper](https://doi.org/10.1075/arcl.7.07gri).
- Row 1514, `pval_value_r`: `0.0001` → `0.255`. Results in Detail > Figure 6: Replication Results Table, Condition x Trial0 x Size0 row, p column. [Locator URL](https://replications.clearerthinking.org/replication-2022psci33-8).
- Row 1514, `reported_success`: `uninformative` → `failed`. Overall Ratings > Replicability. [Locator URL](https://replications.clearerthinking.org/replication-2022psci33-8).
- Row 1517, `n_r`: `136` → `97`. p. 6, Section 3.1 (H1); p. 5, Section 2.3. [Paper](https://doi.org/10.17645/mac.7807).
- Row 1517, `pval_value_r`: `0.006` → `0.325`. p. 7, Section 3.1 (H1); p. 8, Table 1. [Paper](https://doi.org/10.17645/mac.7807).
- Row 1531, `es_value_o`: `0.26` → `0.20`. p. 888, Table 1, Experiment 2. [Paper](https://doi.org/10.1037/a0036477).
- Row 1531, `pval_value_o`: `0.012` → `0.003`. p. 888, Table 1, Experiment 2. [Paper](https://doi.org/10.1037/a0036477).
- Row 1532, `es_value_o`: `0.26` → `0.20`. p. 888, Table 1, Experiment 2. [Paper](https://doi.org/10.1037/a0036477).
- Row 1532, `pval_value_o`: `0.012` → `0.003`. p. 888, Table 1, Experiment 2. [Paper](https://doi.org/10.1037/a0036477).
- Row 1537, `reported_success`: `mixed` → `successful`. p. 187, Discussion. [Paper](https://doi.org/10.2466/20.22.pms.114.1.185-188).
- Row 1538, `reported_success`: `mixed` → `successful`. p. 187, Discussion. [Paper](https://doi.org/10.2466/20.22.pms.114.1.185-188).
- Row 1539, `reported_success`: `mixed` → `failed`. p. 188, Discussion. [Paper](https://doi.org/10.2466/20.22.pms.114.1.185-188).
- Row 1540, `reported_success`: `mixed` → `successful`. p. 187, Discussion. [Paper](https://doi.org/10.2466/20.22.pms.114.1.185-188).
- Row 1555, `n_r`: `443` → `1,020`. accepted manuscript p. 7, Methods (Airbnb data); p. 11, Confirmatory analyses (Table 3, Model 2). [Paper](https://doi.org/10.1016/j.joep.2018.11.004).
- Row 1555, `reported_success`: `mixed` → `failed`. accepted manuscript p. 16, General Discussion. [Paper](https://doi.org/10.1016/j.joep.2018.11.004).
- Row 1557, `n_r`: `16` → `15`. p. 238 (PDF p. 4), Data Analysis and Results (Behavioural Data). [Paper](https://doi.org/10.1037/cep0000225).
- Row 1577, `n_r`: `None` → `20`. p. 2, Participants; p. 3, Results (PDF pp. 3-4). [Paper](https://doi.org/10.1080/00222895.2012.746635).
- Row 1579, `reported_success`: `mixed` → `successful`. p. 5, Results, Average AMP effects by condition; Discussion. [Paper](https://doi.org/10.1111/bjso.12217).
- Row 1580, `reported_success`: `mixed` → `successful`. p. 5, Results, Average AMP effects by condition; Discussion. [Paper](https://doi.org/10.1111/bjso.12217).
- Row 1596, `es_value_o`: `F(1, 135) = 12.8` → `F(1, 136) = 14.3`. p. 7, Results, paragraph preceding Table III. [Paper](https://doi.org/10.1093/her/cyl160).
- Row 1597, `es_value_o`: `F(1, 178) = 10.2` → `F(1, 179) = 12.9`. p. 7, Results, paragraph preceding Table III. [Paper](https://doi.org/10.1093/her/cyl160).
- Row 1609, `reported_success`: `failed` → `successful`. p. 10. [Paper](https://doi.org/10.48550/arxiv.1605.00178).
- Row 1610, `reported_success`: `failed` → `successful`. p. 10. [Paper](https://doi.org/10.48550/arxiv.1605.00178).
- Row 1611, `reported_success`: `failed` → `successful`. pp. 10–11. [Paper](https://doi.org/10.48550/arxiv.1605.00178).
- Row 1612, `reported_success`: `failed` → `successful`. pp. 10–11. [Paper](https://doi.org/10.48550/arxiv.1605.00178).
- Row 1613, `reported_success`: `failed` → `successful`. p. 18. [Paper](https://doi.org/10.48550/arxiv.1605.00178).
- Row 1614, `reported_success`: `failed` → `successful`. p. 18. [Paper](https://doi.org/10.48550/arxiv.1605.00178).
- Row 1620, `n_r`: `431` → `430`. p. 656 (PDF p. 19), Section 4.1.1; p. 657 (PDF p. 20), Section 4.2; Table 4, p. 649 (PDF p. 12). [Paper](https://doi.org/10.1017/s1930297500007774).
- Row 1621, `reported_success`: `mixed` → `failed`. p. 638 (PDF p. 1), Abstract; p. 660 (PDF p. 23), Section 5.2 Results. [Paper](https://doi.org/10.1017/s1930297500007774).
- Row 1622, `reported_success`: `mixed` → `failed`. p. 665 (PDF p. 28), Section 5.3 Discussion. [Paper](https://doi.org/10.1017/s1930297500007774).
- Row 1629, `reported_success`: `failed` → `successful`. Supplemental Materials, Effect Size Comparisons: Original vs Replication, Study 2. [Paper](https://doi.org/10.1016/j.jesp.2020.104052).
- Row 1630, `reported_success`: `failed` → `successful`. Supplemental Materials, Effect Size Comparisons: Original vs Replication, Study 2. [Paper](https://doi.org/10.1016/j.jesp.2020.104052).
- Row 1631, `reported_success`: `failed` → `successful`. Supplemental Materials, Effect Size Comparisons: Original vs Replication, Study 2. [Paper](https://doi.org/10.1016/j.jesp.2020.104052).
- Row 1634, `reported_success`: `failed` → `successful`. Supplemental Materials, Effect Size Comparisons: Original vs Replication, Study 2. [Paper](https://doi.org/10.1016/j.jesp.2020.104052).
- Row 1644, `reported_success`: `mixed` → `successful`. PDF p. 9, Discussion, first paragraph. [Paper](https://doi.org/10.31234/osf.io/dca65).
- Row 1647, `pval_value_r`: `0.1` → `.000`. p. 160 (PDF p. 10), Table 2, Informal competition row, Model 2 (unshaded); also p. 158 (PDF p. 8). [Paper](https://doi.org/10.1177/27550311251323281).
- Row 1648, `pval_value_r`: `0.1` → `.000`. p. 160 (PDF p. 10), Table 2, Informal competition row, Model 3 (unshaded). [Paper](https://doi.org/10.1177/27550311251323281).
- Row 1649, `pval_value_r`: `0.1` → `.000`. p. 160 (PDF p. 10), Table 2, Informal competition row, Model 4 (unshaded). [Paper](https://doi.org/10.1177/27550311251323281).
- Row 1650, `pval_value_r`: `0.1` → `.000`. p. 160 (PDF p. 10), Table 2, Informal competition row, Model 5 (unshaded). [Paper](https://doi.org/10.1177/27550311251323281).
- Row 1651, `pval_value_r`: `0.1` → `.000`. p. 160 (PDF p. 10), Table 2, Informal competition row, Model 6 (unshaded). [Paper](https://doi.org/10.1177/27550311251323281).
- Row 1653, `n_r`: `6` → `3`. p. 236 (PDF p. 14), Figure 2. [Paper](https://doi.org/10.1080/10584609809342367).
- Row 1653, `reported_success`: `successful` → `failed`. p. 235 (PDF p. 13), Intermedia Agenda Setting and Images. [Paper](https://doi.org/10.1080/10584609809342367).
- Row 1654, `n_r`: `6` → `3`. p. 236 (PDF p. 14), Figure 2. [Paper](https://doi.org/10.1080/10584609809342367).
- Row 1654, `reported_success`: `successful` → `failed`. p. 235 (PDF p. 13), Intermedia Agenda Setting and Images. [Paper](https://doi.org/10.1080/10584609809342367).
- Row 1656, `reported_success`: `failed` → `successful`. p. 56 Discussion, The Model's Predictions (PDF p. 10); p. 52-53 Results, Mental Effort (PDF pp. 6-7). [Paper](https://doi.org/10.1007/bf02298289).
- Row 1658, `es_value_r`: `X2(1, N = 167) = 3.481` → `X2(2, N = 167) = 3.481`. p. 103, Table II, Patients (P) vs Controls (C). [Paper](https://doi.org/10.1097/00041444-199322000-00006).
- Row 1660, `reported_success`: `mixed` → `successful`. p. 743, Internal Dynamics among Indicators of Engagement versus Disaffection. [Paper](https://doi.org/10.1002/pits.22027).
- Row 1667, `reported_success`: `successful` → `failed`. p. 37 (PDF p. 4), Findings: Replication of previous study; p. 42 (PDF p. 9), Appendix B. [Paper](https://doi.org/10.2501/jar-40-1-2-35-42).
- Row 1717, `n_r`: `13` → `14`. §5.4 Main Analysis, p. 21; §6.2 Limitations, p. 33. [Paper](https://doi.org/10.17605/osf.io/7weum).
- Row 1717, `reported_success`: `mixed` → `successful`. §5.4.1 Smiling, p. 23; §6.1 General Discussion, p. 30. [Paper](https://doi.org/10.17605/osf.io/7weum).
- Row 1718, `n_r`: `12` → `14`. §5.4 Main Analysis, p. 21; §6.2 Limitations, p. 33. [Paper](https://doi.org/10.17605/osf.io/7weum).
- Row 1718, `reported_success`: `mixed` → `failed`. §5.4.2 Behavioral mannerisms, p. 26; §6.1 General Discussion, p. 31. [Paper](https://doi.org/10.17605/osf.io/7weum).
- Row 1719, `n_r`: `12` → `14`. §5.4 Main Analysis, p. 21; §6.2 Limitations, p. 33. [Paper](https://doi.org/10.17605/osf.io/7weum).
- Row 1722, `reported_success`: `descriptive only` → `successful`. p. 9, §6.1 Attitudinal Factors. [Paper](https://doi.org/10.17645/mac.7666).
- Row 1723, `reported_success`: `descriptive only` → `successful`. p. 9, §6.1 Attitudinal Factors. [Paper](https://doi.org/10.17645/mac.7666).
- Row 1724, `reported_success`: `descriptive only` → `failed`. p. 10, §6.1 Attitudinal Factors. [Paper](https://doi.org/10.17645/mac.7666).
- Row 1725, `reported_success`: `descriptive only` → `failed`. p. 10, §6.1 Attitudinal Factors. [Paper](https://doi.org/10.17645/mac.7666).
- Row 1726, `reported_success`: `descriptive only` → `successful`. p. 11, §6.2 Normative and Resource Factors. [Paper](https://doi.org/10.17645/mac.7666).
- Row 1727, `reported_success`: `descriptive only` → `failed`. p. 11, §6.2 Normative and Resource Factors. [Paper](https://doi.org/10.17645/mac.7666).
- Row 1729, `n_o`: `51` → `37`. Methods, Participants; Results, Single-trial experiment. [Paper](https://doi.org/10.1038/s41598-022-24919-7).
- Row 1729, `n_r`: `74` → `37`. Abstract; Methods, Participants & Sample size estimation; Table 2. [Paper](https://doi.org/10.1038/s41598-024-63724-2).
- Row 1730, `n_o`: `51` → `37`. Methods, Participants; Results, Single-trial experiment. [Paper](https://doi.org/10.1038/s41598-022-24919-7).
- Row 1730, `n_r`: `74` → `37`. Abstract; Methods, Participants & Sample size estimation; Table 2. [Paper](https://doi.org/10.1038/s41598-024-63724-2).
- Row 1734, `n_r`: `None` → `90`. processed_data.csv line 51 (schnall2008), column replication_N. [Paper](https://doi.org/10.1098/rsos.231240). [Locator URL](https://github.com/vboyce/251-254-MA/blob/main/data/processed_data.csv).
- Row 1737, `reported_success`: `failed` → `successful`. p. 2, Results, Data analysis - Other effects. [Paper](https://doi.org/10.1007/s13164-018-0400-9). [Locator URL](https://osf.io/fmynh/files/rts9a).
- Row 1741, `n_o`: `157` → `235`. p. 10 (PDF p. 6), Experiment 2, Section 3.1 Method. [Paper](https://doi.org/10.1023/a%3A1015044207315).
- Row 1743, `es_value_o`: `0.56` → `0.98`. p. 291 (PDF p. 3), Experiment 1, Results and Discussion. [Paper](https://doi.org/10.1037/0096-3445.136.2.289).
- Row 1743, `pval_value_o`: `0.105` → `0.006`. p. 291 (PDF p. 3), Experiment 1, Results and Discussion. [Paper](https://doi.org/10.1037/0096-3445.136.2.289).
- Row 1743, `es_value_r`: `0.04` → `0.02`. p. 40, Table 9a, Thanksgiving Day (Within-subject design). [Locator URL](https://osf.io/ns26x).
- Row 1743, `pval_value_r`: `0.496` → `0.811`. p. 40, Table 9a, Thanksgiving Day (Within-subject design). [Locator URL](https://osf.io/ns26x).
- Row 1743, `reported_success`: `mixed` → `failed`. p. 64, Comparing replication to original findings, DV1: Influence on current mood. [Locator URL](https://osf.io/ns26x).
- Row 1744, `es_value_r`: `0.46` → `0.19`. p. 41, Table 9b, Menstruation. [Locator URL](https://osf.io/ns26x).
- Row 1744, `pval_value_r`: `0.001` → `0.154`. p. 41, Table 9b, Menstruation. [Locator URL](https://osf.io/ns26x).
- Row 1745, `es_value_o`: `0.24` → `0.66`. p. 292 (PDF p. 4), Experiment 2, Results and Discussion. [Paper](https://doi.org/10.1037/0096-3445.136.2.289).
- Row 1745, `pval_value_o`: `0.416` → `0.027`. p. 292 (PDF p. 4), Experiment 2, Results and Discussion. [Paper](https://doi.org/10.1037/0096-3445.136.2.289).
- Row 1745, `es_value_r`: `0.19` → `0.46`. p. 40, Table 9a, Menstruation. [Locator URL](https://osf.io/ns26x).
- Row 1745, `pval_value_r`: `0.154` → `< 0.001`. p. 40, Table 9a, Menstruation. [Locator URL](https://osf.io/ns26x).
- Row 1748, `n_o`: `368` → `377`. Online-first p. 6 (final issue p. 44), Study 2 Sample; p. 9 (final issue p. 47), Table 1 and Political Knowledge. [Paper](https://doi.org/10.1017/xps.2017.21).
- Row 1748, `reported_success`: `mixed` → `successful`. Published p. 106, PDF p. 5, Results (Stage 2). [Paper](https://doi.org/10.1017/xps.2022.35).
- Row 1749, `n_o`: `368` → `377`. Online-first p. 6 (final issue p. 44), Study 2 Sample; p. 9 (final issue p. 47), Table 1 and Political Knowledge. [Paper](https://doi.org/10.1017/xps.2017.21).
- Row 1749, `reported_success`: `mixed` → `successful`. Published p. 102, PDF p. 1, Abstract; Published p. 106, PDF p. 5, Results (Stage 2). [Paper](https://doi.org/10.1017/xps.2022.35).
- Row 1750, `reported_success`: `mixed` → `failed`. Published p. 105, PDF p. 4, Results (Stage 1). [Paper](https://doi.org/10.1017/xps.2022.35).
- Row 1751, `reported_success`: `mixed` → `failed`. Published p. 106, PDF p. 5, Results (Stage 2). [Paper](https://doi.org/10.1017/xps.2022.35).
- Row 1752, `pval_value_o`: `0.2` → `< 0.01`. p. 260 (PDF p. 4), Figure 3B caption and Results and Discussion. [Paper](https://doi.org/10.1016/j.cub.2004.01.029).
- Row 1752, `reported_success`: `failed` → `successful`. Section 3.4.1; Section 4, Discussion. [Paper](https://doi.org/10.1016/j.cortex.2019.03.026).
- Row 1771, `n_r`: `100` → `95`. p. 6, ERP Data, Footnote 2, and Figure 2A. [Paper](https://doi.org/10.3389/fnhum.2019.00119).
- Row 1772, `n_r`: `100` → `95`. p. 6, ERP Data, Footnote 2, and Figure 2B. [Paper](https://doi.org/10.3389/fnhum.2019.00119).
- Row 1786, `reported_success`: `successful` → `failed`. article p. 13 (PDF p. 14), Experiment 3 Discussion; see also article p. 12 (PDF p. 13), Line discrimination task. [Paper](https://doi.org/10.1080/02699931.2020.1863187).
- Row 1788, `n_o`: `62` → `44`. p. 513, Method, Follow-Up; p. 514, Prediction of Psychopathology, Intrusive memories, F(2, 41) = 10.1; Table 1. [Paper](https://doi.org/10.1037/0021-843x.108.3.511).
- Row 1789, `n_o`: `62` → `44`. p. 513, Method, Follow-Up; p. 514, Prediction of Psychopathology, Intrusive memories, F(2, 41) = 13.7; Table 1. [Paper](https://doi.org/10.1037/0021-843x.108.3.511).
- Row 1797, `reported_success`: `successful` → `failed`. p. 1401 (PDF p. 10), Section 3.1; p. 1406 (PDF p. 15), Table 4. [Paper](https://doi.org/10.1017/s1930297500008470).
- Row 1798, `reported_success`: `successful` → `failed`. p. 1401 (PDF p. 10), Section 3.1; p. 1406 (PDF p. 15), Table 4. [Paper](https://doi.org/10.1017/s1930297500008470).
- Row 1825, `es_value_r`: `F(1, 688) = 4.73` → `F(1, 688) = 152.37`. Accepted manuscript printed p. 18, Confirmatory (Pre-Registered) Results, Replication: Decision quality. [Paper](https://doi.org/10.17605/osf.io/knjhu).
- Row 1825, `pval_value_r`: `0.03` → `< 0.001`. Accepted manuscript printed p. 18, Confirmatory (Pre-Registered) Results, Replication: Decision quality. [Paper](https://doi.org/10.17605/osf.io/knjhu).
- Row 1837, `pval_value_o`: `None` → `< .03`. p. 613 (PDF p. 4), Experiment 1 Results and Discussion. [Paper](https://doi.org/10.1037/a0020757).
- Row 1837, `pval_value_r`: `None` → `0.180`. Accepted manuscript p. 18, Section 3.5, Table 6 (Fairness, Replication row). [Paper](https://doi.org/10.1016/j.joep.2022.102509).
- Row 1866, `n_r`: `446` → `1,020`. accepted manuscript p. 7, Methods (Airbnb data); p. 11, Confirmatory analyses (Table 3, Model 1). [Paper](https://doi.org/10.1016/j.joep.2018.11.004).
- Row 1866, `reported_success`: `mixed` → `failed`. accepted manuscript p. 16, General Discussion; p. 20, Conclusion. [Paper](https://doi.org/10.1016/j.joep.2018.11.004).
- Row 1871, `n_r`: `723` → `437`. author manuscript p. 28 (PDF p. 31), Study 1c Methods - Participants. [Paper](https://doi.org/10.1016/j.jesp.2021.104222).
- Row 1878, `n_r`: `221` → `220`. p. 8, Table 6, Total row; Primary confirmatory analyses. [Paper](https://doi.org/10.1525/collabra.192). [Locator URL](https://osf.io/s2389/).
- Row 1883, `es_value_o`: `0.45` → `0.05`. p. 28, Experiment 2, Results, Laptop Preferences. [Paper](https://doi.org/10.1093/jcr/ucz028).
- Row 1884, `es_value_o`: `0.45` → `0.05`. p. 28, Experiment 2, Results, Laptop Preferences. [Paper](https://doi.org/10.1093/jcr/ucz028).
- Row 1906, `n_r`: `300` → `294`. Appendix 2, RMET-scores, p. 20 (PDF p. 11). [Locator URL](https://www.tijdschriftdepsycholoog.nl/wp-content/uploads/2015/10/Dijkstra-K.-Verkoeijen-P.-Van-Kuijk-I.-Soke-Yee-Chow-Bakker-A.-Zwaan-R.-2015.-Leidt-het-lezen-van-literaire-fictie-tot-meer-emphatie.-De-Psycholoog-10-10-21..pdf).
- Row 1910, `pval_value_r`: `0.644` → `0.666`. p. 6, Table 2 (Replication with the same conditions as in the target article, 2 × 2 ANOVA, Singularity and identifiability interaction); p. 11, Table 5 (H3 interaction). [Paper](https://doi.org/10.1017/jdm.2024.31).
- Row 1921, `n_r`: `1086` → `319`. p. 38, Table 12 note; p. 39, Table 13 note. [Paper](https://doi.org/10.17605/osf.io/j9mfn). [Locator URL](https://osf.io/8mqx5).
- Row 1922, `n_r`: `1086` → `327`. p. 41, Table 16 note; p. 42, Table 17 note. [Paper](https://doi.org/10.17605/osf.io/j9mfn). [Locator URL](https://osf.io/8mqx5).
- Row 1922, `pval_value_r`: `0.02` → `0.027`. p. 41, Study 3 results; p. 42, Table 17. [Paper](https://doi.org/10.17605/osf.io/j9mfn). [Locator URL](https://osf.io/8mqx5).
- Row 1923, `n_r`: `1086` → `282`. p. 44, Table 20 note; p. 45, Table 21 note. [Paper](https://doi.org/10.17605/osf.io/j9mfn). [Locator URL](https://osf.io/8mqx5).
- Row 1959, `es_value_o`: `0.05` → `0.036`. p. 1116, Study 2A, Results and Discussion, The Full Causal Chain (Serial Mediation). [Paper](https://doi.org/10.1093/jcr/ucz031).
- Row 1959, `es_value_r`: `0.080` → `0.15`. Replication Results, paragraph 1 (lines 63-67). [Locator URL](https://datacolada.org/89).
- Row 1959, `pval_value_r`: `0.05` → `0.038`. Replication Results, Figure: Original vs. Replication Results: Price-Quality Correlation. [Locator URL](https://datacolada.org/89).
- Row 1959, `reported_success`: `mixed` → `uninformative`. Replication Results, concluding section before Author feedback (lines 106, 119). [Locator URL](https://datacolada.org/89).
- Row 1968, `pval_value_r`: `0.887` → `0.649`. p. 4, Experiment 1, Results. [Paper](https://doi.org/10.3389/fpsyg.2015.01221).
- Row 1973, `reported_success`: `mixed` → `failed`. p. 462, Effect 19, Replication. [Paper](https://doi.org/10.1177/2515245918810225).
- Row 1987, `n_r`: `3582` → `3549`. p. 467, Section 28. [Paper](https://doi.org/10.1177/2515245918810225).
- Row 1990, `pval_value_r`: `None` → `< .001`. Preprint p. 17, Results, Paying to know, Between-subject design replication; Table 1, p. 9. [Paper](https://doi.org/10.1016/j.joep.2020.102350).
- Row 1990, `reported_success`: `mixed` → `successful`. Preprint p. 21, General Discussion, Replications results. [Paper](https://doi.org/10.1016/j.joep.2020.102350).
- Row 2010, `reported_success`: `successful` → `mixed`. p. 37. [Paper](https://doi.org/10.17605/osf.io/qswe3). [Locator URL](https://osf.io/u59ab).
- Row 2011, `reported_success`: `successful` → `mixed`. p. 38. [Paper](https://doi.org/10.17605/osf.io/qswe3). [Locator URL](https://osf.io/u59ab).
- Row 2012, `pval_value_r`: `None` → `< .001`. p. 30, Table 9; p. 41. [Paper](https://doi.org/10.17605/osf.io/qswe3). [Locator URL](https://osf.io/u59ab).
- Row 2026, `reported_success`: `mixed` → `failed`. p. 4, Table 1, Experiment 2, row 6; p. 6, Section 3.3. [Paper](https://doi.org/10.1016/j.joep.2018.12.001).
- Row 2032, `reported_success`: `failed` → `mixed`. p. 5, Table 1, Experiment 5; p. 6, Section 3.3. [Paper](https://doi.org/10.1016/j.joep.2018.12.001).
- Row 2122, `pval_value_o`: `0.001380362` → `< .001`. p. 41, Experiment 1, Product evaluations and thoughts, interdependent trendiness planned contrast. [Paper](https://doi.org/10.1509/jmkr.46.1.37).
- Row 2143, `pval_value_r`: `0.0174` → `0.018`. Replication result, paragraph 21. [Locator URL](https://osf.io/fgdxs).

## Unverified and skipped work

0 effects have no paper checkpoint yet. A checkpoint with unavailable or insufficient fields is not a verified effect.

103 fields exhausted the allowed adjudication attempts and remain unresolved. The remaining dispatch queue contains 0 fields in 0 source groups; after the dispatch cutoff these remain unverified. Failed or truncated replies establish no error unless an individual complete response passes source validation.
The separately authorised source follow-up has 0 additional fields awaiting validated adjudication. These remain unverified until their evidence and target identity pass review.

- original: done: 1721 sides.
- original: locator_insufficient: 439 sides.
- original: paper_unavailable: 4 sides.
- replication: done: 1744 sides.
- replication: locator_insufficient: 413 sides.
- replication: paper_unavailable: 7 sides.

Detailed access/target reasons are retained in the per-effect JSON checkpoints. Frequent access/target reasons:

- 15 sides: Asch (1946), Experiment I: warm versus cold personality lists; Table 2 reports 18 distinct trait-choice outcomes. The supplied generic description and Table 2/page 263 locator do not identify which outcome/test this audit_id targets.
- 15 sides: Pavlović OSF project 74892, First impression replication study (Asch, 1945, Experiment 1): author-provided First_impression_output.pdf contains multiple separate trait-choice contingency tables and Fisher exact tests. Page 2 contains the preceding generous-trait test results and the beginning of the wise-trait table; the supplied locator does not identify one outcome/test.
- 14 sides: Replication study 1: second-year police cadets, intervention versus active control, plus exploratory comparisons with senior officers; multiple outcomes and Time, Group/Sample, interaction, and within-group tests in Results. Supplied locator p. 8 and generic gaze-control/visual-attention description do not identify a unique outcome and test.
- 14 sides: Western university students; Table 2 multiple regressions report PMS and CMM semipartial correlations for multiple moral attitudes. Supplied p. 9 also discusses Table 3 models controlling general perfectionism; predictor, outcome, and model are not uniquely identified.
- 12 sides: Study 1 knowledge-ascription analyses: omnibus story-type test and several pairwise contrasts. The locator does not uniquely identify a contrast.
- 12 sides: Poole (2013), published article, PDF page 7 / printed page 399, Table 2: log annual wages, multinational spillovers 1996–2001. Four model columns report separate F tests for the difference between multinational and domestic spillover coefficients, plus separate coefficient estimates. The supplied locator identifies neither model column nor coefficient/test.
- 12 sides: Verified Haller, Flaherty and Balsvik (2023), DOI 10.18718/81781.29. Newly explicit Table A2 is located on printed p. 23. It reports log annual wage regressions in four specifications for Brazil, Ireland (2005-2010), Ireland (2011-2016), and Norway, with separate coefficient and coefficient-difference tests. The supplied p. 24/Table A2 locator identifies the table but does not identify a country/period, specification column, coefficient, or test; the neutral description is empty and study identifiers are null. No unique target test can be established.
- 11 sides: Experiment 2 identified, but the repeated generic description does not select uniquely among language-form omnibus, pooled contrast, and individual pairwise tests.
- 11 sides: Paper and authors supplementary pre-study report available. Supplied https://osf.io/nfskq is a file locator, but download returned HTTP 403; no retry. Neutral description repeated across 11 assigned IDs does not identify lab, pooled vs pairwise contrast, confirmatory vs extended pilot, or test. No mapping inferred from ID order.
- 10 sides: Locator does not uniquely distinguish a target contrast/outcome from multiple reported tests; no assignment inferred from input order.
- 10 sides: The identified 2014 primary replication article contains four replication samples: Study 1 online and laboratory, and Study 2 online and laboratory. Study 1 has perceived-brightness tests for two distinct samples. Study 2 has estimated-watts and three product-preference tests for each of two samples. The supplied neutral description, null replication study identifier, and page-only locator do not uniquely identify a sample and test.
- 10 sides: Original study 1: senior police officers, individual video-based intervention versus active control; multiple outcomes and Time, Group, Time × Group, and within-group tests in Results. Supplied locator p. 10 and generic gaze-control/visual-attention description do not identify a unique outcome and test.
- 9 sides: Verified replication title and full paper. Study 1 compares 33 adolescent girls with AN and 41 healthy controls; no separate major-depression group. Located emotion-discrimination accuracy analyses on printed p. 946 (PDF p. 4), but the supplied locator does not identify a unique test.
- 8 sides: Replication Experiment 1 object working memory. PDF p. 7 has Fig. 2 with three outcomes and Table 1 with condition, rotation, and condition-by-rotation tests for mental-rotation response time. Other Experiment 1 outcomes are analyzed separately in Tables 2 and 3 on PDF p. 8. The supplied locator does not identify a target outcome or model term. The final Experiment 1 participant sample is reported as 119 on PDF p. 3; this does not identify the target test.
- 8 sides: Experiment 1, outcome manipulation across Water, Movies, Sales and Nazi scenarios. Four scenario-specific t-tests share the supplied locator and description.

## Method and limits

Effect identifiers are one-based data-row indices, excluding the header (worksheet row = input_row_index + 1). T3 sanitisation and extraction workers used Codex gpt-6.1-sol with medium reasoning. Extraction workers received references, studies, neutral descriptions, requested metric labels, and sanitised page/table/primary-source URLs, with no shipped n, estimates, p-values or success verdicts. The first 20 sanitised descriptions and later batch samples were inspected. Original and replication statistics were extracted separately, with printed metric and bound type. Original statistics reproduced only in replication papers or summary tables remain unverified against the original primary source; their secondary evidence is retained. Comparisons require confident matching targets and validated source quotes. Non-obvious disagreements go to Gemini 4 Argon (High); obvious decisions retain a reason and evidence location.

The screen checks positive-integer n, p and r ranges, recognized F/t/chi-square/z reports, and non-nested Pearson r with coded analytic n. Missing tails are labelled as an assumed two-sided screen. The codebook does not enumerate every allowed metric, so unfamiliar labels are not declared invalid. No source-project success rule has been established for automatic significance/direction checks. Rounding intervals use stored cell strings; XLSX may already have lost printed precision. P-value formatting is normalised with exact decimal arithmetic, including scientific notation and strict bounds. Explicit metric synonyms are aligned without converting numbers; partial metrics and unspecified standardisation remain separate. Published corrections take precedence over superseded article text where directly verified. A prior blind target mismatch can be resolved by independent primary evidence confirming the shipped target value, while unresolved wrong-target proposed errors remain unverified.

Documented contrast direction can justify a sign reversal of the printed effect. In nested models, participant or cluster counts and repeated observations have distinct sample roles; an unidentified counting unit remains unverified. Inferred df or N annotations require positive contradictory evidence from the design, counts, reference distribution or reported p before being counted as errors.

Frozen input SHA256: `59545e3fc0c2979d97507097526319ec8c275aae3ac40c0d1a6d327492079e6b`. No dataset changes are made. Full texts are excluded from Git. See `run_log.md`, `consistency.csv`, `results.csv` and `extractions/` for decisions, diagnostics and short evidence quotes.
