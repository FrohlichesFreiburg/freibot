"""
PaddleOCR PDF to Markdown converter.

This module provides a converter using PaddleOCR for extracting
text from PDF documents using Optical Character Recognition.

PaddleOCR provides excellent OCR capabilities for multiple languages
including German. It works well with scanned documents.

Dependencies:
    pip install paddleocr paddlepaddle PyMuPDF

Example usage:
    >>> from workers.pdf_to_md.paddle_ocr import PaddleOCRConverter
    >>> converter = PaddleOCRConverter()
    >>> markdown = converter.convert("scanned_document.pdf")
    >>> print(markdown)
    # Document Title
    ...

    >>> # Configure for German documents
    >>> converter = PaddleOCRConverter(lang="de")
    >>> result = converter.convert_file("german_doc.pdf", "data/md")
"""

from pathlib import Path
from .base import BaseConverter


class PaddleOCRConverter(BaseConverter):
    """
    PDF to Markdown converter using PaddleOCR.

    PaddleOCR provides powerful OCR capabilities with support for
    80+ languages. It works well with scanned documents and images.

    Attributes:
        name: Converter name ("paddle_ocr").
        lang: OCR language (e.g., "de", "en", "ch").
        use_angle_cls: Whether to use angle classification.

    Example:
        >>> converter = PaddleOCRConverter(lang="de")
        >>> markdown = converter.convert("scanned.pdf")
    """

    name = "paddle_ocr"

    # Language mapping from ISO codes to PaddleOCR codes
    LANG_MAP = {
        "de": "german",
        "deu": "german",
        "german": "german",
        "en": "en",
        "eng": "en",
        "english": "en",
        "ch": "ch",
        "chinese": "ch",
        "fr": "french",
        "fra": "french",
        "french": "french",
    }

    def __init__(
        self,
        log_level: str = "INFO",
        lang: str = "de",
        use_textline_orientation: bool = True
    ):
        """
        Initialize the PaddleOCR converter.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            lang: OCR language code (e.g., "de", "en", "ch").
            use_textline_orientation: If True, detect and correct text orientation.

        Example:
            >>> converter = PaddleOCRConverter(lang="de")
            >>> converter = PaddleOCRConverter(lang="en", use_textline_orientation=False)
        """
        super().__init__(log_level)
        self.lang = self.LANG_MAP.get(lang.lower(), lang)
        self.use_textline_orientation = use_textline_orientation
        self._ocr = None

    def _get_ocr(self):
        """
        Lazy initialization of PaddleOCR instance.

        Returns:
            PaddleOCR instance.

        Raises:
            ImportError: If paddleocr is not installed.
        """
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR

                self.logger.debug(f"Initializing PaddleOCR with lang={self.lang}")
                # Suppress PaddleOCR logging by setting environment variable
                import os
                os.environ["FLAGS_minloglevel"] = "3"

                self._ocr = PaddleOCR(
                    use_textline_orientation=self.use_textline_orientation,
                    lang=self.lang,
                )
                self.logger.debug("PaddleOCR initialized")

            except ImportError as e:
                self.logger.error(
                    "PaddleOCR not installed. Install with: "
                    "pip install paddleocr paddlepaddle PyMuPDF"
                )
                raise ImportError(
                    "paddleocr package not found. "
                    "Install with: pip install paddleocr paddlepaddle PyMuPDF"
                ) from e
        return self._ocr

    def convert(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown using PaddleOCR.

        Extracts images from each page of the PDF and performs OCR
        to extract text. Results are formatted as Markdown.

        Args:
            pdf_path: Path to the PDF file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            ImportError: If paddleocr or PyMuPDF is not installed.
            Exception: If conversion fails.

        Example:
            >>> converter = PaddleOCRConverter()
            >>> markdown = converter.convert("data/pdfs/scanned_doc.pdf")
            >>> print(markdown)
            # Page 1

            Extracted text from first page...

            ---

            # Page 2
            ...
        """
        self.logger.debug(f"Converting {pdf_path} with PaddleOCR (lang={self.lang})")

        try:
            import fitz  # PyMuPDF
        except ImportError as e:
            self.logger.error(
                "PyMuPDF not installed. Install with: pip install PyMuPDF"
            )
            raise ImportError(
                "PyMuPDF package not found. Install with: pip install PyMuPDF"
            ) from e

        ocr = self._get_ocr()

        # Open PDF and process each page
        markdown_parts = []
        pdf_document = fitz.open(pdf_path)

        try:
            total_pages = len(pdf_document)
            self.logger.info(f"Processing {total_pages} pages")

            for page_num in range(total_pages):
                self.logger.info(f"Processing page {page_num + 1}/{total_pages}")
                page = pdf_document[page_num]

                # Convert page to image
                mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
                pix = page.get_pixmap(matrix=mat, alpha=False)

                # Convert to numpy array for PaddleOCR
                import numpy as np
                from PIL import Image
                import io

                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                img_array = np.array(img)

                # Perform OCR (use predict for PaddleOCR 3.x)
                result = ocr.predict(img_array)

                # Extract text from OCR results
                page_text = self._extract_text_from_result(result)

                if page_text.strip():
                    markdown_parts.append(f"## Page {page_num + 1}\n\n{page_text}")

        finally:
            pdf_document.close()

        content = "\n\n---\n\n".join(markdown_parts)
        self.logger.debug(f"Conversion complete: {len(content)} characters, {total_pages} pages")
        return content

    def _extract_text_from_result(self, result) -> str:
        """
        Extract text from PaddleOCR result.

        PaddleOCR 3.x returns results in a new dict format:
        [{'rec_texts': [...], 'rec_scores': [...], ...}]

        Legacy format (2.x):
        [[[box], (text, confidence)], ...]

        Args:
            result: OCR result from PaddleOCR.

        Returns:
            Extracted text as a string.
        """
        if not result:
            return ""

        first_result = result[0]
        if not first_result:
            return ""

        # New format (PaddleOCR 3.x): dict with 'rec_texts' key
        if isinstance(first_result, dict) and 'rec_texts' in first_result:
            texts = first_result.get('rec_texts', [])
            return "\n".join(texts) if texts else ""

        # Legacy format (PaddleOCR 2.x): list of [[box], (text, conf)]
        lines = []
        for item in first_result:
            if item and len(item) >= 2:
                text_info = item[1]
                if isinstance(text_info, tuple) and len(text_info) >= 1:
                    text = text_info[0]
                    lines.append(text)

        return "\n".join(lines)

    def is_available(self) -> bool:
        """
        Check if PaddleOCR is available.

        Returns:
            True if paddleocr and PyMuPDF packages are installed.

        Example:
            >>> converter = PaddleOCRConverter()
            >>> converter.is_available()
            True
        """
        try:
            from paddleocr import PaddleOCR
            import fitz
            return True
        except ImportError:
            return False

    def get_description(self) -> str:
        """
        Get a description of this converter.

        Returns:
            Human-readable description of the converter.

        Example:
            >>> converter = PaddleOCRConverter()
            >>> print(converter.get_description())
            PaddleOCR: OCR-based extraction with multi-language support
        """
        return "PaddleOCR: OCR-based extraction with multi-language support"
