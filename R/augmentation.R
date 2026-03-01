# Data Augmentation Functions
# Modular functions for augmenting FReD/FLoRA datasets
# Includes: author overlap, reference cleaning, keyword fetching

library(dplyr)
library(rcrossref)


# ============================================================================
# Author Overlap Augmentation
# ============================================================================

#' Augment dataset with author overlap information
#' Computes author overlap between original and replication studies
#'
#' @param data Tibble with at least doi_o and doi_r columns
#' @param add_pct_column If TRUE, add author_overlap_pct column
#' @return Original data with added author_overlap column(s)
augment_with_author_overlap <- function(data, add_pct_column = TRUE) {

  message("\n=== Augmenting with Author Overlap ===")

  if (!"doi_o" %in% names(data) || !"doi_r" %in% names(data)) {
    warning("Data must have 'doi_o' and 'doi_r' columns. Skipping author overlap augmentation.")
    return(data)
  }

  # Get unique DOI pairs
  doi_pairs <- data %>%
    select(doi_o, doi_r) %>%
    distinct() %>%
    filter(!is.na(doi_o) & !is.na(doi_r))

  message("Found ", nrow(doi_pairs), " unique (doi_o, doi_r) pairs")

  # Compute author overlap
  message("Fetching author data from CrossRef...")
  augmented_pairs <- compute_author_overlap(doi_pairs, CROSSREF_AUTHORS_CACHE)

  message("Computing overlaps...")
  overlap_summary <- augmented_pairs %>%
    group_by(author_overlap) %>%
    count(name = "n_pairs") %>%
    arrange(desc(author_overlap))

  message("\nAuthor overlap distribution:")
  for (i in seq_len(nrow(overlap_summary))) {
    msg <- sprintf("  %d authors: %d pairs",
                   overlap_summary$author_overlap[i],
                   overlap_summary$n_pairs[i])
    message(msg)
  }

  # Merge back to original data
  result <- data %>%
    left_join(
      augmented_pairs %>% select(doi_o, doi_r, author_overlap, author_overlap_pct),
      by = c("doi_o", "doi_r")
    )

  # If add_pct_column is FALSE, remove the percentage column
  if (!add_pct_column) {
    result <- result %>% select(-author_overlap_pct)
  }

  message("✓ Author overlap augmentation complete")
  result
}

#' Compute author overlap from existing author_o and author_r JSON columns
#' This fills in author_overlap for rows where it's missing but author data exists
#'
#' @param data Tibble with author_o and author_r columns (JSON format)
#' @return Data with author_overlap filled in where possible
fill_author_overlap_from_columns <- function(data) {

  if (!all(c("author_o", "author_r") %in% names(data))) {
    message("Missing author_o or author_r columns, skipping fill")
    return(data)
  }

  # Initialize columns if not present

if (!"author_overlap" %in% names(data)) {
    data$author_overlap <- NA_integer_
  }
  if (!"author_overlap_pct" %in% names(data)) {
    data$author_overlap_pct <- NA_real_
  }

  # Find rows that need filling (missing overlap but have both author columns)
  needs_fill <- which(
    is.na(data$author_overlap) &
    !is.na(data$author_o) & nzchar(data$author_o) &
    !is.na(data$author_r) & nzchar(data$author_r)
  )

  if (length(needs_fill) == 0) {
    message("No rows need author overlap filling")
    return(data)
  }

  message(sprintf("Filling author overlap for %d rows from existing author columns...", length(needs_fill)))

  # Helper to extract family names from JSON
  extract_family_names <- function(json_str) {
    tryCatch({
      if (is.na(json_str) || !nzchar(json_str) || json_str == "[]") {
        return(character(0))
      }
      authors <- jsonlite::fromJSON(json_str)
      if (is.data.frame(authors) && "family" %in% names(authors)) {
        return(tolower(trimws(authors$family)))
      }
      character(0)
    }, error = function(e) character(0))
  }

  # Compute overlap for each row
  for (i in needs_fill) {
    authors_o <- extract_family_names(data$author_o[i])
    authors_r <- extract_family_names(data$author_r[i])

    if (length(authors_o) > 0 && length(authors_r) > 0) {
      overlap <- length(intersect(authors_o, authors_r))
      data$author_overlap[i] <- overlap
      # Percentage based on replication authors (measures independence of replication team)
      data$author_overlap_pct[i] <- round(100 * overlap / length(authors_r), 1)
    }
  }

  filled <- sum(!is.na(data$author_overlap[needs_fill]))
  message(sprintf("✓ Filled author overlap for %d rows", filled))

  data
}

