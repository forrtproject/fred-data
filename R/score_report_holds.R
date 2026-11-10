# Keep explicitly held SCORE claims in the source archive, outside release data.
filter_score_report_holds <- function(data,
    hold_file = here::here('cos_score_integration', 'report_references', 'holds.csv')) {
  holds <- read.csv(hold_file, stringsAsFactors = FALSE)
  stopifnot(!anyNA(holds$claim_id), all(nzchar(holds$claim_id)),
            !anyDuplicated(holds$claim_id), all(holds$status %in% c('hold', 'released')))
  held_ids <- holds$claim_id[holds$status == 'hold']
  id_columns <- intersect(c('id', 'claim_id', 'fred_id'), names(data))
  if (length(id_columns) == 0L) stop('SCORE data has no claim identity column')
  held <- Reduce(`|`, lapply(data[id_columns], function(x) x %in% held_ids))
  out <- data[!held, , drop = FALSE]
  attr(out, 'held_score_claims') <- data[held, , drop = FALSE]
  out
}
