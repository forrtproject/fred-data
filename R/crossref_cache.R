# CrossRef and DataCite Caching Functions
# Consolidates citation, DOI metadata, and author caching by data type
# Sources: crossref_citation_cache.R, hackathon prep - flora.qmd, crossref_author_retrieval.qmd

library(stringr)
library(rcrossref)
library(httr)
library(glue)

`%||%` <- function(x, y) if (is.null(x) || length(x) == 0 || all(is.na(x))) y else x
is_doi <- function(x) grepl("^10\\.[0-9]{4,}/\\S+$", x)

# ============================================================================
# Citation Caching (APA/BibTeX)
# ============================================================================

#' Load citation cache from disk
#' @param cache_file Path to cache file (RDS format)
#' @return List with 'apa' and 'bibtex' named lists
load_citation_cache <- function(cache_file = CROSSREF_CITATIONS_CACHE) {
  if (file.exists(cache_file)) {
    readRDS(cache_file)
  } else {
    list(apa = list(), bibtex = list())
  }
}

#' Save citation cache to disk
#' @param cache List with 'apa' and 'bibtex' sublists
#' @param cache_file Path to save cache
save_citation_cache <- function(cache, cache_file = CROSSREF_CITATIONS_CACHE) {
  saveRDS(cache, cache_file)
}

#' Load manual reference overrides from Excel
#' @param manual_ref_file Path to Excel file with columns: key, reference_apa, reference_bibtex,
#'   and optional field columns: title, author, journal, year, volume, issue, pages
#' @return Tibble with manual references
load_manual_references <- function(manual_ref_file = MANUAL_REFERENCES) {
  empty_df <- tibble::tibble(
    key = character(),
    reference_apa = character(),
    reference_bibtex = character(),
    title = character(),
    author = character(),
    journal = character(),
    year = integer(),
    volume = character(),
    issue = character(),
    pages = character()
  )

  if (!file.exists(manual_ref_file)) {
    return(empty_df)
  }

  tryCatch({
    df <- readxl::read_excel(manual_ref_file)
    # Ensure all expected columns exist
    for (col in names(empty_df)) {
      if (!col %in% names(df)) {
        df[[col]] <- if (col == "year") NA_integer_ else NA_character_
      }
    }
    if (exists("URLR_DOIR_MAP_CACHE") && file.exists(URLR_DOIR_MAP_CACHE)) {
      map_df <- tryCatch(readRDS(URLR_DOIR_MAP_CACHE), error = function(e) NULL)
      if (!is.null(map_df) && all(c("url_r", "doi_r") %in% names(map_df))) {
        map_df <- map_df %>%
          dplyr::transmute(
            url_r = tolower(trimws(url_r)),
            doi_r = tolower(trimws(doi_r))
          ) %>%
          dplyr::filter(!is.na(url_r), !is.na(doi_r)) %>%
          dplyr::distinct(url_r, .keep_all = TRUE)

        key_norm <- tolower(trimws(df$key))
        hit <- match(key_norm, map_df$url_r)
        df$key <- ifelse(!is.na(hit), map_df$doi_r[hit], df$key)
      }
    }
    df
  }, error = function(e) {
    warning(sprintf("Could not read manual references file %s", manual_ref_file))
    empty_df
  })
}

#' Parse BibTeX author string to JSON format
#' @param author_str BibTeX author string (e.g., "Family, Given and Family, Given")
#' @return JSON string in CrossRef format
parse_bibtex_authors_to_json <- function(author_str) {
  if (is.na(author_str) || !nzchar(author_str)) return(NA_character_)

  # Split by " and " (BibTeX author separator)
  authors <- strsplit(author_str, "\\s+and\\s+", perl = TRUE)[[1]]
  authors <- trimws(authors)

  author_list <- lapply(seq_along(authors), function(i) {
    a <- authors[i]
    given <- NA_character_
    family <- NA_character_

    if (grepl(",", a)) {
      # Format: "Family, Given" or "Family, Given Middle"
      parts <- strsplit(a, ",\\s*")[[1]]
      family <- trimws(parts[1])
      given <- if (length(parts) > 1) trimws(parts[2]) else NA_character_
    } else {
      # Format: "Given Family" or "Given Middle Family"
      parts <- strsplit(trimws(a), "\\s+")[[1]]
      if (length(parts) >= 2) {
        family <- parts[length(parts)]
        given <- paste(parts[-length(parts)], collapse = " ")
      } else if (length(parts) == 1) {
        family <- parts[1]
      }
    }

    list(
      given = if (!is.na(given) && nzchar(given)) given else NULL,
      family = if (!is.na(family) && nzchar(family)) family else NULL,
      sequence = if (i == 1) "first" else "additional"
    )
  })

  as.character(jsonlite::toJSON(author_list, auto_unbox = TRUE, null = "null"))
}

#' Parse BibTeX string to extract individual fields
#' @param bibtex BibTeX string
#' @return Named list with title, author (as JSON), journal, year, volume, issue, pages
parse_bibtex_fields <- function(bibtex) {
  result <- list(
    title = NA_character_,
    author = NA_character_,
    journal = NA_character_,
    year = NA_integer_,
    volume = NA_character_,
    issue = NA_character_,
    pages = NA_character_
  )

  if (is.na(bibtex) || !nzchar(bibtex)) return(result)

  # Robust BibTeX field extractor
  # Supports:
  #   field = { ... }   (handles nested braces)
  #   field = " ... "   (handles escaped quotes)
  #   field = ' ... '   (handles escaped quotes)
  #   field = bareValue (until comma or newline)
 extract_field <- function(bib, field) {
  if (is.na(bib) || !nzchar(bib)) return(NA_character_)

  bib <- as.character(bib)

  # Find "field =" (case-insensitive)
  m <- regexpr(paste0("(?i)\\b", field, "\\b\\s*=\\s*"), bib, perl = TRUE)
  if (m[1] == -1) return(NA_character_)

  i <- m[1] + attr(m, "match.length") # index right after "field = "
  n <- nchar(bib)

  # Skip whitespace
  while (i <= n && grepl("\\s", substr(bib, i, i))) i <- i + 1
  if (i > n) return(NA_character_)

  start_char <- substr(bib, i, i)

  # -------- braced value { ... } with nested brace support --------
  if (start_char == "{") {
    depth <- 1
    j <- i + 1
    while (j <= n && depth > 0) {
      ch <- substr(bib, j, j)
      if (ch == "{") depth <- depth + 1
      if (ch == "}") depth <- depth - 1
      j <- j + 1
    }
    if (depth != 0) return(NA_character_)

    val <- substr(bib, i + 1, j - 2) # inside outer braces
    return(stringr::str_squish(val))
  }

  # -------- double-quoted value " ... " (supports escaped quotes) --------
  if (start_char == "\"") {
    j <- i + 1
    escaped <- FALSE
    while (j <= n) {
      ch <- substr(bib, j, j)
      if (!escaped && ch == "\"") break
      if (!escaped && ch == "\\") escaped <- TRUE else escaped <- FALSE
      j <- j + 1
    }
    if (j > n) return(NA_character_)

    val <- substr(bib, i + 1, j - 1)
    return(stringr::str_squish(val))
  }

  # -------- single-quoted value ' ... ' (supports escaped quotes) --------
  if (start_char == "'") {
    j <- i + 1
    escaped <- FALSE
    while (j <= n) {
      ch <- substr(bib, j, j)
      if (!escaped && ch == "'") break
      if (!escaped && ch == "\\") escaped <- TRUE else escaped <- FALSE
      j <- j + 1
    }
    if (j > n) return(NA_character_)

    val <- substr(bib, i + 1, j - 1)
    return(stringr::str_squish(val))
  }

  # -------- bare value (until comma or newline) --------
  j <- i
  while (j <= n) {
    ch <- substr(bib, j, j)
    if (ch == "," || ch == "\n" || ch == "\r") break
    j <- j + 1
  }
  val <- substr(bib, i, j - 1)
  val <- gsub("\\s+$", "", val)
  val <- gsub("^\\s+", "", val)
  val <- gsub("[{}\"]", "", val) # light cleanup for bare tokens
  val <- stringr::str_squish(val)

  if (!nzchar(val)) NA_character_ else val
}


# Drop-in replacement for parse_bibtex_fields() using the robust extractor
parse_bibtex_fields <- function(bibtex) {
  result <- list(
    title = NA_character_,
    author = NA_character_,
    journal = NA_character_,
    year = NA_integer_,
    volume = NA_character_,
    issue = NA_character_,
    pages = NA_character_
  )

  if (is.na(bibtex) || !nzchar(bibtex)) return(result)

  result$title <- extract_bibtex_field(bibtex, "title")

  # author -> JSON via your existing helper
  author_str <- extract_bibtex_field(bibtex, "author")
  result$author <- parse_bibtex_authors_to_json(author_str)

  result$journal <- extract_bibtex_field(bibtex, "journal") %||%
    extract_bibtex_field(bibtex, "booktitle") %||%
    extract_bibtex_field(bibtex, "school") %||%
    extract_bibtex_field(bibtex, "institution") %||%
    extract_bibtex_field(bibtex, "publisher")

  year_str <- extract_bibtex_field(bibtex, "year")
  result$year <- if (!is.na(year_str)) suppressWarnings(as.integer(year_str)) else NA_integer_

  result$volume <- extract_bibtex_field(bibtex, "volume")
  result$issue  <- extract_bibtex_field(bibtex, "number")
  result$pages  <- extract_bibtex_field(bibtex, "pages")

  result
}


  result$title <- extract_field(bibtex, "title")

  # Parse author to JSON format
  author_str <- extract_field(bibtex, "author")
  result$author <- parse_bibtex_authors_to_json(author_str)

  result$journal <- extract_field(bibtex, "journal") %||%
    extract_field(bibtex, "booktitle") %||%
    extract_field(bibtex, "school") %||%
    extract_field(bibtex, "institution")
  year_str <- extract_field(bibtex, "year")
  result$year <- if (!is.na(year_str)) suppressWarnings(as.integer(year_str)) else NA_integer_
  result$volume <- extract_field(bibtex, "volume")
  result$issue <- extract_field(bibtex, "number")
  result$pages <- extract_field(bibtex, "pages")

  result
}

#' Fetch a citation from CrossRef for a given DOI
#' @param doi DOI string (e.g., "10.1234/example")
#' @param type Citation format: "bibtex" or "apa"
#' @return Citation string or NA if not found
get_crossref_citation <- function(doi, type = c("bibtex", "apa")) {
  doi <- trimws(doi)

  # Validate DOI format
  if (!grepl("^10\\.[0-9]{4,}/\\S+$", doi)) {
    return(NA_character_)
  }

  type <- match.arg(type)

  # Set CrossRef content negotiation parameters
  if (type == "bibtex") {
    fmt <- "bibtex"
    style <- NULL
  } else if (type == "apa") {
    fmt <- "text"
    style <- "apa"
  }

  # Fetch from CrossRef with error handling
  tryCatch({
    rcrossref::cr_cn(dois = doi, format = fmt, style = style)
  }, error = function(e) {
    NA_character_
  })
}
# ------------------------------------------------------------------------------
# URL-only manual overrides for the replication/reproduction side (R)
# Works on Step-7 column names: ref_r_clean, bibtex_r, title_r, ...
# Does NOT create apa_ref_r / bibtex_ref_r (so later rename() won't break).
# ------------------------------------------------------------------------------

augment_with_manual_url_refs_r <- function(data,
                                          manual_ref_file = MANUAL_REFERENCES,
                                          url_col = "url_r",
                                          recover_title_from_bibtex = TRUE,
                                          verbose = TRUE) {
  stopifnot(is.data.frame(data))

  if (!file.exists(manual_ref_file)) {
    if (verbose) message("Manual refs file not found: ", manual_ref_file, " (skipping)")
    return(data)
  }
  if (!url_col %in% names(data)) {
    if (verbose) message("Column ", url_col, " not found (skipping manual URL merge)")
    return(data)
  }

  # Normalize URLs so https://osf.io/abcd/ matches osf.io/abcd
  norm_url <- function(x) {
    x <- tolower(trimws(as.character(x)))
    x <- gsub("^https?://", "", x)
    x <- gsub("^www\\.", "", x)
    x <- gsub("/+$", "", x)
    dplyr::na_if(x, "")
  }

  has_text_vec <- function(x) {
    x <- trimws(as.character(x))
    !is.na(x) & nzchar(x)
  }

  # Ensure Step-7 columns exist (safe)
  for (nm in c("ref_r_clean","bibtex_r","title_r","author_r","journal_r","volume_r","issue_r","pages_r")) {
    if (!nm %in% names(data)) data[[nm]] <- NA_character_
  }
  if (!"year_r" %in% names(data)) data$year_r <- NA_integer_

  manual_df <- readxl::read_excel(manual_ref_file)

  # Ensure expected manual columns exist
  expected <- c("key","reference_apa","reference_bibtex","title","author","journal","year","volume","issue","pages")
  for (col in expected) if (!col %in% names(manual_df)) manual_df[[col]] <- NA

  manual_url <- manual_df %>%
    dplyr::mutate(
      url_key = norm_url(key),
      reference_apa    = dplyr::na_if(trimws(as.character(reference_apa)), ""),
      reference_bibtex = dplyr::na_if(trimws(as.character(reference_bibtex)), ""),
      title   = dplyr::na_if(trimws(as.character(title)), ""),
      author  = dplyr::na_if(trimws(as.character(author)), ""),
      journal = dplyr::na_if(trimws(as.character(journal)), ""),
      volume  = dplyr::na_if(trimws(as.character(volume)), ""),
      issue   = dplyr::na_if(trimws(as.character(issue)), ""),
      pages   = dplyr::na_if(trimws(as.character(pages)), "")
    ) %>%
    dplyr::filter(!is.na(url_key)) %>%
    dplyr::distinct(url_key, .keep_all = TRUE) %>%
    dplyr::rowwise() %>%
    dplyr::mutate(
      .parsed = list(if (has_text_vec(reference_bibtex)) parse_bibtex_fields(reference_bibtex) else
        list(title=NA_character_, author=NA_character_, journal=NA_character_,
             year=NA_integer_, volume=NA_character_, issue=NA_character_, pages=NA_character_)),
      # Fill missing manual columns from parsed BibTeX
      title  = if (has_text_vec(title)) title else .parsed$title,
      author = if (has_text_vec(author)) author else .parsed$author,   # JSON
      journal= if (has_text_vec(journal)) journal else .parsed$journal,
      year   = if (!is.na(year)) as.integer(year) else .parsed$year,
      volume = if (has_text_vec(volume)) volume else .parsed$volume,
      issue  = if (has_text_vec(issue)) issue else .parsed$issue,
      pages  = if (has_text_vec(pages)) pages else .parsed$pages
    ) %>%
    dplyr::ungroup() %>%
    dplyr::transmute(
      url_key,
      ref_r_clean_manual = reference_apa,
      bibtex_r_manual    = reference_bibtex,
      title_r_manual     = title,
      author_r_manual    = author,
      journal_r_manual   = journal,
      year_r_manual      = year,
      volume_r_manual    = volume,
      issue_r_manual     = issue,
      pages_r_manual     = pages
    )

  before_missing_title <- sum(!has_text_vec(data$title_r))

  out <- data %>%
    dplyr::mutate(.url_key_tmp = norm_url(.data[[url_col]])) %>%
    dplyr::left_join(manual_url, by = c(".url_key_tmp" = "url_key")) %>%
    dplyr::mutate(
      # Fill only when missing
      ref_r_clean = dplyr::coalesce(ref_r_clean, ref_r_clean_manual),
      bibtex_r    = dplyr::coalesce(bibtex_r, bibtex_r_manual),
      title_r     = dplyr::coalesce(title_r, title_r_manual),
      author_r    = dplyr::coalesce(author_r, author_r_manual),
      journal_r   = dplyr::coalesce(journal_r, journal_r_manual),
      year_r      = dplyr::coalesce(year_r, year_r_manual),
      volume_r    = dplyr::coalesce(volume_r, volume_r_manual),
      issue_r     = dplyr::coalesce(issue_r, issue_r_manual),
      pages_r     = dplyr::coalesce(pages_r, pages_r_manual)
    ) %>%
    dplyr::select(-.url_key_tmp, -dplyr::ends_with("_manual"))

  # Optional: recover missing title_r from bibtex_r
  if (recover_title_from_bibtex) {
    need_idx <- which(!has_text_vec(out$title_r) & has_text_vec(out$bibtex_r))
    if (length(need_idx) > 0) {
      recovered <- vapply(out$bibtex_r[need_idx], function(b) parse_bibtex_fields(b)$title, character(1))
      out$title_r[need_idx] <- dplyr::coalesce(out$title_r[need_idx], recovered)
    }
  }

  after_missing_title <- sum(!has_text_vec(out$title_r))

  if (verbose) {
    n_matches <- sum(norm_url(out[[url_col]]) %in% manual_url$url_key, na.rm = TRUE)
    message("=== Manual URL overrides (R side) ===")
    message("URL matches found: ", n_matches)
    message("Missing title_r before: ", before_missing_title)
    message("Missing title_r after : ", after_missing_title)
    message("Titles recovered     : ", before_missing_title - after_missing_title)
  }

  out
}

#' Fetch APA citation from DataCite (fallback for CrossRef)
#' @param doi DOI string
#' @return APA-style citation string or NA
get_datacite_apa <- function(doi) {
  doi <- trimws(doi)
  if (!grepl("^10\\.[0-9]{4,}/\\S+$", doi)) return(NA_character_)

  tryCatch({
    url <- glue("https://api.datacite.org/dois/{URLencode(doi, reserved = TRUE)}")
    res <- httr::GET(url, httr::timeout(10))
    if (httr::status_code(res) != 200) return(NA_character_)

    j <- jsonlite::fromJSON(httr::content(res, "text", encoding = "UTF-8"))
    attr <- j$data$attributes

    # Extract components
    authors <- attr$creators
    if (is.data.frame(authors) && nrow(authors) > 0) {
      author_str <- paste(
        coalesce(authors$name, authors$familyName),
        collapse = ", "
      )
    } else {
      author_str <- "Unknown"
    }
    year <- attr$publicationYear %||% ""
    title <- if (is.data.frame(attr$titles)) {
      attr$titles$title[1]
    } else if (is.list(attr$titles) && length(attr$titles) > 0) {
      attr$titles[[1]]$title %||% attr$titles[[1]]
    } else {
      ""
    }
    publisher <- attr$publisher$name %||% attr$publisher %||% ""

    sprintf("%s (%s). %s. %s. https://doi.org/%s",
            author_str, year, title, publisher, doi)
  }, error = function(e) NA_character_)
}

#' Fetch BibTeX citation from DataCite (fallback for CrossRef)
#' @param doi DOI string
#' @return BibTeX string or NA
get_datacite_bibtex <- function(doi) {
  doi <- trimws(doi)
  if (!grepl("^10\\.[0-9]{4,}/\\S+$", doi)) return(NA_character_)

  tryCatch({
    url <- glue("https://api.datacite.org/dois/{URLencode(doi, reserved = TRUE)}")
    res <- httr::GET(url, httr::timeout(10))
    if (httr::status_code(res) != 200) return(NA_character_)

    j <- jsonlite::fromJSON(httr::content(res, "text", encoding = "UTF-8"))
    attr <- j$data$attributes

    # Extract components
    authors <- attr$creators
    if (is.data.frame(authors) && nrow(authors) > 0) {
      author_str <- paste(
        coalesce(authors$name,
                 paste(authors$givenName, authors$familyName)),
        collapse = " and "
      )
    } else {
      author_str <- ""
    }
    year <- attr$publicationYear %||% ""
    title <- if (is.data.frame(attr$titles)) {
      attr$titles$title[1]
    } else if (is.list(attr$titles) && length(attr$titles) > 0) {
      attr$titles[[1]]$title %||% attr$titles[[1]]
    } else {
      ""
    }
    publisher <- attr$publisher$name %||% attr$publisher %||% ""
    key <- gsub("[^a-zA-Z0-9]", "", doi)

    sprintf(
      "@misc{%s,\n  author = {%s},\n  title = {%s},\n  year = {%s},\n  publisher = {%s},\n  doi = {%s}\n}",
      key, author_str, title, year, publisher, doi
    )
  }, error = function(e) NA_character_)
}

authors_to_crossref_json <- function(author) {
 # rcrossref returns author as a list containing a tibble (from list-column)
  if (is.null(author) || length(author) == 0) return(NA_character_)

 # If author is a list containing a data frame, extract it
  if (is.list(author) && !is.data.frame(author) && length(author) >= 1) {
    author <- author[[1]]
  }

  if (!is.data.frame(author) || nrow(author) == 0) return(NA_character_)

  df <- tibble::as_tibble(author)
  keep <- intersect(c("given", "family", "sequence", "ORCID", "affiliation"), names(df))
  if (length(keep) == 0) return(NA_character_)
  df <- df[, keep, drop = FALSE]
  as.character(jsonlite::toJSON(df, auto_unbox = TRUE, null = "null"))
}

# ---- cache I/O ----
load_ref_fields_cache <- function(cache_file = CROSSREF_REF_FIELDS_CACHE) {
  if (!file.exists(cache_file)) {
    return(tibble::tibble(
      doi = character(),
      title = character(),
      authors_json = character(),
      journal = character(),
      year = integer(),
      volume = character(),
      issue = character(),
      pages = character(),
      source = character()
    ))
  }
  readRDS(cache_file)
}

save_ref_fields_cache <- function(cache_df, cache_file = CROSSREF_REF_FIELDS_CACHE) {
  saveRDS(cache_df, cache_file)
}

# ---- CrossRef parsing (for rcrossref tibble format) ----
# rcrossref::cr_works()$data returns a tibble with dot-separated column names
# and dates as character strings like "2023-08-16"

extract_year_crossref <- function(x) {
  # rcrossref returns dates as character strings like "2023-08-16" or "2023"
  for (field in c("issued", "published.print", "published.online", "created")) {
    val <- x[[field]]
    if (!is.null(val) && length(val) > 0 && !all(is.na(val))) {
      val <- val[1]
      if (!is.na(val) && nzchar(val)) {
        # Extract year (first 4 digits)
        year <- suppressWarnings(as.integer(substr(as.character(val), 1, 4)))
        if (!is.na(year) && year > 1800 && year < 2100) {
          return(year)
        }
      }
    }
  }
  NA_integer_
}

extract_pages_crossref <- function(x) {
  page <- x$page %||% NA_character_
  page <- page[1]
  if (is.na(page) || !nzchar(page)) return(NA_character_)
  page <- str_squish(as.character(page))
  if (!nzchar(page)) NA_character_ else page
}

extract_journal_crossref <- function(x) {
 # rcrossref uses container.title (with dot, not hyphen)
  jt <- x$container.title %||% x$short.container.title %||% character(0)
  if (length(jt) >= 1 && !is.na(jt[1]) && nzchar(jt[1])) {
    return(str_squish(jt[1]))
  }
  NA_character_
}

extract_title_crossref <- function(x) {
  t <- x$title %||% character(0)
  if (length(t) >= 1 && !is.na(t[1]) && nzchar(t[1])) {
    return(str_squish(t[1]))
  }
  NA_character_
}

extract_volume_issue_crossref <- function(x) {
 # Use [[ ]] to avoid partial matching (x$issue would match x$issued)
  vol <- x[["volume"]] %||% NA_character_
  iss <- x[["issue"]] %||% NA_character_
  vol <- vol[1]
  iss <- iss[1]
  vol <- if (!is.na(vol) && nzchar(vol)) as.character(vol) else NA_character_
  iss <- if (!is.na(iss) && nzchar(iss)) as.character(iss) else NA_character_
  list(volume = vol, issue = iss)
}

parse_crossref_work_to_fields <- function(work) {
  vi <- extract_volume_issue_crossref(work)
  tibble::tibble(
    title = extract_title_crossref(work),
    authors_json = authors_to_crossref_json(work$author),
    journal = extract_journal_crossref(work),
    year = extract_year_crossref(work),
    volume = vi$volume,
    issue = vi$issue,
    pages = extract_pages_crossref(work)
  )
}

# ---- CrossRef fetch + cache (fields) ----
get_crossref_reference_fields <- function(dois,
                                          cache_file = CROSSREF_REF_FIELDS_CACHE,
                                          manual_refs = MANUAL_REFERENCES,
                                          progress = TRUE) {
  dois <- tolower(trimws(dois))
  out <- tibble::tibble(doi = dois)

  # Load manual references (highest priority)
  manual_refs_df <- load_manual_references(manual_refs)


  # Process manual overrides - extract fields from BibTeX if not provided
  manual_fields <- NULL

  if (nrow(manual_refs_df) > 0) {
    # Filter to only keys that are in the requested DOIs
    manual_subset <- manual_refs_df %>%
      dplyr::mutate(key = tolower(key)) %>%
      dplyr::filter(key %in% dois)

    if (nrow(manual_subset) > 0) {
      # Helper to check if value is non-empty (safe for NA)
      has_value <- function(x) isTRUE(!is.na(x) && nzchar(as.character(x)))

      manual_fields <- manual_subset %>%
        dplyr::rowwise() %>%
        dplyr::mutate(
          # Parse BibTeX if individual fields not provided
          .parsed = list(if (has_value(reference_bibtex)) {
            parse_bibtex_fields(reference_bibtex)
          } else {
            list(title = NA_character_, author = NA_character_, journal = NA_character_,
                 year = NA_integer_, volume = NA_character_, issue = NA_character_, pages = NA_character_)
          }),
          # Use explicit fields if provided, otherwise fall back to parsed BibTeX
          title = if (has_value(title)) title else .parsed$title,
          authors_json = if (has_value(author)) author else .parsed$author,
          journal = if (has_value(journal)) journal else .parsed$journal,
          year = if (has_value(as.character(year))) as.integer(year) else .parsed$year,
          volume = if (has_value(volume)) volume else .parsed$volume,
          issue = if (has_value(issue)) issue else .parsed$issue,
          pages = if (has_value(pages)) pages else .parsed$pages,
          source = "manual"
        ) %>%
        dplyr::ungroup() %>%
        dplyr::select(doi = key, title, authors_json, journal, year, volume, issue, pages, source)
    }
  }

  # Determine which DOIs still need fetching
  valid <- !is.na(dois) & is_doi(dois)
  unique_dois <- unique(dois[valid])

  # Exclude DOIs that have manual overrides
  manual_dois <- if (!is.null(manual_fields)) manual_fields$doi else character(0)
  unique_dois <- setdiff(unique_dois, manual_dois)

  cache_df <- load_ref_fields_cache(cache_file)
  cached_dois <- cache_df$doi %||% character(0)

  need <- setdiff(unique_dois, cached_dois)

  if (length(need) > 0) {
    if (progress) message("Fetching CrossRef reference fields for ", length(need), " DOI(s)...")

    pb <- NULL
    if (progress) {
      pb <- utils::txtProgressBar(min = 0, max = length(need), style = 3)
      on.exit(if (!is.null(pb)) close(pb), add = TRUE)
    }

    new_rows <- vector("list", length(need))
    names(new_rows) <- need

    for (i in seq_along(need)) {
      d <- need[[i]]

      row <- tryCatch({
        w <- rcrossref::cr_works(dois = d)$data
        if (!is.data.frame(w) || nrow(w) < 1) stop("No data returned")
        # Convert first row to list for extraction functions
        work <- as.list(w[1, ])

        parse_crossref_work_to_fields(work) %>%
          mutate(doi = d, source = "crossref") %>%
          select(doi, title, authors_json, journal, year, volume, issue, pages, source)
      }, error = function(e) {
        tibble::tibble(
          doi = d,
          title = NA_character_,
          authors_json = NA_character_,
          journal = NA_character_,
          year = NA_integer_,
          volume = NA_character_,
          issue = NA_character_,
          pages = NA_character_,
          source = "crossref_error"
        )
      })

      new_rows[[d]] <- row
      if (!is.null(pb)) utils::setTxtProgressBar(pb, i)
    }

    new_df <- dplyr::bind_rows(new_rows)

    cache_df <- cache_df %>%
      dplyr::filter(!doi %in% new_df$doi) %>%
      dplyr::bind_rows(new_df)

    save_ref_fields_cache(cache_df, cache_file)
  }

  # Combine: manual overrides take priority, then cache
  result <- out %>%
    dplyr::left_join(cache_df, by = "doi") %>%
    dplyr::select(doi, title, authors_json, journal, year, volume, issue, pages, source)

  # Override with manual fields where available
 if (!is.null(manual_fields) && nrow(manual_fields) > 0) {
  # rows_update() requires unique keys in y (manual_fields$doi)
  manual_fields <- manual_fields %>%
    dplyr::mutate(doi = tolower(trimws(doi))) %>%
    dplyr::group_by(doi) %>%
    dplyr::summarise(
      title = dplyr::first(na.omit(title)),
      authors_json = dplyr::first(na.omit(authors_json)),
      journal = dplyr::first(na.omit(journal)),
      year = dplyr::first(na.omit(year)),
      volume = dplyr::first(na.omit(volume)),
      issue = dplyr::first(na.omit(issue)),
      pages = dplyr::first(na.omit(pages)),
      source = "manual",
      .groups = "drop"
    )
    result <- result %>%
      dplyr::rows_update(manual_fields, by = "doi", unmatched = "ignore")
  }

  result
}

get_datacite_reference_fields <- function(dois,
                                          cache_file = CROSSREF_REF_FIELDS_CACHE,
                                          progress = TRUE) {

  dois <- tolower(trimws(dois))
  out <- tibble::tibble(doi = dois)

  valid <- !is.na(dois) & is_doi(dois)
  unique_dois <- unique(dois[valid])

  cache_df <- load_ref_fields_cache(cache_file)
  cached_subset <- cache_df %>% dplyr::filter(doi %in% unique_dois)

  # fetch only those not in cache OR those previously cached but missing key fields
  need <- setdiff(unique_dois, cached_subset$doi)

  if (length(need) > 0) {
    if (progress) message("Fetching DataCite reference fields for ", length(need), " DOI(s)...")

    pb <- NULL
    if (progress) {
      pb <- utils::txtProgressBar(min = 0, max = length(need), style = 3)
      on.exit(if (!is.null(pb)) close(pb), add = TRUE)
    }

    new_rows <- vector("list", length(need))
    names(new_rows) <- need

    for (i in seq_along(need)) {
      d <- need[[i]]

      row <- tryCatch({
        url <- glue::glue("https://api.datacite.org/dois/{URLencode(d, reserved = TRUE)}")
        res <- httr::GET(url, httr::timeout(10))
        if (httr::status_code(res) != 200) stop("DataCite status ", httr::status_code(res))

        j <- jsonlite::fromJSON(httr::content(res, "text", encoding = "UTF-8"))
        attr <- j$data$attributes

        # title
        title <- NA_character_
        if (is.data.frame(attr$titles) && nrow(attr$titles) > 0) {
          title <- attr$titles$title[1] %||% NA_character_
        } else if (is.list(attr$titles) && length(attr$titles) > 0) {
          title <- attr$titles[[1]]$title %||% attr$titles[[1]] %||% NA_character_
        }
        title <- if (!is.na(title) && nzchar(title)) stringr::str_squish(title) else NA_character_

        # journal-ish container (best-effort; DataCite is heterogeneous)
        journal <- attr$container$title %||% attr$`container-title` %||% attr$publisher %||% NA_character_
        journal <- if (!is.na(journal) && nzchar(journal)) stringr::str_squish(journal) else NA_character_

        # year
        year <- suppressWarnings(as.integer(attr$publicationYear %||% NA))

        # pages (often absent in DataCite)
        pages <- NA_character_

        # AUTHORS AS JSON (convert DataCite creators to CrossRef-like shape)
        creators <- attr$creators %||% list()
        authors_json <- NA_character_
        if (is.data.frame(creators) && nrow(creators) > 0) {
          given <- creators$givenName %||% rep(NA_character_, nrow(creators))
          family <- creators$familyName %||% rep(NA_character_, nrow(creators))
          name <- creators$name %||% rep(NA_character_, nrow(creators))

          # if family missing but "name" present, attempt split on last space
          family2 <- ifelse(!is.na(family) & nzchar(family), family, NA_character_)
          given2  <- ifelse(!is.na(given) & nzchar(given), given, NA_character_)

          need_split <- (is.na(family2) | !nzchar(family2)) & !is.na(name) & nzchar(name)
          if (any(need_split)) {
            parts <- strsplit(name[need_split], "\\s+")
            fam_guess <- vapply(parts, function(p) if (length(p) >= 1) p[[length(p)]] else NA_character_, character(1))
            giv_guess <- vapply(parts, function(p) if (length(p) >= 2) paste(p[1:(length(p)-1)], collapse = " ") else NA_character_, character(1))
            family2[need_split] <- fam_guess
            given2[need_split] <- giv_guess
          }

          # sequence: first/additional
          seqv <- rep("additional", nrow(creators))
          if (nrow(creators) >= 1) seqv[1] <- "first"

          df_json <- tibble::tibble(
            given = given2,
            family = family2,
            sequence = seqv
          ) %>%
            dplyr::mutate(
              given = dplyr::na_if(given, ""),
              family = dplyr::na_if(family, "")
            )

          authors_json <- jsonlite::toJSON(df_json, auto_unbox = TRUE, null = "null")
        }

        tibble::tibble(
          doi = d,
          title = title,
          authors_json = authors_json,
          journal = journal,
          year = year,
          volume = NA_character_,
          issue = NA_character_,
          pages = pages,
          source = "datacite"
        )
      }, error = function(e) {
        tibble::tibble(
          doi = d,
          title = NA_character_,
          authors_json = NA_character_,
          journal = NA_character_,
          year = NA_integer_,
          volume = NA_character_,
          issue = NA_character_,
          pages = NA_character_,
          source = "datacite_error"
        )
      })

      new_rows[[d]] <- row
      if (!is.null(pb)) utils::setTxtProgressBar(pb, i)
    }

    new_df <- dplyr::bind_rows(new_rows)

    cache_df <- cache_df %>%
      dplyr::filter(!doi %in% new_df$doi) %>%
      dplyr::bind_rows(new_df)

    save_ref_fields_cache(cache_df, cache_file)
  }

  out %>%
    dplyr::left_join(cache_df, by = "doi") %>%
    dplyr::select(doi, title, authors_json, journal, year, volume, issue, pages, source)
}

#' Get APA and/or BibTeX references for DOIs/keys
#' Four-tier lookup: manual overrides → cache → CrossRef → DataCite
#' Note: API queries (CrossRef/DataCite) only happen for valid DOIs.
#' Non-DOI keys can still be resolved via manual_refs.
#'
#' @param doi_vec Vector of DOI strings (or other keys for manual lookup)
#' @param cache Path to cache file (default from cache_config)
#' @param manual_refs Path to manual references file
#' @param format Which format(s) to return: "both" (default), "apa", or "bibtex"
#' @param return_source If TRUE, include source columns
#' @param progress If TRUE, show progress messages
#' @return Tibble with: doi, reference_apa and/or reference_bibtex, [source cols]
get_references <- function(doi_vec,
                           cache = CROSSREF_CITATIONS_CACHE,
                           manual_refs = MANUAL_REFERENCES,
                           format = c("both", "apa", "bibtex"),
                           return_source = FALSE,
                           include_fields = TRUE,
                           fields_cache = CROSSREF_REF_FIELDS_CACHE,
                           progress = TRUE) {

  fields_fallback_datacite <- TRUE # whether to fallback to DataCite for missing fields, no longer exposed as argument
  format <- match.arg(format)
  cache_path <- cache

  # Load manual references (highest priority)
  manual_refs_df <- load_manual_references(manual_refs)

  cache_exists <- file.exists(cache_path)
  if (progress) {
    message(if (cache_exists) {
      sprintf("Using existing cache at %s", cache_path)
    } else {
      sprintf("Initializing new cache at %s", cache_path)
    })
  }

  # Load or initialize cache
  cache_obj <- load_citation_cache(cache_path)

  # Normalize keys to lowercase for consistent caching
  doi_vec <- tolower(doi_vec)
  unique_keys <- unique(doi_vec)
  n_unique <- length(unique_keys)

  # DOI validation helper
  is_doi <- function(x) grepl("^10\\.[0-9]{4,}/\\S+$", x)

  # Track where each reference came from (separate for apa/bibtex)
  sources_apa <- character(length(unique_keys))
  sources_bibtex <- character(length(unique_keys))
  names(sources_apa) <- unique_keys
  names(sources_bibtex) <- unique_keys

  # Progress bar
  pb <- NULL
  if (progress && n_unique > 0) {
    pb <- utils::txtProgressBar(min = 0, max = n_unique, style = 3)
    on.exit(close(pb), add = TRUE)
  }

  # Loop through unique keys
  for (i in seq_along(unique_keys)) {
    d <- unique_keys[i]

    # === APA ===
    if (format %in% c("both", "apa")) {
      # 1. Check manual references (works for any key, not just DOIs)
      manual_apa <- manual_refs_df %>%
        dplyr::filter(tolower(key) == d) %>%
        dplyr::pull(reference_apa) %>%
        dplyr::first()

      if (!is.na(manual_apa) && nzchar(manual_apa)) {
        cache_obj$apa[[d]] <- manual_apa
        sources_apa[i] <- "manual"
      } else {
        # 2. Check cache
        apa_cached <- cache_obj$apa[[d]]

        if (!is.null(apa_cached) && !is.na(apa_cached[1]) && nzchar(apa_cached[1])) {
          sources_apa[i] <- "cached"
        } else if (!is_doi(d)) {
          # Not a DOI, can't query APIs
          cache_obj$apa[[d]] <- NA_character_
          sources_apa[i] <- "not_found"
        } else {
          # 3. Try CrossRef
          if (progress) {
            message(sprintf("(%d/%d) Fetching citations for %s", i, n_unique, d))
          }
          apa_cr <- get_crossref_citation(d, "apa")

          if (!is.na(apa_cr) && length(apa_cr) > 0 && nzchar(apa_cr)) {
            cache_obj$apa[[d]] <- apa_cr
            sources_apa[i] <- "crossref"
          } else {
            # 4. Fallback to DataCite
            apa_dc <- get_datacite_apa(d)
            if (!is.na(apa_dc) && nzchar(apa_dc)) {
              cache_obj$apa[[d]] <- apa_dc
              sources_apa[i] <- "datacite"
            } else {
              cache_obj$apa[[d]] <- NA_character_
              sources_apa[i] <- "not_found"
            }
          }
        }
      }
    }

    # === BibTeX ===
    if (format %in% c("both", "bibtex")) {
      # 1. Check manual references
      manual_bib <- manual_refs_df %>%
        dplyr::filter(tolower(key) == d) %>%
        dplyr::pull(reference_bibtex) %>%
        dplyr::first()

      if (!is.na(manual_bib) && nzchar(manual_bib)) {
        cache_obj$bibtex[[d]] <- manual_bib
        sources_bibtex[i] <- "manual"
      } else {
        # 2. Check cache
        bib_cached <- cache_obj$bibtex[[d]]

        if (!is.null(bib_cached) && !is.na(bib_cached[1]) && nzchar(bib_cached[1])) {
          sources_bibtex[i] <- "cached"
        } else if (!is_doi(d)) {
          cache_obj$bibtex[[d]] <- NA_character_
          sources_bibtex[i] <- "not_found"
        } else {
          # 3. Try CrossRef
          bib_cr <- get_crossref_citation(d, "bibtex")

          if (!is.na(bib_cr) && length(bib_cr) > 0 && nzchar(bib_cr)) {
            cache_obj$bibtex[[d]] <- bib_cr
            sources_bibtex[i] <- "crossref"
          } else {
            # 4. Fallback to DataCite
            bib_dc <- get_datacite_bibtex(d)
            if (!is.na(bib_dc) && nzchar(bib_dc)) {
              cache_obj$bibtex[[d]] <- bib_dc
              sources_bibtex[i] <- "datacite"
            } else {
              cache_obj$bibtex[[d]] <- NA_character_
              sources_bibtex[i] <- "not_found"
            }
          }
        }
      }
    }

    if (!is.null(pb)) {
      utils::setTxtProgressBar(pb, i)
    }
  }

  # Save updated cache to disk
  save_citation_cache(cache_obj, cache_path)

  if (progress && n_unique > 0) {
    message("Reference retrieval complete.")
  }

  # Map back to original order and build result tibble
  result <- tibble::tibble(doi = doi_vec)

  if (format %in% c("both", "apa")) {
    apa_final <- vapply(doi_vec, function(d) {
      ref <- cache_obj$apa[[d]]
      if (is.null(ref) || length(ref) != 1 || is.na(ref[1]) || !nzchar(ref[1])) {
        NA_character_
      } else {
        ref
      }
    }, character(1))

    if (format == "apa") {
      result$reference <- apa_final
    } else {
      result$reference_apa <- apa_final
    }

    if (return_source) {
      src_apa <- vapply(doi_vec, function(d) sources_apa[d], character(1))
      if (format == "apa") {
        result$source <- src_apa
      } else {
        result$source_apa <- src_apa
      }
    }
  }

  if (format %in% c("both", "bibtex")) {
    bib_final <- vapply(doi_vec, function(d) {
      ref <- cache_obj$bibtex[[d]]
      if (is.null(ref) || length(ref) != 1 || is.na(ref[1]) || !nzchar(ref[1])) {
        NA_character_
      } else {
        ref
      }
    }, character(1))

    if (format == "bibtex") {
      result$reference <- bib_final
    } else {
      result$reference_bibtex <- bib_final
    }

    if (return_source) {
      src_bib <- vapply(doi_vec, function(d) sources_bibtex[d], character(1))
      if (format == "bibtex") {
        result$source <- src_bib
      } else {
        result$source_bibtex <- src_bib
      }
    }
  }

  if (include_fields) {
    fields_cr <- get_crossref_reference_fields(
      doi_vec,
      cache_file = fields_cache,
      progress = progress
    )

    fields_out <- fields_cr

    if (fields_fallback_datacite) {
      miss <- fields_out %>%
        mutate(.miss = (is.na(title) | !nzchar(title)) |
                 (is.na(authors_json) | !nzchar(authors_json)) |
                 (is.na(journal) | !nzchar(journal)) |
                 is.na(year) |
                 (is.na(volume) | !nzchar(volume)) |
                 (is.na(issue) | !nzchar(issue)) |
                 (is.na(pages) | !nzchar(pages))) %>%
        filter(.miss & !is.na(doi) & is_doi(doi)) %>%
        distinct(doi) %>%
        pull(doi)

      if (length(miss) > 0) {
        fields_dc <- get_datacite_reference_fields(
          miss,
          cache_file = fields_cache,
          progress = progress
        )

        fields_out <- fields_out %>%
          left_join(fields_dc, by = "doi", suffix = c("", "_dc")) %>%
          transmute(
            doi,
            title  = coalesce(title, title_dc),
            authors_json = coalesce(authors_json, authors_json_dc),
            journal = coalesce(journal, journal_dc),
            year   = coalesce(year, year_dc),
            volume = coalesce(volume, volume_dc),
            issue  = coalesce(issue, issue_dc),
            pages  = coalesce(pages, pages_dc),
            source = coalesce(source, source_dc)
          )

        save_ref_fields_cache(
          load_ref_fields_cache(fields_cache) %>%
            filter(!doi %in% fields_out$doi) %>%
            bind_rows(fields_out),
          fields_cache
        )
      }
    }

    result <- result %>%
      left_join(
        fields_out %>% select(doi, title, author = authors_json, journal, year, volume, issue, pages),
        by = "doi"
      )
  }

  result

}

# ============================================================================
# DOI Metadata Caching (from CrossRef and DataCite)
# ============================================================================

#' Load DOI metadata cache
#' @param cache_file Path to cache file
#' @return Tibble with cached DOI metadata
load_doi_cache <- function(cache_file = CROSSREF_DOI_CACHE) {
  if (!file.exists(cache_file)) {
    return(tibble::tibble(
      doi = character(),
      title = character(),
      authors = character(),
      year = integer(),
      source = character()
    ))
  }

  readRDS(cache_file)
}

#' Save DOI metadata cache
#' @param cache_df Tibble with DOI metadata
#' @param cache_file Path to save cache
save_doi_cache <- function(cache_df, cache_file = CROSSREF_DOI_CACHE) {
  saveRDS(cache_df, cache_file)
}

# ============================================================================
# Author Caching (from CrossRef)
# ============================================================================

#' Load author cache from Excel
#' @param cache_file Path to cache file
#' @return Tibble with author data
load_author_cache <- function(cache_file = CROSSREF_AUTHORS_CACHE) {
  if (!file.exists(cache_file)) {
    return(tibble::tibble(
      doi = character(),
      authors_json = character()
    ))
  }

  readxl::read_excel(cache_file)
}

#' Save author cache to Excel
#' @param cache_df Tibble with author data
#' @param cache_file Path to save cache
save_author_cache <- function(cache_df, cache_file = CROSSREF_AUTHORS_CACHE) {
  openxlsx::write.xlsx(cache_df, cache_file, overwrite = TRUE)
}

#' Get CrossRef authors for DOIs with caching
#' @param dois Vector of DOI strings
#' @param cache_file Path to cache file
#' @param batch_size Batch size for API calls
#' @return Tibble with doi and authors_json columns
get_crossref_authors <- function(dois,
                                cache_file = CROSSREF_AUTHORS_CACHE,
                                batch_size = 50) {

  dois <- tolower(trimws(dois))
  unique_dois <- unique(dois[!is.na(dois)])

  # Load existing cache
  cache_df <- load_author_cache(cache_file)
  cached_dois <- if (nrow(cache_df) > 0) cache_df$doi else character(0)

  # Find uncached DOIs
  uncached_dois <- setdiff(unique_dois, cached_dois)

  if (length(uncached_dois) > 0) {
    message("Fetching author data for ", length(uncached_dois), " new DOI(s)...")

    new_results <- tibble::tibble(doi = character(), authors_json = character())

    # Fetch in batches
    for (i in seq(1, length(uncached_dois), by = batch_size)) {
      batch <- uncached_dois[i:min(i + batch_size - 1, length(uncached_dois))]
      message(sprintf("  Batch %d-%d", i, min(i + batch_size - 1, length(uncached_dois))))

      for (doi in batch) {
        tryCatch({
          # CrossRef API call
          cr_result <- rcrossref::cr_cn(doi, format = "json")
          authors_json <- jsonlite::toJSON(cr_result$author %||% list())

          new_results <- bind_rows(new_results, tibble::tibble(
            doi = doi,
            authors_json = authors_json
          ))
        }, error = function(e) {
          message("    Error fetching ", doi, ": ", e$message)
        })
      }
    }

    # Append to cache and save
    cache_df <- bind_rows(cache_df, new_results)
    save_author_cache(cache_df, cache_file)
  }

  # Return all requested DOIs with their cached author data
  result <- tibble::tibble(doi = dois) %>%
    left_join(cache_df, by = "doi")

  result
}

# ============================================================================
# Author Overlap Computation
# ============================================================================

#' Compute author overlap between two studies
#' @param data Tibble with doi_o and doi_r columns
#' @param authors_cache_file Path to author cache
#' @return Tibble with original data plus author_overlap column
compute_author_overlap <- function(data,
                                  authors_cache_file = CROSSREF_AUTHORS_CACHE) {

  # Get all unique DOIs
  unique_dois <- unique(c(data$doi_o, data$doi_r))
  unique_dois <- unique_dois[!is.na(unique_dois)]

  # Fetch author data (with caching)
  authors_df <- get_crossref_authors(unique_dois, authors_cache_file)

  # Function to extract author family names from JSON
  extract_author_names <- function(authors_json) {
    tryCatch({
      if (is.na(authors_json) || authors_json == "[]") {
        return(character(0))
      }
      authors_list <- jsonlite::fromJSON(authors_json)
      if (is.data.frame(authors_list) && "family" %in% names(authors_list)) {
        tolower(authors_list$family)
      } else {
        character(0)
      }
    }, error = function(e) character(0))
  }

  # Compute overlap for each row
  data <- data %>%
    left_join(authors_df %>% rename(authors_json_o = authors_json),
              by = c("doi_o" = "doi")) %>%
    left_join(authors_df %>% rename(authors_json_r = authors_json),
              by = c("doi_r" = "doi")) %>%
    rowwise() %>%
    mutate(
      authors_o = list(extract_author_names(authors_json_o)),
      authors_r = list(extract_author_names(authors_json_r)),
      author_overlap = length(intersect(authors_o, authors_r)),
      # Percentage based on replication authors (measures independence of replication team)
      author_overlap_pct = if (length(authors_r) > 0) {
        round(100 * author_overlap / length(authors_r), 1)
      } else {
        NA_real_
      }
    ) %>%
    ungroup() %>%
    select(-authors_json_o, -authors_json_r, -authors_o, -authors_r)

  data
}
