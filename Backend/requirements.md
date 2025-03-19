# Backend Implementation Documentation for Nexlify

## Overview

This documentation outlines the backend implementation for Nexlify, an application that generates Markdown documentation for web pages. The backend is built using Python with FastAPI for API handling and leverages the `crawl4ai` package for web crawling. The goal is to provide a clear guide with code snippets that Windsurf's Cascade AI can use to generate the backend code.

## About the Application

Nexlify enables users to create Markdown files from single or multiple URLs. It includes an automatic crawling feature to document all pages under a root URL, respecting `robots.txt` and utilizing `sitemap.xml`. Users can exclude links from the output, download files individually or in bulk, and dynamically add URLs via the UI.

### Technology Stack

- **Frontend:** Next.js
- **UI Components:** ShadCN
- **Backend:** Python (FastAPI)
- **Crawling:** `crawl4ai`

## Core Features

### 1. Page Documentation Generation

- Accepts one or multiple URLs from the user.
- Converts each page's HTML into a Markdown file.
- Provides an option to exclude hyperlinks from the Markdown output.

### 2. Automatic Page Crawling

- Allows crawling all pages under a given URL when enabled.
- Respects website restrictions by checking `robots.txt`.
- Retrieves URLs from `sitemap.xml` for comprehensive crawling.

### 3. Bulk Download

- Supports downloading individual Markdown files or all files as a ZIP archive.
- Names files based on the original page titles.

### 4. Dynamic Input Fields

- Enables users to add multiple URLs dynamically via the frontend.
- Backend processes these inputs seamlessly.

## Backend Components

- **API Endpoints:** Handle requests for crawling, Markdown generation, and file downloads.
- **Crawling Logic:** Uses `crawl4ai` to fetch page content, respecting site rules.
- **Markdown Generation:** Converts HTML to Markdown with customizable options.
- **File Handling:** Manages file storage and bulk download preparation.

## API Endpoints

### POST /crawl

- **Description:** Initiates crawling and Markdown generation for provided URLs.
- **Input:** List of URLs, options (enable_crawling, exclude_links).
- **Output:** Status response and file identifiers.

### GET /download/{filename}

- **Description:** Downloads a specific Markdown file.
- **Input:** Filename.
- **Output:** Markdown file.

### GET /download/bulk

- **Description:** Downloads all generated Markdown files as a ZIP archive.
- **Output:** ZIP file.

## Code Snippets

### 1. API Endpoint for Crawling

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawler import crawl_single_page
from utils import generate_markdown, save_file

app = FastAPI()

class CrawlRequest(BaseModel):
    urls: list[str]
    enable_crawling: bool = False
    exclude_links: bool = False

@app.post("/crawl")
async def crawl(request: CrawlRequest):
    try:
        results = []
        for url in request.urls:
            html = await crawl_single_page(url)
            markdown = generate_markdown(html, exclude_links=request.exclude_links)
            filename = save_file(markdown, url)
            results.append({"url": url, "filename": filename})
        return {"status": "success", "files": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Crawling a Single Page

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def crawl_single_page(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        if result.success:
            return result.html
        else:
            raise Exception(f"Failed to crawl {url}: {result.error_message}")
```

### 3. Generating Markdown

```python
from markdownify import markdownify

def generate_markdown(html: str, exclude_links: bool = False):
    if exclude_links:
        # Placeholder for link removal logic
        html = html  # Modify this to strip links if needed
    return markdownify(html)
```

### 4. File Handling and Download

```python
from fastapi import Response
from starlette.responses import FileResponse
import os

def save_file(markdown: str, url: str) -> str:
    filename = url.split("/")[-1] or "index"  # Simplified naming
    file_path = f"/path/to/files/{filename}.md"
    with open(file_path, "w") as f:
        f.write(markdown)
    return filename

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/path/to/files/{filename}.md"
    return FileResponse(file_path, media_type="text/markdown", filename=f"{filename}.md")

@app.get("/download/bulk")
async def download_bulk():
    # Placeholder for ZIP creation logic
    zip_path = "/path/to/zip/archive.zip"
    return FileResponse(zip_path, media_type="application/zip", filename="markdown_files.zip")
```