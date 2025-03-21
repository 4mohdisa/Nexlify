"""
Crawler functions exactly matching the requirements document
"""
import asyncio
import logging
from playwright.async_api import async_playwright
from markdownify import markdownify
import os
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

async def crawl_single_page(url: str, wait_time: int = 5, scroll_count: int = 3):
    """
    Crawl a single page using Playwright to handle dynamic content.
    
    Args:
        url: The URL to crawl
        wait_time: Time to wait after initial load (seconds)
        scroll_count: Number of times to scroll for lazy-loaded content
    """
    url = str(url)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    logger.info(f"Attempting to crawl URL: {url}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate and wait for network idle
            await page.goto(url, wait_until="networkidle")
            
            # Scroll to trigger lazy-loaded content
            for i in range(scroll_count):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)  # Wait for content to load after each scroll
            
            # Additional wait for any remaining dynamic content
            await asyncio.sleep(wait_time)
            
            # Capture fully rendered HTML
            html = await page.content()
            await browser.close()
            
            # Process with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            base_url = url
            for tag in soup.find_all(['a', 'img', 'link', 'script']):
                for attr in ['href', 'src']:
                    if tag.has_attr(attr) and not tag[attr].startswith(('http://', 'https://', 'data:', 'javascript:')):
                        if tag[attr].startswith('/'):
                            # Fix the formula from the issue resolution doc
                            parts = base_url.split('/')
                            if len(parts) >= 3:
                                base = '/'.join(parts[:3])  # Get domain part
                                tag[attr] = f"{base}{tag[attr]}"
                        else:
                            tag[attr] = f"{base_url.rstrip('/')}/{tag[attr].lstrip('/')}"
            
            processed_html = str(soup)
            logger.info(f"Successfully crawled {url} with Playwright")
            return processed_html
    
    except Exception as e:
        logger.error(f"Failed to crawl {url}: {str(e)}")
        raise Exception(f"Failed to crawl {url}: {str(e)}")

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
    
    return f"{filename}.md"
