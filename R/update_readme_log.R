#!/usr/bin/env Rscript
# update_readme_log.R
# Updates the Flora Dataset chart in README.md after each pipeline run.
# The chart shows 3 lines over time: total rows, replications, reproductions.
#
# Usage:
#   Rscript R/update_readme_log.R <flora_csv_path> <readme_path>
#
# Arguments:
#   flora_csv_path - Path to the new flora.csv (default: output/flora.csv)
#   readme_path    - Path to README.md (default: README.md)

args <- commandArgs(trailingOnly = TRUE)

flora_path  <- if (length(args) >= 1) args[1] else file.path("output", "flora.csv")
readme_path <- if (length(args) >= 2) args[2] else "README.md"

START_MARKER <- "<!-- FLORA_UPDATE_LOG_START -->"
END_MARKER   <- "<!-- FLORA_UPDATE_LOG_END -->"

# ── Read new flora.csv ──────────────────────────────────────────────────────
if (!file.exists(flora_path)) {
  stop(sprintf("flora.csv not found at: %s", flora_path))
}

flora    <- read.csv(flora_path, check.names = FALSE)
new_rows <- nrow(flora)
date_str <- strftime(Sys.time(), "%Y-%m-%d", tz = "UTC")

# Breakdown by type (replication / reproduction)
replication_count  <- 0L
reproduction_count <- 0L
if ("type" %in% names(flora)) {
  counts             <- table(flora$type, useNA = "no")
  replication_count  <- if ("replication"  %in% names(counts)) as.integer(counts["replication"])  else 0L
  reproduction_count <- if ("reproduction" %in% names(counts)) as.integer(counts["reproduction"]) else 0L
}

cat(sprintf("Date        : %s\n", date_str))
cat(sprintf("Total       : %d\n", new_rows))
cat(sprintf("Replications: %d\n", replication_count))
cat(sprintf("Reproductions: %d\n", reproduction_count))

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

# ── Parse existing chart data between markers ────────────────────────────────
section      <- readme[(start_line + 1):(end_line - 1)]
section_text <- paste(section, collapse = "\n")

# Extract the bracketed content for a named pattern (first capture group).
extract_bracket_content <- function(text, pattern) {
  m <- regexec(pattern, text, perl = TRUE)
  hits <- regmatches(text, m)[[1]]
  if (length(hits) < 2 || !nzchar(hits[2])) return(character(0))
  hits[2]
}

parse_quoted_list <- function(text) {
  raw <- extract_bracket_content(text, '(?s)x-axis\\s*\\[([^\\]]*)\\]')
  if (!length(raw)) return(character(0))
  gsub('"', "", trimws(strsplit(raw, ",")[[1]]))
}

parse_numeric_list_named <- function(text, line_name) {
  pattern <- sprintf('(?s)line\\s+"%s"\\s*\\[([^\\]]*)\\]', line_name)
  raw <- extract_bracket_content(text, pattern)
  if (!length(raw)) return(integer(0))
  as.integer(trimws(strsplit(raw, ",")[[1]]))
}

parse_numeric_list_positional <- function(text, position) {
  hits <- regmatches(text, gregexpr('line\\s+\\[([^\\]]*)\\]', text, perl = TRUE))[[1]]
  if (length(hits) < position) return(integer(0))
  inner <- sub('.*?\\[([^\\]]*)\\].*', '\\1', hits[[position]], perl = TRUE)
  as.integer(trimws(strsplit(inner, ",")[[1]]))
}

# Try named format first (backward compat), then positional
parse_numeric_list <- function(text, line_name, position) {
  result <- parse_numeric_list_named(text, line_name)
  if (!length(result)) result <- parse_numeric_list_positional(text, position)
  result
}

existing_dates  <- parse_quoted_list(section_text)
existing_total  <- parse_numeric_list(section_text, "Total", 1)
existing_replic <- parse_numeric_list(section_text, "Replications", 2)
existing_reprod <- parse_numeric_list(section_text, "Reproductions", 3)

# ── Append or replace today's entry ─────────────────────────────────────────
# If today's date already appears as the last entry, update it in-place.
if (length(existing_dates) > 0 && tail(existing_dates, 1) == date_str) {
  n <- length(existing_dates)
  existing_total[n]  <- new_rows
  existing_replic[n] <- replication_count
  existing_reprod[n] <- reproduction_count
} else {
  existing_dates  <- c(existing_dates, date_str)
  existing_total  <- c(existing_total,  new_rows)
  existing_replic <- c(existing_replic, replication_count)
  existing_reprod <- c(existing_reprod, reproduction_count)
}

# ── Build updated Mermaid chart ──────────────────────────────────────────────
fmt_str_list <- function(vals) paste0("[", paste(sprintf('"%s"', vals), collapse = ", "), "]")
fmt_int_list <- function(vals) paste0("[", paste(as.integer(vals), collapse = ", "), "]")

new_chart <- c(
  "```mermaid",
  "xychart-beta",
  '    title "FLoRA Dataset Size Over Time (Total / Replications / Reproductions)"',
  sprintf("    x-axis %s", fmt_str_list(existing_dates)),
  sprintf("    line %s", fmt_int_list(existing_total)),
  sprintf("    line %s", fmt_int_list(existing_replic)),
  sprintf("    line %s", fmt_int_list(existing_reprod)),
  "```",
  "",
  sprintf("> **Latest (%s):** Total = %d | Replications = %d | Reproductions = %d",
          tail(existing_dates, 1), tail(existing_total, 1),
          tail(existing_replic, 1), tail(existing_reprod, 1))
)

# ── Write updated README ─────────────────────────────────────────────────────
readme_updated <- c(
  readme[seq_len(start_line)],
  new_chart,
  readme[end_line:length(readme)]
)

writeLines(readme_updated, readme_path)
cat(sprintf("✓ README.md chart updated for %s (total=%d, repl=%d, repr=%d)\n",
            date_str, new_rows, replication_count, reproduction_count))
