# Cache file paths (by data type, not purpose)
# Sourced by helper scripts to ensure consistent cache locations

# Base cache directory (project-relative)
CACHE_DIR <- here::here("cache")

# CrossRef/DataCite DOI metadata cache
CROSSREF_DOI_CACHE <- file.path(CACHE_DIR, "crossref_doi_cache.rds")

# CrossRef citations cache (APA/BibTeX references)
CROSSREF_CITATIONS_CACHE <- file.path(CACHE_DIR, "crossref_citations.rds")

CROSSREF_REF_FIELDS_CACHE <- file.path(CACHE_DIR, "crossref_fields.rds")

# CrossRef author lists cache
CROSSREF_AUTHORS_CACHE <- file.path(CACHE_DIR, "crossref_authors.xlsx")

# Author overlap computation results
AUTHOR_OVERLAP_CACHE <- file.path(CACHE_DIR, "author_overlap.xlsx")

# Manual reference overrides (highest priority in 3-tier lookup)
MANUAL_REFERENCES <- file.path(CACHE_DIR, "manual_references.xlsx")

# OpenAlex keywords cache
OPENALEX_CACHE <- file.path(CACHE_DIR, "openalex_keywords_language.csv")

# Validation report from last run (for incremental reporting)
VALIDATION_REPORT_CACHE <- here::here("output", "validation_report.rds")
