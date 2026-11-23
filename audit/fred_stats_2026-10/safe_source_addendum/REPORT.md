# Safe replacement chapter: findings and pending availability decisions

The complete Piniel (2024) chapter is accepted as a primary source. Exact coverage of the initially missing sources increases from 248/255 to **249/255**. Fresh blind validation and independent review add **0 verified field instances and 0 confirmed errors**. The cumulative result remains **493 confirmed field errors across 381 rows**. Source availability is distinct from statistical verification.

## Decisions to review

- **Chan & Feldman, row 1308 replication:** Lukas confirms the Weinstein (1984) replication/extension is offline. The linked Google Doc returns 404 to the connected account; prior signed-in Chrome export failed. Flag continued inclusion or possible removal for review. Do not remove the record or change its statistical verdict merely because the report is unavailable.
- **Armon (row 2106), Yang (row 2129), Ku (row 2149):** the responsible OSF/COS team should confirm availability and provide stable primary replication report/manuscript links. Original papers and preregistration forms do not establish the reports' availability. Exact URLs, source keys, evidence and requests are in [the four availability follow-ups](availability_followups.md) and [machine-readable flags](availability_followups.json).

These flags are routed through the parent draft PR155 workflow. No separate email or Slack message was sent, no removal was made, and no statistical verdict changed on availability grounds.

## Chapter validation

The requested DOI is 10.1007/978-3-031-55844-3_4. The safe user-supplied replacement is distinct from the blocked Drive object, which remains unchanged. The transferred complete chapter has 23 pages, printed 49–71, extracted from full-book PDF 57–79. Its PDF SHA256 is `e29a595a5aeb29c3cdd92387ce7414b88757ab6dd5946c8d75f158142092c18b`. The full book remains on the Mac; no full-book hash verification is claimed on this box. Parent checks covered PDF/text hashes, chapter title/DOI, the first/last rendered pages and the target results page. All 15 private addendum/transfer objects passed direct remote content verification; upload/error queues were empty.

One fresh native Codex gpt-6.1-sol medium child received only the neutral inputs and primary chapter, covering eligible replication sides 188,1957,1958. The three original sides were preserved. Each replication checkpoint moved from `paper_unavailable` to `locator_insufficient`. No predictor was assigned by row order or matching coded numbers.

The neutral descriptions and p.63 locator identify a regression of general language anxiety on three scales, without distinguishing the predictor for any row. The printed candidates are retained without individual-row assignment:

| Predictor | Printed standardized beta | Same-predictor p bound |
|---|---:|---:|
| Input anxiety |0.18|<0.05|
| Process anxiety |0.43|<0.01|
| Output anxiety |0.31|<0.01|

The separately printed model F and adjusted R² are not substituted for these coefficients. The chapter reports 134 recruited students, while the regression residual degrees of freedom imply 133 under ordinary least squares. No explicit critical-model analytic N or explanation of the discrepancy is provided, so neither total is asserted as the target analytic sample. The broad mixed narrative includes psychometric structure findings and does not establish an individual-row regression verdict.

An independent Gemini 4 Argon (High) call reviewed all 12 candidate field decisions (three numeric fields and author-reported success for each row), inspecting the target and methods context. Its complete reply passed the exact-source quote validator for all 12 items; all were `undeterminable`. No incomplete response, unsupported predictor mapping or df-only sample guess was counted as verification. See [field reviews](field_reviews.csv), blind checkpoints in `extractions/`, and retained raw/validated review receipts.

All prior verified fields, completed sides/verdicts, historical pass files/completion markers and prior provenance entries are protected by the baseline and final accounting check. The frozen workbook, shipped files, pipeline, main checkout and FLoRA are unchanged. No acquisition task, schedule, historical deadline extension, paid API or incremental model spend was introduced. Candidate values and availability flags remain evidence for review, not dataset edits.
