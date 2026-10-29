# FLoRA blind audit — provisional

This report is provisional until the parent finalizes the audit. Blind disagreement alone establishes no error. Agreements require supported identity and quotes found in saved text; confirmed errors require an obvious or Argon decision with a reason, location and verified quote.

35 input rows have at least one confirmed field error; 1048 / 2818 rows are fully resolved. 523 blind targets have no proposed shipped counterpart; these are not errors by default.

## Coverage

Works: 2344 total; 1462 attempted; 1383 with verified saved text (1005 full text, 378 abstract); 1383 with validated usable coding. Rows fully resolved: 1048 / 2818.

Coverage is prioritized and depends on text access. This is not a representative sample. Rates use correct + confirmed-error rows as field-specific evaluable denominators. Bounds put every unverified row first outside, then inside the error count over all applicable input rows; they are sensitivity bounds, not binomial confidence intervals. Confidence is descriptive only. Study status is reported separately and does not change type agreement.

## Confirmed field error rates

- type: 10 / 1480 (0.7%); 1338 unverified; all-row unresolved bounds 0.4%–47.8% (N=2818)
- original: 2 / 1490 (0.1%); 1328 unverified; all-row unresolved bounds 0.1%–47.2% (N=2818)
- outcome: 31 / 1052 (2.9%); 1766 unverified; all-row unresolved bounds 1.1%–63.8% (N=2818)
- outcome_computation: 0 / 87 (0.0%); 118 unverified; all-row unresolved bounds 0.0%–57.6% (N=205)
- outcome_robustness: 0 / 105 (0.0%); 100 unverified; all-row unresolved bounds 0.0%–48.8% (N=205)

### By source

- COS:
  - type: 1 / 484 (0.2%); 236 unverified; all-row unresolved bounds 0.1%–32.9% (N=720)
  - original: 0 / 487 (0.0%); 233 unverified; all-row unresolved bounds 0.0%–32.4% (N=720)
  - outcome: 11 / 305 (3.6%); 415 unverified; all-row unresolved bounds 1.5%–59.2% (N=720)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- SCORE:
  - type: 0 / 29 (0.0%); 59 unverified; all-row unresolved bounds 0.0%–67.0% (N=88)
  - original: 0 / 29 (0.0%); 59 unverified; all-row unresolved bounds 0.0%–67.0% (N=88)
  - outcome: 0 / 24 (0.0%); 64 unverified; all-row unresolved bounds 0.0%–72.7% (N=88)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- i4r:
  - type: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
  - original: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
  - outcome: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
  - outcome_computation: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
  - outcome_robustness: 0 / 0 (not estimable); 1 unverified; all-row unresolved bounds 0.0%–100.0% (N=1)
- openalex:
  - type: 1 / 131 (0.8%); 135 unverified; all-row unresolved bounds 0.4%–51.1% (N=266)
  - original: 0 / 134 (0.0%); 132 unverified; all-row unresolved bounds 0.0%–49.6% (N=266)
  - outcome: 1 / 105 (1.0%); 161 unverified; all-row unresolved bounds 0.4%–60.9% (N=266)
  - outcome_computation: 0 / 1 (0.0%); 6 unverified; all-row unresolved bounds 0.0%–85.7% (N=7)
  - outcome_robustness: 0 / 4 (0.0%); 3 unverified; all-row unresolved bounds 0.0%–42.9% (N=7)
- openalex_snapshot:
  - type: 0 / 50 (0.0%); 43 unverified; all-row unresolved bounds 0.0%–46.2% (N=93)
  - original: 0 / 50 (0.0%); 43 unverified; all-row unresolved bounds 0.0%–46.2% (N=93)
  - outcome: 0 / 39 (0.0%); 54 unverified; all-row unresolved bounds 0.0%–58.1% (N=93)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- replications:
  - type: 8 / 676 (1.2%); 777 unverified; all-row unresolved bounds 0.6%–54.0% (N=1453)
  - original: 2 / 679 (0.3%); 774 unverified; all-row unresolved bounds 0.1%–53.4% (N=1453)
  - outcome: 19 / 500 (3.8%); 953 unverified; all-row unresolved bounds 1.3%–66.9% (N=1453)
  - outcome_computation: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
  - outcome_robustness: 0 / 0 (not estimable); 0 unverified; all-row unresolved bounds not estimable (N=0)
- reproductions:
  - type: 0 / 110 (0.0%); 87 unverified; all-row unresolved bounds 0.0%–44.2% (N=197)
  - original: 0 / 111 (0.0%); 86 unverified; all-row unresolved bounds 0.0%–43.7% (N=197)
  - outcome: 0 / 79 (0.0%); 118 unverified; all-row unresolved bounds 0.0%–59.9% (N=197)
  - outcome_computation: 0 / 86 (0.0%); 111 unverified; all-row unresolved bounds 0.0%–56.3% (N=197)
  - outcome_robustness: 0 / 101 (0.0%); 96 unverified; all-row unresolved bounds 0.0%–48.7% (N=197)

### By evidence_level

- abstract:
  - type: 3 / 253 (1.2%); 126 unverified; all-row unresolved bounds 0.8%–34.0% (N=379)
  - original: 0 / 254 (0.0%); 125 unverified; all-row unresolved bounds 0.0%–33.0% (N=379)
  - outcome: 5 / 177 (2.8%); 202 unverified; all-row unresolved bounds 1.3%–54.6% (N=379)
  - outcome_computation: 0 / 0 (not estimable); 3 unverified; all-row unresolved bounds 0.0%–100.0% (N=3)
  - outcome_robustness: 0 / 3 (0.0%); 0 unverified; all-row unresolved bounds 0.0%–0.0% (N=3)
- full_text:
  - type: 7 / 1227 (0.6%); 190 unverified; all-row unresolved bounds 0.5%–13.9% (N=1417)
  - original: 2 / 1236 (0.2%); 181 unverified; all-row unresolved bounds 0.1%–12.9% (N=1417)
  - outcome: 26 / 875 (3.0%); 542 unverified; all-row unresolved bounds 1.8%–40.1% (N=1417)
  - outcome_computation: 0 / 87 (0.0%); 31 unverified; all-row unresolved bounds 0.0%–26.3% (N=118)
  - outcome_robustness: 0 / 102 (0.0%); 16 unverified; all-row unresolved bounds 0.0%–13.6% (N=118)
- none:
  - type: 0 / 0 (not estimable); 1022 unverified; all-row unresolved bounds 0.0%–100.0% (N=1022)
  - original: 0 / 0 (not estimable); 1022 unverified; all-row unresolved bounds 0.0%–100.0% (N=1022)
  - outcome: 0 / 0 (not estimable); 1022 unverified; all-row unresolved bounds 0.0%–100.0% (N=1022)
  - outcome_computation: 0 / 0 (not estimable); 84 unverified; all-row unresolved bounds 0.0%–100.0% (N=84)
  - outcome_robustness: 0 / 0 (not estimable); 84 unverified; all-row unresolved bounds 0.0%–100.0% (N=84)

## Every confirmed input-row error

Complete quotes, locations, reasons and corrected values are retained in [results.csv](results.csv), keyed by the immutable input row index.

- Row 14, [replicating work](https://doi.org/10.1007/s11469-021-00695-9): outcome: successful → mixed.
- Row 18, [replicating work](https://doi.org/10.1038/s41598-025-10331-4): original: 10.1037/a0010932 → Obedience To Authority: An Experimental View.
- Row 37, [replicating work](https://doi.org/10.1186/ar3789): outcome: successful → mixed.
- Row 65, [replicating work](https://doi.org/10.1080/02619768.2014.882308): outcome: successful → mixed.
- Row 77, [replicating work](https://doi.org/10.1080/16506073.2015.1015163): outcome: successful → mixed.
- Row 152, [replicating work](https://doi.org/10.1002/aepp.13377): type: replication → reproduction; outcome: successful → outcome_computation: computationally reproducible; outcome_robustness: robust.
- Row 163, [replicating work](https://doi.org/10.2466/07.10.17.pr0.107.4.139-144): outcome: mixed → failed.
- Row 167, [replicating work](https://doi.org/10.1017/s0272263112000903): outcome: mixed → failed.
- Row 173, [replicating work](https://doi.org/10.1007/s10648-023-09729-1): outcome: mixed → failed.
- Row 177, [replicating work](https://doi.org/10.1186/1471-2415-14-140): original: 10.1038/ng.2578 → 10.1074/jbc.M111.275990.
- Row 229, [replicating work](https://doi.org/10.1103/physrevstper.10.010110): type: replication → not_a_replication.
- Row 279, [replicating work](https://doi.org/10.1002/jclp.70017): outcome: mixed → failed.
- Row 365, [replicating work](https://doi.org/10.5964/jnc.7029): outcome: failed → mixed.
- Row 451, [replicating work](https://doi.org/10.1093/alcalc/agag013): type: replication → reproduction; outcome: successful → outcome_computation: cannot_be_determined; outcome_robustness: robustness challenges.
- Row 453, [replicating work](https://doi.org/10.1016/j.jenvp.2026.102956): outcome: successful → mixed.
- Row 505, [replicating work](https://doi.org/10.1073/pnas.2103313118): outcome: failed → successful.
- Row 823, [replicating work](https://doi.org/10.1016/j.heliyon.2024.e32467): outcome: successful → mixed.
- Row 833, [replicating work](https://doi.org/10.4054/demres.2025.53.29): type: replication → reproduction.
- Row 835, [replicating work](https://doi.org/10.1257/mac.6.3.1): type: replication → reproduction; outcome: mixed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 1005, [replicating work](https://doi.org/10.29338/wp2019-15): type: replication → reproduction; outcome: failed → outcome_computation: computationally reproducible; outcome_robustness: robustness challenges.
- Row 1184, [replicating work](https://doi.org/10.1080/01434632.2020.1730861): outcome: failed → mixed.
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
- Row 2299, [replicating work](https://doi.org/10.1371/journal.pone.0253023): type: replication → reproduction; outcome: successful → outcome_computation: computational issues; outcome_robustness: robust.

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
512 unmatched blind targets remain unverified. Ambiguous proposed pairs remain in results.csv with flags and unverified verdicts.

## Skips and validation issues

- blinding compromised; coding excluded: 3 works.
- no_text: 40 works.
- paper identity conflict; coding excluded: 7 works.
- source scope incomplete; coding excluded: 1 works.
- unattempted: 910 works.
- Argon 186c024fa1d798a4: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 2736b815e9f115a4: unresolved after 2 attempts; Unterminated string starting at: line 274 column 17 (char 26129). 25 independently valid field decisions recovered; remaining fields stay unverified.
- Argon 9b3c6d39a871d365: unresolved after 2 attempts; invalid decision or quote: outcome. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Argon ed1f7b7135e869e8: unresolved after 2 attempts; Read-only CLI auto-denied command permission on both attempts; no valid JSON response.. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon f4ef4cba54e4ea6b: unresolved after 2 attempts; invalid decision or quote: outcome. 0 independently valid field decisions recovered; remaining fields stay unverified.
- Argon f8c599bb24ccfef4: unresolved after 2 attempts; invalid decision or quote: original. 1 independently valid field decisions recovered; remaining fields stay unverified.
- Blinding exclusion ba34c6d310f46998: original coding quarantined; only a fresh-child coding may enter primary results. See blinding_incidents.json.
- Blinding exclusion 70514ece3a503ace: original coding quarantined; only a fresh-child coding may enter primary results. See blinding_incidents.json.
- Blinding exclusion 70514ece3a503ace: original coding quarantined; only a fresh-child coding may enter primary results. See blinding_incidents.json.
- Blinding exclusion 90fc66bb120fe3cd: original coding quarantined; only a fresh-child coding may enter primary results. See blinding_incidents.json.
- Blinding exclusion 90fc66bb120fe3cd: original coding quarantined; only a fresh-child coding may enter primary results. See blinding_incidents.json.
- Blinding exclusion 8db82a3ab7b437eb: original coding quarantined; only a fresh-child coding may enter primary results. See blinding_incidents.json.
- Blinding exclusion 8db82a3ab7b437eb: original coding quarantined; only a fresh-child coding may enter primary results. See blinding_incidents.json.

## Time per work

Elapsed time supplied for 1430 / 2344 works; missing times are not imputed. The total is worker time, not wall-clock audit duration.
Total reported worker time: 97574.1 seconds.
Per-work elapsed time and skips are recorded in [work_times.csv](work_times.csv).
