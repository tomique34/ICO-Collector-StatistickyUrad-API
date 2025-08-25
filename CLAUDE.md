# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based ICO (Slovak company identification number) collection tool that uses the Slovak Statistical Office (Štatistický úrad SR) REST API to fetch company information. The project processes Excel files containing company names and enriches them with ICO numbers and additional company details.

## Architecture

The project contains two main Python scripts:

- **get_ico_chatgpt.py**: Basic ICO lookup implementation with rate limiting and concurrent processing
- **get_ico_v2.py**: Enhanced version with advanced features including company name normalization, query variants, detailed logging, and progress tracking

Both scripts use the same core approach:
1. Load company names from Excel file
2. Clean/normalize company names (v2 only)
3. Query the RPO API with rate limiting
4. Extract ICO from API responses
5. Export enriched data to Excel and CSV

### Key Components

- **Name Normalization** (v2): Removes legal entity suffixes (s.r.o., a.s., etc.) and handles Slovak diacritics
- **Rate Limiting**: Implements sliding window rate limiter to respect API limits (60 requests/minute)
- **Concurrent Processing**: Uses ThreadPoolExecutor with configurable worker count
- **Error Handling**: Retry logic with exponential backoff for API failures
- **Progress Tracking** (v2): Visual progress bar using tqdm

## Development Setup

### Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Dependencies
- pandas: Excel/CSV processing
- requests: HTTP API calls
- openpyxl: Excel file handling
- tqdm: Progress bars (v2 only)
- concurrent.futures: Parallel processing

## API Integration

**Base URL**: `https://api.statistics.sk/rpo/v1/search`

**Parameters**:
- `fullName`: Company name to search
- `onlyActive`: Filter for active companies only

**Documentation**: https://susrrpo.docs.apiary.io/#/reference/0/vyhladavanie-po/vyhladavanie-po/200

## Running the Scripts

### Basic Version
```bash
python get_ico_chatgpt.py
```
Requires `test_120firiem.xlsx` input file with "Firma" column.

### Enhanced Version
```bash
python get_ico_v2.py
```
Prompts for input file path interactively.

## Configuration

Key constants in both scripts:
- `MAX_WORKERS`: Concurrent thread count (default: 6)
- `MAX_REQ_PER_MIN`: API rate limit (default: 60)
- `REQUEST_TIMEOUT`: API timeout in seconds (default: 12)
- `RETRY_COUNT`: Max retry attempts (default: 3)
- `BATCH_SIZE`: Processing batch size (default: 60)

## Output Files

Scripts generate:
- Enhanced Excel file with ICO data
- CSV export for further processing
- Log files in LOGS/ directory (v2 only)

## Logging

The v2 script creates timestamped log files in the `LOGS/` directory with detailed processing information including API failures, retry attempts, and processing statistics.

## Testing

Test with the included `test_120firiem.xlsx` file containing sample Slovak company names. The file should have a "Firma" column with company names to process.