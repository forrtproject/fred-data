# Phase 3 & 4 Completion Summary

## Phase 3: Pipeline Files Creation ✅

### Created Files

#### 1. pipelines/fred/prepare_fred.qmd
**Status**: ✅ Complete and ready to execute

**Content**:
- Step 1: Load helper functions (data_cleaning, augmentation)
- Step 2: Download FReD from Google Sheets
- Step 3: COS Integration (optional, environment-controlled)
- Step 4: Data Cleaning (uses `clean_fred_data()`)
- Step 5: Data Validation (framework ready for full validation)
- Step 6: Generate IDs (fred_id, entry_id, effect_id)
- Step 7: Data Augmentation (author overlap, references, keywords)
- Step 8: Save to output/FReD.xlsx

**Features**:
- Self-documenting Quarto format
- Interactive HTML output with expandable sections
- Progress logging at each step
- Summary statistics
- Error handling with fallbacks
- Environment-based COS toggle
- COS integration is optional and easy to disable

**Running the pipeline**:
```bash
# Without COS data
quarto render pipelines/fred/prepare_fred.qmd

# With COS data
export ENABLE_COS_MERGE=TRUE
quarto render pipelines/fred/prepare_fred.qmd

# Output: output/FReD.xlsx
```

---

#### 2. pipelines/flora/prepare_flora.qmd
**Status**: ✅ Complete and ready to execute

**Content**:
- Step 1: Load helper functions (augmentation, crossref_cache)
- Step 2: Download FLoRA from Google Sheets
- Step 3: Data Preparation (select relevant columns)
- Step 4: Deduplication (by doi_o, doi_r pairs)
- Step 5: DOI Validation
- Step 6: Fetch Metadata (framework for full implementation)
- Step 7: Clean References (augment with APA references)
- Step 8: Add Privacy-Preserving IDs (3-char hash prefixes)
- Step 9: Format for Output
- Step 10: Save to output/flora.csv

**Features**:
- Independent from FReD pipeline
- Deduplication by DOI pairs
- Privacy-preserving hash prefixes for API lookup
- Reference augmentation with manual overrides
- Summary statistics for quality control
- Interactive HTML output

**Running the pipeline**:
```bash
quarto render pipelines/flora/prepare_flora.qmd

# Output: output/flora.csv
```

---

## Phase 4: COS Integration Setup ✅

### Created/Updated Files

#### 1. cos_integration/README.md
**Status**: ✅ Complete documentation

**Contains**:
- Overview of COS integration
- File structure documentation
- Enabling/disabling instructions
- Preparation instructions
- How the integration works
- Column matching explanation
- Data consistency guarantees
- Troubleshooting guide

---

### COS Integration Design

The COS integration is controlled by a single environment variable:

```bash
# Enable COS data merging
export ENABLE_COS_MERGE=TRUE

# Run FReD pipeline with COS data merged
quarto render pipelines/fred/prepare_fred.qmd
```

**How it works**:

1. `pipelines/fred/prepare_fred.qmd` checks: `COS_INTEGRATION_ENABLED <- Sys.getenv("ENABLE_COS_MERGE", "FALSE") == "TRUE"`

2. If TRUE:
   - Reads `cos_integration/cos_test_set_phase1_prepared.xlsx`
   - Finds common columns between FReD and COS data
   - Merges on matching columns
   - Applies same cleaning and augmentation to both datasets

3. Output: Single `output/FReD.xlsx` containing both FReD and COS data

**Advantages**:
- Easy to toggle on/off without code changes
- No breaking changes to existing FReD processing
- Both datasets get identical cleaning and augmentation
- Can be disabled for future releases by setting `ENABLE_COS_MERGE=FALSE`
- Easy to remove entirely: delete cos_integration/ folder and remove conditional block

---

## Pipeline Dependencies & Data Flow

```
┌─────────────────────────────────────────────────┐
│                    pipelines/fred                │
│              prepare_fred.qmd                     │
└─────────────────────────────────────────────────┘
                    ↓
    ┌───────────────────────────────┐
    │ 1. Download FReD (Google Sheets)
    │ 2. Filter for validated-chosen
    │ 3. [Optional] Merge COS data
    │ 4. Clean: clean_fred_data()
    │ 5. Validate: [framework ready]
    │ 6. Generate IDs
    │ 7. Augment:
    │    - author_overlap
    │    - clean_references
    │    - keywords
    │ 8. Save → output/FReD.xlsx
    └───────────────────────────────┘
                    ↓
            [output/FReD.xlsx]

┌─────────────────────────────────────────────────┐
│                   pipelines/flora                │
│             prepare_flora.qmd                    │
└─────────────────────────────────────────────────┘
                    ↓
    ┌───────────────────────────────┐
    │ 1. Download FLoRA (Google Sheets)
    │ 2. Select relevant columns
    │ 3. Deduplicate (doi_o, doi_r)
    │ 4. Validate DOI format
    │ 5. Fetch metadata [framework]
    │ 6. Augment:
    │    - clean_references
    │    - privacy IDs
    │ 7. Format for output
    │ 8. Save → output/flora.csv
    └───────────────────────────────┘
                    ↓
             [output/flora.csv]
```

---

## Helper Function Integration

Both pipelines use shared helper functions:

### FReD Pipeline Uses:
- `clean_fred_data()` from R/data_cleaning.R
- `augment_with_author_overlap()` from R/augmentation.R
- `augment_with_clean_references()` from R/augmentation.R
- `augment_with_keywords()` from R/augmentation.R

### FLoRA Pipeline Uses:
- `augment_with_clean_references()` from R/augmentation.R

### Both Use:
- `load_citation_cache()`, `get_apa_references()` via R/augmentation.R
- `get_crossref_authors()` for author overlap via R/augmentation.R
- Cache configuration from R/cache_config.R

---

## Testing Pipelines

### Quick Test: FReD Pipeline

```bash
# Check configuration
cat pipelines/fred/prepare_fred.qmd | head -30

# Render (will run actual pipeline)
quarto render pipelines/fred/prepare_fred.qmd

# Check output
ls -lh output/FReD.xlsx
file output/FReD.xlsx
```

### Quick Test: FLoRA Pipeline

```bash
# Check configuration
cat pipelines/flora/prepare_flora.qmd | head -30

# Render (will run actual pipeline)
quarto render pipelines/flora/prepare_flora.qmd

# Check output
ls -lh output/flora.csv
wc -l output/flora.csv
```

### Test COS Integration

```bash
# Without COS (default)
quarto render pipelines/fred/prepare_fred.qmd
# FReD.xlsx will contain only main FReD data

# With COS
export ENABLE_COS_MERGE=TRUE
quarto render pipelines/fred/prepare_fred.qmd
# FReD.xlsx will contain merged FReD + COS data
# (assuming cos_test_set_phase1_prepared.xlsx exists)

# Back to default
export ENABLE_COS_MERGE=FALSE
```

---

## Optional: Release Pipelines

Release pipelines are ready to be created but are optional:

### pipelines/fred/release_fred.qmd (not yet created)
Would allow automated release of FReD to OSF with versioning

### pipelines/flora/release_flora.qmd (not yet created)
Would allow automated release of FLoRA to OSF with versioning

These would use `release_to_osf()` from R/release_helpers.R

---

## Environment Setup

Before running pipelines, ensure:

1. **Set up environment variables** (optional but recommended):
   ```bash
   # Copy template
   cp .env.example .env

   # Edit .env with your settings:
   # OSF_TOKEN=your_token_here
   # ENABLE_COS_MERGE=FALSE
   # OPENALEX_MAILTO=your_email@example.com
   ```

2. **Load environment**:
   ```bash
   set -a; source .env; set +a
   ```

3. **Or use environment variable directly**:
   ```bash
   export ENABLE_COS_MERGE=TRUE
   ```

---

## Next Steps

### Phase 5: Backwards Compatibility
- [ ] Create symlinks: `FReD.xlsx` → `output/FReD.xlsx`
- [ ] Create symlinks: `flora.csv` → `output/flora.csv`
- [ ] Archive old script files to archive/
- [ ] Update root README.md with new structure

### Other Improvements
- [ ] Complete R/data_validation.R (extract from dataset validation.Rmd)
- [ ] Create optional release pipelines (fred and flora)
- [ ] Add continuous integration checks
- [ ] Create validation workflow

---

## Summary Statistics

| Item | Count |
|------|-------|
| New pipeline files | 2 (.qmd) |
| COS documentation | 1 (README.md) |
| Execution steps in FReD pipeline | 8 |
| Execution steps in FLoRA pipeline | 10 |
| Shared helper functions used | 6+ |
| Environment variables supported | 3 |
| Output formats | 2 (Excel, CSV) |

---

## Files Ready for Execution

✅ Fully functional and can be run immediately:
- `pipelines/fred/prepare_fred.qmd`
- `pipelines/flora/prepare_flora.qmd`

🔄 Framework ready, full implementation pending:
- Data validation (existing validation.Rmd can be used as-is)
- Full metadata fetching (helper functions exist)
- Release pipelines (can be created from R/release_helpers.R)

---

**Completion Date**: 2025-12-17
**Phase 3 Status**: ✅ COMPLETE
**Phase 4 Status**: ✅ COMPLETE
**Ready for Phase 5**: ✅ YES
