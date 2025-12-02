# Shared CrossRef citation caching functions
# Used by both FLoRA and COS reports for consistent reference handling

# Default cache file name (relative to working directory by default)
CIT_CACHE_FILE <- "crossref_citation_cache.rds"

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

# Fetch a citation for a DOI from CrossRef, either in BibTeX or APA style
get_crossref_citation <- function(doi, type = c("bibtex", "apa")) {
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

# Get APA references for a vector of DOIs using cache
# Returns a tibble with doi and reference columns
# This is a simplified version for COS report that only needs APA citations
get_apa_references <- function(doi_vec, cache = CIT_CACHE_FILE, progress = TRUE) {
  cache_path <- cache
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

  # Loop over unique DOIs and resolve APA
  for (i in seq_along(unique_dois)) {
    d <- unique_dois[i]

    # Try to get APA from cache first; if missing, ask CrossRef
    apa_cr <- cache$apa[[d]]
    
    if (is.null(apa_cr)) {
      if (progress) {
        message(sprintf("(%d/%d) Fetching APA citation from CrossRef for %s", i, n_unique, d))
      }
      # Not in cache, fetch from CrossRef
      apa_cr <- get_crossref_citation(d, "apa")
      cache$apa[[d]] <- apa_cr
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

  # Save updated APA cache to disk for future runs
  save_citation_cache(cache, cache_path)
  
  if (progress && n_unique > 0) {
    message("APA retrieval complete.")
  }

  # Return a tibble with DOI and reference
  tibble::tibble(
    doi = doi_vec,
    reference = apa_final
  )
}
