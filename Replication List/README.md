# FLoRA: FORRT Library of Replications and Reproductions

This folder contains the consolidated FLoRA generation script and outputs.

## Main File

**FLoRA.qmd** - The consolidated Quarto document that generates the FLoRA dataset by:
- Pulling replication data from the FORRT Google Sheets
- Validating and deduplicating DOI pairs
- Augmenting with bibliometric metadata from CrossRef
- Enriching with keywords, field, and language data from OpenAlex
- Adding metapaper coding and publication status classification
- Generating APA and BibTeX citations with caching for efficiency

## Outputs

When rendered, FLoRA.qmd generates:
- **FLoRA.csv** - The main FLoRA dataset in CSV format
- **FLoRA.xlsx** - The FLoRA dataset in Excel format
- **crossref_citation_cache.rds** - Citation cache file (auto-generated, gitignored)

## Features

The consolidated FLoRA script combines the best features from the previous versions:

### From list_data_creator.qmd (LibRe²):
- Outcome quotes and sources
- OpenAlex metadata (keywords, field, language)
- Metapaper coding for multi-study replications
- Publication status classification
- Validation filtering (validated - chosen only)
- Exclusion logic for metapapers without URLs

### From hackathon prep - flora.qmd:
- CrossRef citation caching mechanism for efficiency
- Fallback logic for APA/BibTeX generation
- Streamlined metadata handling
- Support for non-journal article types

## Usage

To regenerate the FLoRA dataset:

1. Ensure you have R and the required packages installed:
   - dplyr, readr, rcrossref, purrr, jsonlite, glue, stringr, rlang, httr, digest, openxlsx

2. Run the Quarto document:
   ```bash
   quarto render FLoRA.qmd
   ```

   Or in R:
   ```r
   quarto::quarto_render("FLoRA.qmd")
   ```

## History

This file consolidates two previous FLoRA generation scripts:
- `list_data_creator.qmd` (original version, focused on LibRe²)
- `hackathon prep - flora.qmd` (Luke's hackathon version)

Both have been removed in favor of this unified version.
