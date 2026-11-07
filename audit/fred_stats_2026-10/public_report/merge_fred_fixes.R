# FReD statistics audit, frozen b48a7d6 snapshot, 30 October 2026.
# Source this file for the in-memory function, or run the command-line example below.
# install.packages(c("readxl", "writexl", "digest"))  # once, if needed
# Rscript merge_fred_fixes.R FReD.xlsx FReD_corrected.xlsx
# Keep fred_fixes.csv and row_guard.csv beside this script.

FRED_INPUT_SHA256 <- "59545e3fc0c2979d97507097526319ec8c275aae3ac40c0d1a6d327492079e6b"
FRED_FIX_SHA256 <- "6ef958334e4769f88827641a96238a1c7effd9046f201ac524d792f344cb3ee1"
FRED_GUARD_SHA256 <- "39a04f53140949884b92a63c9914f48fdc4860e6c71e444323990cef47fb090e"

.fred_text <- function(x) {
  x <- as.character(x)
  x[is.na(x)] <- ""
  trimws(gsub("\r\n", "\n", x, fixed = TRUE))
}
.fred_key <- function(x) {
  do.call(paste, c(lapply(x[c("entry_id", "effect_id", "fred_id")], .fred_text),
                   sep = "\037"))
}
.fred_read_csv <- function(path) {
  read.csv(path, colClasses = "character", na.strings = character(),
           check.names = FALSE, fileEncoding = "UTF-8-BOM", comment.char = "")
}
.fred_check_hash <- function(path, expected) {
  if (!requireNamespace("digest", quietly = TRUE)) stop("Install the digest package.")
  if (!file.exists(path) || digest::digest(file = path, algo = "sha256") != expected)
    stop("Missing or changed audit download: ", path, call. = FALSE)
}

# Check every target before changing any value. Returns a copy and a cell-level log.
# fred may be reordered, but the three-part key and all protected target descriptions,
# references, studies, metrics, nesting and tails must match the audited records.
# All fields being changed must contain the expected old OR already-patched value.
# Unchanged columns, rows, ordering and column types are retained. Statistical fields
# in the frozen workbook are character columns, preserving bounds and printed strings.
apply_fred_fixes <- function(fred, fix_file = "fred_fixes.csv", guard_file = "row_guard.csv") {
  .fred_check_hash(fix_file, FRED_FIX_SHA256)
  .fred_check_hash(guard_file, FRED_GUARD_SHA256)
  fixes <- .fred_read_csv(fix_file)
  guards <- .fred_read_csv(guard_file)
  if (!is.data.frame(fred) || nrow(fred) != 2164L || anyDuplicated(names(fred)))
    stop("Expected the audited 2,164-row FReD data frame with unique column names.")
  required <- unique(c(names(guards), fixes$target_column))
  if (!all(required %in% names(fred))) stop("Required FReD columns are missing.")
  keys <- .fred_key(fred)
  if (anyDuplicated(keys) || any(.fred_text(fred$effect_id) == ""))
    stop("Missing or duplicate FReD record keys.")
  guard_rows <- match(.fred_key(guards), keys)
  if (anyNA(guard_rows)) stop("Audited record keys are absent; do not join by row number or fred_id alone.")
  for (column in names(guards)) {
    different <- .fred_text(fred[[column]][guard_rows]) != .fred_text(guards[[column]])
    if (any(different)) stop("Target identity conflict in ", column, "; effect_id ",
                            guards$effect_id[which(different)[1]], ". No fixes applied.")
  }
  target_rows <- match(.fred_key(fixes), keys)
  if (anyNA(target_rows) || anyDuplicated(paste(.fred_key(fixes), fixes$target_column)))
    stop("Missing or duplicate patch targets.")
  old <- new <- logical(nrow(fixes))
  for (i in seq_len(nrow(fixes))) {
    current <- .fred_text(fred[[fixes$target_column[i]]][target_rows[i]])
    old[i] <- current == .fred_text(fixes$old_value[i])
    new[i] <- current == .fred_text(fixes$new_value[i])
  }
  bad <- which(!old & !new)
  if (length(bad)) stop("Value conflict at effect_id ", fixes$effect_id[bad[1]],
                       ", column ", fixes$target_column[bad[1]], ". No fixes applied.")
  # Reject type-incompatible writes during preflight, before editing the copy.
  for (i in which(!new)) {
    column <- fred[[fixes$target_column[i]]]
    if (is.factor(column) || (!is.character(column) && !is.numeric(column)))
      stop("Unsupported target-column type: ", fixes$target_column[i])
    if (is.numeric(column) && !is.finite(suppressWarnings(as.numeric(fixes$new_value[i]))))
      stop("A text correction cannot be written into a numeric target column.")
  }
  corrected <- fred
  for (i in which(!new)) {
    column <- fixes$target_column[i]
    value <- fixes$new_value[i]
    if (is.numeric(corrected[[column]])) value <- as.numeric(value)
    corrected[[column]][target_rows[i]] <- value
  }
  log <- fixes
  log$status <- ifelse(new, "already_applied", "applied")
  list(data = corrected, changes = log,
       summary = c(confirmed_field_errors = 493L, affected_rows = 381L,
                   physical_cells_applied = sum(!new), already_applied = sum(new)))
}

.fred_cli <- function(args) {
  if (length(args) != 2L) stop("Usage: Rscript merge_fred_fixes.R FReD.xlsx FReD_corrected.xlsx")
  for (package in c("readxl", "writexl", "digest"))
    if (!requireNamespace(package, quietly = TRUE)) stop("Install package: ", package)
  input <- normalizePath(args[1], mustWork = TRUE)
  output <- normalizePath(args[2], mustWork = FALSE)
  if (input == output || file.exists(output)) stop("Choose a NEW output path; existing files are never overwritten.")
  if (!grepl("\\.xlsx$", output, ignore.case = TRUE)) stop("The output must end in .xlsx.")
  .fred_check_hash(input, FRED_INPUT_SHA256)
  script_arg <- grep("^--file=", commandArgs(), value = TRUE)
  directory <- dirname(normalizePath(sub("^--file=", "", script_arg[1]), mustWork = TRUE))
  fred <- readxl::read_xlsx(input, trim_ws = FALSE)
  result <- apply_fred_fixes(fred, file.path(directory, "fred_fixes.csv"), file.path(directory, "row_guard.csv"))
  log_path <- paste0(tools::file_path_sans_ext(output), "_changes.csv")
  if (file.exists(log_path)) stop("The change-log path already exists: ", log_path)
  # Write beside the destination, then rename; no write targets the input workbook.
  temporary <- tempfile("fred-fixed-", tmpdir = dirname(output), fileext = ".xlsx")
  on.exit(unlink(temporary), add = TRUE)
  writexl::write_xlsx(result$data, temporary)
  if (!file.rename(temporary, output)) stop("Could not move the completed workbook to its new output path.")
  write.csv(result$changes, log_path, row.names = FALSE, na = "", fileEncoding = "UTF-8")
  cat("Wrote", output, "and", log_path, "\n")
  print(result$summary)
}
if (sys.nframe() == 0L) .fred_cli(commandArgs(trailingOnly = TRUE))
