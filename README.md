# Paper Downloader

This program searches for papers that cite a given paper and downloads them using open-access APIs.

## Features

- Searches for papers that cite a given paper using Google Scholar via Serper API or Selenium
- Downloads papers from open-access sources (Arxiv, Semantic Scholar)
- Organizes results in folders named after the original paper
- Tracks papers that couldn't be downloaded in `unavailable.txt`

## Requirements

- Python 3.6+
- API keys for Serper (required for download.py) and optionally Semantic Scholar
- Python packages listed in `requirements.txt`

## Installation

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Set up your API keys in environment variables:
   ```
   export SERPER_API_KEY="your_serper_api_key"
   export SEMANTIC_SCHOLAR_API_KEY="your_semantic_scholar_api_key"  # Optional
   ```

3. Specify the LLM you want to use in `llm_cfg` variable in `filter.py` and `filter_comment.py`

## Usage
```
python3 download.py
python3 filter.py
python3 filter_comment.py
```
