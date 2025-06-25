#' Cleans a FReD dataframe with safe, automated actions.
#'
#' @param data A raw FReD dataframe.
#' @return A list containing `cleaned_data` (the cleaned dataframe) and `report`
#'         (a Markdown string detailing the cleaning actions taken).
clean_fred_data <- function(data) {

  # --- Storage for report items ---
  cleaning_report <- list()

  # --- Create a copy to modify ---
  cleaned_data <- data

  # --- Helper function to report changes ---
  add_report_item <- function(report_list, message) {
    report_list[[length(report_list) + 1]] <- message
    return(report_list)
  }

  # --- 1. Trim and squish Whitespace from all character columns ---
  # Calculate changes before applying them
  char_cols <- names(cleaned_data)[sapply(cleaned_data, is.character)]
  trimmed_changes <- cleaned_data %>%
    mutate(across(all_of(char_cols), ~ str_squish(.))) %>%
    mutate(across(all_of(char_cols), ~ str_trim(.))) %>%
    summarise(across(all_of(char_cols), ~ sum(.x != data[[cur_column()]], na.rm = TRUE))) %>%
    pivot_longer(everything()) %>%
    filter(value > 0)

  if (nrow(trimmed_changes) > 0) {
    # Apply the change
    cleaned_data <- cleaned_data %>%
      mutate(across(all_of(char_cols), ~ str_squish(.))) %>%
      mutate(across(all_of(char_cols), ~ str_trim(.)))
    report_message <- glue::glue("Trimmed leading/trailing/repeated whitespace from {sum(trimmed_changes$value)} cell(s) in columns: `{paste(trimmed_changes$name, collapse=', ')}`.")
    cleaning_report <- add_report_item(cleaning_report, report_message)
  }

  # --- 2. Standardize NA values (convert "NA", "N/A" to NA) ---
  na_changes_before <- sum(sapply(cleaned_data, function(x) sum(is.na(x))))

  cleaned_data <- cleaned_data %>%
    mutate(across(where(is.character), ~ na_if(., "NA"))) %>%
    mutate(across(where(is.character), ~ na_if(., "N/A"))) %>%
    mutate(across(where(is.character), ~ na_if(., "#N/A")))


  na_changes_after <- sum(sapply(cleaned_data, function(x) sum(is.na(x))))
  na_rows_affected <- na_changes_after - na_changes_before

  if (na_rows_affected > 0) {
    report_message <- glue::glue("Converted {na_rows_affected} string(s) ('NA' or 'N/A') to proper `NA` values.")
    cleaning_report <- add_report_item(cleaning_report, report_message)
  }

  # --- 3. Clean Reference Columns (remove DOIs) ---
  ref_cols <- c("ref_o", "ref_r")
  # Pattern to find DOIs formatted as a prefix OR a full URL
  doi_pattern <- "\\s*(doi: ?10[./]\\S+|https?://(dx\\.)?doi\\.org/10[./]\\S+)"

  ref_changes <- cleaned_data %>%
    summarise(across(all_of(ref_cols), ~ sum(str_detect(., regex(doi_pattern, ignore_case = TRUE)), na.rm = TRUE))) %>%
    pivot_longer(everything()) %>%
    filter(value > 0)

  if (nrow(ref_changes) > 0) {
    cleaned_data <- cleaned_data %>%
      mutate(across(all_of(ref_cols), ~ str_remove_all(., regex(doi_pattern, ignore_case = TRUE))))
    total_ref_changes <- sum(ref_changes$value)
    report_message <- glue::glue("Removed DOI strings (both URL and prefix format) from {total_ref_changes} cell(s) in `ref_o`/`ref_r` columns.")
    cleaning_report <- add_report_item(cleaning_report, report_message)
  }

  # --- 4. Clean DOI Columns (remove URL prefix) ---
  doi_cols <- c("doi_o", "doi_r")
  url_prefix <- "https://doi.org/"

  doi_prefix_changes <- cleaned_data %>%
    summarise(across(all_of(doi_cols), ~ sum(str_starts(., url_prefix), na.rm = TRUE))) %>%
    pivot_longer(everything()) %>%
    filter(value > 0)

  if (nrow(doi_prefix_changes) > 0) {
    cleaned_data <- cleaned_data %>%
      mutate(across(all_of(doi_cols), ~ str_remove(., fixed(url_prefix))))
    total_doi_prefix_changes <- sum(doi_prefix_changes$value)
    report_message <- glue::glue("Removed '{url_prefix}' prefix from {total_doi_prefix_changes} cell(s) in `doi_o`/`doi_r` columns.")
    cleaning_report <- add_report_item(cleaning_report, report_message)
  }

  # --- 5. Clean ES Value Columns (Standardize stats, spacing, brackets) ---
  es_cols <- c("es_value_o", "es_value_r")

  # Capture state before changes to count modifications
  data_before_es_clean <- cleaned_data

  # Apply all transformations sequentially to the target columns
  cleaned_data <- cleaned_data %>%
    mutate(across(all_of(es_cols), ~ {
      # Assign to a temporary variable for modification
      val <- .
      # Standardize various spellings of X2 [χ², x2, χ2] into X2
      val <- str_replace_all(val, regex("[χx]2|χ²", ignore_case = TRUE), "X2")
      # Remove a space after ^t and ^F
      val <- str_replace_all(val, "(^t|^F)\\s+", "\\1")
      # Ensure there are single spaces around any =
      val <- str_replace_all(val, "\\s*=\\s*", " = ")
      val <- str_replace_all(val, "-\\s+", "-")
      # Capitalise Z
      val <- str_replace_all(val, "^z", "Z")
      # Ensure - is not a longer dash, e.g. en (–) or em (—) dash
      val <- str_replace_all(val, "[-–—]", "-")
      # Replace [] with ()
      val <- str_replace_all(val, "\\[", "(")
      val <- str_replace_all(val, "\\]", ")")
      val <- str_replace_all(val, "X2\\((\\d+),\\s*N\\s*=\\s*\\d+\\)", "X2(\\1)")
      val <- str_trim(str_squish(val))
      # Return the modified value
      val
    }, .names = "{.col}")) # Ensure the operation modifies the columns in place

  # Calculate the total number of cells changed in the es_value columns
  es_changes <- sum(cleaned_data$es_value_o != data_before_es_clean$es_value_o, na.rm = TRUE) +
    sum(cleaned_data$es_value_r != data_before_es_clean$es_value_r, na.rm = TRUE)

  if (es_changes > 0) {
    report_message <- glue::glue("Standardized formatting for {es_changes} cell(s) in `es_value_o`/`es_value_r` (e.g., 'X2', spacing around '=', brackets).")
    cleaning_report <- add_report_item(cleaning_report, report_message)
  }

  # --- Finalize Report ---
  final_report_string <- ""
  if (length(cleaning_report) > 0) {
    report_header <- "## FReD Automatic Cleaning Report\n\n"
    report_body <- paste0("- ✅ ", cleaning_report, collapse = "\n")
    final_report_string <- paste0(report_header, report_body)
  } else {
    final_report_string <- "## FReD Automatic Cleaning Report\n\n- No automatic cleaning actions were required."
  }

  return(list(cleaned_data = cleaned_data, report = final_report_string))
}
