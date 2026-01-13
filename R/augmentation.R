# Data Augmentation Functions
# Modular functions for augmenting FReD/FLoRA datasets
# Includes: author overlap, reference cleaning, keyword fetching

library(tidyverse)
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

