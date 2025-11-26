"""
Abstract base class for PDF to Markdown converters.

This module defines the interface that all converter implementations must follow.
Each converter (MarkItDown, Unstructured, Marker-PDF, PaddleOCR, Pandoc) inherits
from BaseConverter and implements the convert() method.

Example usage:
    >>> from workers.pdf_to_md.markitdown import MarkItDownConverter
    >>> converter = MarkItDownConverter()
    >>> result = converter.convert_file("document.pdf", "output/markitdown")
"""

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .utils import (
    setup_logging,
    get_output_path,
    file_exists_and_not_empty,
    format_duration,
    save_markdown,
)


class BaseConverter(ABC):
    """
    Abstract base class for PDF to Markdown converters.

    Provides common functionality for all converters including logging,
    output path management, and skip logic for existing files.

    Attributes:
        name: The name of the converter (e.g., "markitdown", "paddle_ocr").
        logger: Logger instance for this converter.

    Example:
        >>> class MyConverter(BaseConverter):
        ...     name = "my_converter"
        ...     def convert(self, pdf_path: str) -> str:
        ...         return "# Converted content"
        ...
        >>> converter = MyConverter()
        >>> converter.convert_file("doc.pdf", "output")
    """

    name: str = "base"

    def __init__(self, log_level: str = "INFO"):
        """
        Initialize the converter with logging.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

        Example:
            >>> converter = MarkItDownConverter(log_level="DEBUG")
        """
        self.logger = setup_logging(log_level, logger_name=f"pdf_to_md.{self.name}")

    @abstractmethod
    def convert(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown.

        This method must be implemented by all converter subclasses.

        Args:
            pdf_path: Path to the PDF file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            NotImplementedError: If not implemented by subclass.
            Exception: Various exceptions depending on the converter implementation.

        Example:
            >>> markdown = converter.convert("document.pdf")
            >>> print(markdown[:100])
            # Document Title
            ...
        """
        raise NotImplementedError("Subclasses must implement convert()")

    def convert_file(
        self,
        pdf_path: str,
        output_base_dir: str,
        skip_existing: bool = True
    ) -> Optional[Path]:
        """
        Convert a PDF file and save the result to a markdown file.

        Handles the full conversion workflow including:
        - Checking if output already exists (skip if requested)
        - Converting the PDF to markdown
        - Saving the result to the appropriate output directory
        - Logging progress and errors

        Args:
            pdf_path: Path to the PDF file to convert.
            output_base_dir: Base directory for output files (e.g., "data/md").
            skip_existing: If True, skip files that already have output.

        Returns:
            Path to the output file if conversion was performed, None if skipped.

        Example:
            >>> converter = MarkItDownConverter()
            >>> result = converter.convert_file(
            ...     "data/pdfs/report.pdf",
            ...     "data/md",
            ...     skip_existing=True
            ... )
            >>> print(result)
            data/md/markitdown/report.md
        """
        pdf_path_obj = Path(pdf_path)
        output_path = get_output_path(pdf_path, output_base_dir, self.name)

        # Check if output already exists
        if skip_existing and file_exists_and_not_empty(output_path):
            self.logger.info(f"Skipping {pdf_path_obj.name} - output already exists")
            return None

        self.logger.info(f"Converting {pdf_path_obj.name} with {self.name}")

        start_time = time.time()
        try:
            markdown_content = self.convert(str(pdf_path_obj))

            if not markdown_content or not markdown_content.strip():
                self.logger.warning(f"Empty result for {pdf_path_obj.name}")
                return None

            save_markdown(markdown_content, output_path)

            duration = time.time() - start_time
            self.logger.info(
                f"Converted {pdf_path_obj.name} -> {output_path.name} "
                f"({format_duration(duration)})"
            )
            return output_path

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Failed to convert {pdf_path_obj.name}: {str(e)} "
                f"({format_duration(duration)})"
            )
            raise

    def is_available(self) -> bool:
        """
        Check if this converter is available (dependencies installed).

        Subclasses should override this method to check for required
        dependencies and return False if they are not available.

        Returns:
            True if the converter can be used, False otherwise.

        Example:
            >>> converter = PandocConverter()
            >>> if converter.is_available():
            ...     result = converter.convert("document.pdf")
            ... else:
            ...     print("Pandoc is not installed")
        """
        return True

    def get_description(self) -> str:
        """
        Get a description of this converter.

        Returns:
            Human-readable description of the converter.

        Example:
            >>> converter = MarkItDownConverter()
            >>> print(converter.get_description())
            MarkItDown: Microsoft's document converter for PDF to Markdown
        """
        return f"{self.name}: PDF to Markdown converter"
