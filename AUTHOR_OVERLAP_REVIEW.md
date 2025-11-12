# Author Overlap Pipeline Review & Analysis

## Test Results Summary

### Current Status
- **COS Dataset**: 1,699 rows with 623 unique study pairs
- **DOIs Referenced**: 796 unique DOIs (original + replication studies)
- **Author Data Files**:
  - `crossref_retrieved_authors.xlsx`: Empty (headers only, 0 rows)
  - `crossref_author_overlap.xlsx`: Empty (headers only, 0 rows)
  - **Status**: Author retrieval script has NOT been run yet

### Key Finding
The pipeline infrastructure is correctly set up, but no author data has been retrieved from CrossRef yet. Once the `crossref_author_retrieval.qmd` script is executed with the COS dataset, the pipeline can be fully tested.

---

## Robustness Issues Identified

### Issue 1: Incomplete Handling of Missing Family Names

**Location**: [crossref_author_retrieval.qmd:113-123](crossref_author_retrieval.qmd#L113-L123)

**Problem**: The current implementation falls back from `family` to `name` field, but doesn't account for:
- Authors with neither field
- Empty strings or whitespace-only values in both fields
- Nested author structures (e.g., organizations instead of people)
- Authors represented as pure strings instead of objects

**Current Code**:
```r
family <- if ("family" %in% names(authors)) authors$family[i] else NA
name <- if ("name" %in% names(authors)) authors$name[i] else NA

final_name <- if (!is.na(family) && nzchar(as.character(family))) {
  family
} else if (!is.na(name) && nzchar(as.character(name))) {
  name
} else {
  NA_character_
}
```

**Issues with this approach**:
1. `nzchar()` can fail on complex objects
2. When both `family` and `name` are missing, returns `NA_character_` silently
3. No logging of how many authors are dropped per record
4. No handling of author literals (single values instead of objects)

---

### Issue 2: Silent Failure on Malformed JSON Structures

**Location**: [crossref_author_retrieval.qmd:105-108](crossref_author_retrieval.qmd#L105-L108)

**Problem**: The function checks if `authors` is a data.frame OR list, but CrossRef can return:
- Arrays of objects (list of lists)
- Single objects (list of lists with 1 element)
- Strings or other unexpected types
- Null values

When none of these conditions are met, it silently returns `character(0)` with no indication something went wrong.

---

### Issue 3: No Tracking of Extraction Quality

**Problem**: The pipeline doesn't track:
- How many authors per study had extractable names
- Extraction failure rates
- Which studies lose all authors due to malformed data
- Data quality issues before they propagate to the overlap analysis

This makes debugging difficult and prevents identifying systematic data quality issues.

---

## Recommended Improvements

### 1. More Robust Author Name Extraction

**Enhanced extraction function**:

```r
extract_author_names_robust <- function(author_json, doi = NA) {
  if (is.na(author_json) || author_json == "" || is.null(author_json)) {
    return(list(names = character(0), status = "empty_input"))
  }

  tryCatch({
    authors <- jsonlite::fromJSON(author_json, simplifyDataFrame = FALSE)

    if (is.null(authors) || length(authors) == 0) {
      return(list(names = character(0), status = "null_result"))
    }

    # Convert to list format if it's a data frame
    if (is.data.frame(authors)) {
      authors <- split(authors, seq(nrow(authors))) %>%
        lapply(function(x) as.list(x))
    }

    # Ensure it's a list of items
    if (!is.list(authors) || (!is.null(names(authors)) && !"family" %in% names(authors))) {
      # It's a single author or malformed
      authors <- list(authors)
    }

    names_extracted <- character()
    dropped_count <- 0

    for (i in seq_along(authors)) {
      author <- authors[[i]]

      # Skip if not a list/data frame
      if (!is.list(author) && !is.data.frame(author)) {
        # Try to convert string representation
        if (is.character(author)) {
          name <- trimws(tolower(author[1]))
          if (nzchar(name)) {
            names_extracted <- c(names_extracted, name)
          }
        } else {
          dropped_count <- dropped_count + 1
        }
        next
      }

      # Extract family name (primary) or given/name (fallback)
      family <- author[["family"]] %||% author[["given"]] %||% author[["name"]]

      if (is.na(family) || !is.character(family) || !nzchar(as.character(family))) {
        dropped_count <- dropped_count + 1
        next
      }

      final_name <- trimws(tolower(as.character(family[1])))
      if (nzchar(final_name)) {
        names_extracted <- c(names_extracted, final_name)
      } else {
        dropped_count <- dropped_count + 1
      }
    }

    return(list(
      names = unique(names_extracted),
      status = "success",
      total_authors = length(authors),
      extracted = length(names_extracted),
      dropped = dropped_count
    ))

  }, error = function(e) {
    return(list(
      names = character(0),
      status = paste("error:", e$message),
      doi = doi
    ))
  })
}
```

**Benefits**:
- Returns structured output with status information
- Handles more edge cases
- Tracks extraction success rate
- Provides debugging information (dropped authors, etc.)

---

### 2. Add Validation Step Before Overlap Computation

**New section in pipeline**:

```r
# Validate author data quality before computing overlap
author_validation <- study_pairs %>%
  left_join(authors_df %>% rename(doi_o = doi, authors_o = authors), by = "doi_o") %>%
  left_join(authors_df %>% rename(doi_r = doi, authors_r = authors), by = "doi_r") %>%
  rowwise() %>%
  mutate(
    extraction_o = list(extract_author_names_robust(authors_o, doi_o)),
    extraction_r = list(extract_author_names_robust(authors_r, doi_r)),
    names_o = extraction_o$names,
    names_r = extraction_r$names,
    both_successful = (extraction_o$status == "success" & extraction_r$status == "success"),
    either_has_names = (length(names_o) > 0 | length(names_r) > 0)
  ) %>%
  ungroup()

# Quality report
cat("\n=== AUTHOR EXTRACTION QUALITY REPORT ===\n")
cat(sprintf("Study pairs analyzed: %d\n", nrow(author_validation)))
cat(sprintf("Both studies have extractable authors: %d (%.1f%%)\n",
            sum(author_validation$both_successful),
            100 * mean(author_validation$both_successful)))
cat(sprintf("At least one study has authors: %d (%.1f%%)\n",
            sum(author_validation$either_has_names),
            100 * mean(author_validation$either_has_names)))
```

---

### 3. Add Logging for Debugging

**Recommendation**: Add detailed logging that tracks:
- Number of authors per study
- Extraction success/failure rates per DOI
- Common failure patterns
- Studies with 0 extractable authors

This will help identify systematic issues with specific publishers or DOI patterns.

---

## Next Steps

1. **Run Author Retrieval**: Execute `crossref_author_retrieval.qmd` with the full COS dataset
   - This will populate the author data files
   - Expected: ~800 DOI lookups against CrossRef

2. **Test Pipeline**: Once author data is populated:
   - Re-run `test_author_overlap_pipeline.R` to examine actual author data structures
   - Identify any CrossRef-specific patterns or issues
   - Validate extraction function performance

3. **Implement Improvements** (if needed based on test results):
   - Update extraction function with robustness enhancements
   - Add validation reporting
   - Implement logging

4. **Generate Overlap Results**:
   - Compute final author overlap statistics
   - Validate against sample of study pairs
   - Integrate into COS report

---

## Testing Checklist

- [ ] Author retrieval script executed successfully
- [ ] Author data files populated with expected number of records
- [ ] No invalid JSON structures encountered
- [ ] Extraction function handles all author formats
- [ ] Overlap computation completes without errors
- [ ] Overlap statistics reasonable (check % with author overlap)
- [ ] Sample validation: manually verify some overlapping pairs
- [ ] COS report generates successfully with author_overlap variable

---

## Code Quality Notes

The existing pipeline follows good practices:
- ✓ Modular structure (retrieval → extraction → overlap)
- ✓ Error handling with tryCatch
- ✓ Proper data validation (lowercasing DOIs, filtering)
- ✓ Clear separation of concerns

Areas for enhancement:
- More defensive error handling
- Structured status returns instead of silent failures
- Better logging and debugging information
- Performance metrics (extraction success rates, etc.)
