# Missing-source follow-up results

The separately authorised follow-up added 84 verified field instances, including 8 confirmed coding errors. The integrated audit now contains **416 errors across 322 effect rows**, compared with 408 errors across 315 rows before this pass.

At least one field is verified for **1605/2,164 effects (74.2%)**; all seven fields are verified for **82/2,164 (3.8%)**. The 80% goal remains unmet. These access-dependent findings do not estimate the error rate of all FReD effects.

## Sources and validation

All **255 deduplicated source groups** received a finite acquisition attempt: 244 valid DOIs and 11 reference/URL-only groups. Acquisition used the download-paper skill script and bounded alternative routes through OpenCode DeepSeek v4.1 Flash Free, followed by GLM 5.3 Flash Free. The parent stopped DeepSeek after a duplicate-runner error and stopped GLM after completion of the finite pass and repeated unchanged Wayback rate-limit failures. Both model tasks and their exact-owned runners are stopped. No paid acquisition or incremental model charges were used.

Independent parent review accepted **18 full article/manuscript artifacts**, **one primary supplement** for narrow validation, and **one primary author project table** reached through an exact OSF row locator. These are accepted evidence artifacts, not 20 newly recovered main articles. A second primary supplement was retained without an identifiable target. Abstract-only pages, supplements masquerading as main articles, and a secondary prereplication form did not establish main-paper access. Manuscript, proof, and OCR versions remain labelled.

**22 fresh blind Codex gpt-6.1-sol medium batches** produced 65 side-level attempts for **63 distinct previously unavailable sides**, including two new-context rechecks of Blair row 330. Final statuses are 49 done and 14 locator-insufficient; done status alone does not establish that all three statistics are verified. Existing completed sides and author verdicts were preserved. Nonobvious disagreements received independent Gemini 4 Argon (High) adjudication. One obvious omission was resolved by direct PDF-page inspection. No follow-up adjudication remains pending.

The exact Boyce author table identified the positive-versus-neutral emotion congruency test. The original Blair paper then supported its participant count and p-value, while the table directly supported the replication F statistic. The table did not identify the replication sample counting unit or exclusions, so its sample-size observation remains unverified. Its project outcome codes were not treated as replication authors’ narrative verdicts.

The follow-up gained 44 effects with any verified original statistic (830 to 874), three with any verified replication statistic (1,254 to 1,257), 12 with any verified field (1,593 to 1,605), and one with all seven fields (81 to 82). Full original-statistic coverage increased from 235 to 239; full replication-statistic coverage remains 475.

## New confirmed errors

| Row | Field | Shipped | Correction |
|---:|---|---|---|
| 45 | pval_value_o | (blank) | < .01 |
| 60 | reported_success | successful | failed |
| 653 | n_o | 31 | 37 |
| 693 | pval_value_o | 0.025 | 0.047 |
| 944 | es_value_o | 0.26 | 0.326 |
| 970 | pval_value_o | 0.001 | 0.010 |
| 1079 | es_value_o | F(1, 444) = 4.88 | F(1, 444) = 4.63 |
| 1083 | es_value_o | X2(3, N = 1593) = 166.88 | X2(6, N = 1593) = 62.25 |

Exact locations, reasons, and all newly evaluable fields are in [field_changes.csv](field_changes.csv). [summary.json](summary.json) records the accounting; [source_outcomes.csv](source_outcomes.csv) records all 255 formal-source outcomes, and [primary_locator_checks.json](primary_locator_checks.json) records the two additional exact OSF routes. The author table is an evidence variant of an existing source group, so it does not increase the 255-source denominator.

## Remaining limits and preservation

Most initially unavailable sources remain unavailable. Other retrieved sources still lack a uniquely identified outcome, analytic sample, requested printed metric, or author verdict. Original statistics quoted only by replication authors remain secondary evidence. No p-value was calculated from a test statistic, and no effect-size conversion was used to manufacture comparability. The original six terminal scope holds and exhausted-review decisions remain unchanged.

All 408 baseline errors and every baseline verified field verdict/correction remain intact. The original completion marker, deadlines, run manifest, and hold file match their baseline SHA256 hashes. The shipped workbook and pipeline were not edited. The workbook SHA256 remains `59545e3fc0c2979d97507097526319ec8c275aae3ac40c0d1a6d327492079e6b`.

Full source artifacts remain private and excluded from Git. The final archive contains **330 files (19,868,137 bytes)**; a direct remote content check found 330 matches and zero differences, and paths/sizes matched the inventory. The local cache remains available. Verification covers downloads, OCR, the exact locator artifacts, and all 20 canonical evidence texts.

Validation: 40 regression tests (33 original plus seven follow-up integration safeguards), all 2,164 checkpoint schemas and export totals, exact retained evidence quotations, baseline preservation assertions, and private remote archive verification.
