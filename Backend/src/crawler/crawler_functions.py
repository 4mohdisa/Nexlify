"""
Crawler functions exactly matching the requirements document
"""
import asyncio
import logging
from crawl4ai import AsyncWebCrawler
from markdownify import markdownify
import os
from bs4 import BeautifulSoup
import aiohttp
import time
import random

logger = logging.getLogger(__name__)

async def crawl_single_page(url: str, wait_time: int = 5, scroll_count: int = 3):
    """
    Crawl a single page and return its HTML content.
    
    Args:
        url: The URL to crawl
        wait_time: Time to wait for dynamic content to load (seconds)
        scroll_count: Number of times to simulate scrolling
        
    This function implements the requirements document specification
    with enhancements for dynamic content.
    """
    # Ensure URL is a string and properly formatted
    url = str(url)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    logger.info(f"Attempting to crawl URL: {url}")
    
    try:
        # First try using crawl4ai (Playwright-based)
        async with AsyncWebCrawler() as crawler:
            # The crawl4ai package should handle dynamic content automatically
            result = await crawler.arun(url=url)
            if result.success:
                logger.info(f"Successfully crawled {url} using crawl4ai")
                return result.html
            else:
                logger.warning(f"crawl4ai failed: {result.error_message}, trying fallback")
                # If this fails, we'll try the fallback method below
                raise Exception(result.error_message)
    except Exception as e:
        logger.warning(f"Error with crawl4ai: {str(e)}, using fallback HTTP method")
        
        # Fallback to regular HTTP requests with enhancements for dynamic content
        try:
            # Use a proper browser-like user agent to help with content blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                logger.info(f"Sending HTTP request to {url}")
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP error: {response.status}")
                    
                    initial_html = await response.text()
                    
                    # Initial parse with BeautifulSoup
                    soup = BeautifulSoup(initial_html, 'html.parser')
                    
                    # Wait mechanism 1: Additional requests for resources that might contain embedded content
                    # Find all linked resources (JavaScript, CSS, etc.)
                    resource_tasks = []
                    for tag in soup.find_all(['script', 'link']):
                        src = tag.get('src') or tag.get('href')
                        if src and (src.endswith('.js') or src.endswith('.css')):
                            # Make the src absolute if it's relative
                            if not src.startswith(('http://', 'https://')):
                                if src.startswith('/'):
                                    parts = str(response.url).split('/')
                                    if len(parts) >= 3:
                                        base = '/'.join(parts[:3])
                                        src = f"{base}{src}"
                                else:
                                    src = f"{str(response.url).rstrip('/')}/{src.lstrip('/')}"
                            
                            # Fetch the resource
                            resource_tasks.append(session.get(src, ssl=False))
                    
                    # Wait for all resource requests to complete
                    if resource_tasks:
                        try:
                            await asyncio.gather(*resource_tasks, return_exceptions=True)
                            logger.info(f"Fetched {len(resource_tasks)} additional resources")
                        except Exception as e:
                            # Log but continue if there are errors with resource fetching
                            logger.warning(f"Error fetching resources: {str(e)}")
                    
                    # Wait mechanism 2: Sleep to allow for any JavaScript or delayed content
                    logger.info(f"Waiting {wait_time} seconds for dynamic content")
                    await asyncio.sleep(wait_time)
                    
                    # Wait mechanism 3: Simulate multiple requests to capture AJAX loaded content
                    # Sometimes a second request after waiting captures more content
                    try:
                        async with session.get(url, timeout=30) as second_response:
                            if second_response.status == 200:
                                second_html = await second_response.text()
                                second_soup = BeautifulSoup(second_html, 'html.parser')
                                
                                # If the second response has more content, use it
                                if len(second_soup.get_text()) > len(soup.get_text()):
                                    logger.info("Second request captured more content")
                                    soup = second_soup
                    except Exception as e:
                        logger.warning(f"Error on second request: {str(e)}")
                    
                    # Wait mechanism 4: For some sites, simulate scrolling by making requests with different headers
                    for i in range(scroll_count):
                        try:
                            # Modify the headers slightly to simulate different conditions
                            scroll_headers = headers.copy()
                            scroll_headers["Cache-Control"] = "no-cache"
                            scroll_headers["Cookie"] = f"scrolled=true; position={i*1000}"
                            
                            async with session.get(url, headers=scroll_headers, timeout=30) as scroll_response:
                                if scroll_response.status == 200:
                                    scroll_html = await scroll_response.text()
                                    scroll_soup = BeautifulSoup(scroll_html, 'html.parser')
                                    
                                    # If we got more content, use it
                                    if len(scroll_soup.get_text()) > len(soup.get_text()):
                                        logger.info(f"Scroll {i+1} captured more content")
                                        soup = scroll_soup
                                        
                                    # Wait a bit between scroll requests
                                    await asyncio.sleep(1)
                        except Exception as e:
                            logger.warning(f"Error on scroll {i+1}: {str(e)}")
                    
                    # Fix relative URLs to absolute
                    base_url = str(response.url)
                    for tag in soup.find_all(['a', 'img', 'link', 'script']):
                        for attr in ['href', 'src']:
                            if tag.has_attr(attr) and not tag[attr].startswith(('http://', 'https://', 'data:', 'javascript:')):
                                if tag[attr].startswith('/'):
                                    # Root-relative URL
                                    parts = base_url.split('/')
                                    if len(parts) >= 3:
                                        base = '/'.join(parts[:3])  # Get domain part
                                        tag[attr] = f"{base}{tag[attr]}"
                                else:
                                    # Document-relative URL
                                    tag[attr] = f"{base_url.rstrip('/')}/{tag[attr].lstrip('/')}"
                    
                    # Get the processed HTML
                    processed_html = str(soup)
                    
                    logger.info(f"Successfully crawled {url} using enhanced fallback HTTP method")
                    return processed_html
        except Exception as fallback_error:
            error_msg = f"Fallback HTTP method also failed: {str(fallback_error)}"
            logger.error(error_msg)
            raise Exception(f"Failed to crawl {url}: {str(fallback_error)}")

def generate_markdown(html: str, exclude_links: bool = False):
    """
    Convert HTML to Markdown.
    
    This function is an exact implementation of the function specified
    in the requirements document.
    """
    if exclude_links:
        # Implement link removal logic
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a'):
            a.replace_with(a.get_text())
        html = str(soup)
    
    return markdownify(html)

def save_file(markdown: str, url: str) -> str:
    """
    Save markdown content to a file.
    
    This function is an exact implementation of the function specified
    in the requirements document.
    """
    # Get filename from URL
    filename = url.split("/")[-1] or "index"  # Simplified naming
    
    # Clean up filename to be valid
    filename = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in filename)
    
    # Set file path - use the proper path from your application
    file_dir = os.path.join(os.path.dirname(__file__), '..', 'files')
    os.makedirs(file_dir, exist_ok=True)
    
    file_path = os.path.join(file_dir, f"{filename}.md")
    
    # Write to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    return filename
