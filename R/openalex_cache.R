# OpenAlex metadata + caching
# Vectorised OpenAlex lookup with persistent CSV cache for keywords and language
#
# Uses `httr`, `jsonlite`, and `readr` plus base R only.

library(httr)
library(jsonlite)
library(readr)

# Helper: normalize DOI for cache keys
normalize_doi <- function(doi) {
  if (is.na(doi)) return(NA_character_)
  d <- trimws(as.character(doi))
  if (!nzchar(d)) return(NA_character_)
  tolower(d)
}

load_openalex_cache <- function(cache_file = OPENALEX_CACHE) {
  if (!file.exists(cache_file)) {
    data.frame(doi = character(0), keywords = character(0), language = character(0), stringsAsFactors = FALSE)
  } else {
    readr::read_csv(cache_file, show_col_types = FALSE, col_types = readr::cols(
      doi = readr::col_character(),
      keywords = readr::col_character(),
      language = readr::col_character()
    ))
  }
}

save_openalex_cache <- function(df, cache_file = OPENALEX_CACHE) {
  dir.create(dirname(cache_file), showWarnings = FALSE, recursive = TRUE)
  # ensure unique by doi, keep first occurrence
  if (nrow(df) > 0) {
    df <- df[!duplicated(df$doi), , drop = FALSE]
  }
  readr::write_csv(df, cache_file)
}

# Internal single-DOI fetcher (returns list with doi, keywords, language)
fetch_openalex_single <- function(doi, mailto = NULL, fallback_to_concepts = TRUE, n_concepts = 10) {
  doi_norm <- normalize_doi(doi)
  if (is.na(doi_norm)) return(list(doi = NA_character_, keywords = NA_character_, language = NA_character_))

  base_url <- "https://api.openalex.org/works/"
  encoded_doi <- URLencode(doi, reserved = TRUE)
  url <- paste0(base_url, "doi:", encoded_doi)

  q <- list(select = "id,doi,display_name,language,keywords,concepts")
  if (!is.null(mailto)) q$mailto <- mailto

  res <- tryCatch({
    resp <- httr::GET(url, query = q, httr::user_agent("R (OpenAlex lookup)"), httr::timeout(10))
    if (httr::http_error(resp)) return(NULL)
    jsonlite::fromJSON(httr::content(resp, as = "text", encoding = "UTF-8"), simplifyVector = TRUE)
  }, error = function(e) NULL)

  if (is.null(res)) {
    return(list(doi = doi_norm, keywords = NA_character_, language = NA_character_))
  }

  lang <- if (!is.null(res$language)) res$language else NA_character_

  kws <- NULL
  if (!is.null(res$keywords) && length(res$keywords) > 0) {
    if (is.character(res$keywords)) {
      kws <- res$keywords
    } else if (is.data.frame(res$keywords)) {
      # try common column names
      if ("display_name" %in% names(res$keywords)) {
        kws <- res$keywords$display_name
      } else if ("keyword" %in% names(res$keywords)) {
        kws <- res$keywords$keyword
      }
    }
  }

  if ((is.null(kws) || length(kws) == 0) && fallback_to_concepts && !is.null(res$concepts)) {
    if (is.data.frame(res$concepts)) {
      kws <- head(res$concepts$display_name, n_concepts)
    }
  }

  kws <- unique(na.omit(as.character(kws)))
  kws <- kws[nzchar(kws)]
  kw_combined <- if (length(kws)) paste(kws, collapse = ", ") else NA_character_

  list(doi = doi_norm, keywords = kw_combined, language = lang)
}


#' Get OpenAlex language metadata (vectorised)
#'
#' Fetch language for a vector of DOIs from OpenAlex with persistent CSV caching.
#'
#' @param dois Character vector of DOIs. May contain NA and duplicates; output preserves order and duplicates.
#' @param mailto Optional contact email passed to OpenAlex queries.
#' @param cache_file Path to CSV cache file where results are read from and appended to. Default: OPENALEX_CACHE.
#'
#' @return A data.frame with columns `doi`, `language` in that order; rows correspond 1:1 to input `dois`
#'   (preserving duplicates and NA inputs).
#'
#' @examples
#' # Single DOI
#' # get_openalex_language("10.1038/s41586-020-2649-2", mailto = "you@example.com")
#' # Multiple DOIs (vectorised)
#' # get_openalex_language(c("10.1038/s41586-020-2649-2", NA))
get_openalex_language <- function(dois,
                                  mailto = "lukas.wallrich@gmail.com",
                                  cache_file = OPENALEX_CACHE) {
  # Preserve original input order and values
  input_dois <- as.character(dois)
  normalized_inputs <- vapply(input_dois, normalize_doi, character(1))

  # Load cache
  cache_df <- load_openalex_cache(cache_file)
  if (nrow(cache_df) > 0) {
    cache_df$doi <- vapply(cache_df$doi, as.character, character(1))
  }

  unique_norm <- unique(normalized_inputs[!is.na(normalized_inputs)])
  already_cached <- if (nrow(cache_df) > 0) cache_df$doi else character(0)
  to_fetch <- setdiff(unique_norm, already_cached)

  new_rows <- data.frame(
    doi = character(0),
    language = character(0),
    stringsAsFactors = FALSE
  )

  if (length(to_fetch) > 0) {
    new_rows <- map(
      to_fetch,
      ~{
        res <- fetch_openalex_single(.x, mailto = mailto)
        data.frame(
          doi = res$doi,
          language = res$language,
          stringsAsFactors = FALSE
        )
      },
      .progress = TRUE
    ) %>%
      bind_rows() %>%
      bind_rows(new_rows)

    cache_df <- bind_rows(cache_df, new_rows)
    save_openalex_cache(cache_df, cache_file)
  }

  # Ensure cache structure
  if (nrow(cache_df) == 0) {
    cache_df <- data.frame(
      doi = character(0),
      language = character(0),
      stringsAsFactors = FALSE
    )
  }

  # Map inputs to cache
  out_language <- character(length(normalized_inputs))

  for (i in seq_along(normalized_inputs)) {
    nd <- normalized_inputs[i]
    if (is.na(nd)) {
      out_language[i] <- NA_character_
    } else {
      idx <- match(nd, cache_df$doi)
      if (is.na(idx)) {
        out_language[i] <- NA_character_
      } else {
        lang <- cache_df$language[idx]
        out_language[i] <-
          ifelse(is.null(lang) || is.na(lang) || !nzchar(lang),
                 NA_character_,
                 as.character(lang))
      }
    }
  }

  data.frame(
    doi = input_dois,
    language = out_language,
    stringsAsFactors = FALSE
  )
}



