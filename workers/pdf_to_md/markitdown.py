"""
MarkItDown PDF to Markdown converter.

This module provides a converter using Microsoft's MarkItDown library
for converting PDF documents to Markdown format.

MarkItDown is a fast converter that works well with text-based PDFs.
For scanned documents, consider using Azure Document Intelligence
or another OCR-capable converter.

Dependencies:
    pip install markitdown[pdf]

Example usage:
    >>> from workers.pdf_to_md.markitdown import MarkItDownConverter
    >>> converter = MarkItDownConverter()
    >>> markdown = converter.convert("document.pdf")
    >>> print(markdown)
    # Document Title
    ...

    >>> # Convert with logging
    >>> converter = MarkItDownConverter(log_level="DEBUG")
    >>> result = converter.convert_file("doc.pdf", "data/md")
    >>> print(result)
    data/md/markitdown/doc.md
"""

from .base import BaseConverter


class MarkItDownConverter(BaseConverter):
    """
    PDF to Markdown converter using Microsoft's MarkItDown library.

    MarkItDown is a fast and simple converter that works best with
    text-based PDFs. It preserves document structure and formatting.

    Attributes:
        name: Converter name ("markitdown").
        _md: MarkItDown instance (lazy initialized).

    Example:
        >>> converter = MarkItDownConverter()
        >>> # Check if available
        >>> if converter.is_available():
        ...     markdown = converter.convert("report.pdf")
        ...     print(markdown[:100])
    """

    name = "markitdown"

    def __init__(self, log_level: str = "INFO"):
        """
        Initialize the MarkItDown converter.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

        Example:
            >>> converter = MarkItDownConverter(log_level="DEBUG")
        """
        super().__init__(log_level)
        self._md = None

    def _get_markitdown(self):
        """
        Lazy initialization of MarkItDown instance.

        Returns:
            MarkItDown instance.

        Raises:
            ImportError: If markitdown is not installed.
        """
        if self._md is None:
            try:
                from markitdown import MarkItDown
                self._md = MarkItDown()
                self.logger.debug("MarkItDown instance initialized")
            except ImportError as e:
                self.logger.error(
                    "MarkItDown not installed. Install with: pip install markitdown[pdf]"
                )
                raise ImportError(
                    "markitdown package not found. "
                    "Install with: pip install markitdown[pdf]"
                ) from e
        return self._md

    def convert(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown using MarkItDown.

        Args:
            pdf_path: Path to the PDF file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            ImportError: If markitdown is not installed.
            Exception: If conversion fails.

        Example:
            >>> converter = MarkItDownConverter()
            >>> markdown = converter.convert("data/pdfs/report.pdf")
            >>> print(markdown)
            # Report Title

            ## Section 1
            Content of section 1...
        """
        self.logger.debug(f"Converting {pdf_path} with MarkItDown")

        md = self._get_markitdown()
        result = md.convert(pdf_path)

        # MarkItDown returns a result object with markdown or text_content attribute
        if hasattr(result, 'markdown'):
            content = result.markdown
        elif hasattr(result, 'text_content'):
            content = result.text_content
        else:
            content = str(result)

        self.logger.debug(f"Conversion complete: {len(content)} characters")
        return content

    def is_available(self) -> bool:
        """
        Check if MarkItDown is available.

        Returns:
            True if markitdown package is installed, False otherwise.

        Example:
            >>> converter = MarkItDownConverter()
            >>> converter.is_available()
            True
        """
        try:
            from markitdown import MarkItDown
            return True
        except ImportError:
            return False

    def get_description(self) -> str:
        """
        Get a description of this converter.

        Returns:
            Human-readable description of the converter.

        Example:
            >>> converter = MarkItDownConverter()
            >>> print(converter.get_description())
            MarkItDown: Microsoft's document converter - fast, best for text-based PDFs
        """
        return "MarkItDown: Microsoft's document converter - fast, best for text-based PDFs"
