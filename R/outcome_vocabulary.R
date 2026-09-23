# Canonical outcome vocabulary for FLoRA and FReD
#
# FLoRA (`outcome`) and FReD (`reported_success`) draw on the same set of coding
# sheets, but each sheet has drifted slightly in how it spells the codes
# (underscores vs spaces, "descriptive" vs "descriptive only", "unclear" vs
# "uninformative", legacy "success"/"failure"). Left unnormalised, the variants
# survive into the released datasets and — worse — make `pick_outcome()` in
# preprint_dedup.R treat a spelling difference as a genuine outcome clash,
# producing concatenated values like "successful || success".
#
# This file is the single source of truth for the allowed values. Both pipelines
# normalise against it at ingest; validate_flora.R validates against it.

# --- Allowed values -------------------------------------------------------

VALID_REPLICATION_OUTCOMES <- c(
  "successful",
  "failed",
  "mixed",
  "uninformative",
  "descriptive only",
  "statistically successful but flawed"
)

# Reproductions are coded on two axes (computational reproducibility and
# robustness) — the reproductions sheet keeps them in separate columns, and
# combine_reproduction_outcome() joins them into one "<computational>,
# <robustness>" label for the single `outcome` column. The axis wording follows
# the coding sheet ("computationally reproducible"); "not checked" is qualified
# with its axis so the combined label is unambiguous.
VALID_REPRODUCTION_OUTCOMES <- c(
  "computationally reproducible, robust",
  "computationally reproducible, robustness challenges",
  "computationally reproducible, robustness not checked",
  "computational issues, robust",
  "computational issues, robustness challenges",
  "computational issues, robustness not checked",
  "computation not checked, robust",
  "computation not checked, robustness challenges",
  "computation not checked, robustness not checked"
)

VALID_OUTCOMES <- c(VALID_REPLICATION_OUTCOMES, VALID_REPRODUCTION_OUTCOMES)

# Separator used to retain a genuine clash between different outcomes on rows
# that are merged during preprint deduplication. Such values are deliberately
# NOT in VALID_OUTCOMES, so validate_flora.R's outcome check surfaces them.
OUTCOME_CLASH_SEP <- " || "

# --- Aliases --------------------------------------------------------------
# Keys are match-normalised (lowercase, underscores and punctuation runs
# collapsed to single spaces). Only variants actually observed in the source
# sheets or in previously released data are listed — an unrecognised value is
# passed through untouched so validation flags it rather than silently
# absorbing it into the wrong category.

OUTCOME_ALIASES <- c(
  # replications sheet
  "statistically successful but fundamentally flawed" = "statistically successful but flawed",
  "statistically successful but flawed"               = "statistically successful but flawed",
  # NB: "unclear" and "cannot be determined" are deliberately NOT aliased to
  # "uninformative" — they mean something different (the coder could not reach a
  # verdict, vs. the study being unable to inform the claim). They stay
  # unmapped so validate_flora.R flags them for re-coding at source.
  # validated_export (i4r / openalex imports)
  "descriptive"                                       = "descriptive only",
  # legacy vocabulary from pre-2026 imports
  "success"                                           = "successful",
  "failure"                                           = "failed",
  "successful replication"                            = "successful",
  "failed replication"                                = "failed",
  "mixed results"                                     = "mixed"
)

# Per-axis aliases for reproduction outcomes, keyed like OUTCOME_ALIASES. Used
# both to combine the reproductions sheet's two columns and to canonicalise
# already-combined labels from other sources (e.g. the validated export's
# "computational issues, not checked").
REPRO_COMPUTATIONAL_ALIASES <- c(
  "computationally reproducible" = "computationally reproducible",
  "computationally successful"   = "computationally reproducible",
  "computational issues"         = "computational issues",
  "computation not checked"      = "computation not checked",
  "not checked"                  = "computation not checked"
)

REPRO_ROBUSTNESS_ALIASES <- c(
  "robust"                 = "robust",
  "robustness challenges"  = "robustness challenges",
  "robustness not checked" = "robustness not checked",
  "not checked"            = "robustness not checked"
)

#' Match-normalise an outcome string for alias lookup.
#'
#' Lowercases, turns underscores/hyphens into spaces, and squishes whitespace.
#' Commas are preserved because the reproduction codes are comma-delimited
#' two-part labels (e.g. "computational issues, robust").
match_key <- function(x) {
  x <- tolower(trimws(as.character(x)))
  x <- gsub("[_\\-]+", " ", x)
  x <- gsub("\\s+", " ", x)
  trimws(x)
}

#' Canonicalise a combined "<computational>, <robustness>" reproduction label.
#'
#' @param keys Match-normalised labels (see match_key()).
#' @return The canonical label where both axes are recognised, else NA.
canonical_reproduction_label <- function(keys) {
  vapply(keys, function(k) {
    axes <- trimws(strsplit(k, ",", fixed = TRUE)[[1]])
    if (length(axes) != 2) return(NA_character_)
    comp <- REPRO_COMPUTATIONAL_ALIASES[axes[1]]
    rob  <- REPRO_ROBUSTNESS_ALIASES[axes[2]]
    if (is.na(comp) || is.na(rob)) return(NA_character_)
    paste(comp, rob, sep = ", ")
  }, character(1), USE.NAMES = FALSE)
}

#' Combine the reproductions sheet's two outcome axes into one outcome label.
#'
#' Each axis is mapped onto its canonical wording. A blank axis on a row whose
#' other axis is coded counts as "not checked"; a row with both axes blank gets
#' NA. An unrecognised axis value (e.g. "technical failure") is kept verbatim so
#' validate_flora.R flags the combined label for re-coding at source.
#'
#' @param computational,robustness Character vectors of raw axis values.
#' @return Character vector of combined labels.
combine_reproduction_outcome <- function(computational, robustness) {
  canon_axis <- function(x, aliases) {
    x <- trimws(as.character(x))
    key <- match_key(x)
    out <- ifelse(key %in% names(aliases), unname(aliases[key]), x)
    ifelse(is.na(x) | !nzchar(x), NA_character_, out)
  }
  comp <- canon_axis(computational, REPRO_COMPUTATIONAL_ALIASES)
  rob  <- canon_axis(robustness, REPRO_ROBUSTNESS_ALIASES)
  ifelse(
    is.na(comp) & is.na(rob), NA_character_,
    paste(ifelse(is.na(comp), "computation not checked", comp),
          ifelse(is.na(rob), "robustness not checked", rob),
          sep = ", ")
  )
}

#' Combine per-axis quote (or quote-source) columns into one string.
#'
#' Identical non-empty values collapse to one unlabelled value; otherwise each
#' non-empty value is prefixed with its axis and joined with OUTCOME_CLASH_SEP,
#' matching how the pipelines join multiple quotes elsewhere.
combine_reproduction_quotes <- function(computational, robustness) {
  clean <- function(x) {
    x <- trimws(as.character(x))
    ifelse(is.na(x) | !nzchar(x), NA_character_, x)
  }
  comp <- clean(computational)
  rob  <- clean(robustness)
  ifelse(
    is.na(comp) & is.na(rob), NA_character_,
    ifelse(!is.na(comp) & !is.na(rob) & comp == rob, comp,
    ifelse(is.na(rob), paste0("Computational: ", comp),
    ifelse(is.na(comp), paste0("Robustness: ", rob),
           paste0("Computational: ", comp, OUTCOME_CLASH_SEP, "Robustness: ", rob))))
  )
}

#' Recode outcome values onto the canonical vocabulary.
#'
#' Handles clash values produced by preprint deduplication ("A || B") by
#' normalising each component: if the components collapse to a single canonical
#' value the clash disappears, otherwise it is retained for validation to pick
#' up.
#'
#' @param x Character vector of raw outcome values.
#' @return Character vector of the same length. Values with no known canonical
#'   form are returned trimmed but otherwise unchanged.
normalise_outcome <- function(x) {
  x <- as.character(x)
  out <- vapply(x, function(v) {
    if (is.na(v)) return(NA_character_)
    v <- trimws(v)
    if (!nzchar(v)) return(NA_character_)

    parts <- trimws(strsplit(v, OUTCOME_CLASH_SEP, fixed = TRUE)[[1]])
    parts <- parts[nzchar(parts)]
    if (length(parts) == 0) return(NA_character_)

    keys <- match_key(parts)
    repro <- canonical_reproduction_label(keys)
    canonical <- ifelse(
      keys %in% names(OUTCOME_ALIASES), OUTCOME_ALIASES[keys],
      ifelse(keys %in% match_key(VALID_OUTCOMES),
             VALID_OUTCOMES[match(keys, match_key(VALID_OUTCOMES))],
             ifelse(!is.na(repro), repro, parts))
    )
    canonical <- unique(unname(canonical))
    paste(canonical, collapse = OUTCOME_CLASH_SEP)
  }, character(1), USE.NAMES = FALSE)
  out
}

#' Report how many values a normalisation pass changed, and to what.
#'
#' Returns a data frame of from/to/n for logging in the pipelines.
outcome_recode_summary <- function(before, after) {
  changed <- !is.na(before) & (is.na(after) | before != after)
  if (!any(changed)) {
    return(data.frame(from = character(), to = character(), n = integer()))
  }
  tab <- table(before[changed], after[changed])
  idx <- which(tab > 0, arr.ind = TRUE)
  data.frame(
    from = rownames(tab)[idx[, "row"]],
    to   = colnames(tab)[idx[, "col"]],
    n    = as.integer(tab[idx]),
    stringsAsFactors = FALSE
  )
}
