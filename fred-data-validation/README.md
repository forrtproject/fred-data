# FRED Data Validation Pipeline

Automated validation pipeline for replication studies using LLMs, Crossref API, and GROBID for PDF processing.

## Overview

This project validates replication studies by:
1. **Reference Matching**: Comparing original study references (`ref_o`) with replication references (`ref_r`) to determine if the replication explicitly, implicitly, or unclearly addresses the original study
2. **Abstract Extraction**: Fetching abstracts from Crossref API or extracting from PDFs using GROBID when Crossref data is unavailable
3. **Central Claim Validation**: Using LLMs to determine if claims from original studies are central to the research based on the title and abstract

## Features

- **Parallel Processing**: Multi-threaded execution for efficient processing of large datasets
- **Multiple Abstract Sources**: Prioritizes Crossref API, falls back to PDF extraction via GROBID
- **LLM-Powered Validation**: Uses GPT models with structured output for consistent validation results
- **Comprehensive Logging**: Detailed progress tracking and error reporting
- **CSV Export**: Saves abstracts separately for reuse

## Prerequisites

### Required Software
- Python 3.12.2 or higher
- pip (Python package manager)

### Required Accounts/APIs
- OpenAI API key (for GPT models)
- GROBID server access (default: https://kermitt2-grobid.hf.space/)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fred-data
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv fred_venv
source fred_venv/bin/activate  # On macOS/Linux
# OR
# fred_venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
```txt
pandas
openpyxl
crossref-commons
grobid-client-python
langchain
langchain-openai
langchain-core
pydantic
```

### 4. Set Up API Keys

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or add it to your shell profile (~/.zshrc, ~/.bashrc):

```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## Project Structure

```
fred-data/
├── requirements.txt                	# Python dependencies
├── README.md                       	# This file
├── 2025-10-22_COSdata_validated.xlsx  # Input data file
├── fred_mini.csv  							# Input data file with titles
├── fred_pdfs/                      	# Directory with PDF files
│   └── *.pdf                       	# Original study PDFs
├── output/                         	# GROBID XML output
│   └── *.grobid.tei.xml           		# Extracted XML files
└── fred_venv/                      	# Python virtual environment
```

## Input Data Format

The Excel file (`2025-10-22_COSdata_validated.xlsx`) should contain:

### Required Columns
- `ref_o`: Original study reference (author, year, title)
- `ref_r`: Replication study reference
- `doi_o`: DOI of the original study
- `claim_text_o`: Claim text from the original study
- `file_o`: PDF filename (optional, for PDF processing)

### Optional Columns
All other columns from your dataset will be preserved in the output.

## Usage

### Basic Usage

```bash
python fred-data.py
```

### Processing Configuration

Edit the script to adjust processing parameters:

```python
# Number of parallel workers (adjust based on API rate limits)
max_workers = min(10, os.cpu_count() or 1)

# Model selection
llm = ChatOpenAI(
    model="gpt-5-mini",  # or "gpt-4o-mini", "gpt-4", etc.
    temperature=0.0
)
```

### Test Mode

To process only a subset of records for testing:

```python
# Process only first 10 records
for index, row in df.iloc[:10].iterrows():
```

## Output Files

The script generates three output files:

### 1. Main Results Excel File
**Filename**: `2025-10-22_COSdata_combined_validation_parallel.xlsx`

**New Columns Added:**
- `reference_match`: Classification (explicit/implicit/unclear)
- `ref_match_confidence`: Confidence score (0.0-1.0)
- `ref_match_evidence`: Supporting evidence from text
- `ref_match_explanation`: Detailed reasoning
- `abstract_source`: Where abstract was found (crossref/pdf/none)
- `has_abstract`: Boolean flag
- `abstract_text`: Full abstract text
- `is_central_claim`: Whether claim is central to article
- `claim_confidence`: Confidence score (0.0-1.0)
- `claim_match_type`: How claim maps (exact/construct_mapping/peripheral/unclear)
- `claim_key_evidence`: Supporting evidence from abstract
- `claim_concerns`: Methodological concerns
- `claim_explanation`: Detailed reasoning

### 2. Abstracts CSV
**Filename**: `2025-10-22_abstracts_parallel.csv`

**Columns:**
- `doi_o`: DOI of the original study
- `abstract`: Full abstract text
- `source`: Source of abstract (crossref/pdf)

### 3. Console Output
Real-time progress and statistics printed to console.

## Validation Logic

### Reference Match Classification

1. **EXPLICIT**: `ref_r` contains author names AND/OR publication year from `ref_o`
   - Example: "Replication of Finucane et al.'s (2000) study"

2. **IMPLICIT**: `ref_r` mentions specific topic/construct from `ref_o` but not author/year
   - Example: Original topic "implicit threat-related bias" → Replication "attention bias to social threat"

3. **UNCLEAR**: `ref_r` doesn't mention authors/year or specific topic
   - Example: Generic titles like "Many Labs 2"

### Central Claim Validation

Claims are evaluated as central if they:
- Target the main research question mentioned in title/abstract
- Map to core constructs described in the abstract
- Could be tested by methods consistent with the abstract
- Are emphasized in the title and/or abstract

**Note**: Validation only occurs for non-explicit reference matches to save API calls.

## Performance Optimization

### Parallel Processing
- Uses `ThreadPoolExecutor` for concurrent API calls
- Default: 10 worker threads (configurable)
- Thread-safe statistics tracking with locks

### Caching
- Checks for existing GROBID XML files before reprocessing PDFs
- Reuses abstracts from previous runs if XML files exist

### API Rate Limiting
- Built-in delays between requests
- Configurable worker count to respect API limits
- Error handling and retry logic

## Troubleshooting

### Common Issues

#### 1. Missing OpenAI API Key
```
Error: OpenAI API key not set
```
**Solution**: Export your API key as shown in Setup section

#### 2. GROBID Processing Failures
```
Error processing PDF: Connection timeout
```
**Solution**: Check GROBID server status or use alternative server

#### 3. Memory Issues with Large Datasets
```
MemoryError
```
**Solution**: Reduce `max_workers` or process in batches

#### 4. Invalid JSON Output from LLM
```
Error: Invalid json output
```
**Solution**: Model may be returning malformed JSON. Check model compatibility or adjust prompt.

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Configuration

### Custom GROBID Server

```python
client = GrobidClient(grobid_server="http://your-grobid-server:8070")
```

### Using Different LLM Models

```python
# For cheaper processing
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

# For better accuracy
llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# For Anthropic Claude
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-sonnet-20240229")
```

### Batch Processing

Process data in chunks:

```python
chunk_size = 100
for i in range(0, len(df), chunk_size):
    chunk_df = df.iloc[i:i+chunk_size]
    # Process chunk_df
```

## Contributing

### Code Style
- Follow PEP 8
- Use type hints (Python 3.12+ syntax)
- Add docstrings to functions
- Keep functions focused and testable

### Testing

Run with a small subset first:

```python
df = df.iloc[:10]  # Test with 10 records
```

## License

This project is open source and available under the MIT License.

## Citation

If you use this pipeline in your research, please cite:

```
[Add citation information]
```

## Support

For issues, questions, or contributions, please create an issue on GitHub.

## Acknowledgments

- GROBID for PDF processing
- Crossref for metadata API
- OpenAI for LLM capabilities
- LangChain for LLM orchestration

## Changelog

### Version 1.0.0 (2025-10-23)
- Initial release
- Parallel processing implementation
- Reference matching validation
- Central claim validation
- Abstract extraction from Crossref and PDFs
