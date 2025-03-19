from pydantic import BaseModel
from typing import List

class FileInfo(BaseModel):
    """Information about a generated markdown file"""
    url: str
    filename: str
    title: str

class CrawlResponse(BaseModel):
    """Response model for the crawl endpoint"""
    status: str
    files: List[FileInfo]
    message: str = ""