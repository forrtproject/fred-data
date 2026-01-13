# Generate citation files for FLoRA dataset
# Outputs: output/citation.txt (APA) and CITATION.cff (root)

library(dplyr)
library(googlesheets4)
library(glue)
library(yaml)

# Google Sheets URLs for contributor lists
sheet1_url <- "https://docs.google.com/spreadsheets/d/1NpLZYFO0F-EIwbbP9bLmcvYVZOEIwYxktHgJ3BmVjXA/edit?gid=1455439772#gid=1455439772"
sheet2_url <- "https://docs.google.com/spreadsheets/d/1ioY_RTYQJezb744LFoB6zMRL9YqnSYG9iQv0uGvSDEk/edit?gid=736935521#gid=736935521"

# Read both sheets
gs4_deauth()
contributors1 <- read_sheet(sheet1_url)
contributors2 <- read_sheet(sheet2_url)

# Helper to safely extract numeric from potentially list column
safe_numeric <- function(x) {
  if (is.list(x)) {
    sapply(x, function(el) {
      if (is.null(el) || length(el) == 0) NA_real_
      else as.numeric(el[1])
    })
  } else {
    as.numeric(x)
  }
}

# Standardize column names and select relevant columns
contributors1_clean <- contributors1 |>
  select(
    rank = `Order in publication`,
    given = `First name`,
    middle = `Middle name`,
    family = Surname,
    orcid = `ORCID iD`
  ) |>
  mutate(
    rank = safe_numeric(rank),
    across(where(is.character), as.character)
  )

contributors2_clean <- contributors2 |>
  select(
    rank = `#`,
    given = `First name`,
    middle = `Middle name`,
    family = Surname,
    orcid = `ORCID iD`
  ) |>
  mutate(
    rank = safe_numeric(rank),
    across(where(is.character), as.character)
  )

# Clean up asterisks from names (e.g., "Röseler*" -> "Röseler")
clean_name <- function(x) {
  gsub("\\*$", "", x)
}

# Merge contributors - keep minimum rank for each person
all_contributors <- bind_rows(contributors1_clean, contributors2_clean) |>
  mutate(
    family = clean_name(family),
    given = clean_name(given)
  ) |>
  filter(!is.na(family), !is.na(given)) |>
  group_by(given, family) |>
  summarise(
    rank = min(rank, na.rm = TRUE),
    middle = first(na.omit(middle)),
    orcid = first(na.omit(orcid)),
    .groups = "drop"
  ) |>
  arrange(rank, family, given)

# Identify first authors (Wallrich and Röseler)
first_authors <- all_contributors |>
  filter(
    (family == "Wallrich" & grepl("Lukas", given, ignore.case = TRUE)) |
    (family == "Röseler" & grepl("Lukas", given, ignore.case = TRUE))
  )

# Other authors (excluding the first authors)
other_authors <- all_contributors |>
  filter(
    !(family == "Wallrich" & grepl("Lukas", given, ignore.case = TRUE)),
    !(family == "Röseler" & grepl("Lukas", given, ignore.case = TRUE))
  )

# Current year from Sys.Date
current_year <- format(Sys.Date(), "%Y")
current_date <- format(Sys.Date(), "%Y-%m-%d")

# Format APA author name: "Surname, F. M."
# Uses Unicode-aware approach to handle accented characters (e.g., Patrícia -> P.)
format_apa_author <- function(given, middle = NA, family) {
  # Split given name into parts and take first character of each
  name_parts <- strsplit(given, "\\s+")[[1]]
  given_initials <- paste0(
    sapply(name_parts, function(x) paste0(substr(x, 1, 1), ".")),
    collapse = " "
  )

  # Add middle initial if present
  if (!is.na(middle) && nchar(middle) > 0) {
    middle_initial <- paste0(substr(middle, 1, 1), ".")
    paste0(family, ", ", given_initials, " ", middle_initial)
  } else {
    paste0(family, ", ", given_initials)
  }
}

# Build APA author string - Wallrich first, then Röseler, both with equal contribution marker
wallrich <- first_authors |> filter(family == "Wallrich")
roseler <- first_authors |> filter(family == "Röseler")

apa_first <- paste0(

  format_apa_author(wallrich$given, wallrich$middle, wallrich$family), "*",
  ", & ",
  format_apa_author(roseler$given, roseler$middle, roseler$family), "*"
)

# Format all other authors
other_apa <- other_authors |>
  rowwise() |>
  mutate(apa_name = format_apa_author(given, middle, family)) |>
  pull(apa_name)

# Combine all authors (no truncation)
if (length(other_apa) > 0) {
  apa_authors <- paste0(apa_first, ", ", paste(other_apa, collapse = ", "))
} else {
  apa_authors <- apa_first
}

# Generate APA citation
apa_citation <- glue(
 "{apa_authors} ({current_year}). ",
  "FORRT Library of Replication Attempts (FLoRA) [Data set]. ",
  "OSF. https://doi.org/10.17605/OSF.IO/9R62X"
)

# Add note about equal contribution
apa_full <- paste0(
  apa_citation,
  "\n\n* These authors contributed equally to this work."
)

# Write APA citation to output folder
output_dir <- here::here("output")
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

writeLines(apa_full, file.path(output_dir, "citation.txt"))
message("APA citation written to: ", file.path(output_dir, "citation.txt"))

# Generate CITATION.cff

# Helper to create CFF author entry with ORCID
make_cff_author <- function(given, family, orcid = NA) {
  author <- list(
    `family-names` = family,
    `given-names` = given
  )
  if (!is.na(orcid) && nchar(orcid) > 0) {
    # Ensure ORCID is in proper format (just the ID, not full URL)
    orcid_id <- gsub("https?://orcid\\.org/", "", orcid)
    author$orcid <- paste0("https://orcid.org/", orcid_id)
  }
  author
}

# Build CFF authors list - Wallrich first, then Röseler, then others
cff_authors <- list(
  make_cff_author(wallrich$given, wallrich$family, wallrich$orcid),
  make_cff_author(roseler$given, roseler$family, roseler$orcid)
)

# Add other authors
for (i in seq_len(nrow(other_authors))) {
  cff_authors <- c(cff_authors, list(
    make_cff_author(
      other_authors$given[i],
      other_authors$family[i],
      other_authors$orcid[i]
    )
  ))
}

cff_content <- list(
  `cff-version` = "1.2.0",
  message = "If you use this dataset, please cite it using the metadata from this file.",
  type = "dataset",
  title = "FORRT Library of Replication Attempts (FLoRA)",
  authors = cff_authors,
  `date-released` = current_date,
  version = "1.0.0",
  doi = "10.17605/OSF.IO/9R62X",
  license = "CC-BY-4.0",
  repository = "https://osf.io/9r62x/",
  url = "https://osf.io/9r62x/",
  abstract = "A comprehensive database of replication studies in the social and behavioural sciences.",
  keywords = c("replication", "reproducibility", "meta-science", "open science")
)

# Write CITATION.cff to root
cff_path <- here::here("CITATION.cff")
yaml::write_yaml(cff_content, cff_path)

message("CITATION.cff written to: ", cff_path)

message("\n--- Generated APA Citation ---\n")
cat(apa_full)
message("\n\n--- CITATION.cff generated successfully ---")
