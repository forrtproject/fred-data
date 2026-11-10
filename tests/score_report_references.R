# Run from the repository root: Rscript tests/score_report_references.R
source('R/score_report_references.R')
audit <- read.csv('cos_score_integration/report_references/audit.csv')
data <- data.frame(url_r=audit$url_r, ref_r_clean='stale citation',
                   author_r='[]', reported_success='keep', es_value_r=0.123)
resolved <- apply_score_report_references(data)
fixed <- audit$status == 'corrected'
stopifnot(sum(fixed)==130L, sum(audit$status=='unresolved')==9L,
          all(resolved$ref_r_clean[fixed]==audit$after[fixed]),
          all(resolved$ref_r_clean[!fixed]=='stale citation'),
          all(!is.na(resolved$year_r[fixed])),
          all(grepl('@misc',resolved$bibtex_r[fixed])),
          all(vapply(resolved$author_r[fixed],function(a)
            nrow(jsonlite::fromJSON(a))>0L,logical(1))),
          identical(resolved$reported_success,data$reported_success),
          identical(resolved$es_value_r,data$es_value_r),
          identical(apply_score_report_references(resolved),resolved))
manual <- readxl::read_excel('cache/manual_references.xlsx')
original <- manual[manual$key=='10.1016/j.cognition.2012.05.011',]
stopifnot(nrow(original)==1L, 'De Neys' %in% jsonlite::fromJSON(original$author)$family)
cat('Verified 130 report references, preserved unresolved rows and numerical fields, and idempotency.\n')
