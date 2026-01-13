# Shared CrossRef citation caching functions
# Used by both FLoRA and COS reports for consistent reference handling

# Default cache file name (relative to working directory by default)
CIT_CACHE_FILE <- "crossref_citation_cache.rds"
MANUAL_REF_FILE <- "manual_references.xlsx"

# Load cached APA/BibTeX results if the cache file exists;
# otherwise start with an empty list structure
load_citation_cache <- function(cache_file = CIT_CACHE_FILE) {
  if (file.exists(cache_file)) {
    readRDS(cache_file)
  } else {
    list(apa = list(), bibtex = list())
  }
}

# Save the updated cache back to disk as an RDS file
save_citation_cache <- function(cache, cache_file = CIT_CACHE_FILE) {
  saveRDS(cache, cache_file)
}

# Load manual references from Excel file if it exists
# Returns a tibble with key, reference_apa, reference_bibtex, and ref_old columns
# If file doesn't exist, returns empty tibble
load_manual_references <- function(manual_ref_file = MANUAL_REF_FILE) {
  if (!file.exists(manual_ref_file)) {
    return(tibble::tibble(
      key = character(),
      reference_apa = character(),
      reference_bibtex = character(),
      ref_old = character()
    ))
  }

  tryCatch({
    readxl::read_excel(manual_ref_file)
  }, error = function(e) {
    message(sprintf("Warning: Could not read manual references file %s", manual_ref_file))
    tibble::tibble(
      key = character(),
      reference_apa = character(),
      reference_bibtex = character(),
      ref_old = character()
    )
  })
}

# Fetch a citation for a DOI from CrossRef, either in BibTeX or APA style
get_crossref_citation <- function(doi, type = c("bibtex", "apa")) {

  doi <- trimws(doi)
  #Validate DOI
  if (!grepl("^10\\.[0-9]{4,}/\\S+$", doi)) return(NA_character_)

  type <- match.arg(type)

  if (type == "bibtex") {
    fmt   <- "bibtex"  # CrossRef content-negotiation format for BibTeX
    style <- NULL      # no citation style needed for BibTeX
  } else if (type == "apa") {
    fmt   <- "text"    # plain text output
    style <- "apa"     # APA citation style
  }

  # Try the CrossRef call; if it fails, return NA instead of throwing an error
  tryCatch(
    rcrossref::cr_cn(dois = doi, format = fmt, style = style),
    error = function(e) NA_character_
  )
}

# Get APA references for a vector of DOIs using manual references and cache
# Checks manual_references.xlsx first (allowing overrides), then cache, then CrossRef
# Returns a tibble with doi and reference columns
# If return_source = TRUE, also includes a source column indicating where reference came from
# (manual, cached, crossref, or NA)
get_apa_references <- function(doi_vec,
                               cache = CIT_CACHE_FILE,
                               manual_refs = MANUAL_REF_FILE,
                               return_source = FALSE,
                               progress = TRUE) {
  cache_path <- cache

  # Load manual references (checked first to allow overrides)
  manual_refs_df <- load_manual_references(manual_refs)

  cache_exists <- file.exists(cache_path)
  if (progress) {
    message(if (cache_exists) {
      sprintf("Using existing cache at %s", cache_path)
    } else {
      sprintf("Cache not found; initializing new cache at %s", cache_path)
    })
  }

  # Load (or initialize) the on-disk cache of APA strings
  cache <- load_citation_cache(cache_path)

  # Normalise all DOIs to lowercase for consistent matching & caching
  doi_vec <- tolower(doi_vec)
  unique_dois <- unique(doi_vec)

  n_unique <- length(unique_dois)

  # Lightweight progress logging so we can see where slowdowns occur
  pb <- NULL
  if (progress && n_unique > 0) {
    pb <- utils::txtProgressBar(min = 0, max = n_unique, style = 3)
    on.exit(close(pb), add = TRUE)
  }

  # Track sources for each DOI if requested
  sources <- character(length(unique_dois))
  names(sources) <- unique_dois

  # Loop over unique DOIs and resolve APA
  for (i in seq_along(unique_dois)) {
    d <- unique_dois[i]

    # First, check manual references
    manual_match <- manual_refs_df %>%
      dplyr::filter(tolower(key) == d) %>%
      dplyr::pull(reference_apa) %>%
      dplyr::first()

    if (!is.na(manual_match) && nzchar(manual_match)) {
      cache$apa[[d]] <- manual_match
      sources[i] <- "manual"
    } else {
      # Try to get APA from cache; if missing, ask CrossRef
      apa_cr <- cache$apa[[d]]

      if (is.null(apa_cr) || is.na(apa_cr[1])) {
        if (progress) {
          message(sprintf("(%d/%d) Fetching APA citation from CrossRef for %s", i, n_unique, d))
        }
        # Not in cache, fetch from CrossRef
        apa_cr <- get_crossref_citation(d, "apa")
        cache$apa[[d]] <- apa_cr

        if (is.na(apa_cr)) {
          sources[i] <- "not_found"
        } else {
          sources[i] <- "crossref"
        }
      } else {
        sources[i] <- "cached"
      }
    }

    if (!is.null(pb)) {
      utils::setTxtProgressBar(pb, i)
    }
  }

  # Map APA strings back to original order
  apa_final <- vapply(doi_vec, function(d) {
    apa_cr <- cache$apa[[d]]
    if (is.null(apa_cr) ||
        length(apa_cr) != 1 ||
        is.na(apa_cr[1]) ||
        !nzchar(apa_cr[1])) {
      NA_character_
    } else {
      apa_cr
    }
  }, character(1))

  # Map sources back to original order if requested
  if (return_source) {
    source_final <- vapply(doi_vec, function(d) {
      sources[d]
    }, character(1))
  }

  # Save updated APA cache to disk for future runs
  save_citation_cache(cache, cache_path)

  if (progress && n_unique > 0) {
    message("APA retrieval complete.")
  }

  # Return a tibble with DOI and reference, optionally with source
  result <- tibble::tibble(
    doi = doi_vec,
    reference = apa_final
  )

  if (return_source) {
    result <- result %>% dplyr::mutate(source = source_final)
  }

  result
}
