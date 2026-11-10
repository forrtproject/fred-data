# Keep held or superseded SCORE claims in the source archive, outside release data.
# 'superseded': the pooled row is replaced by separate rows for its individual
# attempts, so releasing it would count the same participants twice.
filter_score_report_holds <- function(data,
    hold_file = here::here('cos_score_integration', 'report_references', 'holds.csv')) {
  holds <- read.csv(hold_file, stringsAsFactors = FALSE)
  stopifnot(!anyNA(holds$claim_id), all(nzchar(holds$claim_id)),
            !anyDuplicated(holds$claim_id),
            all(holds$status %in% c('hold', 'superseded', 'released')))
  held_ids <- holds$claim_id[holds$status %in% c('hold', 'superseded')]
  id_columns <- intersect(c('id', 'claim_id', 'fred_id'), names(data))
  if (length(id_columns) == 0L) stop('SCORE data has no claim identity column')
  held <- Reduce(`|`, lapply(data[id_columns], function(x) x %in% held_ids))
  out <- data[!held, , drop = FALSE]
  attr(out, 'held_score_claims') <- data[held, , drop = FALSE]
  out
}
