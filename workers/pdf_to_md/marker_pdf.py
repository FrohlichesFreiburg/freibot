"""
Marker-PDF to Markdown converter.

This module provides a converter using the Marker library for
converting PDF documents to Markdown format with high accuracy.

Marker uses deep learning models for layout detection and OCR,
producing high-quality Markdown output even for complex documents.

Dependencies:
    pip install marker-pdf

Example usage:
    >>> from workers.pdf_to_md.marker_pdf import MarkerPDFConverter
    >>> converter = MarkerPDFConverter()
    >>> markdown = converter.convert("document.pdf")
    >>> print(markdown)
    # Document Title
    ...

    >>> # Convert with specific output format
    >>> converter = MarkerPDFConverter(output_format="markdown")
    >>> result = converter.convert_file("complex.pdf", "data/md")
"""

from .base import BaseConverter


class MarkerPDFConverter(BaseConverter):
    """
    PDF to Markdown converter using Marker-PDF library.

    Marker provides high-quality PDF conversion using deep learning models.
    It handles complex layouts, tables, equations, and code blocks well.

    Attributes:
        name: Converter name ("marker_pdf").
        output_format: Output format ("markdown", "json", "html").
        force_ocr: Whether to force OCR on all pages.

    Example:
        >>> converter = MarkerPDFConverter()
        >>> markdown = converter.convert("report.pdf")
    """

    name = "marker_pdf"

    def __init__(
        self,
        log_level: str = "INFO",
        output_format: str = "markdown",
        force_ocr: bool = False
    ):
        """
        Initialize the Marker-PDF converter.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            output_format: Output format ("markdown", "json", "html").
            force_ocr: If True, force OCR on all pages even if text is present.

        Example:
            >>> converter = MarkerPDFConverter(force_ocr=True)
            >>> converter = MarkerPDFConverter(output_format="markdown")
        """
        super().__init__(log_level)
        self.output_format = output_format
        self.force_ocr = force_ocr
        self._converter = None
        self._model_dict = None

    def _initialize_converter(self):
        """
        Lazy initialization of Marker converter.

        Creates the model dictionary and converter instance on first use.

        Raises:
            ImportError: If marker-pdf is not installed.
        """
        if self._converter is not None:
            return

        self.logger.debug("Initializing Marker-PDF converter...")

        try:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            from marker.config.parser import ConfigParser

            # Create model dictionary (downloads models on first run)
            self._model_dict = create_model_dict()

            # Configure converter
            config = {
                "output_format": self.output_format,
                "force_ocr": self.force_ocr,
            }
            config_parser = ConfigParser(config)

            # Initialize converter
            self._converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=self._model_dict,
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
            )

            self.logger.debug("Marker-PDF converter initialized")

        except ImportError as e:
            self.logger.error(
                "Marker-PDF not installed. Install with: pip install marker-pdf"
            )
            raise ImportError(
                "marker-pdf package not found. "
                "Install with: pip install marker-pdf"
            ) from e

    def convert(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown using Marker-PDF.

        Uses deep learning models for accurate layout detection and
        text extraction. Handles complex documents well.

        Args:
            pdf_path: Path to the PDF file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            ImportError: If marker-pdf is not installed.
            Exception: If conversion fails.

        Example:
            >>> converter = MarkerPDFConverter()
            >>> markdown = converter.convert("data/pdfs/report.pdf")
            >>> print(markdown)
            # Report Title

            ## Section 1
            Content with **formatting** preserved...

            | Table | Data |
            |-------|------|
            | A     | B    |
        """
        self.logger.debug(f"Converting {pdf_path} with Marker-PDF")

        self._initialize_converter()

        try:
            from marker.output import text_from_rendered

            # Convert the PDF
            rendered = self._converter(pdf_path)

            # Extract text and images
            text, file_ext, images = text_from_rendered(rendered)

            self.logger.debug(
                f"Conversion complete: {len(text)} characters, "
                f"{len(images)} images extracted"
            )

            return text

        except Exception as e:
            self.logger.error(f"Marker-PDF conversion failed: {e}")
            raise

    def is_available(self) -> bool:
        """
        Check if Marker-PDF is available.

        Returns:
            True if marker-pdf package is installed, False otherwise.

        Example:
            >>> converter = MarkerPDFConverter()
            >>> converter.is_available()
            True
        """
        try:
            from marker.converters.pdf import PdfConverter
            return True
        except ImportError:
            return False

    def get_description(self) -> str:
        """
        Get a description of this converter.

        Returns:
            Human-readable description of the converter.

        Example:
            >>> converter = MarkerPDFConverter()
            >>> print(converter.get_description())
            Marker-PDF: High-quality conversion with deep learning models
        """
        return "Marker-PDF: High-quality conversion with deep learning models"
