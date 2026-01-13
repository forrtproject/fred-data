#!/usr/bin/env Rscript
library(readxl)

files_to_check <- c(
  'crossref_retrieved_authors.xlsx',
  'crossref_author_overlap.xlsx'
)

for (filename in files_to_check) {
  if (file.exists(filename)) {
    cat(sprintf("\n%s:\n", filename))
    cat(sprintf("  File size: %.1f KB\n", file.size(filename) / 1024))

    tryCatch({
      df <- read_excel(filename)
      cat(sprintf("  Rows: %d, Columns: %d\n", nrow(df), ncol(df)))
      cat(sprintf("  Column names: %s\n", paste(names(df), collapse=", ")))

      if (nrow(df) > 0) {
        cat(sprintf("  First row of data:\n"))
        for (col in 1:ncol(df)) {
          val <- df[1, col, drop=TRUE]
          if (is.character(val) && nchar(val) > 100) {
            cat(sprintf("    %s: %s...\n", names(df)[col], substr(val, 1, 100)))
          } else {
            cat(sprintf("    %s: %s\n", names(df)[col], val))
          }
        }
      }
    }, error = function(e) {
      cat(sprintf("  Error: %s\n", e$message))
    })
  } else {
    cat(sprintf("\n%s: File not found\n", filename))
  }
}
