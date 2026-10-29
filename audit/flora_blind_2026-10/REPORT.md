# FLoRA blind audit — provisional

This report is provisional until the parent finalizes the audit. Blind disagreement alone establishes no error. Agreements require supported identity and quotes found in saved text; confirmed errors require an obvious or Argon decision with a reason, location and verified quote.

45 input rows have at least one confirmed field error; 1222 / 2818 rows are fully resolved. 602 blind targets have no proposed shipped counterpart; these are not errors by default.

## Coverage

Works: 2344 total; 1744 attempted; 1659 with verified saved text (1221 full text, 438 abstract); 1659 with validated usable coding. Rows fully resolved: 1222 / 2818.

Coverage is prioritized and depends on text access. This is not a representative sample. Rates use correct + confirmed-error rows as field-specific evaluable denominators. Bounds put every unverified row first outside, then inside the error count over all applicable input rows; they are sensitivity bounds, not binomial confidence intervals. Confidence is descriptive only. Study status is reported separately and does not change type agreement.

## Confirmed field error rates

- type: 19 / 1719 (1.1%); 1099 unverified; all-row unresolved bounds 0.7%–39.7% (N=2818)
- original: 2 / 1722 (0.1%); 1096 unverified; all-row unresolved bounds 0.1%–39.0% (N=2818)
- outcome: 38 / 1226 (3.1%); 1592 unverified; all-row unresolved bounds 1.3%–57.8% (N=2818)
- outcome_computation: 0 / 107 (0.0%); 98 unverified; all-row unresolved bounds 0.0%–47.8% (N=205)
- outcome_robustness: 0 / 128 (0.0%); 77 unverified; all-row unresolved bounds 0.0%–37.6% (N=205)

### By source

- COS:
  - type: 1 / 517 (0.2%); 203 unverified; all-row unresolved bounds 0.1%–28.3% (N=720)
  - original: 0 / 519 (0.0%); 201 unverified; all-row unresolved bounds 0.0%–27.9% (N=720)
  - outcome: 11 / 329 (3.3%); 391 unverified; all-row unresolved bounds 1.5%–55.8% (N=720)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- SCORE:
  - type: 0 / 38 (0.0%); 50 unverified; all-row unresolved bounds 0.0%–56.8% (N=88)
  - original: 0 / 38 (0.0%); 50 unverified; all-row unresolved bounds 0.0%–56.8% (N=88)
  - outcome: 0 / 33 (0.0%); 55 unverified; all-row unresolved bounds 0.0%–62.5% (N=88)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- i4r:
  - type: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
  - original: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
  - outcome: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
  - outcome_computation: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
  - outcome_robustness: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
- openalex:
  - type: 3 / 160 (1.9%); 106 unverified; all-row unresolved bounds 1.1%–41.0% (N=266)
  - original: 0 / 161 (0.0%); 105 unverified; all-row unresolved bounds 0.0%–39.5% (N=266)
  - outcome: 3 / 130 (2.3%); 136 unverified; all-row unresolved bounds 1.1%–52.3% (N=266)
  - outcome_computation: 0 / 1 (0.0%); 6 unverified; all-row unresolved bounds 0.0%–85.7% (N=7)
  - outcome_robustness: 0 / 4 (0.0%); 3 unverified; all-row unresolved bounds 0.0%–42.9% (N=7)
- openalex_snapshot:
  - type: 0 / 57 (0.0%); 36 unverified; all-row unresolved bounds 0.0%–38.7% (N=93)
  - original: 0 / 57 (0.0%); 36 unverified; all-row unresolved bounds 0.0%–38.7% (N=93)
  - outcome: 0 / 43 (0.0%); 50 unverified; all-row unresolved bounds 0.0%–53.8% (N=93)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- replications:
  - type: 15 / 811 (1.8%); 642 unverified; all-row unresolved bounds 1.0%–45.2% (N=1453)
  - original: 2 / 809 (0.2%); 644 unverified; all-row unresolved bounds 0.1%–44.5% (N=1453)
  - outcome: 24 / 594 (4.0%); 859 unverified; all-row unresolved bounds 1.7%–60.8% (N=1453)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- reproductions:
  - type: 0 / 136 (0.0%); 61 unverified; all-row unresolved bounds 0.0%–31.0% (N=197)
  - original: 0 / 138 (0.0%); 59 unverified; all-row unresolved bounds 0.0%–29.9% (N=197)
  - outcome: 0 / 97 (0.0%); 100 unverified; all-row unresolved bounds 0.0%–50.8% (N=197)
  - outcome_computation: 0 / 106 (0.0%); 91 unverified; all-row unresolved bounds 0.0%–46.2% (N=197)
  - outcome_robustness: 0 / 124 (0.0%); 73 unverified; all-row unresolved bounds 0.0%–37.1% (N=197)

### By evidence_level

- abstract:
  - type: 3 / 295 (1.0%); 144 unverified; all-row unresolved bounds 0.7%–33.5% (N=439)
  - original: 0 / 296 (0.0%); 143 unverified; all-row unresolved bounds 0.0%–32.6% (N=439)
  - outcome: 5 / 203 (2.5%); 236 unverified; all-row unresolved bounds 1.1%–54.9% (N=439)
  - outcome_computation: 0 / 0 (not estimable); 3 unverified; all-row unresolved bounds 0.0%–100.0% (N=3)
  - outcome_robustness: 0 / 3 (0.0%); 0 unverified; all-row unresolved bounds 0.0%–0.0% (N=3)
- full_text:
  - type: 16 / 1424 (1.1%); 209 unverified; all-row unresolved bounds 1.0%–13.8% (N=1633)
  - original: 2 / 1426 (0.1%); 207 unverified; all-row unresolved bounds 0.1%–12.8% (N=1633)
  - outcome: 33 / 1023 (3.2%); 610 unverified; all-row unresolved bounds 2.0%–39.4% (N=1633)
  - outcome_computation: 0 / 107 (0.0%); 39 unverified; all-row unresolved bounds 0.0%–26.7% (N=146)
  - outcome_robustness: 0 / 125 (0.0%); 21 unverified; all-row unresolved bounds 0.0%–14.4% (N=146)
- none:
  - type: 0 / 0 (not estimable); 746 unverified; all-row unresolved bounds 0.0%–100.0% (N=746)
  - original: 0 / 0 (not estimable); 746 unverified; all-row unresolved bounds 0.0%–100.0% (N=746)
  - outcome: 0 / 0 (not estimable); 746 unverified; all-row unresolved bounds 0.0%–100.0% (N=746)
  - outcome_computation: 0 / 0 (not estimable); 56 unverified; all-row unresolved bounds 0.0%–100.0% (N=56)
  - outcome_robustness: 0 / 0 (not estimable); 56 unverified; all-row unresolved bounds 0.0%–100.0% (N=56)

## Every confirmed input-row error

Complete quotes, locations, reasons and corrected values are retained in [results.csv](results.csv), keyed by the immutable input row index.

- Row 14, [replicating work](https://doi.org/10.1007/s11469-021-00695-9): outcome: successful → mixed.
- Row 17, [replicating work](https://doi.org/10.1080/08993408.2022.2071543): outcome: successful → mixed.
- Row 18, [replicating work](https://doi.org/10.1038/s41598-025-10331-4): original: 10.1037/a0010932 → Obedience To Authority: An Experimental View.
- Row 37, [replicating work](https://doi.org/10.1186/ar3789): outcome: successful → mixed.
- Row 65, [replicating work](https://doi.org/10.1080/02619768.2014.882308): outcome: successful → mixed.
- Row 77, [replicating work](https://doi.org/10.1080/16506073.2015.1015163): outcome: successful → mixed.
- Row 111, [replicating work](https://doi.org/10.1136/injuryprev-2018-043127): type: replication → not_a_replication.
- Row 152, [replicating work](https://doi.org/10.1002/aepp.13377): type: replication → reproduction; outcome: successful → outcome_computation: computationally reproducible; outcome_robustness: robust.
- Row 163, [replicating work](https://doi.org/10.2466/07.10.17.pr0.107.4.139-144): outcome: mixed → failed.
- Row 167, [replicating work](https://doi.org/10.1017/s0272263112000903): outcome: mixed → failed.
- Row 173, [replicating work](https://doi.org/10.1007/s10648-023-09729-1): outcome: mixed → failed.
- Row 177, [replicating work](https://doi.org/10.1186/1471-2415-14-140): original: 10.1038/ng.2578 → 10.1074/jbc.M111.275990.
- Row 229, [replicating work](https://doi.org/10.1103/physrevstper.10.010110): type: replication → not_a_replication.
- Row 242, [replicating work](https://doi.org/10.1371/journal.pone.0209704): type: replication → not_a_replication.
- Row 279, [replicating work](https://doi.org/10.1002/jclp.70017): outcome: mixed → failed.
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
- Row 1024, [replicating work](https://doi.org/10.18718/81781.7): type: replication → reproduction.
- Row 1146, [replicating work](https://doi.org/10.5018/economics-ejournal.ja.2017-13): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1184, [replicating work](https://doi.org/10.1080/01434632.2020.1730861): outcome: failed → mixed.
- Row 1216, [replicating work](https://doi.org/10.32388/e37rhf): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1269, [replicating work](https://doi.org/10.1111/ssqu.13292): type: replication → reproduction; outcome: failed → outcome_computation: computational issues; outcome_robustness: robustness challenges.
- Row 1292, [replicating work](https://doi.org/10.1515/jbnst-2025-0084): type: replication → reproduction; outcome: mixed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
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

Source-version limits: Row 2238 was checked against the verified 2020 working paper; the final 2022 article was not obtained. Row 929 was checked against the verified 2015 draft; the final 2017 article was not obtained. These judgments describe the supplied versions; changes in unseen final versions cannot be ruled out.

## Unmatched blind targets

- Confirmed missing target: Do Get-Out-the-Vote Calls Reduce Turnout? The Importance of Statistical Methods for Field Experiments.; work [replicating work](https://doi.org/10.1017/s000305540505166x), target 1 (argon).
- Confirmed missing target: [Children's understanding of counting](https://doi.org/10.1016/0010-0277(90)90003-3); work [replicating work](https://doi.org/10.5964/jnc.7029), target 0 (argon).
- Confirmed missing target: Fernbach; Kan; Lynch (2015); work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 7 (argon).
- Confirmed missing target: Reframing the ordinary: Imagining time as scarce increases well-being.; work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 9 (argon).
- Confirmed missing target: Evidence for opportunity cost neglect in the poor.; work [replicating work](https://doi.org/10.1073/pnas.2103313118), target 14 (argon).
- Confirmed missing target: [The effects of torture: Two community studies](https://doi.org/10.1207/s15327949pac1203_1); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 0 (argon).
- Confirmed missing target: [A multivariate contextual analysis of torture and cruel, inhuman, and degrading treatments: Implications for an evidence-based definition of torture](https://doi.org/10.1037/a0015681); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 2 (argon).
- Confirmed missing target: [Classifying the torture experiences of refugees living in the United States](https://doi.org/10.1177/0886260506294999); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 3 (argon).
- Confirmed missing target: [Nature of torture, PTSD, and somatic symptoms among political ex-prisoners](https://doi.org/10.1002/jts.20541); work [replicating work](https://doi.org/10.4236/psych.2013.45067), target 4 (argon).
589 unmatched blind targets remain unverified. Ambiguous proposed pairs remain in results.csv with flags and unverified verdicts.

## Skips and validation issues

- blinding compromised; coding excluded: 3 works.
- error: 4 works.
- no_text: 41 works.
- paper identity conflict; coding excluded: 8 works.
- source scope incomplete; coding excluded: 1 works.
- unattempted: 628 works.
- Argon 186c024fa1d798a4: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 2736b815e9f115a4: unresolved after 2 attempts; Unterminated string starting at: line 274 column 17 (char 26129). 25 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 794a282122e9356a: unresolved after 2 attempts; invalid decision or quote: outcome. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 9b3c6d39a871d365: unresolved after 2 attempts; invalid decision or quote: outcome. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon b73243da6a1469dd: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon ed1f7b7135e869e8: unresolved after 2 attempts; Read-only CLI auto-denied command permission on both attempts; no valid JSON response.. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon f4ef4cba54e4ea6b: unresolved after 2 attempts; invalid decision or quote: outcome. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon f8c599bb24ccfef4: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon ff94f0e817af2f69: unresolved after 2 attempts; invalid decision or quote: type. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Blinding incidents affected 13 works; excluded judgments remain quarantined. Only independent fresh-child retries enter primary results; exhausted retries remain unverified. See blinding_incidents.json and post_exposure_exclusions.json for the complete record.

## Time per work

Elapsed time supplied for 1712 / 2344 works; missing times are not imputed. Times describe final saved checkpoints and exclude earlier failed or excluded attempts; this is worker time, not wall-clock audit duration.
Sum of reported final-checkpoint times: 116451.0 seconds.
Per-work elapsed time and skips are recorded in [work_times.csv](work_times.csv).
