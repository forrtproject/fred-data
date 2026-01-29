# Claude Guidelines

## General Principles

- **Always test code after writing it** - run scripts and verify output is correct (unless the changes are trivial)
- **Iterate until it works** - don't stop at the first attempt if output shows issues
- **Handle Unicode properly** - use Unicode-aware string functions, never assume ASCII-only input
- **Check edge cases** - especially with international characters, list columns, and varying data structures

## R/CSV Export

- **Always use `write_excel_csv()` instead of `write_csv()`** - this adds a UTF-8 BOM that Excel needs to correctly display special characters (e.g., umlauts, accents). Without the BOM, Excel will show garbled text like "Wachend√∂rfer" instead of "Wachendörfer".