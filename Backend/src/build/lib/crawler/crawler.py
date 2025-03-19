from typing import List, Optional
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from urllib.robotparser import RobotFileParser
from .sitemap_parser import get_sitemap_urls
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self):
        self.visited_urls = set()
        self.session = None
        self.robots_cache = {}
        self.playwright = None
        self.browser = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_robots_parser(self, base_url: str) -> Optional[RobotFileParser]:
        """Get robots.txt parser for the given URL"""
        if base_url in self.robots_cache:
            return self.robots_cache[base_url]

        try:
            robots_url = urljoin(base_url, "/robots.txt")
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    content = await response.text()
                    parser = RobotFileParser()
                    parser.parse(content.splitlines())
                    self.robots_cache[base_url] = parser
                    return parser
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt for {base_url}: {str(e)}")
        return None

    async def crawl_url(self, url: str, enable_crawling: bool = False) -> dict:
        """Crawl a single URL and optionally its linked pages using Playwright for JavaScript rendering"""
        if url in self.visited_urls:
            return {"success": False, "error": "URL already crawled"}

        try:
            # Check robots.txt
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            robots = await self.get_robots_parser(base_url)
            
            if robots and not robots.can_fetch("*", url):
                return {"success": False, "error": "URL not allowed by robots.txt"}

            self.visited_urls.add(url)
            
            # Use Playwright to render JavaScript content
            page = await self.browser.new_page()
            await page.goto(url, wait_until="networkidle")
            
            # Wait a bit more for any delayed JS content
            await asyncio.sleep(2)
            
            # Get the fully rendered HTML content
            html = await page.content()
            title = await page.title()
            
            # Close the page to free resources
            await page.close()
            
            # Parse with BeautifulSoup for further processing
            soup = BeautifulSoup(html, "html.parser")

            # Get sitemap URLs if crawling is enabled
            additional_urls = []
            if enable_crawling:
                sitemap_urls = await get_sitemap_urls(base_url, self.session)
                additional_urls = [u for u in sitemap_urls if u.startswith(base_url)]

            return {
                "success": True,
                "url": url,
                "title": title,
                "html": html,
                "additional_urls": additional_urls
            }

        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def crawl_urls(self, urls: List[str], enable_crawling: bool = False) -> List[dict]:
        """Crawl multiple URLs and their linked pages if crawling is enabled"""
        results = []
        for url in urls:
            result = await self.crawl_url(url, enable_crawling)
            if result["success"]:
                results.append(result)
                
                # Crawl additional URLs if crawling is enabled
                if enable_crawling and result.get("additional_urls"):
                    for additional_url in result["additional_urls"]:
                        if additional_url not in self.visited_urls:
                            additional_result = await self.crawl_url(additional_url, False)
                            if additional_result["success"]:
                                results.append(additional_result)
        
        return results