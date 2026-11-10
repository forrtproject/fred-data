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
