from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import logging
import os

from models.crawl_request import CrawlRequest
from models.crawl_response import CrawlResponse, FileInfo
from crawler.crawler_functions import crawl_single_page, generate_markdown, save_file

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_urls(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Crawl URLs and convert them to Markdown files
    
    This implements the exact pattern from the requirements document.
    """
    try:
        results = []
        for url in request.urls:
            try:
                # Convert to string to ensure we're passing a string URL
                url_str = str(url)
                
                # Ensure URL has a scheme
                if not url_str.startswith(('http://', 'https://')):
                    url_str = 'https://' + url_str
                
                # Use the enhanced crawler with wait times for dynamic content
                # Adjust wait_time and scroll_count based on the complexity of the site
                html = await crawl_single_page(
                    url_str,
                    wait_time=8,  # Longer wait time for complex JS
                    scroll_count=5  # More scrolls to capture more content
                )
                
                markdown = generate_markdown(html, exclude_links=not request.include_links)
                filename = save_file(markdown, url_str)
                results.append({"url": url_str, "filename": filename})
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                # Continue with other URLs even if one fails
                
        if not results:
            return CrawlResponse(
                status="error",
                files=[],
                message="No URLs were successfully crawled"
            )
                
        return CrawlResponse(
            status="success",
            files=[FileInfo(url=result["url"], filename=result["filename"], title=result["url"].split("/")[-1] or "index") 
                  for result in results],
            message=f"Successfully processed {len(results)} URLs"
        )
    except Exception as e:
        logger.error(f"Error processing URLs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a specific Markdown file
    """
    try:
        # Update file path to match the location in save_file function
        file_dir = os.path.join(os.path.dirname(__file__), '..', 'files')
        file_path = os.path.join(file_dir, f"{filename}.md")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            file_path,
            media_type="text/markdown",
            filename=f"{filename}.md"
        )
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download/bulk")
async def download_bulk_files(filenames: List[str]):
    """
    Download multiple Markdown files as a ZIP archive
    """
    try:
        import zipfile
        from datetime import datetime
        
        # Create a timestamp for the ZIP filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"bulk_download_{timestamp}.zip"
        file_dir = os.path.join(os.path.dirname(__file__), '..', 'files')
        zip_path = os.path.join(file_dir, zip_filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        
        # Create the ZIP file
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for filename in filenames:
                file_path = os.path.join(file_dir, f"{filename}.md")
                if os.path.exists(file_path):
                    # Add file to ZIP with just the filename, not the full path
                    zip_file.write(file_path, f"{filename}.md")
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_filename
        )
    except Exception as e:
        logger.error(f"Error creating ZIP archive: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))