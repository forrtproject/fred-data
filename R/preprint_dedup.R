# Detect and resolve preprint-publication duplicates in FLoRA data
#
# Addresses: https://github.com/.../issues/105
#
# Two kinds of duplicate:
#   1. Replication-side: same doi_o + study_o, but doi_r is both a preprint
#      and a published version of the same paper.
#   2. Original-side: different doi_o values that are preprint/published (or
#      DOI-format variants) of the same original paper.
#
# Workflow:
#   - find_preprint_pub_duplicates() identifies candidates.
#   - resolve_preprint_dedup() detects + applies: by default it drops one DOI
#     from each pair (preprint loses; for DOI variants the non-canonical loses;
#     otherwise doi_2 loses). Pairs listed in cache/confirmed_preprint_duplicates.csv
#     override that default: action=keep_both retains both rows; keep_1/keep_2
#     pick which survives.
#   - apply_confirmed_preprint_dedup() applies *only* keep_1/keep_2 entries
#     from the confirmed file early in the pipeline, so the reference fetch
#     sees canonical DOIs.
#   - Detected candidates + the action taken are logged to
#     output/preprint_dedup_candidates.csv each run.

library(dplyr)
library(jsonlite)
library(stringr)

# ---- constants ----
PREPRINT_DOI_PREFIXES <- c(
"10.31234/",
  "10.31219/",
  "10.17605/",
  "10.48550/",
  "10.1101/",
  "10.2139/",
  "10.20944/",
  "10.21203/",
  "10.53841/"
)

CONFIRMED_DEDUP_PATH <- here::here("cache", "confirmed_preprint_duplicates.csv")
CANDIDATES_PATH      <- here::here("output", "preprint_dedup_candidates.csv")

# ---- helpers ----

#' Check whether a DOI belongs to a known preprint server
is_preprint_doi <- function(doi) {
  vapply(doi, function(d) {
    if (is.na(d) || !nzchar(d)) return(FALSE)
    any(startsWith(tolower(d), PREPRINT_DOI_PREFIXES))
  }, logical(1))
}

#' Normalize a title for fuzzy comparison
normalize_title <- function(title) {
  title <- tolower(trimws(as.character(title)))
  title <- gsub("<[^>]+>", "", title)        # strip HTML tags
  title <- gsub("[^a-z0-9 ]", "", title)     # keep alphanumeric + spaces
  title <- gsub("\\s+", " ", title)          # collapse whitespace
  trimws(title)
}

#' Pairwise title similarity (0-1) using Levenshtein distance
title_similarity <- function(t1, t2) {
  t1 <- normalize_title(t1)
  t2 <- normalize_title(t2)
  if (is.na(t1) || is.na(t2) || !nzchar(t1) || !nzchar(t2)) return(0)
  if (t1 == t2) return(1)
  max_len <- max(nchar(t1), nchar(t2))
  if (max_len == 0) return(0)
  1 - adist(t1, t2)[1, 1] / max_len
}

#' Extract the first author's family name from a CrossRef-style JSON string
#' or from a plain-text author string
extract_first_author <- function(author_str) {
  if (is.na(author_str) || !nzchar(trimws(author_str))) return(NA_character_)
  # Try JSON parse first (CrossRef format)
  parsed <- tryCatch(fromJSON(author_str, simplifyDataFrame = TRUE), error = function(e) NULL)
  if (!is.null(parsed) && is.data.frame(parsed) && "family" %in% names(parsed)) {
    first <- parsed %>% filter(sequence == "first" | row_number() == 1) %>% slice(1)
    return(tolower(trimws(first$family)))
  }
  # Fallback: plain text — take first word (assumed surname)
  tolower(trimws(strsplit(author_str, "[,;&]")[[1]][1]))
}

#' Normalize a DOI to canonical form
#'  - lowercase
#'  - remove double slashes that are typos (10.1037//0022 -> 10.1037/0022)
#'  - decode URL-encoded characters like %3c %3e
normalize_doi <- function(doi) {
  if (is.na(doi) || !nzchar(doi)) return(doi)
  d <- tolower(trimws(doi))
  d <- gsub("^(https?://)?(dx\\.)?doi\\.org/", "", d)
  d <- gsub("^doi:", "", d)
  # Fix double-slash typo (e.g. 10.1037//0022-3514...)
  d <- gsub("^(10\\.[0-9]+)//", "\\1/", d)
  # Decode percent-encoded chars so variant DOIs match
  d <- tryCatch(utils::URLdecode(d), error = function(e) d)
  d
}

# ---- main detection function ----

#' Find candidate preprint-publication duplicates
#'
#' @param data  A data frame with at least: doi_o, doi_r, title_o, title_r,
#'              author_o, author_r, year_o, year_r, study_o
#' @param title_threshold  Minimum title similarity (0-1) to flag a pair
#' @param verbose  Print progress messages
#' @return A tibble of candidate duplicate pairs
find_preprint_pub_duplicates <- function(data,
                                         title_threshold = 0.80,
                                         verbose = TRUE) {
  candidates <- tibble(
    side            = character(),
    doi_1           = character(),
    doi_2           = character(),
    title_1         = character(),
    title_2         = character(),
    title_sim       = numeric(),
    first_author_1  = character(),
    first_author_2  = character(),
    year_1          = character(),
    year_2          = character(),
    is_preprint_1   = logical(),
    is_preprint_2   = logical(),
    group_key       = character(),
    doi_o_group     = character()
  )

  # ----------------------------------------------------------------
  # A) Replication-side: same doi_o, different doi_r
  #    Check both within same study_o and across different study_o
  #    (study_o may differ due to data entry inconsistencies)
  # ----------------------------------------------------------------
  data <- data %>% mutate(.row = row_number())
  groups <- data %>%
    group_by(doi_o) %>%
    filter(n() > 1, !is.na(title_r)) %>%
    group_split()

  if (verbose) cat(sprintf("Checking %d doi_o groups with >1 row for replication-side duplicates...\n",
                            length(groups)))

  for (grp in groups) {
    n <- nrow(grp)
    if (n < 2) next
    for (i in seq_len(n - 1)) {
      for (j in (i + 1):n) {
        # Skip if same doi_r (already deduped by exact match)
        if (!is.na(grp$doi_r[i]) && !is.na(grp$doi_r[j]) &&
            normalize_doi(grp$doi_r[i]) == normalize_doi(grp$doi_r[j])) next

        sim <- title_similarity(grp$title_r[i], grp$title_r[j])
        if (sim < title_threshold) next

        fa1 <- extract_first_author(grp$author_r[i])
        fa2 <- extract_first_author(grp$author_r[j])

        # Require either first-author match or at least one preprint DOI
        author_match <- !is.na(fa1) && !is.na(fa2) && fa1 == fa2
        any_preprint <- is_preprint_doi(grp$doi_r[i]) || is_preprint_doi(grp$doi_r[j])

        if (!author_match && !any_preprint) next

        candidates <- bind_rows(candidates, tibble(
          side           = "replication",
          doi_1          = grp$doi_r[i],
          doi_2          = grp$doi_r[j],
          title_1        = grp$title_r[i],
          title_2        = grp$title_r[j],
          title_sim      = round(sim, 3),
          first_author_1 = fa1 %||% NA_character_,
          first_author_2 = fa2 %||% NA_character_,
          year_1         = as.character(grp$year_r[i]),
          year_2         = as.character(grp$year_r[j]),
          is_preprint_1  = is_preprint_doi(grp$doi_r[i]),
          is_preprint_2  = is_preprint_doi(grp$doi_r[j]),
          group_key      = paste0("doi_o: ", grp$doi_o[1]),
          doi_o_group    = grp$doi_o[1]
        ))
      }
    }
  }

  # ----------------------------------------------------------------
  # B) Original-side: different doi_o pointing to the same paper
  # ----------------------------------------------------------------
  originals <- data %>%
    filter(!is.na(doi_o), !is.na(title_o)) %>%
    distinct(doi_o, .keep_all = TRUE) %>%
    mutate(
      first_author_o = vapply(author_o, extract_first_author, character(1)),
      title_o_norm   = normalize_title(title_o),
      doi_o_norm     = vapply(doi_o, normalize_doi, character(1))
    )

  if (verbose) cat(sprintf("Checking %d unique doi_o for original-side duplicates...\n",
                            nrow(originals)))

  # B1: exact normalized-title match
  title_dupes <- originals %>%
    group_by(title_o_norm) %>%
    filter(n() > 1) %>%
    group_split()

  for (tgrp in title_dupes) {
    n <- nrow(tgrp)
    for (i in seq_len(n - 1)) {
      for (j in (i + 1):n) {
        if (tgrp$doi_o_norm[i] == tgrp$doi_o_norm[j]) next   # same DOI after normalisation

        candidates <- bind_rows(candidates, tibble(
          side           = "original",
          doi_1          = tgrp$doi_o[i],
          doi_2          = tgrp$doi_o[j],
          title_1        = tgrp$title_o[i],
          title_2        = tgrp$title_o[j],
          title_sim      = 1,
          first_author_1 = tgrp$first_author_o[i],
          first_author_2 = tgrp$first_author_o[j],
          year_1         = as.character(tgrp$year_o[i]),
          year_2         = as.character(tgrp$year_o[j]),
          is_preprint_1  = is_preprint_doi(tgrp$doi_o[i]),
          is_preprint_2  = is_preprint_doi(tgrp$doi_o[j]),
          group_key      = paste0("title: ", substr(tgrp$title_o_norm[1], 1, 60)),
          doi_o_group    = NA_character_
        ))
      }
    }
  }

  # B2: DOI-normalisation duplicates (e.g. 10.1037//... vs 10.1037/...)
  doi_norm_dupes <- originals %>%
    group_by(doi_o_norm) %>%
    filter(n() > 1) %>%
    group_split()

  for (dgrp in doi_norm_dupes) {
    n <- nrow(dgrp)
    for (i in seq_len(n - 1)) {
      for (j in (i + 1):n) {
        if (dgrp$doi_o[i] == dgrp$doi_o[j]) next
        # Skip if already captured by title match above
        already <- candidates %>%
          filter(side == "original",
                 (doi_1 == dgrp$doi_o[i] & doi_2 == dgrp$doi_o[j]) |
                 (doi_1 == dgrp$doi_o[j] & doi_2 == dgrp$doi_o[i]))
        if (nrow(already) > 0) next

        candidates <- bind_rows(candidates, tibble(
          side           = "original (DOI variant)",
          doi_1          = dgrp$doi_o[i],
          doi_2          = dgrp$doi_o[j],
          title_1        = dgrp$title_o[i],
          title_2        = dgrp$title_o[j],
          title_sim      = title_similarity(dgrp$title_o[i], dgrp$title_o[j]),
          first_author_1 = dgrp$first_author_o[i],
          first_author_2 = dgrp$first_author_o[j],
          year_1         = as.character(dgrp$year_o[i]),
          year_2         = as.character(dgrp$year_o[j]),
          is_preprint_1  = is_preprint_doi(dgrp$doi_o[i]),
          is_preprint_2  = is_preprint_doi(dgrp$doi_o[j]),
          group_key      = paste0("doi_variant: ", dgrp$doi_o_norm[1]),
          doi_o_group    = NA_character_
        ))
      }
    }
  }

  # B3: fuzzy title match within same first-author block
  author_blocks <- originals %>%
    filter(!is.na(first_author_o)) %>%
    group_by(first_author_o) %>%
    filter(n() > 1) %>%
    group_split()

  for (ablk in author_blocks) {
    n <- nrow(ablk)
    if (n < 2) next
    for (i in seq_len(n - 1)) {
      for (j in (i + 1):n) {
        if (ablk$doi_o_norm[i] == ablk$doi_o_norm[j]) next
        if (ablk$title_o_norm[i] == ablk$title_o_norm[j]) next  # already caught above

        sim <- title_similarity(ablk$title_o[i], ablk$title_o[j])
        if (sim < title_threshold) next

        candidates <- bind_rows(candidates, tibble(
          side           = "original (fuzzy)",
          doi_1          = ablk$doi_o[i],
          doi_2          = ablk$doi_o[j],
          title_1        = ablk$title_o[i],
          title_2        = ablk$title_o[j],
          title_sim      = round(sim, 3),
          first_author_1 = ablk$first_author_o[i],
          first_author_2 = ablk$first_author_o[j],
          year_1         = as.character(ablk$year_o[i]),
          year_2         = as.character(ablk$year_o[j]),
          is_preprint_1  = is_preprint_doi(ablk$doi_o[i]),
          is_preprint_2  = is_preprint_doi(ablk$doi_o[j]),
          group_key      = paste0("author: ", ablk$first_author_o[1]),
          doi_o_group    = NA_character_
        ))
      }
    }
  }

  # deduplicate candidates (a pair may be found by multiple methods)
  candidates <- candidates %>%
    mutate(pair_key = paste0(pmin(doi_1, doi_2), "||", pmax(doi_1, doi_2))) %>%
    distinct(pair_key, .keep_all = TRUE) %>%
    select(-pair_key) %>%
    arrange(side, group_key)

  if (verbose) {
    cat(sprintf("\nFound %d candidate duplicate pairs:\n", nrow(candidates)))
    repl_n <- sum(candidates$side == "replication")
    orig_n <- sum(grepl("^original", candidates$side))
    cat(sprintf("  Replication-side: %d\n", repl_n))
    cat(sprintf("  Original-side:    %d\n", orig_n))
  }

  candidates
}

# ---- derive doi_remove / doi_keep from action ----

#' Given a row from the candidates table with an action filled in,
#' return the DOI to remove and the DOI to keep.
derive_remove_keep <- function(action, doi_1, doi_2) {
  switch(action,
    keep_1 = list(doi_remove = doi_2, doi_keep = doi_1),
    keep_2 = list(doi_remove = doi_1, doi_keep = doi_2),
    list(doi_remove = NA_character_, doi_keep = NA_character_)
  )
}

# ---- apply confirmed duplicates ----

#' Apply confirmed preprint-publication deduplication
#'
#' Reads confirmed_preprint_duplicates.csv (if it exists).
#' The file has the same format as the candidates file; only rows where the
#' `action` column is filled in ("keep_1" or "keep_2") are applied.
#'
#' - Replication-side (action = keep_1/keep_2): removes the row whose doi_r
#'   is the one NOT kept.
#' - Original-side (action = keep_1/keep_2): replaces the removed doi_o with
#'   the kept doi_o in all rows, then re-dedups.
#'
#' @param data  FLoRA data frame (must have doi_o, doi_r)
#' @param confirmed_path  Path to confirmed duplicates CSV
#' @param verbose Print progress
#' @return Updated data frame
apply_confirmed_preprint_dedup <- function(data,
                                            confirmed_path = CONFIRMED_DEDUP_PATH,
                                            verbose = TRUE) {
  # Ensure alt columns exist
  if (!"doi_o_alt" %in% names(data)) data$doi_o_alt <- NA_character_
  if (!"doi_r_alt" %in% names(data)) data$doi_r_alt <- NA_character_

  if (!file.exists(confirmed_path)) {
    if (verbose) cat("No confirmed duplicates file found at:", confirmed_path, "\n")
    return(data)
  }

  confirmed <- readr::read_csv(confirmed_path, show_col_types = FALSE) %>%
    filter(!is.na(action), action %in% c("keep_1", "keep_2"))

  if (nrow(confirmed) == 0) {
    if (verbose) cat("No actionable entries in confirmed duplicates file\n")
    return(data)
  }

  if (verbose) cat(sprintf("Applying %d confirmed duplicate resolutions\n", nrow(confirmed)))

  # Derive doi_remove / doi_keep from action
  resolved <- confirmed %>%
    rowwise() %>%
    mutate(
      doi_remove = derive_remove_keep(action, doi_1, doi_2)$doi_remove,
      doi_keep   = derive_remove_keep(action, doi_1, doi_2)$doi_keep
    ) %>%
    ungroup()

  n_before <- nrow(data)

  # --- Replication-side: transfer doi_r_alt from removed row to kept row, then remove ---
  repl_resolved <- resolved %>% filter(grepl("^replication", side))

  for (i in seq_len(nrow(repl_resolved))) {
    doi_rm <- tolower(repl_resolved$doi_remove[i])
    doi_kp <- tolower(repl_resolved$doi_keep[i])
    doi_o_scope <- tolower(repl_resolved$doi_o_group[i])

    # Skip entries with NA doi_remove (nothing to remove)
    if (is.na(doi_rm)) {
      if (verbose) cat(sprintf("  Skipping replication entry with NA doi_remove (doi_keep=%s)\n", doi_kp))
      next
    }

    # Find all doi_o groups where the kept doi_r exists
    doi_os_with_kept <- unique(tolower(data$doi_o[tolower(data$doi_r) == doi_kp]))

    # Remove doi_r=preprint only where doi_r=published also exists under the same doi_o
    is_target <- tolower(data$doi_r) == doi_rm & tolower(data$doi_o) %in% doi_os_with_kept

    # Store the removed DOI as doi_r_alt on the kept row(s) in those same doi_o groups
    is_kept <- tolower(data$doi_r) == doi_kp & tolower(data$doi_o) %in% doi_os_with_kept
    data$doi_r_alt[is_kept & is.na(data$doi_r_alt)] <- repl_resolved$doi_remove[i]

    # Remove the duplicate rows
    data <- data[!is_target, ]
  }

  if (nrow(repl_resolved) > 0 && verbose) {
    cat(sprintf("  Removed %d replication-side duplicate rows (alt DOIs preserved)\n",
                n_before - nrow(data)))
  }

  # --- Original-side: replace doi_remove with doi_keep, store old in doi_o_alt ---
  orig_resolved <- resolved %>%
    filter(grepl("^original", side))

  if (nrow(orig_resolved) > 0) {
    doi_map <- setNames(tolower(orig_resolved$doi_keep), tolower(orig_resolved$doi_remove))
    matched <- tolower(data$doi_o) %in% names(doi_map)
    data <- data %>%
      mutate(
        doi_o_alt = dplyr::if_else(matched & is.na(doi_o_alt),
                                   doi_o,
                                   doi_o_alt),
        doi_o     = dplyr::if_else(matched,
                                   doi_map[tolower(doi_o)],
                                   doi_o)
      )
    if (verbose) cat(sprintf("  Replaced %d original-side DOIs (alt DOIs preserved)\n",
                              nrow(orig_resolved)))

    # Re-dedup after DOI replacement (may create exact duplicates).
    # Include url_r alongside doi_r so that distinct replications of the same
    # original paper (same doi_o, no doi_r, different url_r — common for SCORE)
    # are not collapsed together.
    norm_url_key <- function(x) {
      x <- tolower(trimws(as.character(x)))
      x <- gsub("^https?://", "", x)
      x <- gsub("^www\\.", "", x)
      x <- gsub("/+$", "", x)
      dplyr::na_if(x, "")
    }
    n_before_dedup <- nrow(data)
    data <- data %>%
      mutate(.url_r_key = norm_url_key(url_r)) %>%
      distinct(doi_o, study_o, coalesce(.url_r_key, doi_r), .keep_all = TRUE) %>%
      select(-.url_r_key)
    if (verbose && nrow(data) < n_before_dedup) {
      cat(sprintf("  Removed %d rows that became duplicates after DOI replacement\n",
                  n_before_dedup - nrow(data)))
    }
  }

  if (verbose) cat(sprintf("  Net rows removed: %d\n", n_before - nrow(data)))
  data
}

# ---- default resolution rule ----

#' Decide which DOI in a candidate pair to drop when no override is set.
#'
#' Rule:
#'   1. If exactly one DOI is a preprint, drop the preprint.
#'   2. For "original (DOI variant)" pairs, drop the non-canonical form
#'      (the one whose normalised DOI differs from itself).
#'   3. Otherwise, deterministically drop doi_2.
#'
#' Returns NULL when either DOI is NA — those pairs cannot be auto-resolved.
default_resolve_pair <- function(side, doi_1, doi_2,
                                  is_preprint_1, is_preprint_2) {
  if (is.na(doi_1) || is.na(doi_2)) return(NULL)

  pp1 <- isTRUE(is_preprint_1)
  pp2 <- isTRUE(is_preprint_2)
  if (pp1 && !pp2) return(list(doi_remove = doi_1, doi_keep = doi_2))
  if (!pp1 && pp2) return(list(doi_remove = doi_2, doi_keep = doi_1))

  if (grepl("DOI variant", side, fixed = TRUE)) {
    canon1 <- normalize_doi(doi_1) == tolower(trimws(doi_1))
    canon2 <- normalize_doi(doi_2) == tolower(trimws(doi_2))
    if (canon1 && !canon2) return(list(doi_remove = doi_2, doi_keep = doi_1))
    if (!canon1 && canon2) return(list(doi_remove = doi_1, doi_keep = doi_2))
  }

  list(doi_remove = doi_2, doi_keep = doi_1)
}

# ---- pipeline integration ----

#' Detect preprint/publication duplicate candidates and apply resolutions.
#'
#' Each detected pair is resolved as follows:
#'   - If `cache/confirmed_preprint_duplicates.csv` has an entry for the pair
#'     with action `keep_both`, both rows are preserved.
#'   - If it has `keep_1` or `keep_2`, that choice is honoured.
#'   - Otherwise the default rule (see `default_resolve_pair`) drops one DOI.
#'
#' Detected pairs and the action taken are logged to
#' `output/preprint_dedup_candidates.csv`.
#'
#' @param data  Augmented FLoRA data (titles/authors must be populated).
#' @param confirmed_path  CSV with override decisions.
#' @param candidates_out  Where to write the detection log.
#' @param title_threshold Title similarity threshold for fuzzy detection.
#' @param verbose Print progress messages.
#' @return Updated data frame.
resolve_preprint_dedup <- function(data,
                                    confirmed_path = CONFIRMED_DEDUP_PATH,
                                    candidates_out = CANDIDATES_PATH,
                                    title_threshold = 0.80,
                                    verbose = TRUE) {
  if (verbose) cat("\n### Preprint-Publication Deduplication\n")

  candidates <- find_preprint_pub_duplicates(data,
                                              title_threshold = title_threshold,
                                              verbose = verbose)
  if (nrow(candidates) == 0) {
    if (verbose) cat("✓ No preprint-publication duplicates detected\n")
    return(data)
  }

  pair_key_for <- function(d1, d2) {
    a <- tolower(d1); b <- tolower(d2)
    paste0(pmin(a, b), "||", pmax(a, b))
  }

  candidates <- candidates %>% mutate(pair_key = pair_key_for(doi_1, doi_2))

  overrides <- if (file.exists(confirmed_path)) {
    readr::read_csv(confirmed_path, show_col_types = FALSE) %>%
      filter(!is.na(action), action %in% c("keep_1", "keep_2", "keep_both")) %>%
      transmute(
        pair_key        = pair_key_for(doi_1, doi_2),
        override_action = action,
        override_doi_1  = doi_1,
        override_doi_2  = doi_2
      )
  } else {
    tibble(pair_key = character(), override_action = character(),
           override_doi_1 = character(), override_doi_2 = character())
  }

  decisions <- candidates %>%
    left_join(overrides, by = "pair_key") %>%
    mutate(
      resolution     = NA_character_,
      applied_action = NA_character_,
      doi_remove     = NA_character_,
      doi_keep       = NA_character_
    )

  for (i in seq_len(nrow(decisions))) {
    if (!is.na(decisions$override_action[i])) {
      act <- decisions$override_action[i]
      if (act == "keep_both") {
        decisions$resolution[i]     <- "override: keep_both"
        decisions$applied_action[i] <- "keep_both"
        next
      }
      rk <- derive_remove_keep(act,
                                decisions$override_doi_1[i],
                                decisions$override_doi_2[i])
      decisions$doi_remove[i]     <- rk$doi_remove
      decisions$doi_keep[i]       <- rk$doi_keep
      decisions$resolution[i]     <- sprintf("override: %s", act)
      decisions$applied_action[i] <- act
    } else {
      rr <- default_resolve_pair(decisions$side[i],
                                  decisions$doi_1[i], decisions$doi_2[i],
                                  decisions$is_preprint_1[i],
                                  decisions$is_preprint_2[i])
      if (is.null(rr)) {
        decisions$resolution[i]     <- "skipped: NA DOI in pair"
        decisions$applied_action[i] <- "skipped"
        next
      }
      decisions$doi_remove[i]     <- rr$doi_remove
      decisions$doi_keep[i]       <- rr$doi_keep
      which_dropped <- if (identical(rr$doi_remove, decisions$doi_1[i])) "doi_1" else "doi_2"
      decisions$resolution[i]     <- sprintf("auto: drop %s", which_dropped)
      decisions$applied_action[i] <- if (which_dropped == "doi_1") "auto_keep_2" else "auto_keep_1"
    }
  }

  if (!"doi_o_alt" %in% names(data)) data$doi_o_alt <- NA_character_
  if (!"doi_r_alt" %in% names(data)) data$doi_r_alt <- NA_character_

  to_apply <- decisions %>% filter(!is.na(doi_remove))

  n_before <- nrow(data)

  repl <- to_apply %>% filter(grepl("^replication", side))
  for (i in seq_len(nrow(repl))) {
    doi_rm <- tolower(repl$doi_remove[i])
    doi_kp <- tolower(repl$doi_keep[i])
    doi_os_with_kept <- unique(tolower(data$doi_o[tolower(data$doi_r) == doi_kp]))
    is_target <- tolower(data$doi_r) == doi_rm & tolower(data$doi_o) %in% doi_os_with_kept
    is_kept   <- tolower(data$doi_r) == doi_kp & tolower(data$doi_o) %in% doi_os_with_kept
    data$doi_r_alt[is_kept & is.na(data$doi_r_alt)] <- repl$doi_remove[i]
    data <- data[!is_target, ]
  }

  orig <- to_apply %>% filter(grepl("^original", side))
  if (nrow(orig) > 0) {
    doi_map <- setNames(tolower(orig$doi_keep), tolower(orig$doi_remove))
    matched <- tolower(data$doi_o) %in% names(doi_map)
    data <- data %>%
      mutate(
        doi_o_alt = dplyr::if_else(matched & is.na(doi_o_alt), doi_o, doi_o_alt),
        doi_o     = dplyr::if_else(matched, unname(doi_map[tolower(doi_o)]), doi_o)
      )

    norm_url_key <- function(x) {
      x <- tolower(trimws(as.character(x)))
      x <- gsub("^https?://", "", x)
      x <- gsub("^www\\.", "", x)
      x <- gsub("/+$", "", x)
      dplyr::na_if(x, "")
    }
    n_before_dedup <- nrow(data)
    data <- data %>%
      mutate(.url_r_key = norm_url_key(url_r)) %>%
      distinct(doi_o, study_o, coalesce(.url_r_key, doi_r), .keep_all = TRUE) %>%
      select(-.url_r_key)
    if (verbose && nrow(data) < n_before_dedup) {
      cat(sprintf("  Removed %d rows that became duplicates after DOI replacement\n",
                  n_before_dedup - nrow(data)))
    }
  }

  log_rows <- decisions %>%
    select(side, doi_1, doi_2, title_1, title_2, title_sim,
           first_author_1, first_author_2, year_1, year_2,
           is_preprint_1, is_preprint_2, group_key, doi_o_group,
           applied_action, resolution)

  instructions <- tibble(
    side           = "INSTRUCTIONS -->",
    doi_1          = "DOI #1",
    doi_2          = "DOI #2",
    title_1        = "(title for doi_1)",
    title_2        = "(title for doi_2)",
    title_sim      = NA_real_,
    first_author_1 = NA_character_,
    first_author_2 = NA_character_,
    year_1         = NA_character_,
    year_2         = NA_character_,
    is_preprint_1  = NA,
    is_preprint_2  = NA,
    group_key      = NA_character_,
    doi_o_group    = NA_character_,
    applied_action = "auto-default = drop one (preprint loses; else doi_2)",
    resolution     = "Override: copy row to confirmed_preprint_duplicates.csv with action keep_both / keep_1 / keep_2"
  )
  out <- bind_rows(instructions, log_rows)
  readr::write_excel_csv(out, candidates_out)

  if (verbose) {
    auto <- sum(grepl("^auto",     decisions$resolution))
    over <- sum(grepl("^override", decisions$resolution))
    skip <- sum(grepl("^skipped",  decisions$resolution))
    cat(sprintf("\n  Detected: %d candidate pairs\n", nrow(decisions)))
    cat(sprintf("  Auto-dropped: %d  |  Override: %d  |  Skipped (NA DOI): %d\n",
                auto, over, skip))
    cat(sprintf("  Net rows removed: %d\n", n_before - nrow(data)))
    cat(sprintf("  Log: %s\n", candidates_out))
    if (over > 0 || auto > 0) {
      cat("  To override an auto-drop, add the row to confirmed_preprint_duplicates.csv\n")
      cat("  with action = keep_both (retain both) or keep_1/keep_2 (flip survivor)\n")
    }
  }

  data
}
