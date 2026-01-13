#!/usr/bin/env Rscript
# Test script for author overlap detection pipeline

library(tidyverse)
library(jsonlite)
library(readxl)

cat("=== AUTHOR OVERLAP PIPELINE TEST ===\n\n")

# Load test data
cat("1. Loading COS validated dataset...\n")
cos_data <- read_excel("COS Reports/2025-11-05_COSdata_validated.xlsx")

cat(sprintf("   - Loaded %d rows\n", nrow(cos_data)))
cat(sprintf("   - Columns: %s\n", paste(names(cos_data), collapse=", ")))

# Extract study pairs with DOIs
cat("\n2. Extracting study pairs with DOIs...\n")
study_pairs <- cos_data %>%
  filter(!is.na(doi_o) & !is.na(doi_r)) %>%
  distinct(doi_o, doi_r) %>%
  mutate(doi_o = tolower(doi_o),
         doi_r = tolower(doi_r))

cat(sprintf("   - Found %d unique study pairs\n", nrow(study_pairs)))

# Load existing author data
cat("\n3. Loading existing author data...\n")
if (file.exists("crossref_retrieved_authors.xlsx")) {
  authors_df <- read_excel("crossref_retrieved_authors.xlsx")
  cat(sprintf("   - Loaded author data for %d DOIs\n", nrow(authors_df)))
} else {
  cat("   - No existing author data found\n")
  authors_df <- tibble(doi = character(), authors = character())
}

# Check which DOIs we have and which are missing
all_dois <- c(study_pairs$doi_o, study_pairs$doi_r) %>% unique() %>% str_subset("^10\\.")
missing_dois <- setdiff(tolower(all_dois), tolower(authors_df$doi))

cat(sprintf("   - Have data for: %d DOIs\n", length(all_dois) - length(missing_dois)))
cat(sprintf("   - Missing data for: %d DOIs\n", length(missing_dois)))

# ===== TEST 1: Examine existing author data structure =====
cat("\n4. EXAMINING EXISTING AUTHOR DATA STRUCTURE...\n")

# Check if we have any author data to examine
if (nrow(authors_df) == 0) {
  cat("\n   ⚠️  No author data available! Author retrieval script may not have been run yet.\n")
} else {
  # Sample a few author records to see their structure
  sample_records <- authors_df %>% slice_head(n = 5)

  for (i in 1:nrow(sample_records)) {
  doi <- sample_records$doi[i]
  authors_json <- sample_records$authors[i]

  cat(sprintf("\n   Sample %d - DOI: %s\n", i, doi))
  cat(sprintf("   JSON length: %d chars\n", nchar(authors_json)))

  tryCatch({
    authors <- fromJSON(authors_json)

    if (is.data.frame(authors)) {
      cat(sprintf("   Structure: data.frame with %d rows and columns: %s\n",
                  nrow(authors), paste(names(authors), collapse=", ")))

      # Show first 3 authors
      cat("   First authors:\n")
      for (j in 1:min(3, nrow(authors))) {
        cat(sprintf("     [%d] ", j))
        if ("family" %in% names(authors)) {
          cat(sprintf("family='%s'", authors$family[j]))
        }
        if ("given" %in% names(authors)) {
          cat(sprintf(", given='%s'", authors$given[j]))
        }
        if ("name" %in% names(authors)) {
          cat(sprintf(", name='%s'", authors$name[j]))
        }
        cat("\n")
      }
    } else if (is.list(authors)) {
      cat(sprintf("   Structure: list with %d elements\n", length(authors)))

      # Show first 3 authors
      cat("   First authors:\n")
      for (j in 1:min(3, length(authors))) {
        cat(sprintf("     [%d] ", j))
        author <- authors[[j]]
        if ("family" %in% names(author)) {
          cat(sprintf("family='%s'", author$family))
        }
        if ("given" %in% names(author)) {
          cat(sprintf(", given='%s'", author$given))
        }
        if ("name" %in% names(author)) {
          cat(sprintf(", name='%s'", author$name))
        }
        cat(" | keys: ", paste(names(author), collapse=", "))
        cat("\n")
      }
    } else {
      cat(sprintf("   Structure: %s\n", class(authors)))
    }
  }, error = function(e) {
    cat(sprintf("   ERROR parsing JSON: %s\n", e$message))
  })
  }
}

# ===== TEST 2: Test author name extraction function =====
cat("\n5. TESTING AUTHOR NAME EXTRACTION FUNCTION...\n")

extract_author_names <- function(author_json) {
  if (is.na(author_json) || author_json == "" || is.null(author_json)) {
    return(character(0))
  }

  tryCatch({
    authors <- jsonlite::fromJSON(author_json)

    if (is.null(authors) || (!is.data.frame(authors) && !is.list(authors))) {
      return(character(0))
    }

    # Handle data frame format
    if (is.data.frame(authors)) {
      names_vec <- character(nrow(authors))
      for (i in seq_len(nrow(authors))) {
        family <- if ("family" %in% names(authors)) authors$family[i] else NA
        name <- if ("name" %in% names(authors)) authors$name[i] else NA

        final_name <- if (!is.na(family) && nzchar(as.character(family))) {
          family
        } else if (!is.na(name) && nzchar(as.character(name))) {
          name
        } else {
          NA_character_
        }

        names_vec[i] <- if (!is.na(final_name)) {
          tolower(trimws(as.character(final_name)))
        } else {
          NA_character_
        }
      }
      return(na.omit(names_vec[nzchar(names_vec)]))
    }

    # Handle list format
    if (is.list(authors)) {
      names_vec <- character(length(authors))
      for (i in seq_along(authors)) {
        author <- authors[[i]]
        family <- if ("family" %in% names(author)) author$family else NA
        name <- if ("name" %in% names(author)) author$name else NA

        final_name <- if (!is.na(family) && nzchar(as.character(family))) {
          family
        } else if (!is.na(name) && nzchar(as.character(name))) {
          name
        } else {
          NA_character_
        }

        names_vec[i] <- if (!is.na(final_name)) {
          tolower(trimws(as.character(final_name)))
        } else {
          NA_character_
        }
      }
      return(na.omit(names_vec[nzchar(names_vec)]))
    }

    return(character(0))
  }, error = function(e) {
    message("Error extracting author names: ", e$message)
    return(character(0))
  })
}

# Test extraction on sample records
if (nrow(authors_df) > 0) {
  cat("\n   Testing extraction on available records:\n")
  for (i in 1:min(3, nrow(authors_df))) {
    doi <- authors_df$doi[i]
    authors_json <- authors_df$authors[i]

    names <- extract_author_names(authors_json)
    cat(sprintf("   DOI %s: extracted %d names\n", doi, length(names)))
    if (length(names) > 0) {
      cat(sprintf("      Names: %s\n", paste(head(names, 3), collapse=", ")))
    }
  }
}

# ===== TEST 3: Check for problematic author records =====
cat("\n6. CHECKING FOR PROBLEMATIC AUTHOR RECORDS...\n")

if (nrow(authors_df) == 0) {
  cat("   ⚠️  No author data to check for issues.\n")
  extraction_results <- tibble()
} else {
  extraction_results <- authors_df %>%
    rowwise() %>%
    mutate(
      extracted_count = length(extract_author_names(authors)),
      json_valid = tryCatch({
        fromJSON(authors)
        TRUE
      }, error = function(e) FALSE)
    ) %>%
    ungroup()

  problematic <- extraction_results %>% filter(!json_valid | extracted_count == 0)
}

if (nrow(extraction_results) > 0) {
  problematic <- extraction_results %>% filter(!json_valid | extracted_count == 0)

  cat(sprintf("\n   Records with invalid JSON: %d\n", sum(!extraction_results$json_valid)))
  cat(sprintf("   Records with NO extracted names: %d\n", sum(extraction_results$extracted_count == 0)))
  cat(sprintf("   Total problematic records: %d\n", nrow(problematic)))

  if (nrow(problematic) > 0) {
  cat("\n   Sample problematic records:\n")
  for (i in 1:min(3, nrow(problematic))) {
    doi <- problematic$doi[i]
    authors_json <- problematic$authors[i]
    cat(sprintf("\n   Problematic %d - DOI: %s\n", i, doi))
    cat(sprintf("   JSON (first 200 chars): %s...\n",
                substr(authors_json, 1, 200)))

    tryCatch({
      parsed <- fromJSON(authors_json)
      cat(sprintf("   Parsed structure: %s\n", paste(class(parsed), collapse=", ")))

      if (is.data.frame(parsed)) {
        cat(sprintf("   Columns: %s\n", paste(names(parsed), collapse=", ")))
      } else if (is.list(parsed) && length(parsed) > 0) {
        cat(sprintf("   List with %d elements, keys in first: %s\n",
                    length(parsed), paste(names(parsed[[1]]), collapse=", ")))
      }
    }, error = function(e) {
      cat(sprintf("   ERROR: %s\n", e$message))
    })
  }
  }
}

# ===== Summary =====
cat("\n7. SUMMARY\n")
cat(sprintf("   - Study pairs with DOIs: %d\n", nrow(study_pairs)))
cat(sprintf("   - Unique DOIs referenced: %d\n", length(all_dois)))
cat(sprintf("   - DOIs with author data: %d (%.1f%%)\n",
            length(all_dois) - length(missing_dois),
            100 * (1 - length(missing_dois) / length(all_dois))))

if (nrow(extraction_results) > 0) {
  cat(sprintf("   - Valid author records: %d (%.1f%%)\n",
              sum(extraction_results$json_valid),
              100 * mean(extraction_results$json_valid)))
  cat(sprintf("   - Records that extract at least 1 name: %d (%.1f%%)\n",
              sum(extraction_results$extracted_count > 0),
              100 * mean(extraction_results$extracted_count > 0)))
} else {
  cat("   - No author records to analyze\n")
}

cat("\n=== TEST COMPLETE ===\n")
