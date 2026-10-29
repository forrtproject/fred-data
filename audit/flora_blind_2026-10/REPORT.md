# FLoRA blind audit — provisional

149 input rows have at least one confirmed field error; 1754 / 2818 rows are fully resolved. 813 blind targets have no proposed shipped counterpart; these are not errors by default.

This report is provisional until the parent finalizes the audit. Blind disagreement alone establishes no error. Agreements require supported identity and quotes found in saved text; confirmed errors require an obvious or Argon decision with a reason, location and verified quote. Quotation checks accept literal text with normalized spacing or the same text with line-end hyphenation removed; they do not repair words or mathematical signs.

## Coverage

Works: 2344 total; 2344 attempted; 2289 with verified saved text (1710 full text, 579 abstract); 2289 with validated usable coding. Rows fully resolved: 1754 / 2818.

Coverage is prioritized and depends on text access. This is not a representative sample. Rates use correct + confirmed-error rows as field-specific evaluable denominators. Bounds put every unverified row first outside, then inside the error count over all applicable input rows; they are sensitivity bounds, not binomial confidence intervals. Confidence is descriptive only. Study status is reported separately and does not change type agreement. Axis-specific rates below use rows shipped as reproductions; dependent outcome replacements after a type correction remain in results.csv and the error list.

## Confirmed field error rates

- type: 31 / 2294 (1.4%); 524 unverified; all-row unresolved bounds 1.1%–19.7% (N=2818)
- original: 14 / 2297 (0.6%); 521 unverified; all-row unresolved bounds 0.5%–19.0% (N=2818)
- outcome: 128 / 1767 (7.2%); 1051 unverified; all-row unresolved bounds 4.5%–41.8% (N=2818)
- outcome_computation: 21 / 176 (11.9%); 29 unverified; all-row unresolved bounds 10.2%–24.4% (N=205)
- outcome_robustness: 6 / 186 (3.2%); 19 unverified; all-row unresolved bounds 2.9%–12.2% (N=205)

### By source

- COS:
  - type: 1 / 604 (0.2%); 116 unverified; all-row unresolved bounds 0.1%–16.2% (N=720)
  - original: 0 / 606 (0.0%); 114 unverified; all-row unresolved bounds 0.0%–15.8% (N=720)
  - outcome: 11 / 394 (2.8%); 326 unverified; all-row unresolved bounds 1.5%–46.8% (N=720)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- SCORE:
  - type: 0 / 60 (0.0%); 28 unverified; all-row unresolved bounds 0.0%–31.8% (N=88)
  - original: 0 / 61 (0.0%); 27 unverified; all-row unresolved bounds 0.0%–30.7% (N=88)
  - outcome: 0 / 52 (0.0%); 36 unverified; all-row unresolved bounds 0.0%–40.9% (N=88)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- i4r:
  - type: 0 / 1 (0.0%); 0 unverified; all-row unresolved bounds 0.0%–0.0% (N=1)
  - original: 0 / 1 (0.0%); 0 unverified; all-row unresolved bounds 0.0%–0.0% (N=1)
  - outcome: 0 / 1 (0.0%); 0 unverified; all-row unresolved bounds 0.0%–0.0% (N=1)
  - outcome_computation: 0 / 1 (0.0%); 0 unverified; all-row unresolved bounds 0.0%–0.0% (N=1)
  - outcome_robustness: 0 / 1 (0.0%); 0 unverified; all-row unresolved bounds 0.0%–0.0% (N=1)
- openalex:
  - type: 4 / 219 (1.8%); 47 unverified; all-row unresolved bounds 1.5%–19.2% (N=266)
  - original: 1 / 221 (0.5%); 45 unverified; all-row unresolved bounds 0.4%–17.3% (N=266)
  - outcome: 7 / 179 (3.9%); 87 unverified; all-row unresolved bounds 2.6%–35.3% (N=266)
  - outcome_computation: 2 / 5 (40.0%); 2 unverified; all-row unresolved bounds 28.6%–57.1% (N=7)
  - outcome_robustness: 2 / 7 (28.6%); 0 unverified; all-row unresolved bounds 28.6%–28.6% (N=7)
- openalex_snapshot:
  - type: 1 / 75 (1.3%); 18 unverified; all-row unresolved bounds 1.1%–20.4% (N=93)
  - original: 1 / 76 (1.3%); 17 unverified; all-row unresolved bounds 1.1%–19.4% (N=93)
  - outcome: 0 / 57 (0.0%); 36 unverified; all-row unresolved bounds 0.0%–38.7% (N=93)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- replications:
  - type: 24 / 1151 (2.1%); 302 unverified; all-row unresolved bounds 1.7%–22.4% (N=1453)
  - original: 12 / 1145 (1.0%); 308 unverified; all-row unresolved bounds 0.8%–22.0% (N=1453)
  - outcome: 87 / 917 (9.5%); 536 unverified; all-row unresolved bounds 6.0%–42.9% (N=1453)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- reproductions:
  - type: 1 / 184 (0.5%); 13 unverified; all-row unresolved bounds 0.5%–7.1% (N=197)
  - original: 0 / 187 (0.0%); 10 unverified; all-row unresolved bounds 0.0%–5.1% (N=197)
  - outcome: 23 / 167 (13.8%); 30 unverified; all-row unresolved bounds 11.7%–26.9% (N=197)
  - outcome_computation: 19 / 170 (11.2%); 27 unverified; all-row unresolved bounds 9.6%–23.4% (N=197)
  - outcome_robustness: 4 / 178 (2.2%); 19 unverified; all-row unresolved bounds 2.0%–11.7% (N=197)

### By evidence_level

- abstract:
  - type: 3 / 380 (0.8%); 215 unverified; all-row unresolved bounds 0.5%–36.6% (N=595)
  - original: 0 / 383 (0.0%); 212 unverified; all-row unresolved bounds 0.0%–35.6% (N=595)
  - outcome: 5 / 261 (1.9%); 334 unverified; all-row unresolved bounds 0.8%–57.0% (N=595)
  - outcome_computation: 0 / 0 (not estimable); 7 unverified; all-row unresolved bounds 0.0%–100.0% (N=7)
  - outcome_robustness: 0 / 3 (0.0%); 4 unverified; all-row unresolved bounds 0.0%–57.1% (N=7)
- full_text:
  - type: 28 / 1914 (1.5%); 256 unverified; all-row unresolved bounds 1.3%–13.1% (N=2170)
  - original: 14 / 1914 (0.7%); 256 unverified; all-row unresolved bounds 0.6%–12.4% (N=2170)
  - outcome: 123 / 1506 (8.2%); 664 unverified; all-row unresolved bounds 5.7%–36.3% (N=2170)
  - outcome_computation: 21 / 176 (11.9%); 20 unverified; all-row unresolved bounds 10.7%–20.9% (N=196)
  - outcome_robustness: 6 / 183 (3.3%); 13 unverified; all-row unresolved bounds 3.1%–9.7% (N=196)
- none:
  - type: 0 / 0 (not estimable); 53 unverified; all-row unresolved bounds 0.0%–100.0% (N=53)
  - original: 0 / 0 (not estimable); 53 unverified; all-row unresolved bounds 0.0%–100.0% (N=53)
  - outcome: 0 / 0 (not estimable); 53 unverified; all-row unresolved bounds 0.0%–100.0% (N=53)
  - outcome_computation: 0 / 0 (not estimable); 2 unverified; all-row unresolved bounds 0.0%–100.0% (N=2)
  - outcome_robustness: 0 / 0 (not estimable); 2 unverified; all-row unresolved bounds 0.0%–100.0% (N=2)

## Every confirmed input-row error

Complete quotes, locations, reasons and corrected values are retained in [results.csv](results.csv), keyed by the immutable, zero-based input row index (0–2817).

- Row 14, [replicating work](https://doi.org/10.1007/s11469-021-00695-9): outcome: successful → mixed.
- Row 15, [replicating work](https://doi.org/10.1016/j.ijgo.2016.06.008): type: replication → not_a_replication.
- Row 17, [replicating work](https://doi.org/10.1080/08993408.2022.2071543): outcome: successful → mixed.
- Row 18, [replicating work](https://doi.org/10.1038/s41598-025-10331-4): original: 10.1037/a0010932 → Obedience To Authority: An Experimental View.
- Row 22, [replicating work](https://doi.org/10.1080/10986065.2020.1818467): outcome: successful → mixed.
- Row 37, [replicating work](https://doi.org/10.1186/ar3789): outcome: successful → mixed.
- Row 38, [replicating work](https://doi.org/10.1187/cbe.19-01-0028): outcome: successful → mixed.
- Row 55, [replicating work](https://doi.org/10.1176/ps.62.4.pss6204_0367): original: 10.1016/j.biopsych.2006.03.040 → 10.1037/a0018915.
- Row 56, [replicating work](https://doi.org/10.1371/journal.pone.0016144): outcome: successful → mixed.
- Row 64, [replicating work](https://doi.org/10.1080/01443410.2013.812615): outcome: successful → mixed.
- Row 65, [replicating work](https://doi.org/10.1080/02619768.2014.882308): outcome: successful → mixed.
- Row 67, [replicating work](https://doi.org/10.1017/s0142716414000137): outcome: successful → failed.
- Row 75, [replicating work](https://doi.org/10.1080/10584609.2014.914612): type: replication → not_a_replication.
- Row 76, [replicating work](https://doi.org/10.3389/fpsyg.2015.01755): outcome: successful → mixed.
- Row 77, [replicating work](https://doi.org/10.1080/16506073.2015.1015163): outcome: successful → mixed.
- Row 84, [replicating work](https://doi.org/10.1093/carcin/bgw047): outcome: successful → failed.
- Row 91, [replicating work](https://doi.org/10.1037/edu0000146): outcome: successful → mixed.
- Row 104, [replicating work](https://doi.org/10.1038/s41598-018-35209-6): original: 10.1016/j.neuroimage.2013.05.039 → 10.1073/pnas.0905267106.
- Row 106, [replicating work](https://doi.org/10.1093/scan/nsy030): outcome: successful → mixed.
- Row 107, [replicating work](https://doi.org/10.3389/fpsyg.2018.00540): type: replication → not_a_replication.
- Row 111, [replicating work](https://doi.org/10.1136/injuryprev-2018-043127): type: replication → not_a_replication.
- Row 121, [replicating work](https://doi.org/10.1177/1359104519838593): outcome: successful → mixed.
- Row 123, [replicating work](https://doi.org/10.1075/target.18159.ola): outcome: successful → mixed.
- Row 127, [replicating work](https://doi.org/10.1177/2165143420908286): original: 10.1177/016264340802300304 → Evaluation of a portable DVD player and system of least prompts to self-prompt cooking task completion by young adults with moderate intellectual disabilities.; outcome: successful → mixed.
- Row 129, [replicating work](https://doi.org/10.1111/jcal.12426): outcome: successful → mixed.
- Row 146, [replicating work](https://doi.org/10.1037/men0000301): outcome: successful → mixed.
- Row 147, [replicating work](https://doi.org/10.1002/smj.3453): outcome: successful → mixed.
- Row 152, [replicating work](https://doi.org/10.1002/aepp.13377): type: replication → reproduction; outcome: successful → outcome_computation: computationally reproducible; outcome_robustness: robust.
- Row 155, [replicating work](https://doi.org/10.2196/51056): outcome: successful → mixed.
- Row 160, [replicating work](https://doi.org/10.1186/s41239-025-00570-w): outcome: successful → mixed.
- Row 163, [replicating work](https://doi.org/10.2466/07.10.17.pr0.107.4.139-144): outcome: mixed → failed.
- Row 167, [replicating work](https://doi.org/10.1017/s0272263112000903): outcome: mixed → failed.
- Row 169, [replicating work](https://doi.org/10.1186/1744-8603-10-19): type: replication → not_a_replication.
- Row 172, [replicating work](https://doi.org/10.20429/ijsotl.2018.120107): outcome: mixed → failed.
- Row 173, [replicating work](https://doi.org/10.1007/s10648-023-09729-1): outcome: mixed → failed.
- Row 176, [replicating work](https://doi.org/10.21203/rs.3.rs-6613854/v1): outcome: mixed → successful.
- Row 177, [replicating work](https://doi.org/10.1186/1471-2415-14-140): original: 10.1038/ng.2578 → 10.1074/jbc.M111.275990.
- Row 180, [replicating work](https://doi.org/10.1523/jneurosci.3973-11.2012): outcome: mixed → statistically successful but flawed.
- Row 183, [replicating work](https://doi.org/10.7554/elife.34364): outcome: mixed → uninformative.
- Row 184, [replicating work](https://doi.org/10.1177/1948550618771003): outcome: mixed → successful.
- Row 192, [replicating work](https://doi.org/10.1177/15346501261416516): type: replication → not_a_replication.
- Row 194, [replicating work](https://doi.org/10.14324/111.444/ucloe.000051): outcome: mixed → uninformative.
- Row 195, [replicating work](https://doi.org/10.1080/02687038.2010.536841): original: 10.1038/nn1601 → 10.1177/0956797611404897; outcome: mixed → successful.
- Row 199, [replicating work](https://doi.org/10.1038/sj.npp.1300311): outcome: mixed → successful.
- Row 208, [replicating work](https://doi.org/10.3758/s13423-019-01708-4): outcome: mixed → failed.
- Row 225, [replicating work](https://doi.org/10.3389/fnins.2012.00115): type: replication → not_a_replication.
- Row 229, [replicating work](https://doi.org/10.1103/physrevstper.10.010110): type: replication → not_a_replication.
- Row 234, [replicating work](https://doi.org/10.1186/s13195-015-0154-x): outcome: mixed → successful.
- Row 238, [replicating work](https://doi.org/10.1525/collabra.97): outcome: mixed → successful.
- Row 242, [replicating work](https://doi.org/10.1371/journal.pone.0209704): type: replication → not_a_replication.
- Row 245, [replicating work](https://doi.org/10.1002/jts.22339): outcome: mixed → successful.
- Row 259, [replicating work](https://doi.org/10.3390/jcm10010052): outcome: mixed → successful.
- Row 261, [replicating work](https://doi.org/10.1111/lang.12438): original: 10.1017/s1366728920000280 → 10.1017/S0272263117000444.
- Row 265, [replicating work](https://doi.org/10.1016/j.ynirp.2022.100147): outcome: mixed → successful.
- Row 267, [replicating work](https://doi.org/10.1086/714812): type: replication → not_a_replication.
- Row 269, [replicating work](https://doi.org/10.1186/s12909-022-03665-4): outcome: mixed → successful.
- Row 276, [replicating work](https://doi.org/10.1017/jdm.2023.48): outcome: mixed → successful.
- Row 279, [replicating work](https://doi.org/10.1002/jclp.70017): outcome: mixed → failed.
- Row 281, [replicating work](https://doi.org/10.1177/15480518251379918): outcome: mixed → failed.
- Row 285, [replicating work](https://doi.org/10.1111/desc.13581): outcome: mixed → failed.
- Row 289, [replicating work](https://doi.org/10.1017/cnj.2023.13): original: 10.1017/s0047404500008472 → Grammatical ideology and its effect on speech.
- Row 291, [replicating work](https://doi.org/10.1037/xap0000270): outcome: failed → mixed.
- Row 292, [replicating work](https://doi.org/10.7554/elife.21634): outcome: failed → uninformative.
- Row 294, [replicating work](https://doi.org/10.1515/gcla-2014-0004): original: 10.7551/mitpress/4117.003.0006 → Sex, syntax, and semantics..
- Row 306, [replicating work](https://doi.org/10.13140/2.1.4432.0644): original: 10.1111/j.1745-6916.2006.00007.x → 10.1037/0022-3514.87.5.586.
- Row 313, [replicating work](https://doi.org/10.1038/s41398-021-01366-y): outcome: failed → mixed.
- Row 322, [replicating work](https://doi.org/10.1080/0003684042000229532): outcome: failed → statistically successful but flawed.
- Row 342, [replicating work](https://doi.org/10.1016/j.compedu.2017.05.013): outcome: failed → mixed.
- Row 346, [replicating work](https://doi.org/10.1177/2053168018787119): type: replication → reproduction; outcome: failed → outcome_computation: not checked; outcome_robustness: robust.
- Row 353, [replicating work](https://doi.org/10.3758/s13414-019-01890-6): outcome: failed → mixed.
- Row 361, [replicating work](https://doi.org/10.1080/20008198.2019.1705599): outcome: failed → statistically successful but flawed.
- Row 364, [replicating work](https://doi.org/10.1093/hcr/hqab013): outcome: failed → mixed.
- Row 365, [replicating work](https://doi.org/10.5964/jnc.7029): outcome: failed → mixed.
- Row 403, [replicating work](https://doi.org/10.1109/tse.2012.46): outcome: successful → mixed.
- Row 411, [replicating work](https://doi.org/10.1177/1745691614545653): outcome: successful → mixed.
- Row 416, [replicating work](https://doi.org/10.7554/elife.26030): outcome: successful → mixed.
- Row 422, [replicating work](https://doi.org/10.1007/s00426-019-01203-4): original: 10.1016/j.brat.2009.11.008 → 10.1177/0956797610384746; outcome: successful → mixed.
- Row 428, [replicating work](https://doi.org/10.1177/20531680231188262): original: 10.31235/osf.io/3ye4b → 10.1111/ajps.12412; outcome: successful → mixed.
- Row 430, [replicating work](https://doi.org/10.1111/padm.13031): outcome: successful → mixed.
- Row 432, [replicating work](https://doi.org/10.1111/jpr.70014): outcome: successful → mixed.
- Row 448, [replicating work](https://doi.org/10.31234/osf.io/ydgh9_v2): outcome: successful → mixed.
- Row 451, [replicating work](https://doi.org/10.1093/alcalc/agag013): type: replication → reproduction; outcome: successful → outcome_computation: cannot_be_determined; outcome_robustness: robustness challenges.
- Row 452, [replicating work](https://doi.org/10.48550/arxiv.2603.15935): outcome: successful → mixed.
- Row 453, [replicating work](https://doi.org/10.1016/j.jenvp.2026.102956): outcome: successful → mixed.
- Row 467, [replicating work](https://doi.org/10.7554/elife.33468): outcome: mixed → failed.
- Row 471, [replicating work](https://doi.org/10.1037/cdp0000775): outcome: mixed → successful.
- Row 485, [replicating work](https://doi.org/10.1037/pspa0000121): outcome: mixed → successful.
- Row 491, [replicating work](https://doi.org/10.7554/elife.73430): outcome: mixed → successful.
- Row 505, [replicating work](https://doi.org/10.1073/pnas.2103313118): outcome: failed → successful.
- Row 512, [replicating work](https://doi.org/10.1177/0038040718801760): outcome: failed → mixed.
- Row 524, [replicating work](https://doi.org/10.2337/db13-1435): outcome: failed → mixed.
- Row 537, [replicating work](https://doi.org/10.7554/elife.56651): outcome: failed → mixed.
- Row 736, [replicating work](https://doi.org/10.1017/s0261444818000368): outcome: successful → mixed.
- Row 823, [replicating work](https://doi.org/10.1016/j.heliyon.2024.e32467): outcome: successful → mixed.
- Row 833, [replicating work](https://doi.org/10.4054/demres.2025.53.29): type: replication → reproduction.
- Row 835, [replicating work](https://doi.org/10.1257/mac.6.3.1): type: replication → reproduction; outcome: mixed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 929, [replicating work](https://doi.org/10.1017/ssh.2017.27): type: replication → reproduction; outcome: mixed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 996, [replicating work](https://doi.org/10.48550/arxiv.2303.08577): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1005, [replicating work](https://doi.org/10.29338/wp2019-15): type: replication → reproduction; outcome: failed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 1024, [replicating work](https://doi.org/10.18718/81781.7): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1146, [replicating work](https://doi.org/10.5018/economics-ejournal.ja.2017-13): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1184, [replicating work](https://doi.org/10.1080/01434632.2020.1730861): outcome: failed → mixed.
- Row 1206, [replicating work](https://doi.org/10.1017/pan.2024.7): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1216, [replicating work](https://doi.org/10.32388/e37rhf): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1269, [replicating work](https://doi.org/10.1111/ssqu.13292): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1292, [replicating work](https://doi.org/10.1515/jbnst-2025-0084): type: replication → reproduction; outcome: mixed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 1347, [replicating work](https://doi.org/10.31234/osf.io/weu9m_v1): outcome computation: computationally reproducible.
- Row 1351, [replicating work](https://doi.org/10.17605/osf.io/fpuh3): outcome computation: computationally reproducible.
- Row 1366, [replicating work](https://doi.org/10.17605/osf.io/x9pd3): outcome computation: computationally reproducible.
- Row 1367, [replicating work](https://doi.org/10.17605/osf.io/dcez6): outcome computation: computational issues.
- Row 1387, [replicating work](https://doi.org/10.17605/osf.io/namvy): outcome computation: computationally reproducible.
- Row 1389, [replicating work](https://doi.org/10.17605/osf.io/w8n3s): outcome computation: computational issues.
- Row 1427, [replicating work](https://doi.org/10.17605/osf.io/5ywth): outcome computation: computational issues.
- Row 1439, [replicating work](https://doi.org/10.17605/osf.io/da26y): type: reproduction → replication; outcome: computationally reproducible, robustness not checked → successful.
- Row 1450, [replicating work](https://doi.org/10.17605/osf.io/nekdp): outcome computation: computational issues; outcome robustness: robust.
- Row 1458, [replicating work](https://doi.org/10.17605/osf.io/8wf3h): outcome computation: technical failure.
- Row 1479, [replicating work](https://doi.org/10.1073/pnas.2103313118): outcome: mixed → failed.
- Row 1717, [replicating work](https://doi.org/10.1098/rsos.231240): outcome: failed → uninformative.
- Row 1836, [replicating work](https://doi.org/10.1073/pnas.2103313118): outcome: mixed → failed.
- Row 1940, [replicating work](https://doi.org/10.1098/rsos.231240): outcome: uninformative → mixed.
- Row 1986, [replicating work](https://doi.org/10.1098/rsos.231240): outcome: successful → mixed.
- Row 2042, [replicating work](https://doi.org/10.1098/rsos.231240): outcome: mixed → failed.
- Row 2046, [replicating work](https://doi.org/10.1098/rsos.231240): outcome: successful → mixed.
- Row 2049, [replicating work](https://doi.org/10.1073/pnas.2103313118): outcome: mixed → successful.
- Row 2068, [replicating work](https://doi.org/10.1098/rsos.231240): outcome: successful → mixed.
- Row 2082, [replicating work](https://doi.org/10.1098/rsos.231240): outcome: failed → successful.
- Row 2125, [replicating work](https://doi.org/10.3389/fped.2021.590040): type: replication → reproduction; outcome: failed → outcome_computation: not checked; outcome_robustness: robustness challenges.
- Row 2166, [replicating work](https://doi.org/10.7275/11867619): type: replication → reproduction; outcome: failed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 2170, [replicating work](https://doi.org/10.31235/osf.io/zugae): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 2238, [replicating work](https://doi.org/10.1002/jae.2922): type: replication → reproduction; outcome: failed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 2269, [replicating work](https://doi.org/10.1002/jae.2861): outcome robustness: robust.
- Row 2299, [replicating work](https://doi.org/10.1371/journal.pone.0253023): type: replication → reproduction; outcome: successful → outcome_computation: computational issues; outcome_robustness: robust.
- Row 2308, [replicating work](https://doi.org/10.1111/nana.12722): outcome computation: computationally reproducible; outcome robustness: robustness challenges.
- Row 2334, [replicating work](https://doi.org/10.5334/irsp.546): outcome computation: not checked.
- Row 2418, [replicating work](https://doi.org/10.1017/s0142716414000137): original: 10.1017/s0142716400010845 → 10.1017/S0142716409990014.
- Row 2429, [replicating work](https://doi.org/10.20381/ruor-28430): type: replication → reproduction; original: 10.7326/0003-4819-127-1-199707010-00007 → Effectiveness of different adjunctive interventions in the management of orthodontically induced white spot lesions: A systematic review of systematic reviews and meta-analyses..
- Row 2630, [replicating work](https://osf.io/7qv89) (DOI unavailable): outcome computation: computational issues.
- Row 2632, [replicating work](https://econjwatch.org/file+download/538/findlaysantosmay2012.pdf) (DOI unavailable): outcome computation: computationally reproducible.
- Row 2633, [replicating work](https://doi.org/10.48550/arxiv.2604.00848): outcome robustness: robust.
- Row 2651, [replicating work](https://osf.io/a672c/) (DOI unavailable): outcome computation: computationally reproducible.
- Row 2652, [replicating work](https://github.com/atyho/ottawa-replication-games-2023/blob/main/ho_huynh_rea_replication_report.pdf) (DOI unavailable): outcome computation: computationally reproducible.
- Row 2654, [replicating work](https://osf.io/xadb6/) (DOI unavailable): outcome computation: computationally reproducible.
- Row 2655, [replicating work](https://hdl.handle.net/10419/303190) (DOI unavailable): outcome computation: computational issues.
- Row 2658, [replicating work](https://osf.io/rt48s/) (DOI unavailable): outcome computation: computationally reproducible.
- Row 2662, [replicating work](https://hdl.handle.net/10419/276960) (DOI unavailable): outcome computation: computationally reproducible.
- Row 2663, [replicating work](https://hdl.handle.net/10419/268943) (DOI unavailable): outcome computation: computationally reproducible.
- Row 2665, [replicating work](https://hdl.handle.net/10419/280748) (DOI unavailable): outcome computation: computationally reproducible.
- Row 2674, [replicating work](https://hdl.handle.net/10419/266385) (DOI unavailable): outcome robustness: robustness challenges.
- Row 2697, [replicating work](https://osf.io/exb67/) (DOI unavailable): outcome robustness: robust.

Source-version limits: Row 2238 was checked against the verified 2020 working paper; the final 2022 article was not obtained. Row 929 was checked against the verified 2015 draft; the final 2017 article was not obtained. These judgments describe the supplied versions; changes in unseen final versions cannot be ruled out.

## Unmatched blind targets

- Confirmed missing target: Conformity and Character; work [replicating work](https://doi.org/10.1371/journal.pone.0294325), target 6 (argon).
- Confirmed missing target: [The effects of information and social conformity on opinion change](https://doi.org/10.1371/journal.pone.0196600); work [replicating work](https://doi.org/10.1371/journal.pone.0294325), target 7 (argon).
- Confirmed missing target: [Knowing what to think by knowing who you are: Self-categorisation and the nature of norm formation, conformity and group polarisation](https://doi.org/10.1111/j.2044-8309.1990.tb00892.x); work [replicating work](https://doi.org/10.31820/pt.28.3.7), target 1 (argon).
- Confirmed missing target: Do Get-Out-the-Vote Calls Reduce Turnout? The Importance of Statistical Methods for Field Experiments.; work [replicating work](https://doi.org/10.1017/s000305540505166x), target 1 (argon).
- Confirmed missing target: Common variants on 9q22.33 and 14q13.3 predispose to thyroid cancer in European populations.; work [replicating work](https://doi.org/10.1093/carcin/bgw047), target 0 (argon).
- Confirmed missing target: The FOXE1 locus is a major genetic determinant for radiation-related thyroid carcinoma in Chernobyl.; work [replicating work](https://doi.org/10.1093/carcin/bgw047), target 1 (argon).
- Confirmed missing target: Genome-wide association study on differentiated thyroid cancer.; work [replicating work](https://doi.org/10.1093/carcin/bgw047), target 2 (argon).
- Confirmed missing target: The variant rs1867277 in FOXE1 gene confers thyroid cancer susceptibility through the recruitment of USF1/USF2 transcription factors.; work [replicating work](https://doi.org/10.1093/carcin/bgw047), target 3 (argon).
- Confirmed missing target: Common obesity-related genetic variants and papillary thyroid cancer risk.; work [replicating work](https://doi.org/10.1093/carcin/bgw047), target 5 (argon).
- Confirmed missing target: Common genetic variants in the 8q24 region and risk of papillary thyroid cancer.; work [replicating work](https://doi.org/10.1093/carcin/bgw047), target 6 (argon).
- Confirmed missing target: Common single nucleotide polymorphisms in genes related to immune function and risk of papillary thyroid cancer.; work [replicating work](https://doi.org/10.1093/carcin/bgw047), target 9 (argon).
- Confirmed missing target: [Enhancing interest and performance with a utility value intervention.](https://doi.org/10.1037/a0019506); work [replicating work](https://doi.org/10.1037/edu0000146), target 1 (argon).
- Confirmed missing target: Replications in Psychology Research; work [replicating work](https://doi.org/10.1075/target.18159.ola), target 0 (argon).
- Confirmed missing target: [Anxiety, depression, traumatic stress and COVID-19-related anxiety in the UK general population during the COVID-19 pandemic.](https://doi.org/10.1192/bjo.2020.109); work [replicating work](https://doi.org/10.3390/jcm10010052), target 0 (argon).
- Confirmed missing target: Career mobility, job match, and overeducation; work [replicating work](https://doi.org/10.1080/0003684042000229532), target 1 (argon).
- Confirmed missing target: [Children's understanding of counting](https://doi.org/10.1016/0010-0277(90)90003-3); work [replicating work](https://doi.org/10.5964/jnc.7029), target 0 (argon).
- Confirmed missing target: [A chromatin-mediated reversible drug-tolerant state in cancer cell subpopulations](https://doi.org/10.1016/j.cell.2010.02.027); work [replicating work](https://doi.org/10.7554/elife.73430), target 0 (argon).
- Confirmed missing target: [Senescence surveillance of pre-malignant hepatocytes limits liver cancer development](https://doi.org/10.1038/nature10599); work [replicating work](https://doi.org/10.7554/elife.73430), target 5 (argon).
- Confirmed missing target: Association of the FOXO3A locus with extreme longevity in a southern Italian centenarian study; work [replicating work](https://doi.org/10.1111/j.1474-9726.2010.00627.x), target 1 (argon).
- Confirmed missing target: Association of FOXO3A variation with human longevity confirmed in German centenarians; work [replicating work](https://doi.org/10.1111/j.1474-9726.2010.00627.x), target 2 (argon).
- Confirmed missing target: Genetic association of FOXO1A and FOXO3A with longevity trait in Han Chinese populations; work [replicating work](https://doi.org/10.1111/j.1474-9726.2010.00627.x), target 3 (argon).
- Confirmed missing target: Association of common genetic variation in the insulin ⁄ IGF1 signaling pathway with human longevity; work [replicating work](https://doi.org/10.1111/j.1474-9726.2010.00627.x), target 4 (argon).
- Confirmed missing target: [Registered replication report: Strack, Martin, & Stepper (1988).](https://doi.org/10.1177/1745691616674458); work [replicating work](https://doi.org/10.1037/pspa0000121), target 1 (argon).
- Confirmed missing target: Fernbach; Kan; Lynch (2015); work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 7 (argon).
- Confirmed missing target: Reframing the ordinary: Imagining time as scarce increases well-being.; work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 9 (argon).
- Confirmed missing target: Evidence for opportunity cost neglect in the poor.; work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 14 (argon).
- Confirmed missing target: Self-awareness and other-awareness II: Mirror self-recognition, social contingency awareness, and synchronic imitation.; work [replicating work](https://doi.org/10.1177/0022022110381114), target 1 (argon).
- Confirmed missing target: Self-awareness in human and chimpanzee infants: What is measured and what is meant by the mark and mirror test?; work [replicating work](https://doi.org/10.1177/0022022110381114), target 2 (argon).
- Confirmed missing target: Development of self-recognition in the infant.; work [replicating work](https://doi.org/10.1177/0022022110381114), target 3 (argon).
- Confirmed missing target: Social cognition and the acquisition of self.; work [replicating work](https://doi.org/10.1177/0022022110381114), target 4 (argon).
- Confirmed missing target: Development of self-recognition, personal pronoun use, and pretend play during the 2nd year.; work [replicating work](https://doi.org/10.1177/0022022110381114), target 5 (argon).
- Confirmed missing target: A longitudinal investigation of self-other discrimination and the emergence of mirror self-recognition.; work [replicating work](https://doi.org/10.1177/0022022110381114), target 6 (argon).
- Confirmed missing target: Mirror-image response during the first two years of life.; work [replicating work](https://doi.org/10.1177/0022022110381114), target 7 (argon).
- Confirmed missing target: How Elastic Are Preferences for Redistribution? Evidence from Randomized Survey Experiments.; work [replicating work](https://doi.org/10.1353/eca.2016.0000), target 0 (argon).
- Confirmed missing target: Do arthroscopic and open stabilization techniques restore equivalent stability to the shoulder in the setting of anterior glenohumeral instability? a systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 1 (argon).
- Confirmed missing target: A case study of discordant overlapping meta-analyses: vitamin d supplements and fracture.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 2 (argon).
- Confirmed missing target: Patellar resurfacing versus patellar retention in primary total knee arthroplasty: a systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 3 (argon).
- Confirmed missing target: Does operative treatment of  rst-time patellar dislocations lead to increased patellofemoral stability? A systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 4 (argon).
- Confirmed missing target: Intra-articular platelet-rich plasma injection for knee osteoarthritis: a summary of meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 5 (argon).
- Confirmed missing target: Is unilateral percutaneous kyphoplasty superior to bilateral percutaneous kyphoplasty for osteoporotic vertebral compression fractures? Evidence from a systematic review of discordant meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 6 (argon).
- Confirmed missing target: Is intramedullary  xation of displaced midshaft clavicle fracture superior to plate  xation? Evidence from a systematic review of discordant meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 7 (argon).
- Confirmed missing target: Laparoscopic cholecystectomy for acute cholecystitis: early or delayed?: Evidence from a systematic review of discordant meta- analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 8 (argon).
- Confirmed missing target: Surgical Versus Conservative Treatments for Displaced Midshaft Clavicular Fractures: A Systematic Review of Overlapping Meta-Analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 9 (argon).
- Confirmed missing target: Overlapping systematic reviews of anterior cruciate ligament reconstruction comparing hamstring autograft with bone-patellar tendon-bone autograft: why are they different? Journal of Bone & Joint Surgery - American Volume, 2007.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 10 (argon).
- Confirmed missing target: Is double-row rotator cuff repair clinically superior to single-row rotator cuff repair: a systematic review of overlapping meta- analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 11 (argon).
- Confirmed missing target: Unilateral versus bilateral percutaneous balloon kyphoplasty for osteoporotic vertebral compression fractures: A systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 12 (argon).
- Confirmed missing target: Intra-articular hyaluronic acid in treating knee osteoarthritis: a PRISMA-compliant systematic review of overlapping meta-analysis.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 13 (argon).
- Confirmed missing target: Does double-bundle anterior cruciate ligament reconstruction improve postoperative knee stability compared with single-bundle techniques? A systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 14 (argon).
- Confirmed missing target: Early versus delayed motion after rotator cuff repair: a systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 15 (argon).
- Confirmed missing target: FokI as a genetic factor of intervertebral disc degeneration: a PRISMA-compliant systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 16 (argon).
- Confirmed missing target: Unilateral versus bilateral balloon kyphoplasty for osteoporotic vertebral compression fractures: a systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 17 (argon).
- Confirmed missing target: Surgical and Non‐Surgical Treatment for 3‐Part and 4‐Part Fractures of the Proximal Humerus: A Systematic Review of Overlapping Meta‐Analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 18 (argon).
- Confirmed missing target: Intramedullary nail versus plate  xation for humeral shaft fractures: a systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 19 (argon).
- Confirmed missing target: Shenyi Capsule ((cid:0)(cid:0)(cid:0)(cid:0)) plus chemotherapy versus chemotherapy for non-small cell lung cancer: a systematic review of overlapping meta-analyses.; work [replicating work](https://doi.org/10.20381/ruor-28430), target 20 (argon).
- Confirmed missing target: [The effects of torture: Two community studies](https://doi.org/10.1207/s15327949pac1203_1); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 0 (argon).
- Confirmed missing target: [A multivariate contextual analysis of torture and cruel, inhuman, and degrading treatments: Implications for an evidence-based definition of torture](https://doi.org/10.1037/a0015681); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 2 (argon).
- Confirmed missing target: [Classifying the torture experiences of refugees living in the United States](https://doi.org/10.1177/0886260506294999); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 3 (argon).
- Confirmed missing target: [Nature of torture, PTSD, and somatic symptoms among political ex-prisoners](https://doi.org/10.1002/jts.20541); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 4 (argon).
682 unmatched blind targets remain unverified. Ambiguous proposed pairs remain in results.csv with flags and unverified verdicts.

## Skips and validation issues

- blinding compromised; coding excluded: 3 works.
- no_text: 43 works.
- paper identity conflict; coding excluded: 8 works.
- source scope incomplete; coding excluded: 1 works.
- Argon 04117bda0ee9a4bf: unresolved after 2 attempts; invalid decision or quote: outcome. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 186c024fa1d798a4: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 2736b815e9f115a4: unresolved after 2 attempts; Unterminated string starting at: line 274 column 17 (char 26129). 25 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 5b3bc0521d2f9aa1: unresolved after 2 attempts; invalid decision or quote: original. 5 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 6c8ce5072ad5bef2: unresolved after 2 attempts; invalid decision or quote: original. 2 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 73bcc3e73f111e2c: unresolved after 2 attempts; invalid decision or quote: type. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 7c772579daf4141a: unresolved after 2 attempts; invalid decision or quote: type. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 9b3c6d39a871d365: unresolved after 2 attempts; invalid decision or quote: outcome. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon b73243da6a1469dd: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon d004173d837cb2ee: unresolved after 2 attempts; failure. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon d8b67a992ec30af2: unresolved after 2 attempts; Second/final response contains unescaped quotation marks in its reason, so no complete valid JSON decision object can be decoded. No JSON repair or third call. The prior count-based verdict remains held; outcome unverified.. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon dd0a356e6efa9ef9: unresolved after 2 attempts; The final review overturns the extension/background exclusion for the two political targets and identifies individual-difference findings as re-tested too. The remaining first-review exclusions used the same motivation/extension rationale without independently settling each specific prior finding. Parent withholds those nine exclusions rather than certifying absence of omissions. Two calls exhausted; no third. This does not establish nine additional omissions.. 4 independently valid field decisions recovered; remaining fields stay unverified.
- Argon ed1f7b7135e869e8: unresolved after 2 attempts; Read-only CLI auto-denied command permission on both attempts; no valid JSON response.. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon f4ef4cba54e4ea6b: unresolved after 2 attempts; invalid decision or quote: outcome. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon f8c599bb24ccfef4: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon ff94f0e817af2f69: unresolved after 2 attempts; invalid decision or quote: type. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Blinding incidents affected 13 works; excluded judgments remain quarantined. Only independent fresh-child retries enter primary results; exhausted retries remain unverified. See blinding_incidents.json and post_exposure_exclusions.json for the complete record.

## Time per work

Elapsed time supplied for 2340 / 2344 works; missing times are not imputed. Times describe final saved checkpoints and exclude earlier failed or excluded attempts; this is worker time, not wall-clock audit duration.
1 reported timing correction(s) are applied from [timing_corrections.json](timing_corrections.json); the original checkpoint times and correction bases remain in work_times.csv. Clock bounds are reported as bounds, not exact measurements.
Sum of reported final-checkpoint times: 164198.3 seconds.
Per-work elapsed time and skips are recorded in [work_times.csv](work_times.csv).
