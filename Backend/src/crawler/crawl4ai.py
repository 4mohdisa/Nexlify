"""
Custom implementation of crawl4ai package
This file provides the AsyncWebCrawler class with the exact same API
as mentioned in the requirements document.
"""
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class CrawlResult:
    success: bool
    html: Optional[str] = None
    error_message: Optional[str] = None

class AsyncWebCrawler:
    """Implementation of crawl4ai.AsyncWebCrawler as specified in the requirements"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        # Use a proper browser-like user agent to help with content blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def arun(self, url: str) -> CrawlResult:
        """
        Crawl a URL and return a CrawlResult with HTML content.
        This matches the exact interface specified in the requirements.
        """
        try:
            logger.info(f"Crawling URL: {url}")
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                    return CrawlResult(
                        success=False,
                        error_message=f"HTTP error: {response.status}"
                    )
                
                html = await response.text()
                
                # Process with BeautifulSoup to ensure we have proper HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Fix relative URLs to absolute
                base_url = response.url.human_repr()
                for tag in soup.find_all(['a', 'img', 'link', 'script']):
                    for attr in ['href', 'src']:
                        if tag.has_attr(attr) and not tag[attr].startswith(('http://', 'https://', 'data:', 'javascript:')):
                            if tag[attr].startswith('/'):
                                # Root-relative URL
                                tag[attr] = f"{response.url.origin().human_repr()}{tag[attr]}"
                            else:
                                # Document-relative URL
                                tag[attr] = f"{base_url.rstrip('/')}/{tag[attr].lstrip('/')}"
                
                # Get the processed HTML
                processed_html = str(soup)
                
                logger.info(f"Successfully crawled {url}")
                return CrawlResult(success=True, html=processed_html)
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return CrawlResult(success=False, error_message=str(e))
