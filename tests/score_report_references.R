# Run from the repository root: Rscript tests/score_report_references.R
source('R/score_report_references.R')
audit <- read.csv('cos_score_integration/report_references/audit.csv')
x <- audit[audit$dataset == 'FReD', ]
data <- data.frame(url_r=x$url_r, ref_r_clean=x$before,
                   reported_success='keep', es_value_r=0.123)
y <- apply_score_report_references(data)
stopifnot(identical(y$reported_success, data$reported_success),
          identical(y$es_value_r, data$es_value_r), nrow(y) == nrow(data))
fixed <- x$status == 'corrected'
stopifnot(all(y$ref_r_clean[fixed] == x$after[fixed]),
          all(y$ref_r_clean[!fixed] == x$before[!fixed]),
          identical(apply_score_report_references(y), y))
cat('Verified overrides, protected fields, unresolved rows and idempotency:',
    sum(fixed), 'corrected rows.\n')

# Validated individual attempts must also beat stale OSF project citations.
components <- read.csv('cos_score_integration/report_references/entry_sheet_intake.csv',
                       stringsAsFactors=FALSE)
input <- data.frame(url_r=components$report_url, ref_r_clean='SCORE/COS stale citation',
                    author_r='[]', title_r='Internal code', reported_success='preserve',
                    es_value_r=0.456)
resolved <- apply_score_report_references(input)
stopifnot(nrow(resolved)==14L, all(resolved$ref_r_clean==components$reference),
          identical(resolved$reported_success,input$reported_success),
          identical(resolved$es_value_r,input$es_value_r),
          all(resolved$year_r==components$reference_year),
          all(grepl('@misc',resolved$bibtex_r)),
          all(vapply(resolved$author_r,function(a) nrow(jsonlite::fromJSON(a))>0L,logical(1))),
          identical(apply_score_report_references(resolved),resolved))
# The validated compound surname must not revert to Crossref's split name.
manual <- readxl::read_excel('cache/manual_references.xlsx')
original <- manual[manual$key=='10.1016/j.cognition.2012.05.011',]
stopifnot(nrow(original)==1L,
          grepl('De Neys, W.',original$reference_apa,fixed=TRUE),
          'De Neys' %in% jsonlite::fromJSON(original$author)$family)
cat('Verified all 14 individual report references/metadata and De Neys original override.\n')
