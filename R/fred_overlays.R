library(dplyr)
library(stringr)

# Verified overlays applied to FReD during preparation.
#
# Corrections reach FReD through files under pipelines/fred/overlays/, applied
# here, never by editing output/FReD.xlsx. For now this handles one overlay:
# the chi-squared conversion flags (forrtproject/fred-data#66).

#' Parse APA chi-squared strings as normalised by clean_fred_data().
#' @return data frame with df, n and chi2 (NA when x is not a chi-squared string)
parse_x2 <- function(x) {
  m <- str_match(x, "^X2\\((\\d+(?:\\.\\d+)?)(?:, (?:N = )?(\\d+(?:\\.\\d+)?))?\\) = (\\d*\\.?\\d+)$")
  data.frame(df = as.numeric(m[, 2]), n = as.numeric(m[, 3]), chi2 = as.numeric(m[, 4]))
}

#' Add es_not_convertible_o / es_not_convertible_r from the chi-squared flag file.
#'
#' Only chi2(1) from a contingency table, with N = the units in that table, may be
#' converted to r. The flag file records a reason for every other chi-squared
#' effect (matched on fred_id, side and es_value). Chi-squared effects missing
#' from the file get the automatic rules (df > 1, no N, chi2 / N > 1); a
#' remaining chi2(1) is left unflagged and reported for manual classification.
#'
#' @param data FReD data with fred_id, es_value_o and es_value_r
#' @param flags_file path to x2_conversion_flags.csv
#' @return list(data = data with the two flag columns, report = list of counts)
apply_x2_conversion_flags <- function(data, flags_file) {
  flags <- read.csv(flags_file, colClasses = "character", na.strings = "", encoding = "UTF-8")
  stopifnot(!anyDuplicated(flags[c("fred_id", "side", "es_value")]),
            all(flags$side %in% c("o", "r")),
            all(flags$convertible %in% c("TRUE", "FALSE")),
            all(!is.na(flags$reason[flags$convertible == "FALSE"])))

  report <- list()
  for (s in c("o", "r")) {
    value <- str_squish(as.character(data[[paste0("es_value_", s)]]))
    side_flags <- flags[flags$side == s, ]
    idx <- match(paste(data$fred_id, value, sep = "\r"),
                 paste(side_flags$fred_id, side_flags$es_value, sep = "\r"))
    reason <- ifelse(!is.na(idx) & side_flags$convertible[idx] == "FALSE",
                     side_flags$reason[idx], NA_character_)

    # Chi-squared effects not in the file: automatic rules only
    p <- parse_x2(value)
    new_x2 <- is.na(idx) & !is.na(p$df)
    reason[new_x2 & p$df > 1] <- "chi-squared with df > 1: not a 2 x 2 contingency table"
    reason[new_x2 & p$df == 1 & is.na(p$n)] <- "chi-squared without N"
    reason[new_x2 & p$df == 1 & !is.na(p$n) & p$chi2 / p$n > 1] <-
      "chi-squared / N > 1: cannot come from a 2 x 2 contingency table with N units"
    unclassified <- new_x2 & is.na(reason)

    data[[paste0("es_not_convertible_", s)]] <- reason
    report[[s]] <- list(
      matched = sum(!is.na(idx)),
      flagged = sum(!is.na(reason)),
      new_auto_flagged = sum(new_x2 & !is.na(reason)),
      unclassified = paste(data$fred_id[unclassified], value[unclassified], sep = ": ")
    )
  }
  # Flags that no longer match a row (e.g., after source-sheet edits)
  keys_now <- c(paste("o", data$fred_id, str_squish(data$es_value_o), sep = "\r"),
                paste("r", data$fred_id, str_squish(data$es_value_r), sep = "\r"))
  stale <- flags[!paste(flags$side, flags$fred_id, flags$es_value, sep = "\r") %in% keys_now, ]
  report$stale <- if (nrow(stale) > 0) paste0(stale$fred_id, " (", stale$side, "): ", stale$es_value) else character(0)
  list(data = data, report = report)
}
