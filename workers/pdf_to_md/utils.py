"""
Utility functions for PDF to Markdown conversion.

This module provides logging configuration, file path utilities, and progress tracking
for the PDF to Markdown conversion workers.

Example usage:
    >>> from workers.pdf_to_md.utils import setup_logging, get_output_path
    >>> logger = setup_logging("INFO")
    >>> output_path = get_output_path("data/pdfs/doc.pdf", "data/md", "markitdown")
"""

import logging
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log levels.

    Uses colorama for cross-platform color support if available,
    otherwise falls back to plain text formatting.

    Example:
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(ColoredFormatter())
        >>> logger.addHandler(handler)
    """

    COLORS = {
        'DEBUG': Fore.CYAN if COLORAMA_AVAILABLE else '',
        'INFO': Fore.GREEN if COLORAMA_AVAILABLE else '',
        'WARNING': Fore.YELLOW if COLORAMA_AVAILABLE else '',
        'ERROR': Fore.RED if COLORAMA_AVAILABLE else '',
        'CRITICAL': Fore.RED + Style.BRIGHT if COLORAMA_AVAILABLE else '',
    }
    RESET = Style.RESET_ALL if COLORAMA_AVAILABLE else ''

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    logger_name: str = "pdf_to_md"
) -> logging.Logger:
    """
    Configure logging with file and console handlers.

    Sets up a logger with both file and console output. The console output
    uses colored formatting if colorama is available. The file output uses
    plain text formatting.

    Args:
        level: Logging level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to log file. If None, uses default location.
        logger_name: Name for the logger instance.

    Returns:
        Configured logger instance.

    Example:
        >>> logger = setup_logging("DEBUG")
        >>> logger.info("Starting conversion")
        [2025-01-15 10:30:00] INFO - pdf_to_md - Starting conversion

        >>> logger = setup_logging("INFO", log_file="/tmp/conversion.log")
        >>> logger.warning("File already exists")
    """
    logger = logging.getLogger(logger_name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Log format
    log_format = "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (plain text)
    if log_file is None:
        # Default log file location
        log_dir = Path(__file__).parent
        log_file = log_dir / "conversion.log"

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def get_output_path(
    pdf_path: str,
    output_base_dir: str,
    converter_name: str
) -> Path:
    """
    Generate the output path for a converted markdown file.

    Creates the appropriate output directory structure based on the converter name
    and returns the full path for the markdown output file.

    Args:
        pdf_path: Path to the source PDF file.
        output_base_dir: Base directory for output files (e.g., "data/md").
        converter_name: Name of the converter (e.g., "markitdown", "paddle_ocr").

    Returns:
        Path object for the output markdown file.

    Example:
        >>> path = get_output_path("data/pdfs/report.pdf", "data/md", "markitdown")
        >>> print(path)
        data/md/markitdown/report.md

        >>> path = get_output_path("/abs/path/doc.pdf", "output", "paddle_ocr")
        >>> print(path)
        output/paddle_ocr/doc.md
    """
    pdf_name = Path(pdf_path).stem
    output_dir = Path(output_base_dir) / converter_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{pdf_name}.md"


def file_exists_and_not_empty(path: Path) -> bool:
    """
    Check if a file exists and is not empty.

    Args:
        path: Path to the file to check.

    Returns:
        True if file exists and has content, False otherwise.

    Example:
        >>> file_exists_and_not_empty(Path("existing_file.md"))
        True
        >>> file_exists_and_not_empty(Path("empty_file.md"))
        False
        >>> file_exists_and_not_empty(Path("nonexistent.md"))
        False
    """
    return path.exists() and path.stat().st_size > 0


def get_pdf_files(input_dir: str) -> list[Path]:
    """
    Get all PDF files from the input directory.

    Recursively searches the input directory for PDF files and returns
    them sorted alphabetically.

    Args:
        input_dir: Directory to search for PDF files.

    Returns:
        List of Path objects for all PDF files found.

    Example:
        >>> pdfs = get_pdf_files("data/pdfs")
        >>> for pdf in pdfs:
        ...     print(pdf.name)
        document1.pdf
        document2.pdf
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    pdf_files = list(input_path.glob("**/*.pdf"))
    return sorted(pdf_files)


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted string like "1m 30s" or "45s".

    Example:
        >>> format_duration(90.5)
        '1m 30s'
        >>> format_duration(45.2)
        '45s'
        >>> format_duration(3661)
        '1h 1m 1s'
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"


def save_markdown(content: str, output_path: Path) -> None:
    """
    Save markdown content to a file.

    Ensures the parent directory exists and writes the content
    with UTF-8 encoding.

    Args:
        content: Markdown content to save.
        output_path: Path where to save the file.

    Example:
        >>> save_markdown("# Hello World", Path("output/doc.md"))
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding='utf-8')
