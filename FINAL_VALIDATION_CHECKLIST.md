# Final Validation Checklist

**Status**: Ready for final validation and testing
**Created**: 2025-12-17
**Purpose**: Complete verification before production release

---

## Overview

This checklist verifies that all reorganization phases are working correctly. Complete each section and check off as you validate.

---

## Phase 1: Directory Structure & Configuration

### Files and Folders
- [ ] `R/` directory exists with 5 helper scripts
  - [ ] `R/cache_config.R` (defines cache paths)
  - [ ] `R/data_cleaning.R` (FReD cleaning)
  - [ ] `R/crossref_cache.R` (citation/author caching)
  - [ ] `R/augmentation.R` (modular augmentation)
  - [ ] `R/release_helpers.R` (OSF automation)
- [ ] `pipelines/` directory exists with independent folders
  - [ ] `pipelines/fred/` with `prepare_fred.qmd`
  - [ ] `pipelines/flora/` with `prepare_flora.qmd`
- [ ] `cache/` directory exists (gitignored)
- [ ] `output/` directory exists (gitignored)
- [ ] `cos_integration/` exists with README.md
- [ ] `archive/old_scripts/` contains archived files

### Configuration Files
- [ ] `.env.example` exists with template
- [ ] `.gitignore` properly excludes:
  - [ ] `cache/` directory
  - [ ] `output/` directory
  - [ ] `.env` file

---

## Phase 2: Helper Scripts Validation

### R/cache_config.R
- [ ] File exists and is sourced correctly
- [ ] Defines all required cache paths:
  - [ ] `CACHE_DIR`
  - [ ] `CROSSREF_DOI_CACHE`
  - [ ] `CROSSREF_CITATIONS_CACHE`
  - [ ] `CROSSREF_AUTHORS_CACHE`
  - [ ] `AUTHOR_OVERLAP_CACHE`
  - [ ] `MANUAL_REFERENCES`
  - [ ] `OPENALEX_KEYWORDS_CACHE`

### R/data_cleaning.R
- [ ] `clean_fred_data()` function exists
- [ ] Returns list with `cleaned_data` and `report`
- [ ] Handles:
  - [ ] Formatting standardization
  - [ ] DOI fixing
  - [ ] Non-printable character removal
  - [ ] Duplicate removal

### R/crossref_cache.R
- [ ] Citation functions work:
  - [ ] `load_citation_cache()`
  - [ ] `get_apa_references()`
  - [ ] Three-tier lookup: manual → cache → API
- [ ] Author functions work:
  - [ ] `get_crossref_authors()`
  - [ ] `compute_author_overlap()`
- [ ] DOI functions work:
  - [ ] `load_doi_cache()`
  - [ ] `save_doi_cache()`

### R/augmentation.R
- [ ] `augment_with_author_overlap()` adds overlap columns
- [ ] `augment_with_clean_references()` adds reference columns
- [ ] `augment_with_keywords()` adds keyword columns
- [ ] Functions handle missing data gracefully
- [ ] Progress logging visible during execution

### R/release_helpers.R
- [ ] `release_to_osf()` function exists
- [ ] Semantic versioning functions work:
  - [ ] `increment_version()`
  - [ ] `prepare_changelog()`
- [ ] OSF interaction functions available

---

## Phase 3: Pipeline Files Validation

### pipelines/fred/prepare_fred.qmd
- [ ] File exists and is executable with `quarto render`
- [ ] Configuration at top of file:
  - [ ] `FRED_GSHEET_URL` defined
  - [ ] `FRED_OUTPUT` set to `output/FReD.xlsx`
  - [ ] `COS_INTEGRATION_ENABLED` checks environment variable
- [ ] All 8 execution steps present and labeled
- [ ] Step 1: Loads helpers (data_cleaning, augmentation, cache_config)
- [ ] Step 2: Downloads from Google Sheets
- [ ] Step 3: COS integration (conditional on ENABLE_COS_MERGE)
- [ ] Step 4: Data cleaning
- [ ] Step 5: Data validation (framework)
- [ ] Step 6: ID generation
- [ ] Step 7: Augmentation (overlap, references, keywords)
- [ ] Step 8: Save to output/FReD.xlsx
- [ ] HTML report generates with collapsible sections

### pipelines/flora/prepare_flora.qmd
- [ ] File exists and is executable with `quarto render`
- [ ] Configuration at top of file:
  - [ ] `FLORA_GSHEET_URL` defined
  - [ ] `FLORA_OUTPUT` set to `output/flora.csv`
- [ ] All 10 execution steps present and labeled
- [ ] Step 1: Loads helpers (augmentation, cache_config)
- [ ] Step 2: Downloads from Google Sheets
- [ ] Step 3: Data preparation (column selection)
- [ ] Step 4: Deduplication by (doi_o, doi_r) pairs
- [ ] Step 5: DOI validation
- [ ] Step 6: Metadata fetching (framework)
- [ ] Step 7: Clean references augmentation
- [ ] Step 8: Privacy-preserving hash prefixes
- [ ] Step 9: Format for output
- [ ] Step 10: Save to output/flora.csv
- [ ] HTML report generates with collapsible sections

---

## Phase 4: COS Integration Validation

### cos_integration/README.md
- [ ] Complete documentation exists
- [ ] Explains toggle mechanism
- [ ] Shows enabling/disabling instructions
- [ ] Technical details documented
- [ ] Troubleshooting section present

### COS Toggle Mechanism
- [ ] `ENABLE_COS_MERGE` environment variable works
- [ ] Default is FALSE (COS disabled)
- [ ] Setting to TRUE includes COS data
- [ ] Setting to FALSE excludes COS data
- [ ] Can be toggled via .env file or export command

### COS Data Integration
- [ ] `cos_integration/cos_test_set_phase1_prepared.xlsx` exists
- [ ] When enabled, merged with FReD on common columns
- [ ] Both datasets processed identically
- [ ] Output contains combined data

---

## Phase 5: Breaking Changes & Migration

### Old Files Archived
- [ ] `archive/old_scripts/` contains old pipeline files:
  - [ ] `clean_cos_fred.R`
  - [ ] `crossref_author_retrieval.qmd`
  - [ ] `crossref_citation_cache.R`
  - [ ] `dataset validation.Rmd`
  - [ ] `hackathon prep - flora.qmd`
  - [ ] Others archived
- [ ] Old scripts are NOT at repository root

### Output Location Changes
- [ ] All output files go to `output/` directory
- [ ] NO symlinks created at root (output/FReD.xlsx → FReD.xlsx)
- [ ] Users must use `output/FReD.xlsx` and `output/flora.csv`
- [ ] This is documented as breaking change

### Documentation Updates
- [ ] README.md replaced with new version
- [ ] New README documents:
  - [ ] Repository structure
  - [ ] Both pipelines
  - [ ] Helper functions
  - [ ] COS integration
  - [ ] Breaking changes
- [ ] Migration path documented

---

## Integration Testing

### Helper Function Testing
Run these commands to verify helper scripts work:

```r
# Test 1: Data Cleaning
source("R/data_cleaning.R")
# Verify clean_fred_data() is defined

# Test 2: Augmentation
source("R/augmentation.R")
# Verify augment_with_author_overlap() is defined
# Verify augment_with_clean_references() is defined
# Verify augment_with_keywords() is defined

# Test 3: Caching
source("R/crossref_cache.R")
# Verify get_apa_references() is defined
# Verify get_crossref_authors() is defined

# Test 4: Release Helpers
source("R/release_helpers.R")
# Verify release_to_osf() is defined
```

- [ ] All sourcing completes without errors
- [ ] All functions defined and accessible

### Pipeline Dry-Run Testing

```bash
# Test 1: FReD Pipeline (without COS)
quarto render pipelines/fred/prepare_fred.qmd

# Check output
ls -lh output/FReD.xlsx
```

- [ ] FReD pipeline completes successfully
- [ ] `output/FReD.xlsx` created
- [ ] File has expected columns
- [ ] HTML report generates

```bash
# Test 2: FLoRA Pipeline
quarto render pipelines/flora/prepare_flora.qmd

# Check output
ls -lh output/flora.csv
wc -l output/flora.csv
```

- [ ] FLoRA pipeline completes successfully
- [ ] `output/flora.csv` created
- [ ] CSV has data rows
- [ ] HTML report generates

### COS Integration Testing

```bash
# Test 3: COS Integration
export ENABLE_COS_MERGE=TRUE
quarto render pipelines/fred/prepare_fred.qmd

# Compare file sizes
ls -lh output/FReD.xlsx
```

- [ ] Executes with ENABLE_COS_MERGE=TRUE
- [ ] Output file created
- [ ] File size appropriate for merged data
- [ ] Pipeline output indicates COS merge happened

```bash
# Test 4: Disable COS
export ENABLE_COS_MERGE=FALSE
quarto render pipelines/fred/prepare_fred.qmd

# Verify smaller file
ls -lh output/FReD.xlsx
```

- [ ] Executes with ENABLE_COS_MERGE=FALSE
- [ ] Output file created
- [ ] File size appropriate for FReD-only data
- [ ] Pipeline output indicates COS was skipped

---

## Documentation Validation

### README.md
- [ ] Exists at repository root
- [ ] Contains all required sections
- [ ] Quick Start section clear and complete
- [ ] Pipeline documentation accurate
- [ ] Breaking changes prominently noted
- [ ] COS integration explained
- [ ] Helper functions documented

### Supporting Documentation
- [ ] `IMPLEMENTATION_STATUS.md` - Current status overview
- [ ] `PHASE2_SUMMARY.md` - Helper script details
- [ ] `PHASE3-4_SUMMARY.md` - Pipeline and COS details
- [ ] `REORGANIZATION_PROGRESS.md` - Historical progress
- [ ] `.env.example` - Configuration template
- [ ] `cos_integration/README.md` - COS toggle instructions

### Documentation Accuracy
- [ ] All file paths correct
- [ ] All function names match actual code
- [ ] All environment variables documented
- [ ] All sections have examples

---

## Code Quality Checks

### No Broken References
- [ ] All `source()` calls point to existing files
- [ ] All function calls match defined functions
- [ ] No hardcoded paths (should use variables)
- [ ] No references to old file locations

### Consistent Styling
- [ ] Function naming: `action_what()` pattern
- [ ] Cache files organized by type (not purpose)
- [ ] Error handling present in all functions
- [ ] Progress logging at key steps

### Independence Verification
- [ ] FReD pipeline can run independently
- [ ] FLoRA pipeline can run independently
- [ ] Neither pipeline depends on output of the other
- [ ] Both use same augmentation and caching infrastructure

---

## Git Status Verification

### Repository Cleanliness
```bash
git status
git log --oneline -10
```

- [ ] Working directory clean or changes intentional
- [ ] No accidental files committed
- [ ] Commit history makes sense
- [ ] Breaking changes documented in commits

### File Tracking
- [ ] `cache/` directory in .gitignore
- [ ] `output/` directory in .gitignore
- [ ] `.env` file in .gitignore
- [ ] Old scripts archived and not tracked at root

---

## Final Checks

### Before Release

1. **Verify Production Readiness**
   - [ ] All pipelines tested and working
   - [ ] All helper functions accessible
   - [ ] Documentation complete and accurate
   - [ ] No TODO items or placeholders remaining

2. **Verify Breaking Changes Are Understood**
   - [ ] Users understand output location changed
   - [ ] Users know how to run new pipelines
   - [ ] Users understand COS toggle mechanism
   - [ ] Old scripts are archived and labeled

3. **Verify COS Toggle Works**
   - [ ] Default state: ENABLE_COS_MERGE=FALSE
   - [ ] Can be toggled without code changes
   - [ ] Can be removed entirely if needed
   - [ ] Instructions clear in cos_integration/README.md

4. **Verify Configuration**
   - [ ] All config options documented
   - [ ] .env.example complete
   - [ ] Environment variables work
   - [ ] Cache paths configurable

---

## Optional Items (Not Required for Release)

- [ ] R/data_validation.R extracted (framework ready)
- [ ] Release pipelines created (pipelines/fred/release_fred.qmd)
- [ ] Continuous integration setup
- [ ] Pre-commit hooks configured
- [ ] Performance optimization complete

---

## Sign-Off

### Completed By
- **Date**: _______________
- **Tester**: _______________
- **Notes**: _______________

### Ready for Production
- [ ] All required items checked
- [ ] All tests passed
- [ ] Documentation verified
- [ ] Breaking changes understood
- [ ] **READY FOR RELEASE** ✓

---

## Rollback Plan (If Issues Found)

If critical issues discovered:

1. Old scripts available in `archive/old_scripts/`
2. Previous README available in git history
3. Can revert specific commits
4. COS toggle can be disabled without code changes

---

## Next Steps After Release

1. Monitor pipeline execution for errors
2. Collect user feedback on new structure
3. Consider CI/CD automation
4. Optional: Create optional release pipelines
5. Optional: Extract data_validation.R fully
6. Optional: Add continuous integration tests

---

**Document Purpose**: Final comprehensive checklist to ensure all reorganization work is complete, tested, and ready for production use.

**Last Updated**: 2025-12-17
**Status**: Ready for validation
