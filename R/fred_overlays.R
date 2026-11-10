library(dplyr)
library(stringr)

# Verified overlays applied to FReD during preparation.
#
# Source rows in the FReD Google Sheet that existed on 2026-11-10 are locked.
# Corrections and classifications reach FReD through files under
# pipelines/fred/overlays/, keyed on the permanent effect_uid (sheet column BO;
# SCORE rows use "score_<id>"), and are re-applied on every build. They are never
# made by editing the sheet or output/FReD.xlsx.
#
# Each overlay row stores the value it was judged against. If the current value
# differs, the overlay still applies and the build lists the effect for re-checking.
#
# For now this handles one overlay: the chi-squared conversion flags
# (forrtproject/fred-data#66).

#' Parse APA chi-squared strings as normalised by clean_fred_data().
#' @return data frame with df, n and chi2 (NA when x is not a chi-squared string)
parse_x2 <- function(x) {
  m <- str_match(x, "^X2\\((\\d+(?:\\.\\d+)?)(?:, (?:N = )?(\\d+(?:\\.\\d+)?))?\\) = (\\d*\\.?\\d+)$")
  data.frame(df = as.numeric(m[, 2]), n = as.numeric(m[, 3]), chi2 = as.numeric(m[, 4]))
}

#' Add es_not_convertible_o / es_not_convertible_r from the chi-squared flag file.
#'
#' Only chi2(1) from a contingency table, with N = the units in that table, may be
#' converted to r. The flag file holds one classification per effect_uid and side,
#' with a reason for every chi-squared that must not be converted. Chi-squared
#' effects missing from the file get the automatic rules (df > 1, no N,
#' chi2 / N > 1); a remaining chi2(1) is left unflagged and reported so that a
#' row can be added to the file.
#'
#' @param data FReD data with effect_uid, es_value_o and es_value_r
#' @param flags_file path to x2_conversion_flags.csv
#' @return list(data = data with the two flag columns, report = list of counts)
apply_x2_conversion_flags <- function(data, flags_file) {
  flags <- read.csv(flags_file, colClasses = "character", na.strings = "", encoding = "UTF-8")
  stopifnot(!anyDuplicated(flags[c("effect_uid", "side")]),
            all(flags$side %in% c("o", "r")),
            all(flags$convertible %in% c("TRUE", "FALSE")),
            all(!is.na(flags$reason[flags$convertible == "FALSE"])))
  uids <- data$effect_uid[!is.na(data$effect_uid)]
  if (anyDuplicated(uids)) stop("effect_uid must be unique before overlays are applied.")

  report <- list()
  for (s in c("o", "r")) {
    value <- str_squish(as.character(data[[paste0("es_value_", s)]]))
    side_flags <- flags[flags$side == s, ]
    idx <- match(data$effect_uid, side_flags$effect_uid)
    reason <- ifelse(!is.na(idx) & side_flags$convertible[idx] == "FALSE",
                     side_flags$reason[idx], NA_character_)

    # Value changed since it was classified: keep the flag, ask for a re-check
    changed <- !is.na(idx) & value != side_flags$judged_es_value[idx]
    changed[is.na(changed)] <- TRUE

    # Chi-squared effects not in the file: automatic rules only
    p <- parse_x2(value)
    new_x2 <- is.na(idx) & !is.na(p$df)
    reason[new_x2 & p$df > 1] <- "chi-squared with df > 1: not a 2 x 2 contingency table"
    reason[new_x2 & p$df == 1 & is.na(p$n)] <- "chi-squared without N"
    reason[new_x2 & p$df == 1 & !is.na(p$n) & p$chi2 / p$n > 1] <-
      "chi-squared / N > 1: cannot come from a 2 x 2 contingency table with N units"
    unclassified <- new_x2 & is.na(reason)

    data[[paste0("es_not_convertible_", s)]] <- reason
    describe <- function(i) {
      if (length(i) == 0) return(character(0))
      paste0(data$effect_uid[i], " (", data$fred_id[i], "): ", value[i])
    }
    report[[s]] <- list(
      matched = sum(!is.na(idx)),
      flagged = sum(!is.na(reason)),
      new_auto_flagged = sum(new_x2 & !is.na(reason)),
      unclassified = describe(which(unclassified)),
      changed = describe(which(changed & !is.na(idx)))
    )
  }
  # Flags whose effect is no longer in the data (e.g., status changed in the sheet)
  missing <- flags[!flags$effect_uid %in% data$effect_uid, ]
  report$missing <- if (nrow(missing) > 0) paste0(missing$effect_uid, " (", missing$side, ")") else character(0)
  list(data = data, report = report)
}
