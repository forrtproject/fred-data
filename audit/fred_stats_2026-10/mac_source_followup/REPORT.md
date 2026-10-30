# Mac source recovery: batch 1 validation

The first Mac transfer supplied **34 independently source-reviewed full articles**. Fresh blind checking added **203 verified field instances**, including **17 confirmed errors**, relative to the pre-Mac audit. Current totals are **433 confirmed errors across 335 effect rows**.

Any field is verified for **1621/2,164 effects (74.9%)**, compared with 1,605 before this pass. All seven fields are verified for **86/2,164**, compared with 82 before this pass. The 80% goal remains unmet. Field counts include repeated original statistics across replication rows and do not estimate a representative error rate for FReD.

## Acquisition and evidence

The Mac pass uses real Chrome, Apple Events JavaScript, and signed-in Birkbeck EBSCO/publisher access. The acquisition pass ended at 10:44 UTC on 30 October 2026, within its separate 11:53 UTC ceiling. It recovered 58 full articles after assessing 100 source groups; 42 assessed groups remained unresolved and 137 were not attempted after the active routes stopped. This report covers only private batch 01. The additional 24 articles in batch 02 are entering separate blind validation; source acceptance alone establishes no audit-field verification.

All 102 PDF, text, and neutral-input hashes were checked on receipt. Parent checks independently verified actual PDF page counts and freshly parsed PDF title/header and reference sections, retaining the Mac’s visual identity/completeness evidence and source-version labels. Croninger et al.’s article retains an ARTICLE IN PRESS header despite its full journal pagination, so equivalence to any later revision was not assumed.

The private batch archive contains 104 files, including the two manifests. A direct remote content check found 104 matches and zero differences. All 34 canonical evidence-text hashes also match acceptance records, and the private cloud upload queue was empty when checked. Original Mac and box artifacts remain available; full texts are excluded from Git.

## Blind validation and independent review

The parent filtered the transferred neutral targets against current checkpoints, retaining only still-paper_unavailable sides. **38 fresh T3 Codex gpt-6.1-sol medium batches** examined **188 distinct target sides**. Final checkpoint statuses are **127 done** and **61 locator-insufficient**. A done status can contain missing fields or a target mismatch; field verification requires the separate evidence, target, sample, metric, and bound checks.

**18 independent Gemini 4 Argon (High) calls** reviewed **77 field disagreements** through the Antigravity CLI. Complete responses were collected and passed strict exact-source quotation checks. Parent quote-only repairs are recorded separately and retain the original worker output or raw review plus its hash; no numeric value, verdict, or target was changed by a quotation repair. PDF citations were mapped only to their hash-verified canonical text from the same accepted PDF.

The nested country-panel sample-size disagreements remain unverified: 12 country clusters, 324 nominal country-years, and the usable post-lag regression sample are different quantities. Repeated neutral locators that do not distinguish accountability contrasts, conflicting study/page metadata, and missing identity-integration targets also remain unverified. Retrieval and numerical agreement did not resolve these ambiguities. Printed metrics were retained without conversions, and author-reported success was not inferred from significance.

## Confirmed changes

| Row index | Field | Shipped | Correction |
|---:|---|---|---|
| 146 | pval_value_o | (blank) | < .001 |
| 210 | pval_value_o | 0.01 | 0.72 |
| 221 | reported_success | failed | successful |
| 222 | pval_value_r | 0.003 | 0.010 |
| 222 | reported_success | mixed | successful |
| 355 | n_o | 124 | 261 |
| 501 | es_value_o | 0.987 | 0.989 |
| 664 | n_r | 28 | 31 |
| 665 | es_value_r | F(1, 36) = 6.77 | F(1, 36) = 2.95 |
| 665 | pval_value_r | 0.01 | 0.09 |
| 931 | n_o | 194 | 179 |
| 932 | n_o | 194 | 179 |
| 987 | n_o | 18 | 33 |
| 1215 | reported_success | successful | mixed |
| 1557 | n_r | 16 | 15 |
| 1788 | n_o | 62 | 44 |
| 1789 | n_o | 62 | 44 |

Row indices exclude the worksheet header. Exact evidence locations, resolutions, and all newly verified field instances are in [batch_01_field_changes.csv](batch_01_field_changes.csv); machine-readable accounting is in [batch_01_summary.json](batch_01_summary.json).

## Preservation and remaining work

All 416 pre-Mac confirmed errors and every pre-Mac verified field verdict/correction remain intact. Existing completed sides and author verdicts were protected during integration. The original audit completion marker, run manifest/deadlines, six scope holds, and completed Linux follow-up records remain unchanged. The shipped workbook and pipeline were not edited. Workbook SHA256 remains `59545e3fc0c2979d97507097526319ec8c275aae3ac40c0d1a6d327492079e6b`.

Validation includes44 regression tests (33 original, seven protected-integration checks, and four quotation-gap safeguards), all 2,164 checkpoint schemas and export totals, exact retained evidence, baseline preservation assertions, and private content-hash verification.

Mac acquisition is complete; do not restart it. The verified batch 02 transfer is being deduplicated against [accepted_sources.json](accepted_sources.json), filtered to eligible still-unavailable sides, and validated through fresh blind batches. Neither historical schedule should be restarted.
