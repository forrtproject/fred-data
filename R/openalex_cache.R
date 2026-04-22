# OpenAlex metadata + caching
# Vectorised OpenAlex lookup with persistent CSV cache for keywords and language
#
# Uses `httr`, `jsonlite`, and `readr` plus base R only.

library(dplyr)
library(httr)
library(jsonlite)
library(purrr)
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
    read_csv(cache_file, show_col_types = FALSE, col_types = cols(
      doi = col_character(),
      keywords = col_character(),
      language = col_character()
    ))
  }
}

save_openalex_cache <- function(df, cache_file = OPENALEX_CACHE) {
  dir.create(dirname(cache_file), showWarnings = FALSE, recursive = TRUE)
  # ensure unique by doi, keep first occurrence
  if (nrow(df) > 0) {
    df <- df[!duplicated(df$doi), , drop = FALSE]
  }
  write_excel_csv(df, cache_file)
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
    resp <- GET(url, query = q, user_agent("R (OpenAlex lookup)"), timeout(10))
    if (http_error(resp)) return(NULL)
    fromJSON(content(resp, as = "text", encoding = "UTF-8"), simplifyVector = TRUE)
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

# ---- Abstract fetching ----

load_openalex_abstracts_cache <- function(cache_file = OPENALEX_ABSTRACTS_CACHE) {
  if (!file.exists(cache_file)) {
    data.frame(doi = character(0), abstract = character(0), stringsAsFactors = FALSE)
  } else {
    read_csv(cache_file, show_col_types = FALSE, col_types = cols(
      doi = col_character(),
      abstract = col_character()
    ))
  }
}

save_openalex_abstracts_cache <- function(df, cache_file = OPENALEX_ABSTRACTS_CACHE) {
  dir.create(dirname(cache_file), showWarnings = FALSE, recursive = TRUE)
  if (nrow(df) > 0) {
    df <- df[!duplicated(df$doi), , drop = FALSE]
  }
  write_excel_csv(df, cache_file)
}

#' Reconstruct abstract from OpenAlex inverted index
#'
#' @param inverted_index Named list where keys are words and values are position vectors
#' @return Plain text abstract string
reconstruct_abstract <- function(inverted_index) {
  if (is.null(inverted_index) || length(inverted_index) == 0) return(NA_character_)

  words <- names(inverted_index)
  # Build position-to-word mapping
  pos_word <- character(0)
  for (i in seq_along(words)) {
    positions <- unlist(inverted_index[[i]])
    if (length(positions) > 0) {
      for (p in positions) {
        pos_word[as.character(p)] <- words[i]
      }
    }
  }

  if (length(pos_word) == 0) return(NA_character_)

  # Sort by position and join
  sorted_positions <- sort(as.integer(names(pos_word)))
  paste(pos_word[as.character(sorted_positions)], collapse = " ")
}

#' Fetch abstract for a single DOI from OpenAlex
#'
#' @param doi A single DOI string
#' @param mailto Optional contact email
#' @return list with doi and abstract
fetch_openalex_abstract_single <- function(doi, mailto = NULL) {
  doi_norm <- normalize_doi(doi)
  if (is.na(doi_norm)) return(list(doi = NA_character_, abstract = NA_character_))

  base_url <- "https://api.openalex.org/works/"
  encoded_doi <- URLencode(doi, reserved = TRUE)
  url <- paste0(base_url, "doi:", encoded_doi)

  q <- list(select = "id,doi,abstract_inverted_index")
  if (!is.null(mailto)) q$mailto <- mailto

  res <- tryCatch({
    resp <- GET(url, query = q, user_agent("R (OpenAlex lookup)"), timeout(10))
    if (http_error(resp)) return(list(doi = doi_norm, abstract = NA_character_))
    fromJSON(content(resp, as = "text", encoding = "UTF-8"), simplifyVector = FALSE)
  }, error = function(e) NULL)

  if (is.null(res)) {
    return(list(doi = doi_norm, abstract = NA_character_))
  }

  abstract <- reconstruct_abstract(res$abstract_inverted_index)
  list(doi = doi_norm, abstract = abstract)
}

#' Get OpenAlex abstracts (vectorised)
#'
#' Fetch abstracts for a vector of DOIs from OpenAlex with persistent CSV caching.
#'
#' @param dois Character vector of DOIs
#' @param mailto Optional contact email
#' @param cache_file Path to CSV cache file
#' @return A data.frame with columns `doi`, `abstract`; rows correspond 1:1 to input `dois`
get_openalex_abstracts <- function(dois,
                                   mailto = "lukas.wallrich@gmail.com",
                                   cache_file = OPENALEX_ABSTRACTS_CACHE) {
  input_dois <- as.character(dois)
  normalized_inputs <- vapply(input_dois, normalize_doi, character(1))

  cache_df <- load_openalex_abstracts_cache(cache_file)
  if (nrow(cache_df) > 0) {
    cache_df$doi <- vapply(cache_df$doi, as.character, character(1))
  }

  unique_norm <- unique(normalized_inputs[!is.na(normalized_inputs)])
  already_cached <- if (nrow(cache_df) > 0) cache_df$doi else character(0)
  to_fetch <- setdiff(unique_norm, already_cached)

  if (length(to_fetch) > 0) {
    cat(sprintf("Fetching %d abstracts from OpenAlex...\n", length(to_fetch)))
    new_rows <- map(
      to_fetch,
      ~{
        res <- fetch_openalex_abstract_single(.x, mailto = mailto)
        data.frame(doi = res$doi, abstract = res$abstract, stringsAsFactors = FALSE)
      },
      .progress = TRUE
    ) %>%
      bind_rows()

    cache_df <- bind_rows(cache_df, new_rows)
    save_openalex_abstracts_cache(cache_df, cache_file)
  }

  # Map inputs to cache
  out_abstract <- character(length(normalized_inputs))
  for (i in seq_along(normalized_inputs)) {
    nd <- normalized_inputs[i]
    if (is.na(nd)) {
      out_abstract[i] <- NA_character_
    } else {
      idx <- match(nd, cache_df$doi)
      out_abstract[i] <- if (is.na(idx)) NA_character_ else cache_df$abstract[idx]
    }
  }

  data.frame(doi = input_dois, abstract = out_abstract, stringsAsFactors = FALSE)
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

# ---- Work-ID-keyed field lookup ----
#
# Many replication studies (theses, working papers) have an OpenAlex work ID
# but no DOI. When the source stores the URL form (https://openalex.org/W...),
# we fetch title/authors/year/journal by work ID so those rows survive the
# title filter at the end of the flora pipeline.

load_openalex_work_fields_cache <- function(cache_file = OPENALEX_WORK_FIELDS_CACHE) {
  if (!file.exists(cache_file)) {
    tibble::tibble(work_id = character(), title = character(),
                   authors_json = character(), journal = character(),
                   year = integer(), source = character())
  } else {
    read_csv(cache_file, show_col_types = FALSE,
             col_types = cols(
               work_id = col_character(), title = col_character(),
               authors_json = col_character(), journal = col_character(),
               year = col_integer(), source = col_character()
             ))
  }
}

save_openalex_work_fields_cache <- function(df,
                                             cache_file = OPENALEX_WORK_FIELDS_CACHE) {
  dir.create(dirname(cache_file), showWarnings = FALSE, recursive = TRUE)
  if (nrow(df) > 0) df <- df[!duplicated(df$work_id), , drop = FALSE]
  write_excel_csv(df, cache_file)
}

# Extract the work ID from an OpenAlex URL (or pass through if already bare)
extract_openalex_work_id <- function(x) {
  x <- trimws(as.character(x))
  m <- regmatches(x, regexpr("W\\d{5,}", x, perl = TRUE))
  ifelse(length(m) == 0 || !nzchar(m), NA_character_, m)
}

fetch_openalex_work_fields_single <- function(work_id, mailto = NULL) {
  url <- paste0("https://api.openalex.org/works/", work_id)
  q <- list(select = "id,doi,display_name,publication_year,authorships,primary_location")
  if (!is.null(mailto)) q$mailto <- mailto

  res <- tryCatch(
    GET(url, query = q, user_agent("R (OpenAlex work lookup)"), timeout(12)),
    error = function(e) NULL
  )
  if (is.null(res) || http_error(res)) {
    return(tibble::tibble(work_id = work_id, title = NA_character_,
                          authors_json = NA_character_, journal = NA_character_,
                          year = NA_integer_, source = "openalex_error"))
  }

  j <- tryCatch(fromJSON(content(res, as = "text", encoding = "UTF-8"),
                         simplifyVector = FALSE),
                error = function(e) NULL)
  if (is.null(j)) {
    return(tibble::tibble(work_id = work_id, title = NA_character_,
                          authors_json = NA_character_, journal = NA_character_,
                          year = NA_integer_, source = "openalex_error"))
  }

  # Authors → CrossRef-style JSON (given/family/sequence)
  authors_json <- NA_character_
  if (!is.null(j$authorships) && length(j$authorships) > 0) {
    df <- lapply(seq_along(j$authorships), function(i) {
      auth <- j$authorships[[i]]$author
      raw  <- j$authorships[[i]]$raw_author_name %||% NULL
      name <- auth$display_name %||% raw %||% NA_character_
      if (is.na(name) || !nzchar(name)) return(NULL)
      parts <- strsplit(name, "\\s+")[[1]]
      family <- if (length(parts) > 0) parts[[length(parts)]] else NA_character_
      given  <- if (length(parts) > 1) paste(parts[-length(parts)], collapse = " ") else NA_character_
      list(given = given, family = family,
           sequence = if (i == 1) "first" else "additional")
    })
    df <- Filter(Negate(is.null), df)
    if (length(df) > 0) {
      authors_json <- as.character(toJSON(df, auto_unbox = TRUE, null = "null"))
    }
  }

  journal <- j$primary_location$source$display_name %||% NA_character_
  year <- suppressWarnings(as.integer(j$publication_year %||% NA))
  title <- j$display_name %||% NA_character_

  tibble::tibble(
    work_id = work_id,
    title = if (!is.na(title) && nzchar(title)) title else NA_character_,
    authors_json = authors_json,
    journal = if (!is.na(journal) && nzchar(journal)) journal else NA_character_,
    year = year,
    source = "openalex"
  )
}

#' Fetch OpenAlex bibliographic fields for a vector of work IDs or OpenAlex URLs
#'
#' Caches results in `openalex_work_fields.csv`. Returns one row per input,
#' preserving order; missing work IDs get all-NA rows.
get_openalex_work_fields <- function(work_ids,
                                      mailto = "lukas.wallrich@gmail.com",
                                      cache_file = OPENALEX_WORK_FIELDS_CACHE,
                                      progress = TRUE) {
  input <- vapply(work_ids, extract_openalex_work_id, character(1))
  out <- tibble::tibble(input = input)

  cache_df <- load_openalex_work_fields_cache(cache_file)
  unique_ids <- unique(input[!is.na(input)])
  need <- setdiff(unique_ids,
                  cache_df$work_id[cache_df$source != "openalex_error"])

  if (length(need) > 0) {
    if (progress) message("Fetching OpenAlex fields for ", length(need), " work ID(s)...")
    pb <- NULL
    if (progress) {
      pb <- utils::txtProgressBar(min = 0, max = length(need), style = 3)
      on.exit(if (!is.null(pb)) close(pb), add = TRUE)
    }
    new_rows <- vector("list", length(need))
    for (i in seq_along(need)) {
      new_rows[[i]] <- fetch_openalex_work_fields_single(need[[i]], mailto = mailto)
      if (!is.null(pb)) utils::setTxtProgressBar(pb, i)
      Sys.sleep(0.1)
    }
    new_df <- bind_rows(new_rows)
    cache_df <- cache_df %>%
      filter(!work_id %in% new_df$work_id) %>%
      bind_rows(new_df)
    save_openalex_work_fields_cache(cache_df, cache_file)
  }

  out %>%
    left_join(cache_df, by = c("input" = "work_id")) %>%
    select(work_id = input, title, authors_json, journal, year, source)
}

#' Patch missing replication-side fields from OpenAlex when url_r is an
#' OpenAlex URL. Must run after Step 7 / 7b so that title_r etc. columns exist.
augment_with_openalex_url_refs_r <- function(data,
                                              url_col = "url_r",
                                              verbose = TRUE) {
  stopifnot(is.data.frame(data))
  if (!url_col %in% names(data)) return(data)

  has_text_vec <- function(x) {
    x <- trimws(as.character(x))
    !is.na(x) & nzchar(x)
  }
  for (nm in c("title_r", "author_r", "journal_r", "year_r")) {
    if (!nm %in% names(data)) {
      data[[nm]] <- if (nm == "year_r") NA_integer_ else NA_character_
    }
  }

  work_id <- vapply(data[[url_col]], extract_openalex_work_id, character(1))
  need_idx <- which(!has_text_vec(data$title_r) & !is.na(work_id))
  if (length(need_idx) == 0) {
    if (verbose) message("=== OpenAlex URL overrides (R side) ===\nNo rows to patch.")
    return(data)
  }

  fields <- get_openalex_work_fields(unique(work_id[need_idx]), progress = verbose)

  idx_match <- match(work_id[need_idx], fields$work_id)
  patch <- fields[idx_match, ]
  data$title_r[need_idx]  <- dplyr::coalesce(data$title_r[need_idx],  patch$title)
  data$author_r[need_idx] <- dplyr::coalesce(data$author_r[need_idx], patch$authors_json)
  data$journal_r[need_idx]<- dplyr::coalesce(data$journal_r[need_idx],patch$journal)
  data$year_r[need_idx]   <- dplyr::coalesce(data$year_r[need_idx],   patch$year)

  if (verbose) {
    recovered <- sum(has_text_vec(patch$title))
    message("=== OpenAlex URL overrides (R side) ===\n",
            "URL matches resolved: ", length(need_idx), "\n",
            "Titles recovered    : ", recovered)
  }
  data
}

