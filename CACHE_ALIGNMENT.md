# CrossRef Citation Cache Alignment

This document describes the changes made to align reference processing between COS Reports and FLoRA.

## Overview

Previously, COS Reports and FLoRA used different methods for managing CrossRef citations:
- **COS Reports**: Downloaded `crossref_retrieved_references.xlsx` from GitHub each time
- **FLoRA**: Used a local cache file `crossref_citation_cache.rds` with caching functions

These have now been aligned to use a common caching approach.

## Changes

### New Shared Cache Module: `crossref_citation_cache.R`

This file contains the shared citation caching functions:
- `load_citation_cache()`: Load cache from disk or initialize empty
- `save_citation_cache(cache)`: Save cache to disk
- `get_crossref_citation(doi, type)`: Fetch citation from CrossRef
- `get_apa_references(doi_vec)`: Get APA references for multiple DOIs using cache

### Updated Files

1. **COS Reports/cos_report.qmd**
   - Now sources `crossref_citation_cache.R`
   - Uses `get_apa_references()` to fetch citations with caching
   - Falls back to local file when available, otherwise loads from GitHub main

2. **hackathon prep - flora.qmd**
   - Now sources `crossref_citation_cache.R`
   - Continues to use `override_with_crossref()` for advanced fallback logic
   - Shares the same underlying cache functions

3. **.gitignore**
   - Added `crossref_citation_cache.rds` to ignore list

## Benefits

1. **Consistency**: Both COS and FLoRA now use the same caching mechanism
2. **Efficiency**: Citations are cached locally, reducing API calls to CrossRef
3. **Offline capability**: Cached citations can be used without internet access
4. **Shared cache**: Both scripts share the same cache file, avoiding duplicate work

## How to Verify

To verify the changes work correctly:

1. **Run FLoRA script** (`hackathon prep - flora.qmd`):
   ```r
   # This should create crossref_citation_cache.rds if it doesn't exist
   # and populate it with citations
   ```

2. **Run COS Report** (`COS Reports/cos_report.qmd`):
   ```r
   # This should reuse the cache created by FLoRA
   # and add any new citations to it
   ```

3. **Check cache file**:
   ```r
   cache <- readRDS("crossref_citation_cache.rds")
   str(cache)  # Should show list with 'apa' and 'bibtex' elements
   length(cache$apa)  # Number of cached APA citations
   ```

## Migration Notes

- The existing `crossref_retrieved_references.xlsx` file is no longer used by COS Reports
- The `crossref_ref_retrieval.qmd` script can still be used for other purposes
- The cache file will be built up incrementally as scripts are run
- Cache is local to each user/machine and not committed to git

## Troubleshooting

If you encounter issues:

1. **Delete the cache file** to start fresh:
   ```bash
   rm crossref_citation_cache.rds
   ```

2. **Check cache file permissions**: Ensure the script has write access

3. **Verify rcrossref package**: Ensure `rcrossref` is installed and working

4. **Check network connectivity**: Initial cache population requires internet access
