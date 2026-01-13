# FReD Repository Reorganization - Progress Report

## Completed ✅

### Phase 1: Directory Structure & Configuration
- [x] Created directory structure:
  - `R/` - Helper scripts folder
  - `pipelines/fred/` and `pipelines/flora/` - Independent pipeline folders
  - `cache/` and `output/` with `.gitkeep` files
  - `cos_integration/` - COS toggle folder

- [x] Created configuration files:
  - `R/cache_config.R` - Centralized cache paths by data type
  - `.env.example` - Environment variable template
  - Updated `.gitignore` - Cache, output, and env files

- [x] Created `R/data_cleaning.R`
  - Moved complete `clean_fred_data()` function from `clean_cos_fred.R`
  - All helper functions included (`standardize_es_stat()`, `add_report_item()`)
  - Ready to use in pipelines

## In Progress 🔄

### Phase 2: Helper Function Extraction

The following files need to be extracted from existing scripts. Due to their size and complexity, they require careful handling:

#### `R/crossref_cache.R` (Consolidate by data type)
**Sources to merge:**
- `crossref_citation_cache.R` - APA/BibTeX caching functions
  - `load_citation_cache()`
  - `save_citation_cache()`
  - `get_crossref_citation()`
  - `get_apa_references()`
  - `load_manual_references()`

- `hackathon prep - flora.qmd` - DOI metadata functions
  - `load_doi_cache()`
  - `save_doi_cache()`
  - `get_doi_data_unified_cached()`
  - Helper functions for CrossRef/DataCite API calls

- `crossref_author_retrieval.qmd` - Author functions
  - `get_crossref_authors()`
  - `extract_author_identifiers()`
  - `normalize_to_ascii()`

**Status:** Ready for extraction - these are well-defined functions

#### `R/data_validation.R` (Extract from dataset validation.Rmd)
**Key function:** `validate_fred_data()`
**Includes:**
- Main validation function with 18+ validation checks
- 13+ helper functions for building error labels
- Configuration constants (VALID_ES_TYPES, TEST_STAT_REGEX, etc.)
- Incremental validation support

**Status:** Large file (600+ lines) - needs careful extraction

#### `R/augmentation.R` (New file - modular functions)
**Functions to create:**
- `augment_with_author_overlap(data)` - Compute author overlap
- `augment_with_clean_references(data)` - Fetch and clean references
- `augment_with_keywords(data)` - Fetch OpenAlex keywords

**Status:** Ready to create - will source from existing scripts

#### `R/release_helpers.R` (Refactor from release/release_dataset.R)
**Functions to extract:**
- `release_to_osf()` - Generic release function
- Helper functions for changelog and upload

**Status:** Ready for refactoring

## TODO 📋

### Phase 2b: Helper Script Completion
1. Extract and consolidate `R/crossref_cache.R`
2. Extract functions to `R/data_validation.R`
3. Create `R/augmentation.R` with modular functions
4. Create `R/release_helpers.R` with refactored release logic

### Phase 3: Create Pipeline Files
1. Create `pipelines/fred/prepare_fred.qmd`
   - Download FReD from Google Sheets
   - Clean and validate
   - Merge COS data (if enabled)
   - Call augmentation functions
   - Save to `output/FReD.xlsx`

2. Create `pipelines/fred/release_fred.qmd`
   - Optional: Release to OSF

3. Create `pipelines/flora/prepare_flora.qmd`
   - Download FLoRA from Google Sheets
   - Deduplicate, fetch metadata
   - Call augmentation functions
   - Save to `output/flora.csv`

4. Create `pipelines/flora/release_flora.qmd`
   - Optional: Release to OSF

### Phase 4: COS Integration Setup
1. Rename `cos_test1_addition/` → `cos_integration/`
2. Convert `prepare_cos_phase1.Rmd` → `prepare_cos_data.R`
3. Create `cos_integration/README.md` with toggle instructions

### Phase 5: Migration & Compatibility
1. Create symlinks for backwards compatibility
2. Archive old script files
3. Update README.md with new structure

### Phase 6: Testing
1. Test each pipeline independently
2. Verify cache migration
3. Validate output consistency

## Strategy for Completion

**Recommendation:** Continue with helper script extraction in the following order:

1. **Quick wins** - Extract simpler functions first:
   - `R/crossref_cache.R` - Well-defined citation caching functions
   - `R/release_helpers.R` - Modular release functions

2. **Create augmentation layer** - New file combining multiple sources:
   - `R/augmentation.R` - Simplify by calling existing helpers

3. **Handle large extraction** - Process carefully:
   - `R/data_validation.R` - Extract in focused way, keep constants locally

4. **Create pipelines** - Now that helpers are in place:
   - Pipelines can call helper functions
   - Each pipeline is self-contained with its own config

5. **Test and validate** - Ensure everything works together

## Notes

- **Pipeline independence:** Each dataset pipeline (fred/, flora/) has its own configuration at the top of the .qmd file
- **Cache consolidation:** All caches are now organized by data type in the `cache/` folder
- **Backwards compatibility:** Old files will remain in root and/or archive folder until validation is complete
- **COS toggle:** Works via environment variable `ENABLE_COS_MERGE`

## Files Status Summary

| File | Status | Location |
|------|--------|----------|
| `R/cache_config.R` | ✅ Created | New file |
| `R/data_cleaning.R` | ✅ Created | New location |
| `R/crossref_cache.R` | 🔄 Ready | To create |
| `R/data_validation.R` | 🔄 Ready | To create |
| `R/augmentation.R` | 🔄 Ready | To create |
| `R/release_helpers.R` | 🔄 Ready | To create |
| `pipelines/fred/prepare_fred.qmd` | 📋 Pending | To create |
| `pipelines/flora/prepare_flora.qmd` | 📋 Pending | To create |
| `cos_integration/` | 📋 Pending | To reorganize |

---

**Last updated:** 2025-12-17
