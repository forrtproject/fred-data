# Rebuild the original-field projection of current production FReD, no workbook write.
library(readr)
library(dplyr)
library(jsonlite)
source('R/data_cleaning.R')
source('R/fred_overlays.R')
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2)
raw <- read_csv(args[1], skip=1, show_col_types=FALSE)
frame <- raw %>% filter(status=='validated - chosen', is.na(exclusion)) %>% mutate(score_entry=FALSE)
result <- clean_fred_data(frame)
x <- result$cleaned_data %>% mutate(doi_o=tolower(doi_o), doi_r=tolower(doi_r)) %>%
 mutate(across(c(doi_o,doi_r), ~gsub('^doi:', '', gsub('^(https?://)?(dx\\.)?doi\\.org/', '', .))))
fixes <- read_csv('pipelines/fred/overlays/audit_corrections.csv', col_types=cols(.default=col_character()), na=character(), show_col_types=FALSE)
# Success fields are joined later by production; excluded here because this is an
# original-only coding projection. Every present source field receives its approved fix.
skipped <- fixes %>% filter(!field %in% names(x))
stopifnot(all(skipped$field %in% c('reported_success','reported_success_quote','reported_success_quote_source')))
applicable <- tempfile(fileext='.csv')
write_csv(fixes %>% filter(field %in% names(x)), applicable, na='')
corrected <- apply_audit_corrections(x, applicable)
unlink(applicable)
x <- corrected$data
x$fred_id <- sub('_[a-z]{1,2}$','',x$id)
flags <- apply_x2_conversion_flags(x,'pipelines/fred/overlays/x2_conversion_flags.csv')
x <- flags$data
stopifnot(!anyNA(x$effect_uid), all(nzchar(x$effect_uid)), !anyDuplicated(x$effect_uid))
keep <- c('effect_uid','ref_o','doi_o','study_o','file_o','link_o','claim_text_o','claim_page_o','n_o','es_value_o','es_type_o','es_repr_o','pval_value_o','pval_type_o','pval_tails_o')
write_csv(x %>% arrange(effect_uid) %>% select(all_of(keep)), args[2], na='')
write_json(list(raw_rows=nrow(raw), published_rows=nrow(x), audit=corrected$report, excluded_success_fields=nrow(skipped), x2=flags$report, eligibility="status == 'validated - chosen' and exclusion missing; SCORE disabled, production default", projection='Original-only projection: current production filtering/cleaning/DOI normalisation and all applicable verified audit corrections; bibliographic augmentation and author-success join excluded, not a full workbook rebuild.'), paste0(args[2], '.report.json'), pretty=TRUE, auto_unbox=TRUE)
writeLines(result$report,paste0(args[2], '.cleaning.md'))
cat(nrow(raw),'raw sheet rows;',nrow(x),'current published FReD effects rebuilt.\n')
