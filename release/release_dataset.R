library(stringr)
library(dplyr)
library(glue)
library(osfr)

# --------------------
# Parameters
# - `dataset`: which dataset to release, either "fred" or "flora"
# - `github_raw_urls`: named list of raw GitHub URLs for each dataset
# - `filenames`: target filenames as they appear on OSF for each dataset
# - `osf_folder_map`: named list mapping dataset -> OSF folder name (direct child of project)
# - `osf_project` and `osf_token`: OSF project id and token
# --------------------
params <- list(
  github_raw_urls = list(
Test text    fred = "https://raw.githubusercontent.com/<user>/<fred-repo>/<branch>/path/to/FReD.xlsx",
    flora = "https://raw.githubusercontent.com/<user>/<flora-repo>/<branch>/path/to/flora.csv"
  ),
  filenames = list(
    fred = "FReD.xlsx",
    flora = "flora.csv"
  ),
  osf_folder_map = list(
    fred = "0 Data",
    flora = "0 Data/Flora"
  ),
  osf_project = "9r62x",
  osf_token = Sys.getenv("OSF_TOKEN")
)

## Download and upload file
process_excel_file <- function(data_folder,
                               old_version,
                               github_raw_url = NULL,
                               filename = "FReD.xlsx",
                               keep_sheets = c("Data", "FORRT R&R (editable)", "Additional Studies to be added", "Contributors FReD", "key variables"),
                               ...) {

  # Find archive folder and current data file on OSF
  archive_folder <- osfr::osf_ls_files(data_folder, type = "folder") %>%
    dplyr::filter(name == "Archive")

  data_file <- osfr::osf_ls_files(data_folder) %>%
    dplyr::filter(name == filename)

  temp_dir <- tempdir()

  # Download the existing file from OSF for archiving
  osfr::osf_download(data_file, temp_dir, conflicts = "overwrite")

  # compute archive name (preserve extension)
  archived_name <- glue("{tools::file_path_sans_ext(filename)}_{old_version}.{tools::file_ext(filename)}")
  file.rename(file.path(temp_dir, filename), file.path(temp_dir, archived_name))

  # If a GitHub raw URL is provided, download that file and upload it directly.
  if (!is.null(github_raw_url)) {
    dest <- file.path(temp_dir, filename)
    download.file(github_raw_url, dest, mode = "wb")
  } else {
    # Fallback: original Google Sheets behaviour
    f <- file.path(temp_dir, filename)
    # download from previously configured Google Sheets link (expect caller to pass it via ...)
    gsheet_link <- list(...)[["gsheet_link"]]
    if (is.null(gsheet_link)) stop("No source specified: provide 'github_raw_url' or 'gsheet_link'.")
    download.file(gsheet_link, f, mode = "wb")

    dat <- try(openxlsx::read.xlsx(f, sheet = 1))
    if (inherits(dat, "try-error")) {
      download.file(gsheet_link, f, mode = "wb")
      dat <- try(openxlsx::read.xlsx(f, sheet = 1))
      if (inherits(dat, "try-error")) {
        stop("Error reading the new data file. Please check the status of the download link and try again.")
      }
      message("Google Sheets download initially failed. Second attempt succeeded, but please check result.")
    }

    wb <- openxlsx::loadWorkbook(f)
    all_sheets <- openxlsx::getSheetNames(f)

    if (setdiff(keep_sheets, all_sheets) |> length() > 0) {
      warning("The following sheets could not be found and will be missing from released dataset ", 
              paste(setdiff(keep_sheets, all_sheets), collapse = ", "))
    } 

    sheets_to_remove <- setdiff(all_sheets, keep_sheets)
    if (length(sheets_to_remove) > 0) {
      for(sheet_name in sheets_to_remove) {
        openxlsx::removeWorksheet(wb, sheet_name)
        cat("Removed sheet:", sheet_name, "\n")
      }
      # Save workbook after removing sheets
      openxlsx::saveWorkbook(wb, f, overwrite = TRUE)
    } else {
      cat("No sheets needed to be removed.\n")
    }
  }

  # Upload archive and the new file to OSF
  osfr::osf_upload(archive_folder, file.path(temp_dir, archived_name), conflicts = "overwrite")
  osfr::osf_upload(data_folder, file.path(temp_dir, filename), conflicts = "overwrite")
}


prepare_changelog <- function (release_notes,
                               version_type,
                               data_folder,
                               changelog_file = "https://osf.io/fj3xc") {

  temp_dir <- tempdir()
  osfr::osf_download(osfr::osf_retrieve_file(changelog_file), temp_dir, conflicts = "overwrite")
  markdown_content <- readLines(file.path(temp_dir, "change_log.md"), warn = FALSE) %>% paste(collapse = "\n")

  current_version <- extract_current_version(markdown_content)
  next_version <-  increment_version(current_version, version_type)

  markdown_content <- update_markdown_metadata(markdown_content = markdown_content, new_version = next_version, release_notes = release_notes)

  return(list(old_version = current_version, new_changelog = markdown_content))

}

upload_changelog <- function(changelog,
                             data_folder) {
  temp_dir <- tempdir()
  writeLines(changelog, file.path(temp_dir, "change_log.md"))
  osfr::osf_upload(data_folder, file.path(temp_dir, "change_log.md"), conflicts = "overwrite")

}

release_new_version <- function(release_notes,
                                version_type = c("minor", "major", "patch"),
                                dataset = params$dataset,
                                osf_project = params$osf_project,
                                osf_folder = NULL,
                                osf_token = params$osf_token,
                                ...) {
  if (is.null(dataset) || !(dataset %in% names(params$github_raw_urls))) {
    stop("Please provide a valid 'dataset' (one of: ", paste(names(params$github_raw_urls), collapse = ", "), ")")
  }
  if (osf_token == "" || is.null(osf_token)) {
    stop("Please provide the osf_token argument or set the environment variable OSF_TOKEN")
  }

  # Authenticate to OSF and locate project
  osfr::osf_auth(osf_token)
  osf_project <- osfr::osf_retrieve_node(osf_project)

  # Determine target folder for this dataset (supports nested paths like "0 Data/Flora")
  if (is.null(osf_folder)) {
    osf_folder <- params$osf_folder_map[[dataset]]
  }

  # Traverse folder path segments to find the target folder node
  folder_segments <- strsplit(osf_folder, "/")[[1]]
  current_node <- osf_project
  for (seg in folder_segments) {
    children <- osfr::osf_ls_files(current_node, type = "folder")
    matched <- children %>% dplyr::filter(name == seg)
    if (nrow(matched) == 0) stop(glue("OSF folder segment not found: {seg}"))
    # matched may be a tibble with a single row; extract the OSF folder (component) as a node
    current_node <- osfr::osf_retrieve_node(matched$id[1])
  }
  data_folder <- current_node

  # Prepare changelog (uses data_folder for context)
  changelog <- prepare_changelog(release_notes = release_notes, version_type = version_type, data_folder, ...)

  # Determine GitHub URL and filename for this dataset
  github_raw_url <- params$github_raw_urls[[dataset]]
  filename <- params$filenames[[dataset]]

  # Process file: archive existing and upload the new file from GitHub
  process_excel_file(data_folder = data_folder, old_version = changelog$old_version, github_raw_url = github_raw_url, filename = filename, ...)

  # Upload updated changelog
  upload_changelog(changelog = changelog$new_changelog, data_folder)

  message("Successfully released version ", increment_version(changelog$old_version, version_type), " for dataset ", dataset)
}

# Function to extract the current version from Markdown
extract_current_version <- function(markdown_content) {
  version_pattern <- "(?<=\\*\\*Version:\\*\\* )\\d+\\.\\d+\\.\\d+"
  version_matches <- str_extract(markdown_content, version_pattern)
  version_matches
}

# Function to increment version number
increment_version <- function(version, version_type = c("minor", "major", "patch")) {
  version_type <- version_type[1]
  version_numbers <- as.numeric(str_split(version, "[.]")[[1]])
  if (version_type == "major") {
    version_numbers[1] <- version_numbers[1] + 1
    version_numbers[2] <- 0
    version_numbers[3] <- 0
  } else if (version_type == "minor") {
    version_numbers[2] <- version_numbers[2] + 1
    version_numbers[3] <- 0
  } else if (version_type == "patch") {
    version_numbers[3] <- version_numbers[3] + 1
  }
  paste(version_numbers, collapse = ".")
}

update_markdown_metadata <- function(markdown_content, new_version, release_notes, release_date = Sys.Date()) {
  # Format the release date
  formatted_date <- format(release_date, "%Y-%m-%d")

  # Define a more robust pattern that matches the version line, with an optional existing date
  version_pattern <- "(### Current Version\\n- \\*\\*Version:\\*\\* )[\\d\\.v]+(?: \\(.*?\\))?"
  # Create the replacement string with the new version and date
  version_replacement <- glue("\\1{new_version} ({formatted_date})")

  # Update the version section using the new pattern and replacement
  markdown_content <- sub(version_pattern, version_replacement, markdown_content, perl = TRUE)
  # --- END OF MODIFIED PART ---

  # Correctly format and insert the new release notes, now including the date
  new_notes_formatted <- paste0("    ", str_replace_all(release_notes, "\n", "\n    "))
  new_notes_section <- glue("### Latest Release Notes\n- **Notes for Version {new_version} ({formatted_date})**\n{new_notes_formatted}\n\n### Previous Release Notes")


  # Move the old "Latest Release Notes" to "Previous Release Notes" and insert the new release notes
  markdown_content <- sub("### Latest Release Notes", new_notes_section, markdown_content)
  previous_notes <- str_extract(markdown_content, "(?<=### Latest Release Notes\n).+?(?=### Previous Release Notes)")

  if (!is.na(previous_notes)) {
    markdown_content <- sub("### Previous Release Notes", glue("{previous_notes}\n### Previous Release Notes"), markdown_content)
  }

  split_content <- str_split(markdown_content, "(### Previous Release Notes\n)", n = 2, simplify = TRUE)
  if (length(split_content) > 1) {
    split_content[2] <- split_content[2] %>% str_remove_all("### Previous Release Notes\n") %>% str_replace_all("\n\n", "\n")
    markdown_content <- paste0(split_content[1], "### Previous Release Notes\n", split_content[2])
  }
  markdown_content
}
