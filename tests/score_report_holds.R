# Run from the repository root: Rscript tests/score_report_holds.R
# The seven pooled SCORE rows are superseded by their individual attempts and stay excluded.
source('R/score_report_holds.R')
raw <- read.csv('cos_score_integration/cos_test_set_phase1.csv', check.names=FALSE)
prepared <- readxl::read_excel('cos_score_integration/cos_test_set_phase1_prepared.xlsx')
held_ids <- paste0(c('AvOr','LyLd','zlm2','plLK','EQxa','8wZ0','AgO1'), '_single-trace')
for (data in list(raw, prepared)) {
  key <- if ('claim_id' %in% names(data)) 'claim_id' else 'id'
  filtered <- filter_score_report_holds(data)
  held <- attr(filtered, 'held_score_claims')
  stopifnot(nrow(data)==132L, nrow(filtered)==125L, nrow(held)==7L,
            setequal(held[[key]], held_ids), !any(filtered[[key]] %in% held_ids))
  # Compare every field, including all outcomes and effect sizes, without coercion.
  attr(filtered, 'held_score_claims') <- NULL
  expected <- data[!data[[key]] %in% held_ids, , drop=FALSE]
  stopifnot(identical(filtered, expected))
}
# Execute the actual integration chunk against a control row and the real source.
library(dplyr)
qmd <- readLines('pipelines/fred/prepare_fred.qmd')
a <- grep('^```\\{r score-integration\\}', qmd)
b <- which(seq_along(qmd)>a & qmd=='```')[1]
env <- new.env()
env$SCORE_INTEGRATION_ENABLED <- TRUE
env$SCORE_DATA_PATH <- 'cos_score_integration/cos_test_set_phase1_prepared.xlsx'
env$fred_raw <- data.frame(id='control', n_r='123', es_value_r='0.25', statistical_success='control')
eval(parse(text=qmd[(a+1):(b-1)]), envir=env)
stopifnot(nrow(env$fred_raw)==126L, sum(env$fred_raw$score_entry)==125L,
          !any(env$fred_raw$id %in% held_ids),
          env$fred_raw$es_value_r[env$fred_raw$id=='control']=='0.25')
# Restoration is an explicit manifest edit, not a change to source values.
manifest <- read.csv('cos_score_integration/report_references/holds.csv')
manifest$status[1] <- 'released'
tmp <- tempfile(fileext='.csv')
write.csv(manifest, tmp, row.names=FALSE)
restored <- filter_score_report_holds(raw, tmp)
manifest$status[1] <- 'typo'
write.csv(manifest, tmp, row.names=FALSE)
stopifnot(inherits(try(filter_score_report_holds(raw, tmp), silent=TRUE), 'try-error'))
unlink(tmp)
stopifnot(nrow(restored)==126L, manifest$claim_id[1] %in% restored$claim_id)
stopifnot(all(read.csv('cos_score_integration/report_references/holds.csv')$status == 'superseded'))
cat('Seven superseded aggregates verified on both sources and actual integration; retained values unchanged; restoration verified.\n')
