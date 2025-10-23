
# Save DOI_R and study homogeneity ----------------------------------------

# this script has been used for one time coding

# download most recent version
ds <- openxlsx::read.xlsx("https://github.com/forrtproject/FReD-data/raw/refs/heads/main/COS%20Reports/2025-10-22_COSdata_validated.xlsx")

ds$identifier_r <- paste(ds$doi_r, ds$url_r, sep = ", ")

# count number of findings per doi_r
entry_counter <- aggregate(ds, r_r ~ identifier_r, FUN = function(x){length(x)})
names(entry_counter) <- c("identifier_r", "doicounter")

# add counter to dataset
ds_entrycount <- merge(x = ds, y = entry_counter, by = "identifier_r")
names(ds_entrycount)

keep <- c(
  "doi_r",             "ref_o",
  "doi_o",               "study_o",             "ref_r",               "url_r",               "study_r",
  "description",         "claim_text_o",        "claim_page_o",
  "n_o",                 "es_value_o",          "es_type_o",
  "n_r", "es_value_r",          "es_type_r",
  # "file_o",              "file_r",
  "replication_success", "outcome",             "outcome_quote",
  "out_quote_source",    "doicounter", "identifier_r"
)

ds_ec <- ds_entrycount[, keep]

ds_ec <- ds_ec[!duplicated(ds_ec$ref_r), ]

# code any of these entries as meta papers
metapapers <- c(
"10.1038--s41562-024-02062-9",
"10.3389/fcomm.2022.1048896", # 10 cases of sensory research
"10.1073/pnas.2103313118", # scarcity effects
"10.1177/0956797619831612", # Soto
"10.1007/s13164-018-0400-9", # X-PHI
"10.1038/s41562-018-0399-z", # Camerer 2018
"10.1098/rsos.231240", # Boyce
"10.1027/1864-9335/a000178", # ML1
"10.1177/2515245918810225", # ML2
"10.1016/j.jesp.2015.10.012", # ML3
# "10.1177/2515245920958687", # ML5 NOT because it is focusing on a single study
"10.1126/science.aac4716", # RP:P
"10.1038/s41562-024-02062-9", # Holzmeister et al. 2024
"10.1177/08902070221094216", # SVO development
"10.1126/science.aaf0918" # Camerer 2016
)

ds_ec$metapaper_r <- ds_ec$doi_r %in% metapapers

openxlsx::write.xlsx(ds_ec, file = "data augmentation/ds_for_homogeneitycoding_identifier.xlsx")

