"""
Pandoc-style PDF to Markdown converter.

This module provides a converter using pdfminer.six for extracting text
from PDF documents. The extracted text is formatted as Markdown.

Note: Pandoc itself doesn't support PDF as input format. This converter
uses pdfminer.six (the same library used by MarkItDown) to extract text
and formats it as Markdown.

Dependencies:
    pip install pdfminer-six

Example usage:
    >>> from workers.pdf_to_md.pandoc import PandocConverter
    >>> converter = PandocConverter()
    >>> markdown = converter.convert("document.pdf")
    >>> print(markdown)
    # Document Title
    ...

    >>> # Check if available
    >>> if converter.is_available():
    ...     result = converter.convert_file("doc.pdf", "data/md")
"""

from pathlib import Path
from .base import BaseConverter


class PandocConverter(BaseConverter):
    """
    PDF to Markdown converter using pdfminer.six.

    This converter uses pdfminer.six to extract text from PDF files
    and formats it as Markdown. It works best with text-based PDFs.

    Note: For scanned documents, use an OCR-capable converter like
    PaddleOCR or Unstructured.

    Attributes:
        name: Converter name ("pandoc").
        page_separator: String to use between pages.

    Example:
        >>> converter = PandocConverter()
        >>> if converter.is_available():
        ...     markdown = converter.convert("report.pdf")
    """

    name = "pandoc"

    def __init__(
        self,
        log_level: str = "INFO",
        page_separator: str = "\n\n---\n\n"
    ):
        """
        Initialize the Pandoc converter.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            page_separator: String to insert between pages.

        Example:
            >>> converter = PandocConverter()
            >>> converter = PandocConverter(page_separator="\\n\\n")
        """
        super().__init__(log_level)
        self.page_separator = page_separator

    def convert(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown using pdfminer.six.

        Extracts text from each page of the PDF and formats it
        as Markdown with page separators.

        Args:
            pdf_path: Path to the PDF file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            ImportError: If pdfminer.six is not installed.
            Exception: If conversion fails.

        Example:
            >>> converter = PandocConverter()
            >>> markdown = converter.convert("data/pdfs/text_doc.pdf")
            >>> print(markdown)
            ## Page 1

            Document content from page 1...

            ---

            ## Page 2
            ...
        """
        self.logger.debug(f"Converting {pdf_path} with pdfminer.six")

        try:
            from pdfminer.high_level import extract_text, extract_pages
            from pdfminer.layout import LAParams, LTTextContainer
        except ImportError as e:
            self.logger.error(
                "pdfminer-six not installed. Install with: pip install pdfminer-six"
            )
            raise ImportError(
                "pdfminer-six package not found. Install with: pip install pdfminer-six"
            ) from e

        try:
            # Extract text page by page
            laparams = LAParams(
                line_margin=0.5,
                word_margin=0.1,
                char_margin=2.0,
                boxes_flow=0.5,
            )

            pages = []
            page_num = 0

            for page_layout in extract_pages(pdf_path, laparams=laparams):
                page_num += 1
                page_text = []

                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        text = element.get_text().strip()
                        if text:
                            page_text.append(text)

                if page_text:
                    page_content = "\n\n".join(page_text)
                    pages.append(f"## Page {page_num}\n\n{page_content}")

            content = self.page_separator.join(pages)

            self.logger.debug(f"Conversion complete: {len(content)} characters, {page_num} pages")
            return content

        except Exception as e:
            self.logger.error(f"pdfminer conversion failed: {e}")
            # Try simple extraction as fallback
            return self._simple_extraction(pdf_path)

    def _simple_extraction(self, pdf_path: str) -> str:
        """
        Simple text extraction fallback.

        Uses pdfminer's high-level extract_text function.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Extracted text or empty string if extraction fails.
        """
        self.logger.debug("Attempting simple text extraction")

        try:
            from pdfminer.high_level import extract_text
            text = extract_text(pdf_path)
            return text if text else ""
        except Exception as e:
            self.logger.warning(f"Simple extraction also failed: {e}")
            return ""

    def is_available(self) -> bool:
        """
        Check if pdfminer.six is available.

        Returns:
            True if pdfminer.six package is installed, False otherwise.

        Example:
            >>> converter = PandocConverter()
            >>> converter.is_available()
            True
        """
        try:
            from pdfminer.high_level import extract_text
            return True
        except ImportError:
            return False

    def get_description(self) -> str:
        """
        Get a description of this converter.

        Returns:
            Human-readable description of the converter.

        Example:
            >>> converter = PandocConverter()
            >>> print(converter.get_description())
            Pandoc: Text extraction with pdfminer - fast, best for text-based PDFs
        """
        return "Pandoc: Text extraction with pdfminer - fast, best for text-based PDFs"
