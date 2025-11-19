# Shared CrossRef citation caching functions
# Used by both FLoRA and COS reports for consistent reference handling

# File on disk where we cache citation strings from CrossRef
CIT_CACHE_FILE <- "crossref_citation_cache.rds"

# Load cached APA/BibTeX results if the cache file exists;
# otherwise start with an empty list structure
load_citation_cache <- function() {
  if (file.exists(CIT_CACHE_FILE)) {
    readRDS(CIT_CACHE_FILE)
  } else {
    list(apa = list(), bibtex = list())
  }
}

# Save the updated cache back to disk as an RDS file
save_citation_cache <- function(cache) {
  saveRDS(cache, CIT_CACHE_FILE)
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
get_apa_references <- function(doi_vec) {
  # Load (or initialize) the on-disk cache of APA strings
  cache <- load_citation_cache()
  
  # Normalise all DOIs to lowercase for consistent matching & caching
  doi_vec <- tolower(doi_vec)
  
  # Prepare output vectors
  apa_final <- vector("character", length(doi_vec))
  
  # Loop over each DOI and resolve APA
  for (i in seq_along(doi_vec)) {
    d <- doi_vec[i]
    
    # Try to get APA from cache first; if missing, ask CrossRef
    apa_cr <- cache$apa[[d]]
    
    if (is.null(apa_cr)) {
      # Not in cache, fetch from CrossRef
      apa_cr <- get_crossref_citation(d, "apa")
      cache$apa[[d]] <- apa_cr
    }
    
    # Store result (may be NA if CrossRef lookup failed)
    apa_final[i] <- if (is.na(apa_cr) || !nzchar(apa_cr)) NA_character_ else apa_cr
  }
  
  # Save updated APA cache to disk for future runs
  save_citation_cache(cache)
  
  # Return a tibble with DOI and reference
  tibble::tibble(
    doi = doi_vec,
    reference = apa_final
  )
}
