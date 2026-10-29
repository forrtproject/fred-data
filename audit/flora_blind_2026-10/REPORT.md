# FLoRA blind audit — provisional

This report is provisional until the parent finalizes the audit. Blind disagreement alone establishes no error. Agreements require supported identity and quotes found in saved text; confirmed errors require an obvious or Argon decision with a reason, location and verified quote. Quotation checks accept literal text with normalized spacing or the same text with line-end hyphenation removed; they do not repair words or mathematical signs.

77 input rows have at least one confirmed field error; 1674 / 2818 rows are fully resolved. 814 blind targets have no proposed shipped counterpart; these are not errors by default.

## Coverage

Works: 2344 total; 2344 attempted; 2289 with verified saved text (1710 full text, 579 abstract); 2289 with validated usable coding. Rows fully resolved: 1674 / 2818.

Coverage is prioritized and depends on text access. This is not a representative sample. Rates use correct + confirmed-error rows as field-specific evaluable denominators. Bounds put every unverified row first outside, then inside the error count over all applicable input rows; they are sensitivity bounds, not binomial confidence intervals. Confidence is descriptive only. Study status is reported separately and does not change type agreement.

## Confirmed field error rates

- type: 19 / 2274 (0.8%); 544 unverified; all-row unresolved bounds 0.7%–20.0% (N=2818)
- original: 10 / 2291 (0.4%); 527 unverified; all-row unresolved bounds 0.4%–19.1% (N=2818)
- outcome: 65 / 1687 (3.9%); 1131 unverified; all-row unresolved bounds 2.3%–42.4% (N=2818)
- outcome_computation: 9 / 161 (5.6%); 44 unverified; all-row unresolved bounds 4.4%–25.9% (N=205)
- outcome_robustness: 3 / 181 (1.7%); 24 unverified; all-row unresolved bounds 1.5%–13.2% (N=205)

### By source

- COS:
  - type: 1 / 605 (0.2%); 115 unverified; all-row unresolved bounds 0.1%–16.1% (N=720)
  - original: 0 / 607 (0.0%); 113 unverified; all-row unresolved bounds 0.0%–15.7% (N=720)
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
  - type: 3 / 214 (1.4%); 52 unverified; all-row unresolved bounds 1.1%–20.7% (N=266)
  - original: 0 / 218 (0.0%); 48 unverified; all-row unresolved bounds 0.0%–18.0% (N=266)
  - outcome: 3 / 172 (1.7%); 94 unverified; all-row unresolved bounds 1.1%–36.5% (N=266)
  - outcome_computation: 0 / 3 (0.0%); 4 unverified; all-row unresolved bounds 0.0%–57.1% (N=7)
  - outcome_robustness: 0 / 5 (0.0%); 2 unverified; all-row unresolved bounds 0.0%–28.6% (N=7)
- openalex_snapshot:
  - type: 0 / 74 (0.0%); 19 unverified; all-row unresolved bounds 0.0%–20.4% (N=93)
  - original: 0 / 75 (0.0%); 18 unverified; all-row unresolved bounds 0.0%–19.4% (N=93)
  - outcome: 0 / 57 (0.0%); 36 unverified; all-row unresolved bounds 0.0%–38.7% (N=93)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- replications:
  - type: 15 / 1138 (1.3%); 315 unverified; all-row unresolved bounds 1.0%–22.7% (N=1453)
  - original: 10 / 1142 (0.9%); 311 unverified; all-row unresolved bounds 0.7%–22.1% (N=1453)
  - outcome: 40 / 859 (4.7%); 594 unverified; all-row unresolved bounds 2.8%–43.6% (N=1453)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- reproductions:
  - type: 0 / 182 (0.0%); 15 unverified; all-row unresolved bounds 0.0%–7.6% (N=197)
  - original: 0 / 187 (0.0%); 10 unverified; all-row unresolved bounds 0.0%–5.1% (N=197)
  - outcome: 11 / 152 (7.2%); 45 unverified; all-row unresolved bounds 5.6%–28.4% (N=197)
  - outcome_computation: 9 / 157 (5.7%); 40 unverified; all-row unresolved bounds 4.6%–24.9% (N=197)
  - outcome_robustness: 3 / 175 (1.7%); 22 unverified; all-row unresolved bounds 1.5%–12.7% (N=197)

### By evidence_level

- abstract:
  - type: 3 / 380 (0.8%); 215 unverified; all-row unresolved bounds 0.5%–36.6% (N=595)
  - original: 0 / 383 (0.0%); 212 unverified; all-row unresolved bounds 0.0%–35.6% (N=595)
  - outcome: 5 / 261 (1.9%); 334 unverified; all-row unresolved bounds 0.8%–57.0% (N=595)
  - outcome_computation: 0 / 0 (not estimable); 7 unverified; all-row unresolved bounds 0.0%–100.0% (N=7)
  - outcome_robustness: 0 / 3 (0.0%); 4 unverified; all-row unresolved bounds 0.0%–57.1% (N=7)
- full_text:
  - type: 16 / 1894 (0.8%); 276 unverified; all-row unresolved bounds 0.7%–13.5% (N=2170)
  - original: 10 / 1908 (0.5%); 262 unverified; all-row unresolved bounds 0.5%–12.5% (N=2170)
  - outcome: 60 / 1426 (4.2%); 744 unverified; all-row unresolved bounds 2.8%–37.1% (N=2170)
  - outcome_computation: 9 / 161 (5.6%); 35 unverified; all-row unresolved bounds 4.6%–22.4% (N=196)
  - outcome_robustness: 3 / 178 (1.7%); 18 unverified; all-row unresolved bounds 1.5%–10.7% (N=196)
- none:
  - type: 0 / 0 (not estimable); 53 unverified; all-row unresolved bounds 0.0%–100.0% (N=53)
  - original: 0 / 0 (not estimable); 53 unverified; all-row unresolved bounds 0.0%–100.0% (N=53)
  - outcome: 0 / 0 (not estimable); 53 unverified; all-row unresolved bounds 0.0%–100.0% (N=53)
  - outcome_computation: 0 / 0 (not estimable); 2 unverified; all-row unresolved bounds 0.0%–100.0% (N=2)
  - outcome_robustness: 0 / 0 (not estimable); 2 unverified; all-row unresolved bounds 0.0%–100.0% (N=2)

## Every confirmed input-row error

Complete quotes, locations, reasons and corrected values are retained in [results.csv](results.csv), keyed by the immutable input row index.

- Row 14, [replicating work](https://doi.org/10.1007/s11469-021-00695-9): outcome: successful → mixed.
- Row 17, [replicating work](https://doi.org/10.1080/08993408.2022.2071543): outcome: successful → mixed.
- Row 18, [replicating work](https://doi.org/10.1038/s41598-025-10331-4): original: 10.1037/a0010932 → Obedience To Authority: An Experimental View.
- Row 22, [replicating work](https://doi.org/10.1080/10986065.2020.1818467): outcome: successful → mixed.
- Row 37, [replicating work](https://doi.org/10.1186/ar3789): outcome: successful → mixed.
- Row 55, [replicating work](https://doi.org/10.1176/ps.62.4.pss6204_0367): original: 10.1016/j.biopsych.2006.03.040 → 10.1037/a0018915.
- Row 56, [replicating work](https://doi.org/10.1371/journal.pone.0016144): outcome: successful → mixed.
- Row 64, [replicating work](https://doi.org/10.1080/01443410.2013.812615): outcome: successful → mixed.
- Row 65, [replicating work](https://doi.org/10.1080/02619768.2014.882308): outcome: successful → mixed.
- Row 77, [replicating work](https://doi.org/10.1080/16506073.2015.1015163): outcome: successful → mixed.
- Row 91, [replicating work](https://doi.org/10.1037/edu0000146): outcome: successful → mixed.
- Row 104, [replicating work](https://doi.org/10.1038/s41598-018-35209-6): original: 10.1016/j.neuroimage.2013.05.039 → 10.1073/pnas.0905267106.
- Row 106, [replicating work](https://doi.org/10.1093/scan/nsy030): outcome: successful → mixed.
- Row 111, [replicating work](https://doi.org/10.1136/injuryprev-2018-043127): type: replication → not_a_replication.
- Row 123, [replicating work](https://doi.org/10.1075/target.18159.ola): outcome: successful → mixed.
- Row 127, [replicating work](https://doi.org/10.1177/2165143420908286): original: 10.1177/016264340802300304 → Evaluation of a portable DVD player and system of least prompts to self-prompt cooking task completion by young adults with moderate intellectual disabilities.; outcome: successful → mixed.
- Row 129, [replicating work](https://doi.org/10.1111/jcal.12426): outcome: successful → mixed.
- Row 146, [replicating work](https://doi.org/10.1037/men0000301): outcome: successful → mixed.
- Row 152, [replicating work](https://doi.org/10.1002/aepp.13377): type: replication → reproduction; outcome: successful → outcome_computation: computationally reproducible; outcome_robustness: robust.
- Row 155, [replicating work](https://doi.org/10.2196/51056): outcome: successful → mixed.
- Row 163, [replicating work](https://doi.org/10.2466/07.10.17.pr0.107.4.139-144): outcome: mixed → failed.
- Row 167, [replicating work](https://doi.org/10.1017/s0272263112000903): outcome: mixed → failed.
- Row 172, [replicating work](https://doi.org/10.20429/ijsotl.2018.120107): outcome: mixed → failed.
- Row 173, [replicating work](https://doi.org/10.1007/s10648-023-09729-1): outcome: mixed → failed.
- Row 176, [replicating work](https://doi.org/10.21203/rs.3.rs-6613854/v1): outcome: mixed → successful.
- Row 177, [replicating work](https://doi.org/10.1186/1471-2415-14-140): original: 10.1038/ng.2578 → 10.1074/jbc.M111.275990.
- Row 184, [replicating work](https://doi.org/10.1177/1948550618771003): outcome: mixed → successful.
- Row 195, [replicating work](https://doi.org/10.1080/02687038.2010.536841): original: 10.1038/nn1601 → 10.1177/0956797611404897; outcome: mixed → successful.
- Row 199, [replicating work](https://doi.org/10.1038/sj.npp.1300311): outcome: mixed → successful.
- Row 229, [replicating work](https://doi.org/10.1103/physrevstper.10.010110): type: replication → not_a_replication.
- Row 242, [replicating work](https://doi.org/10.1371/journal.pone.0209704): type: replication → not_a_replication.
- Row 261, [replicating work](https://doi.org/10.1111/lang.12438): original: 10.1017/s1366728920000280 → 10.1017/S0272263117000444.
- Row 279, [replicating work](https://doi.org/10.1002/jclp.70017): outcome: mixed → failed.
- Row 289, [replicating work](https://doi.org/10.1017/cnj.2023.13): original: 10.1017/s0047404500008472 → Grammatical ideology and its effect on speech.
- Row 294, [replicating work](https://doi.org/10.1515/gcla-2014-0004): original: 10.7551/mitpress/4117.003.0006 → Sex, syntax, and semantics..
- Row 306, [replicating work](https://doi.org/10.13140/2.1.4432.0644): original: 10.1111/j.1745-6916.2006.00007.x → 10.1037/0022-3514.87.5.586.
- Row 365, [replicating work](https://doi.org/10.5964/jnc.7029): outcome: failed → mixed.
- Row 451, [replicating work](https://doi.org/10.1093/alcalc/agag013): type: replication → reproduction; outcome: successful → outcome_computation: cannot_be_determined; outcome_robustness: robustness challenges.
- Row 453, [replicating work](https://doi.org/10.1016/j.jenvp.2026.102956): outcome: successful → mixed.
- Row 505, [replicating work](https://doi.org/10.1073/pnas.2103313118): outcome: failed → successful.
- Row 823, [replicating work](https://doi.org/10.1016/j.heliyon.2024.e32467): outcome: successful → mixed.
- Row 833, [replicating work](https://doi.org/10.4054/demres.2025.53.29): type: replication → reproduction.
- Row 835, [replicating work](https://doi.org/10.1257/mac.6.3.1): type: replication → reproduction; outcome: mixed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 929, [replicating work](https://doi.org/10.1017/ssh.2017.27): type: replication → reproduction; outcome: mixed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 996, [replicating work](https://doi.org/10.48550/arxiv.2303.08577): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1005, [replicating work](https://doi.org/10.29338/wp2019-15): type: replication → reproduction; outcome: failed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 1024, [replicating work](https://doi.org/10.18718/81781.7): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1146, [replicating work](https://doi.org/10.5018/economics-ejournal.ja.2017-13): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1184, [replicating work](https://doi.org/10.1080/01434632.2020.1730861): outcome: failed → mixed.
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
- Row 2170, [replicating work](https://doi.org/10.31235/osf.io/zugae): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 2238, [replicating work](https://doi.org/10.1002/jae.2922): type: replication → reproduction; outcome: failed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 2299, [replicating work](https://doi.org/10.1371/journal.pone.0253023): type: replication → reproduction; outcome: successful → outcome_computation: computational issues; outcome_robustness: robust.
- Row 2674, [replicating work](https://hdl.handle.net/10419/266385) (DOI unavailable): outcome robustness: robustness challenges.
- Row 2697, [replicating work](https://osf.io/exb67/) (DOI unavailable): outcome robustness: robust.

Source-version limits: Row 2238 was checked against the verified 2020 working paper; the final 2022 article was not obtained. Row 929 was checked against the verified 2015 draft; the final 2017 article was not obtained. These judgments describe the supplied versions; changes in unseen final versions cannot be ruled out.

## Unmatched blind targets

- Confirmed missing target: [Knowing what to think by knowing who you are: Self-categorisation and the nature of norm formation, conformity and group polarisation](https://doi.org/10.1111/j.2044-8309.1990.tb00892.x); work [replicating work](https://doi.org/10.31820/pt.28.3.7), target 1 (argon).
- Confirmed missing target: Do Get-Out-the-Vote Calls Reduce Turnout? The Importance of Statistical Methods for Field Experiments.; work [replicating work](https://doi.org/10.1017/s000305540505166x), target 1 (argon).
- Confirmed missing target: [Enhancing interest and performance with a utility value intervention.](https://doi.org/10.1037/a0019506); work [replicating work](https://doi.org/10.1037/edu0000146), target 1 (argon).
- Confirmed missing target: Replications in Psychology Research; work [replicating work](https://doi.org/10.1075/target.18159.ola), target 0 (argon).
- Confirmed missing target: [Children's understanding of counting](https://doi.org/10.1016/0010-0277(90)90003-3); work [replicating work](https://doi.org/10.5964/jnc.7029), target 0 (argon).
- Confirmed missing target: Fernbach; Kan; Lynch (2015); work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 7 (argon).
- Confirmed missing target: Reframing the ordinary: Imagining time as scarce increases well-being.; work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 9 (argon).
- Confirmed missing target: Evidence for opportunity cost neglect in the poor.; work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 14 (argon).
- Confirmed missing target: [The effects of torture: Two community studies](https://doi.org/10.1207/s15327949pac1203_1); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 0 (argon).
- Confirmed missing target: [A multivariate contextual analysis of torture and cruel, inhuman, and degrading treatments: Implications for an evidence-based definition of torture](https://doi.org/10.1037/a0015681); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 2 (argon).
- Confirmed missing target: [Classifying the torture experiences of refugees living in the United States](https://doi.org/10.1177/0886260506294999); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 3 (argon).
- Confirmed missing target: [Nature of torture, PTSD, and somatic symptoms among political ex-prisoners](https://doi.org/10.1002/jts.20541); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 4 (argon).
788 unmatched blind targets remain unverified. Ambiguous proposed pairs remain in results.csv with flags and unverified verdicts.

## Skips and validation issues

- blinding compromised; coding excluded: 3 works.
- no_text: 43 works.
- paper identity conflict; coding excluded: 8 works.
- source scope incomplete; coding excluded: 1 works.
- Argon 186c024fa1d798a4: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 2736b815e9f115a4: unresolved after 2 attempts; Unterminated string starting at: line 274 column 17 (char 26129). 25 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 5b3bc0521d2f9aa1: unresolved after 2 attempts; invalid decision or quote: original. 5 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 6c8ce5072ad5bef2: unresolved after 2 attempts; invalid decision or quote: original. 2 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 73bcc3e73f111e2c: unresolved after 2 attempts; invalid decision or quote: type. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 9b3c6d39a871d365: unresolved after 2 attempts; invalid decision or quote: outcome. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon b73243da6a1469dd: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon ed1f7b7135e869e8: unresolved after 2 attempts; Read-only CLI auto-denied command permission on both attempts; no valid JSON response.. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon f4ef4cba54e4ea6b: unresolved after 2 attempts; invalid decision or quote: outcome. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon f8c599bb24ccfef4: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon ff94f0e817af2f69: unresolved after 2 attempts; invalid decision or quote: type. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Blinding incidents affected 13 works; excluded judgments remain quarantined. Only independent fresh-child retries enter primary results; exhausted retries remain unverified. See blinding_incidents.json and post_exposure_exclusions.json for the complete record.

## Time per work

Elapsed time supplied for 2340 / 2344 works; missing times are not imputed. Times describe final saved checkpoints and exclude earlier failed or excluded attempts; this is worker time, not wall-clock audit duration.
Sum of reported final-checkpoint times: 164323.3 seconds.
Per-work elapsed time and skips are recorded in [work_times.csv](work_times.csv).
