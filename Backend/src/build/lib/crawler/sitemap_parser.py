import aiohttp
from typing import List
import logging
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

async def get_sitemap_urls(base_url: str, session: aiohttp.ClientSession) -> List[str]:
    """Get URLs from sitemap.xml"""
    urls = set()
    try:
        # Try common sitemap paths
        sitemap_paths = ["/sitemap.xml", "/sitemap_index.xml", "/sitemap/sitemap.xml"]
        
        for path in sitemap_paths:
            sitemap_url = urljoin(base_url, path)
            try:
                async with session.get(sitemap_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        urls.update(parse_sitemap(content))
                        break
            except Exception as e:
                logger.debug(f"Failed to fetch sitemap from {sitemap_url}: {str(e)}")
                continue
    
    except Exception as e:
        logger.warning(f"Error processing sitemap for {base_url}: {str(e)}")
    
    return list(urls)

def parse_sitemap(content: str) -> List[str]:
    """Parse sitemap XML content and extract URLs"""
    urls = set()
    try:
        root = ET.fromstring(content)
        
        # Handle both sitemap index and urlset
        namespaces = {
            'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'
        }
        
        # Try to find URLs in sitemap index
        sitemaps = root.findall('.//sm:loc', namespaces)
        
        # If no sitemaps found, look for URLs directly
        if not sitemaps:
            sitemaps = root.findall('.//loc')
        
        for loc in sitemaps:
            if loc.text:
                urls.add(loc.text.strip())
    
    except Exception as e:
        logger.error(f"Error parsing sitemap content: {str(e)}")
    
    return list(urls)