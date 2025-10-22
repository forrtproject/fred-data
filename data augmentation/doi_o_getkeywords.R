

# Get Keywords for doi_o --------------------------------------------------


# download 2025-09-26 version
ds <- openxlsx::read.xlsx("https://github.com/forrtproject/FReD-data/raw/refs/heads/main/COS%20Reports/2025-09-26_COSdata_validated.xlsx")


# OpenAlex keyword search -------------------------------------------------

# install.packages(c("httr", "jsonlite"))  # uncomment if needed
library(httr)
library(jsonlite)

get_openalex_keywords <- function(doi, mailto = NULL, fallback_to_concepts = TRUE, n_concepts = 10) {
  base_url <- "https://api.openalex.org/works/"
  # Encode only the DOI part so slashes become %2F but keep "doi:" literal
  encoded_doi <- URLencode(doi, reserved = TRUE)
  url <- paste0(base_url, "doi:", encoded_doi)

  q <- list(select = "id,doi,display_name,keywords,concepts")
  if (!is.null(mailto)) q$mailto <- mailto

  resp <- GET(url, query = q, user_agent("R script (OpenAlex lookup)"))
  if (http_error(resp)) {
    stop(sprintf("HTTP %s: %s", status_code(resp), content(resp, as = "text", encoding = "UTF-8")))
  }
  x <- fromJSON(content(resp, as = "text", encoding = "UTF-8"), simplifyVector = TRUE)

  # Try explicit keywords first
  kws <- NULL
  if (!is.null(x$keywords)) {
    if (is.character(x$keywords)) {
      kws <- x$keywords
    } else if (is.data.frame(x$keywords)) {
      nm <- names(x$keywords)
      pick <- intersect(c("display_name", "keyword", "name", "value"), nm)
      if (length(pick)) kws <- unique(na.omit(as.character(x$keywords[[pick[1]]])))
    } else if (is.list(x$keywords)) {
      # list of lists
      kws <- unique(na.omit(as.character(unlist(lapply(
        x$keywords,
        function(k) k[["display_name"]] %||% k[["keyword"]] %||% k[["name"]] %||% k
      )))))
    }
  }

  # Fallback to top-N concepts if no explicit keywords
  if ((is.null(kws) || length(kws) == 0) && fallback_to_concepts && !is.null(x$concepts)) {
    cons <- x$concepts
    if (is.data.frame(cons) && "display_name" %in% names(cons)) {
      if ("score" %in% names(cons)) {
        cons <- cons[order(cons$score, decreasing = TRUE), , drop = FALSE]
      }
      kws <- head(unique(as.character(cons$display_name)), n_concepts)
    } else if (is.list(cons)) {
      # list of concepts
      dn <- unlist(lapply(cons, function(cn) cn[["display_name"]]))
      sc <- unlist(lapply(cons, function(cn) cn[["score"]]))
      ord <- order(ifelse(is.na(sc), 0, sc), decreasing = TRUE)
      kws <- head(unique(as.character(dn[ord])), n_concepts)
    }
  }

  # Clean up
  kws <- unique(trimws(kws))
  kws[nzchar(kws)]
}

`%||%` <- function(a, b) if (!is.null(a) && length(a) > 0) a else b

# Example: get keywords for the requested DOI
keywords <- get_openalex_keywords("10.4148/1944-9771.1299", mailto = "you@example.com")
print(keywords)
str(keywords)

dois <- unique(ds$doi_o)
dois <- dois[!is.na(dois) & grepl("^10", dois)]
dois <- dois[!is.na(dois)]

# dois is your vector of DOIs
kwdat <- data.frame(
  doi_o = dois,
  keywords = NA_character_,
  error = NA_character_,
  stringsAsFactors = FALSE
)

for (idx in seq_along(dois)) {
  res <- tryCatch(
    {
      kw <- get_openalex_keywords(dois[idx], mailto = "lukas.roeseler@uni-muenster.de")
      list(kw = kw, err = NA_character_)
    },
    error = function(e) list(kw = character(0), err = conditionMessage(e))
  )

  kwdat$keywords[idx] <- if (length(res$kw) > 0) paste(res$kw, collapse = ", ") else NA_character_
  kwdat$error[idx]    <- res$err
}

kwdat




