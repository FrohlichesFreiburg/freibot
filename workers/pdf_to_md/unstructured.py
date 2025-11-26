"""
Unstructured.io PDF to Markdown converter.

This module provides a converter using the Unstructured library
for extracting structured content from PDF documents.

Unstructured provides advanced layout detection, table extraction,
and OCR capabilities. It works well with complex documents.

Dependencies:
    pip install unstructured[pdf] unstructured-inference

Example usage:
    >>> from workers.pdf_to_md.unstructured import UnstructuredConverter
    >>> converter = UnstructuredConverter()
    >>> markdown = converter.convert("document.pdf")
    >>> print(markdown)
    # Document Title
    ...

    >>> # Use high-resolution strategy for better results
    >>> converter = UnstructuredConverter(strategy="hi_res")
    >>> result = converter.convert_file("complex.pdf", "data/md")
"""

from .base import BaseConverter


class UnstructuredConverter(BaseConverter):
    """
    PDF to Markdown converter using Unstructured.io library.

    Unstructured provides powerful document parsing with layout detection,
    table inference, and OCR support. The hi_res strategy uses deep learning
    models for better accuracy.

    Attributes:
        name: Converter name ("unstructured").
        strategy: Extraction strategy ("fast", "hi_res", "auto").
        languages: OCR languages (e.g., ["deu", "eng"]).

    Example:
        >>> converter = UnstructuredConverter(strategy="hi_res")
        >>> markdown = converter.convert("report.pdf")
    """

    name = "unstructured"

    def __init__(
        self,
        log_level: str = "INFO",
        strategy: str = "auto",
        languages: list[str] = None
    ):
        """
        Initialize the Unstructured converter.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            strategy: Extraction strategy:
                - "fast": Quick extraction without layout models
                - "hi_res": High-resolution with layout detection
                - "auto": Automatically choose based on document
            languages: List of OCR languages (e.g., ["deu", "eng"]).
                      Default is German and English.

        Example:
            >>> converter = UnstructuredConverter(strategy="hi_res")
            >>> converter = UnstructuredConverter(languages=["deu", "eng", "fra"])
        """
        super().__init__(log_level)
        self.strategy = strategy
        self.languages = languages or ["deu", "eng"]

    def convert(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown using Unstructured.

        Extracts structured elements from the PDF and formats them
        as Markdown. Tables are detected and formatted appropriately.

        Args:
            pdf_path: Path to the PDF file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            ImportError: If unstructured is not installed.
            Exception: If conversion fails.

        Example:
            >>> converter = UnstructuredConverter()
            >>> markdown = converter.convert("data/pdfs/report.pdf")
            >>> print(markdown)
            # Report Title

            ## Section 1
            Content...

            | Col1 | Col2 |
            |------|------|
            | A    | B    |
        """
        self.logger.debug(f"Converting {pdf_path} with Unstructured (strategy={self.strategy})")

        try:
            from unstructured.partition.pdf import partition_pdf
        except ImportError as e:
            self.logger.error(
                "Unstructured not installed. Install with: "
                "pip install unstructured[pdf] unstructured-inference"
            )
            raise ImportError(
                "unstructured package not found. "
                "Install with: pip install unstructured[pdf] unstructured-inference"
            ) from e

        # Partition the PDF
        elements = partition_pdf(
            filename=pdf_path,
            strategy=self.strategy,
            languages=self.languages,
            infer_table_structure=True,
        )

        # Convert elements to Markdown
        markdown_parts = []
        for element in elements:
            category = getattr(element, 'category', None)
            text = element.text if hasattr(element, 'text') else str(element)

            if not text or not text.strip():
                continue

            # Format based on element type
            if category == "Title":
                markdown_parts.append(f"# {text}")
            elif category == "Header":
                markdown_parts.append(f"## {text}")
            elif category == "Table":
                # Try to get HTML table representation
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'text_as_html'):
                    html_table = element.metadata.text_as_html
                    if html_table:
                        markdown_parts.append(self._html_table_to_markdown(html_table))
                    else:
                        markdown_parts.append(text)
                else:
                    markdown_parts.append(text)
            elif category == "ListItem":
                markdown_parts.append(f"- {text}")
            else:
                markdown_parts.append(text)

        content = "\n\n".join(markdown_parts)
        self.logger.debug(f"Conversion complete: {len(content)} characters, {len(elements)} elements")
        return content

    def _html_table_to_markdown(self, html: str) -> str:
        """
        Convert HTML table to Markdown table.

        Args:
            html: HTML table string.

        Returns:
            Markdown table string.
        """
        try:
            import re

            # Extract rows
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
            if not rows:
                return html

            markdown_rows = []
            for i, row in enumerate(rows):
                # Extract cells (th or td)
                cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL | re.IGNORECASE)
                # Clean HTML tags from cells
                clean_cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                markdown_rows.append("| " + " | ".join(clean_cells) + " |")

                # Add header separator after first row
                if i == 0:
                    separator = "| " + " | ".join(["---"] * len(clean_cells)) + " |"
                    markdown_rows.append(separator)

            return "\n".join(markdown_rows)
        except Exception:
            return html

    def is_available(self) -> bool:
        """
        Check if Unstructured is available.

        Returns:
            True if unstructured package is installed, False otherwise.

        Example:
            >>> converter = UnstructuredConverter()
            >>> converter.is_available()
            True
        """
        try:
            from unstructured.partition.pdf import partition_pdf
            return True
        except ImportError:
            return False

    def get_description(self) -> str:
        """
        Get a description of this converter.

        Returns:
            Human-readable description of the converter.

        Example:
            >>> converter = UnstructuredConverter()
            >>> print(converter.get_description())
            Unstructured: Advanced document parsing with layout detection and OCR
        """
        return "Unstructured: Advanced document parsing with layout detection and OCR"
