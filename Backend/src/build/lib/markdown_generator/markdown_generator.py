from bs4 import BeautifulSoup
from markdownify import markdownify as md
import logging

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    def __init__(self, include_links: bool = True, data_type: str = "full-page"):
        self.include_links = include_links
        self.data_type = data_type

    def _prepare_html(self, html: str) -> str:
        """Prepare HTML content based on data type"""
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()

        if self.data_type == "text-only":
            # Keep only text content
            for tag in soup.find_all(True):
                if tag.name not in ["p", "br"]:
                    tag.unwrap()

        elif self.data_type == "headings-only":
            # Keep only headings
            for tag in soup.find_all(True):
                if not tag.name.startswith("h"):
                    tag.decompose()

        if not self.include_links:
            # Remove all links while keeping their text content
            for link in soup.find_all("a"):
                link.unwrap()

        return str(soup)

    def convert_to_markdown(self, html: str, title: str = None) -> str:
        """Convert HTML to Markdown with specified options"""
        try:
            # Add title if provided
            if title:
                html = f"<h1>{title}</h1>{html}"

            # Prepare HTML based on options
            prepared_html = self._prepare_html(html)

            # Convert to Markdown
            markdown = md(prepared_html,
                        heading_style="atx",  # Use # style headings
                        bullets="-",  # Use - for unordered lists
                        autolinks=self.include_links)  # Include URLs as links if enabled

            return markdown.strip()

        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}")
            return ""