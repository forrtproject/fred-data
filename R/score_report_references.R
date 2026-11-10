# Apply only the report bylines verified in the SCORE audit. Cached project
# contributor lists are not report authors; these verified rows take priority.
apply_score_report_references <- function(data,
    audit_file = here::here('cos_score_integration', 'report_references', 'audit.csv'),
    manual_file = here::here('cache', 'manual_references.xlsx'),
    component_file = here::here('cos_score_integration', 'report_references', 'entry_sheet_intake.csv')) {
  audit <- read.csv(audit_file, stringsAsFactors = FALSE)
  components <- read.csv(component_file, stringsAsFactors = FALSE)
  keys <- unique(c(audit$url_r[audit$dataset == 'FReD' & audit$status == 'corrected'],
                   components$report_url))
  normalize <- function(x) tolower(sub('/+$', '', trimws(x)))
  refs <- readxl::read_excel(manual_file)
  refs <- refs[normalize(refs$key) %in% normalize(keys), ]
  refs <- refs[!duplicated(normalize(refs$key)), ]
  idx <- match(normalize(data$url_r), normalize(refs$key))
  found <- which(!is.na(idx))
  fields <- c(ref_r_clean = 'reference_apa', bibtex_r = 'reference_bibtex',
              title_r = 'title', author_r = 'author', journal_r = 'journal', year_r = 'year')
  for (field in names(fields)) {
    if (!field %in% names(data)) data[[field]] <- NA
    data[[field]][found] <- refs[[fields[[field]]]][idx[found]]
  }
  data
}
