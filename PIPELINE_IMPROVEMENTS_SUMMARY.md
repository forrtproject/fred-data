# Author Overlap Pipeline - Implementation Summary

## Overview

I've reviewed and improved the author overlap detection pipeline to address robustness issues, particularly in author name extraction when dealing with varied CrossRef data structures.

## Key Findings

### Current Status
- **Infrastructure**: ✓ Correctly set up
- **Author Data Files**: ⚠️ Empty (awaiting first retrieval run)
- **Test Dataset**: ✓ COS data loaded (1,699 rows, 623 unique study pairs, 796 unique DOIs)
- **Pipeline Logic**: ✓ Sound, with improvements made

### Critical Issue Addressed
**Original problem**: Not all CrossRef returns have a "family" field for author names, and the fallback logic was incomplete.

**Solution**: Implemented a more robust extraction function with multiple fallback paths:
1. Primary: `family` field (typical author structure)
2. Secondary: `given` field (when family missing)
3. Tertiary: Generic `name` field (organization names, etc.)
4. Handles string representations and edge cases

## Changes Made

### 1. [crossref_author_retrieval.qmd](crossref_author_retrieval.qmd) - Enhanced Extraction Function

**Improvements**:
- ✓ More defensive `NULL` and type checking
- ✓ Handles both dataframe and list formats from JSON parsing
- ✓ Falls back through multiple name fields (family → given → name)
- ✓ Handles string author representations
- ✓ Returns unique names only (eliminates duplicates)
- ✓ Better error messages for debugging

**Before** (lines 95-165 original):
```r
# Limited fallback logic, silent failures on edge cases
family <- if ("family" %in% names(authors)) authors$family[i] else NA
name <- if ("name" %in% names(authors)) authors$name[i] else NA
# Falls back from family to name, but doesn't handle given names
```

**After** (lines 95-174 updated):
```r
# Robust multi-level fallback
family <- author[["family"]]
given <- author[["given"]]
name <- author[["name"]]

# Priority: family > given > name
if (!is.null(family) && is.character(family) && nzchar(trimws(family[1]))) {
  extracted <- trimws(tolower(family[1]))
} else if (!is.null(given) && is.character(given) && nzchar(trimws(given[1]))) {
  extracted <- trimws(tolower(given[1]))
} else if (!is.null(name) && is.character(name) && nzchar(trimws(name[1]))) {
  extracted <- trimws(tolower(name[1]))
}
```

### 2. [crossref_author_retrieval.qmd](crossref_author_retrieval.qmd) - Added Quality Reporting

**New sections added**:
- Extraction quality tracking (lines 176-211)
- Reports percentage of study pairs where names could be extracted
- Provides debugging information during pipeline execution
- Helps identify systematic data quality issues

**New output**:
```
=== AUTHOR EXTRACTION QUALITY ===
Study pairs with both studies having data: XXX
Pairs where names could be extracted from both: XXX (X.X% of pairs with data)
```

### 3. Documentation

Created comprehensive analysis documents:

- **[AUTHOR_OVERLAP_REVIEW.md](AUTHOR_OVERLAP_REVIEW.md)**:
  - Detailed robustness issues identified
  - Specific code locations and problems
  - Recommended improvements with code examples

- **[test_author_overlap_pipeline.R](test_author_overlap_pipeline.R)**:
  - Comprehensive test script for pipeline validation
  - Tests author data structure and extraction function
  - Identifies problematic records
  - Provides quality metrics

- **[check_author_files.R](check_author_files.R)**:
  - Quick utility to examine author data files
  - Shows file structure and sample data

## How to Run the Pipeline

### Step 1: Retrieve Author Data

Run the author retrieval script to fetch author data from CrossRef:

```bash
# In R/RStudio or via Quarto/RMarkdown rendering:
Rscript -e 'quarto::quarto_render("crossref_author_retrieval.qmd")'
# Or open crossref_author_retrieval.qmd in RStudio and render
```

This will:
- Fetch author data for ~796 unique DOIs from COS dataset
- Store raw author data in JSON format in `crossref_retrieved_authors.xlsx`
- Compute author overlap for study pairs
- Save overlap results to `crossref_author_overlap.xlsx`
- Display quality metrics about extraction success rate

**Expected output**:
```
=== AUTHOR EXTRACTION QUALITY ===
Study pairs with both studies having data: XXX
Pairs where names could be extracted from both: XXX (X.X% of pairs with data)
Study pairs with author overlap: XXX (X.X%)
```

### Step 2: Validate with Test Script

After running the retrieval script:

```bash
Rscript test_author_overlap_pipeline.R
```

This will:
- Examine actual author data structures retrieved from CrossRef
- Test the extraction function on real data
- Identify any problematic records
- Report quality metrics

### Step 3: Integration in COS Report

The overlap data is automatically loaded in the COS report (already configured):

**In [COS Reports/cos_report.qmd](COS%20Reports/cos_report.qmd) (lines 268-281)**:
```r
author_overlap <- readxl::read_excel("../crossref_author_overlap.xlsx")

ds <- ds %>%
  mutate(doi_r = tolower(doi_r),
         doi_o = tolower(doi_o)) %>%
  left_join(
    author_overlap %>%
      mutate(doi_o = tolower(doi_o),
             doi_r = tolower(doi_r)),
    by = c("doi_o", "doi_r")
  )
```

The `author_overlap` variable is now available in the dataset with values:
- `TRUE`: At least one author in common
- `FALSE`: No authors in common
- `NA`: Author data unavailable for one or both studies

## Expected Behavior Changes

### Before
- Only extracts author names from `family` field
- No fallback for `given` name field
- Silent failures when neither exists
- No quality reporting

### After
- ✓ Extracts from `family` (primary), `given` (secondary), or `name` (tertiary)
- ✓ Handles string author representations
- ✓ Quality reporting shows extraction success rates
- ✓ Better debugging information for failures
- ✓ Returns unique names (no duplicates)

## Testing Checklist

Before considering the pipeline complete, verify:

- [ ] `crossref_author_retrieval.qmd` runs without errors
- [ ] Author files populated with data (not empty)
- [ ] Quality report shows reasonable extraction rates (>80% ideally)
- [ ] No JSON parsing errors reported
- [ ] Sample records manually verified for accuracy
- [ ] `test_author_overlap_pipeline.R` runs successfully
- [ ] COS report generates with `author_overlap` variable
- [ ] Sample of overlapping pairs verified as correct

## Troubleshooting

### Issue: "No author data retrieved"
**Cause**: Author retrieval script hasn't been run or network error
**Fix**: Run `crossref_author_retrieval.qmd` and check network connectivity

### Issue: "Extraction quality very low (<50%)"
**Cause**: CrossRef returns unusual author formats for some publishers
**Solution**:
- Review problematic DOI patterns
- Check CrossRef API response format for affected publishers
- May need additional fallback fields

### Issue: "No author overlap found"
**Cause**: Could be correct (replication studies with different authors) or extraction failure
**Debug**:
- Run `test_author_overlap_pipeline.R` to check extraction quality
- Manually verify sample study pairs

## Files Modified

1. **[crossref_author_retrieval.qmd](crossref_author_retrieval.qmd)** - Enhanced with robust extraction
2. **[AUTHOR_OVERLAP_REVIEW.md](AUTHOR_OVERLAP_REVIEW.md)** - New detailed analysis
3. **[test_author_overlap_pipeline.R](test_author_overlap_pipeline.R)** - New test script
4. **[check_author_files.R](check_author_files.R)** - New diagnostic script

Files not modified (but integrate with improvements):
- `COS Reports/cos_report.qmd` - Already configured to load overlap data
- `crossref_retrieved_authors.xlsx` - Populated by script
- `crossref_author_overlap.xlsx` - Generated by script

## Next Steps

1. **Run the retrieval**: Execute `crossref_author_retrieval.qmd` to populate author data
2. **Test with real data**: Use `test_author_overlap_pipeline.R` to validate extraction
3. **Generate reports**: Let COS report automatically include author_overlap variable
4. **Validate results**: Spot-check some overlapping pairs manually

## Notes

The implementation is compatible with the existing ref_retrieval pattern and follows the same modular design (retrieve → extract → overlap → integrate). The improvements focus on defensive programming and robustness without changing the overall pipeline structure.
