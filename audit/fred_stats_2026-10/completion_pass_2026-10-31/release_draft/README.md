# FReD completion checkpoint corrections

Interim validated checkpoint: 575 confirmed field decisions affecting 436 rows, expressed as 1087 physical cell updates. The broader completion pass remains active. Unverified fields are not patched. All 6,411 baseline verified decisions remain unchanged.

Use only the frozen b48a7d6 workbook whose SHA256 is checked by the R script. The merger verifies record identities, expected old values and download hashes. It writes a separate corrected workbook and change log; the source workbook and preparation pipeline are unchanged. Excel styling is not preserved. Reapplication to the corrected R object is a no-op.

Install readxl, writexl and digest in R, unzip beside the frozen FReD.xlsx, then run:

```sh
Rscript merge_fred_fixes.R FReD.xlsx FReD_corrected.xlsx
```

All 16 R integration checks passed, including reordered rows, conflicts without mutation, hash tampering, safe reruns and an Excel round trip. The original workbook remained byte-identical. See release_summary.json for counts and confirmed_corrections.csv for evidence references and reasons. Primary PDFs and full texts are excluded.
