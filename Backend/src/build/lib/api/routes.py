from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import logging
import os

from models.crawl_request import CrawlRequest
from models.crawl_response import CrawlResponse, FileInfo
from crawler.crawler import WebCrawler
from markdown_generator.markdown_generator import MarkdownGenerator
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)
router = APIRouter()
file_handler = FileHandler()

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_urls(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Crawl URLs and convert them to Markdown files
    """
    try:
        async with WebCrawler() as crawler:
            # Crawl URLs
            results = await crawler.crawl_urls(
                urls=[str(url) for url in request.urls],
                enable_crawling=request.enable_crawling
            )

            if not results:
                return CrawlResponse(
                    status="error",
                    files=[],
                    message="No URLs were successfully crawled"
                )

            # Convert to Markdown
            markdown_generator = MarkdownGenerator(
                include_links=request.include_links,
                data_type=request.data_type
            )

            files = []
            for result in results:
                if result["success"]:
                    # Convert HTML to Markdown
                    markdown = markdown_generator.convert_to_markdown(
                        html=result["html"],
                        title=result["title"]
                    )

                    # Save to file
                    filename = file_handler.save_markdown(
                        content=markdown,
                        url=result["url"],
                        title=result["title"]
                    )

                    if filename:
                        files.append(FileInfo(
                            url=result["url"],
                            filename=filename,
                            title=result["title"]
                        ))

            # Schedule cleanup of old files
            background_tasks.add_task(file_handler.cleanup_old_files)

            return CrawlResponse(
                status="success",
                files=files,
                message=f"Successfully processed {len(files)} URLs"
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
        file_path = file_handler.get_file_path(filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            file_path,
            media_type="text/markdown",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/bulk")
async def download_bulk(filenames: List[str]):
    """
    Download multiple Markdown files as a ZIP archive
    """
    try:
        zip_filename = file_handler.create_zip_archive(filenames)
        if not zip_filename:
            raise HTTPException(
                status_code=500,
                detail="Failed to create ZIP archive"
            )

        zip_path = file_handler.get_file_path(zip_filename)
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_filename
        )

    except Exception as e:
        logger.error(f"Error creating ZIP archive: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))