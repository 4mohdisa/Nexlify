import os
import zipfile
import logging
from typing import List
from urllib.parse import urlparse
import re
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(tempfile.gettempdir(), "nexlify")
        os.makedirs(self.output_dir, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be safe for all operating systems"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces and dots with underscores
        filename = re.sub(r'[\s.]+', '_', filename)
        # Ensure filename is not too long
        return filename[:255]

    def _get_unique_filename(self, base_filename: str) -> str:
        """Get a unique filename by appending a number if necessary"""
        counter = 1
        filename = base_filename
        while os.path.exists(os.path.join(self.output_dir, f"{filename}.md")):
            filename = f"{base_filename}_{counter}"
            counter += 1
        return f"{filename}.md"

    def save_markdown(self, content: str, url: str, title: str = None) -> str:
        """Save markdown content to a file and return the filename"""
        try:
            # Generate filename from title or URL
            if title:
                base_filename = self._sanitize_filename(title)
            else:
                parsed_url = urlparse(url)
                path_parts = parsed_url.path.split("/")
                base_filename = path_parts[-1] if path_parts[-1] else parsed_url.netloc

            # Get unique filename
            filename = self._get_unique_filename(base_filename)
            
            # Save file
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return filename

        except Exception as e:
            logger.error(f"Error saving markdown file: {str(e)}")
            return ""

    def create_zip_archive(self, filenames: List[str]) -> str:
        """Create a ZIP archive containing the specified markdown files"""
        try:
            # Create temporary ZIP file
            zip_filename = "markdown_files.zip"
            zip_path = os.path.join(self.output_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for filename in filenames:
                    file_path = os.path.join(self.output_dir, filename)
                    if os.path.exists(file_path):
                        zipf.write(file_path, filename)

            return zip_filename

        except Exception as e:
            logger.error(f"Error creating ZIP archive: {str(e)}")
            return ""

    def get_file_path(self, filename: str) -> str:
        """Get full path for a file in the output directory"""
        return os.path.join(self.output_dir, filename)

    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up files older than specified hours"""
        try:
            current_time = Path().stat().st_mtime
            for file in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file)
                file_age = (current_time - Path(file_path).stat().st_mtime) / 3600
                if file_age > max_age_hours:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old file: {file}")

        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")