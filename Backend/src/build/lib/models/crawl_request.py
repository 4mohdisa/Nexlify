from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class CrawlRequest(BaseModel):
    """Request model for the crawl endpoint"""
    urls: List[HttpUrl]
    enable_crawling: bool = False
    include_links: bool = True
    data_type: str = "full-page"  # Options: full-page, text-only, headings-only