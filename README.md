# Website RAG

Website RAG is a Streamlit-based retrieval-augmented generation (RAG) application for crawling, indexing, and querying website content from a sitemap. It uses sitemap-aware page discovery, URL scoring and filtering, content extraction, chunking, embeddings, and an LLM-powered retrieval workflow to answer questions grounded in crawled web data.

## Features

- Sitemap-based website crawling
- URL scoring and filtering for relevant pages
- Web page extraction using Crawl4AI
- Chunking and embedding pipeline for document retrieval
- RAG-based question answering through a Streamlit interface
- AWS Bedrock integration for foundation model inference

## Project Structure

```text
.
├── KB/
│   └── crawl_results.jsonl
├── Versions/
│   └── Version 2/
│       ├── app.py
│       ├── crawler.py
│       ├── retrive.py
│       ├── v2.py
│       ├── depricated/
│       └── utils/
├── main.py
├── pyproject.toml
├── README.md
└── .venv/ (created by uv)
```

## Prerequisites

This project uses `uv` for dependency and environment management.

## Setup

Install project dependencies:

```bash
uv sync
```

Start the application:

```bash
uv run streamlit run ".\Versions\Version 2\app.py"
```

If Playwright browser binaries are not installed, run:

```bash
uv run playwright install chromium
```

## Environment Variables

This project uses AWS Bedrock for the foundation model.

Create your environment variables in a `.env` file or export them in your shell before running the app:

```bash
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_REGION_NAME=""
model="amazon.nova-lite-v1:0"
```

## Architecture

The application follows a sitemap-driven ingestion and retrieval pipeline:

```text
Streamlit UI
  -> Sitemap URL parser
  -> Scoring and filtering
  -> Crawl and fetch web pages
  -> Chunk and embed content
  -> Prepare RAG chain
  -> User question answering
```

### Retrieval flow

```text
User question
  -> Streamlit UI
  -> RAG Chain
  -> Relevant document retrieval
  -> LLM response generation
  -> Streamlit UI
  -> User
```

## Workflow

1. Parse the sitemap and identify candidate URLs.
2. Score and filter pages based on relevance and quality.
3. Crawl and fetch the selected pages.
4. Split the extracted content into manageable chunks.
5. Generate embeddings and store them for retrieval.
6. Use the RAG chain to answer user queries grounded in indexed content.

## Notes

The project is designed around website knowledge extraction for question answering over a target domain, with examples such as sitemap-driven domains like `https://tata.cars` and content crawling via Crawl4AI.

## Future Enhancement

Improved sitemap crawling, if pdfs are present, introduce complex workflow that downloads the pdfs and creates embedding for the same.


## License

This project is currently intended for personal or internal use unless otherwise specified.


