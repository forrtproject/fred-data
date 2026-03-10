#!/usr/bin/env Rscript
# update_readme_log.R
# Updates the Flora Dataset Update Log table in README.md after each pipeline run.
#
# Usage:
#   Rscript R/update_readme_log.R <old_rows> <flora_csv_path> <readme_path>
#
# Arguments:
#   old_rows       - Row count of flora.csv before this pipeline run
#   flora_csv_path - Path to the new flora.csv (default: output/flora.csv)
#   readme_path    - Path to README.md (default: README.md)

args <- commandArgs(trailingOnly = TRUE)

if (length(args) >= 1) {
  old_rows <- as.integer(args[1])
  if (is.na(old_rows)) {
    stop(sprintf("old_rows argument must be an integer; got: %s", args[1]))
  }
} else {
  stop("old_rows argument is required")
}
flora_path   <- if (length(args) >= 2) args[2] else file.path("output", "flora.csv")
readme_path  <- if (length(args) >= 3) args[3] else "README.md"

START_MARKER <- "<!-- FLORA_UPDATE_LOG_START -->"
END_MARKER   <- "<!-- FLORA_UPDATE_LOG_END -->"

# ── Read new flora.csv ──────────────────────────────────────────────────────
if (!file.exists(flora_path)) {
  stop(sprintf("flora.csv not found at: %s", flora_path))
}

flora <- read.csv(flora_path, check.names = FALSE)
new_rows <- nrow(flora)

# ── Compute stats ───────────────────────────────────────────────────────────
diff       <- new_rows - old_rows
change_str <- if (diff > 0) paste0("+", diff) else as.character(diff)
date_str   <- strftime(Sys.time(), "%Y-%m-%d", tz = "UTC")

# Breakdown by type (replication / reproduction) if column exists
type_breakdown <- ""
if ("type" %in% names(flora)) {
  counts <- table(flora$type, useNA = "no")
  parts  <- paste(names(counts), counts, sep = ": ", collapse = "; ")
  type_breakdown <- parts
}

cat(sprintf("Old rows: %d\n", old_rows))
cat(sprintf("New rows: %d\n", new_rows))
cat(sprintf("Change  : %s\n", change_str))
if (nzchar(type_breakdown)) cat(sprintf("By type : %s\n", type_breakdown))

# ── Build new table row ──────────────────────────────────────────────────────
type_col <- if (nzchar(type_breakdown)) type_breakdown else "-"
new_row  <- sprintf("| %s | %d | %d | %s | %s |", date_str, old_rows, new_rows, change_str, type_col)

# ── Read README ──────────────────────────────────────────────────────────────
if (!file.exists(readme_path)) {
  stop(sprintf("README.md not found at: %s", readme_path))
}

readme <- readLines(readme_path, warn = FALSE)

start_line <- which(readme == START_MARKER)
end_line   <- which(readme == END_MARKER)

if (length(start_line) != 1 || length(end_line) != 1) {
  stop(sprintf(
    "Could not locate update log markers in README.md.\nExpected exactly one '%s' and one '%s'.",
    START_MARKER, END_MARKER
  ))
}

if (start_line >= end_line) {
  stop("START marker must appear before END marker in README.md")
}

# Insert new row just after the table header separator (most-recent-first ordering)
# within the marker-bounded section, so the row remains part of the table even if
# the markers are moved outside the table header.

# Find the table header separator line (e.g., "| --- | --- |") between the markers.
header_sep_line <- NA_integer_
for (i in seq(from = start_line + 1, to = end_line - 1)) {
  if (grepl("^\\s*\\|\\s*:?-{3,}:?\\s*(\\|\\s*:?-{3,}:?\\s*)*\\|?\\s*$", readme[i])) {
    header_sep_line <- i
    break
  }
}

# If a header separator was found, insert after it; otherwise fall back to after START_MARKER.
insert_after_line <- if (!is.na(header_sep_line)) header_sep_line else start_line

readme_updated <- c(
  readme[1:insert_after_line],
  new_row,
  readme[(insert_after_line + 1):length(readme)]
)

writeLines(readme_updated, readme_path)
cat(sprintf("✓ README.md updated with new log row: %s\n", new_row))
