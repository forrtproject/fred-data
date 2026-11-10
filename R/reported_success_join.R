library(dplyr)

# Join the success coding sheet (reported_success, quote, quote source) to FReD effects.
#
# A replication is identified by its DOI where it has one: the replication's doi_r, or a
# doi.org link in url_r (e.g. an OSF DOI). Rows are matched on the original DOI, that
# replication DOI and the study numbers. A replication without a DOI, or a DOI key that
# fits several different success-sheet entries (e.g. many reports sharing one paper's
# DOI), falls back to the replication URL. If every key that fits has disagreeing
# entries, the first validated entry is used (as the previous URL-only join did) and the
# effect is reported. Unmatched rows keep no label here; Step 8 then falls back to the
# main sheet's own outcome columns.

#' Normalise DOIs: lower case, no whitespace, no resolver prefix. NA unless it starts "10.".
normalise_doi <- function(x) {
  x <- tolower(gsub("\\s", "", as.character(x)))
  x <- sub("^(https?://)?(dx\\.)?doi\\.org/", "", x)
  x <- sub("^doi:", "", x)
  ifelse(!is.na(x) & startsWith(x, "10."), x, NA_character_)
}

#' Normalise URLs for matching: lower case, no whitespace, https, no "www.", no trailing slash.
normalise_url <- function(x) {
  x <- tolower(gsub("\\s", "", as.character(x)))
  x <- sub("^http://", "https://", x)
  x <- sub("^https://www\\.", "https://", x)
  x <- sub("/+$", "", x)
  ifelse(is.na(x) | x == "", NA_character_, x)
}

#' Replication keys: `rep_doi` (doi_r, else a DOI given as url_r) and `rep_url`
#' (url_r, else doi_r, as the previous join used).
replication_keys <- function(doi_r, url_r) {
  rep_doi <- coalesce(normalise_doi(doi_r), normalise_doi(url_r))
  rep_url <- coalesce(normalise_url(url_r), normalise_doi(doi_r))
  list(rep_doi = rep_doi, rep_url = rep_url)
}

#' Prepare the success sheet: usable entries only, keyed for both joins.
prepare_success_sheet <- function(success) {
  keys <- replication_keys(success$doi_r, success$url_r)
  success %>%
    mutate(doi_o = normalise_doi(doi_o), rep_doi = keys$rep_doi, rep_url = keys$rep_url,
           chosen = validation %in% "validated - chosen") %>%
    filter(!is.na(outcome), !validation %in% "validated - discarded") %>%
    transmute(doi_o, rep_doi, rep_url, study_o = as.character(study_o), study_r = as.character(study_r), chosen,
              reported_success = outcome, reported_success_quote = outcome_quote,
              reported_success_quote_source = out_quote_source)
}

# One entry per key: validated - chosen first; a key whose best entries disagree is ambiguous.
unique_by <- function(success, key) {
  success %>%
    filter(!is.na(.data[[key]])) %>%
    group_by(doi_o, .data[[key]], study_o, study_r) %>%
    filter(chosen == max(chosen)) %>%
    mutate(ambiguous = n_distinct(reported_success, reported_success_quote, reported_success_quote_source) > 1) %>%
    slice_head(n = 1) %>%
    ungroup()
}

#' Add reported_success, reported_success_quote, reported_success_quote_source and
#' reported_success_match ("doi", "url", "doi_ambiguous", "url_ambiguous" or NA) to `data`.
#'
#' @return list(data, report): report counts rows by kind of match and lists the effects
#'   whose success-sheet entries disagree.
join_reported_success <- function(data, success) {
  s <- prepare_success_sheet(success)
  cols <- c("reported_success", "reported_success_quote", "reported_success_quote_source")
  keys <- replication_keys(data$doi_r, data$url_r)
  d <- data %>% mutate(.row = row_number(), .doi_o = normalise_doi(doi_o), .rep_doi = keys$rep_doi,
                       .rep_url = keys$rep_url, .study_o = as.character(study_o), .study_r = as.character(study_r))

  # Match in order of reliability: unique DOI key, unique URL key, then (as the previous
  # join did) the first validated entry of a key whose entries disagree.
  tiers <- list(c("rep_doi", FALSE, "doi"), c("rep_url", FALSE, "url"),
                c("rep_doi", TRUE, "doi_ambiguous"), c("rep_url", TRUE, "url_ambiguous"))
  matched <- NULL
  for (tier in tiers) {
    key <- tier[1]; dkey <- paste0(".", key)
    m <- d %>%
      filter(!.row %in% matched$.row) %>%
      select(.row, .doi_o, all_of(dkey), .study_o, .study_r) %>%
      inner_join(unique_by(s, key) %>% filter(ambiguous == as.logical(tier[2])),
                 by = setNames(c("doi_o", key, "study_o", "study_r"), c(".doi_o", dkey, ".study_o", ".study_r"))) %>%
      mutate(reported_success_match = tier[3])
    matched <- bind_rows(matched, m %>% select(.row, all_of(cols), reported_success_match))
  }
  stopifnot(!anyDuplicated(matched$.row))
  ambiguous <- d %>% filter(.row %in% matched$.row[grepl("ambiguous", matched$reported_success_match)])

  out <- d %>%
    select(-any_of(c(cols, "reported_success_match"))) %>%
    left_join(matched, by = ".row") %>%
    arrange(.row) %>%
    select(-.row, -.doi_o, -.rep_doi, -.rep_url, -.study_o, -.study_r)
  report <- list(
    entries = nrow(s),
    matched = table(factor(matched$reported_success_match, c("doi", "url", "doi_ambiguous", "url_ambiguous"))),
    unmatched = nrow(data) - nrow(matched),
    ambiguous = sprintf("%s (%s, %s): success-sheet entries disagree; first validated entry used",
                        ambiguous$effect_uid, ambiguous$.doi_o, coalesce(ambiguous$.rep_doi, ambiguous$.rep_url)))
  list(data = out, report = report)
}
