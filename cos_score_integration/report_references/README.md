# SCORE report-author corrections

`cache/manual_references.xlsx` supplies verified author, title, year, APA and BibTeX metadata for 130 FReD rows: 116 existing rows and 14 newly entered individual attempts. Multiple rows can cite the same report. The workbook also preserves the original-study author’s compound surname **De Neys** for DOI `10.1016/j.cognition.2012.05.011`.

## Method and audit

1. Identify SCORE rows in the read-only export and follow their OSF project/report links.
2. Retrieve the reports through OSF’s public API and read their bylines. Credit the report writers rather than the project’s SCORE administrators.
3. Use a report date where available; otherwise use its file deposit year. Supply bracketed descriptive titles identifying the original study, rather than presenting internal codes as publication titles.
4. Store the verified metadata in the manual workbook. `audit.csv` retains each FReD row ID, lookup key, before/after citation, API endpoint, byline evidence, year basis and report SHA-256. All records were checked on 10 November 2026; incremental API cost was US$0.

Two individual reports have no printed byline. With approval, `score_component_9977` is attributed to John E. Edlund using document-author metadata and the OSF contributors; `score_component_276` is attributed to Bence Bago and Balazs Aczel using the file name, PDF metadata and OSF contributors. Their evidence is explicit in the audit. Nine other rows remain unresolved: five lack an established byline and four have deleted report files without identified replacements. No authors or DOIs were invented.

The small post-join override is necessary because the existing manual URL helper only fills missing values: it would retain cached project citations over corrected report citations. The override uses only the corrected report keys in this audit and changes bibliographic fields.

## Scope and checks

One-off verification covered all 130 report citations, author metadata, unresolved-row preservation, numerical-field preservation and idempotency. Generated exports, effect sizes and success coding are outside this PR. A full notebook build was not run (`rcrossref` is unavailable here).

FLoRA uses its own sources and correction log; its corrections are in [flora-validation PR #26](https://github.com/forrtproject/flora-validation/pull/26). The seven superseded pooled rows are excluded in [PR #169](https://github.com/forrtproject/fred-data/pull/169). Remaining reference problems are tracked in [issue #168](https://github.com/forrtproject/fred-data/issues/168), implementing the decision in [issue #162](https://github.com/forrtproject/fred-data/issues/162).

The [full investigation at the pre-trim commit](https://github.com/forrtproject/fred-data/tree/a3d0f8f3e/cos_score_integration/report_references) preserves the raw evidence, aggregate investigation, entry-sheet links and approved coding records without including them in this change.
