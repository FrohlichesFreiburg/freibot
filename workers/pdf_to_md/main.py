#!/usr/bin/env python3
"""
PDF to Markdown Conversion Worker - Main Entry Point.

This script provides a command-line interface for converting PDF files
to Markdown format using various converter backends.

Available converters:
    - markitdown: Microsoft's MarkItDown (fast, text-based PDFs)
    - unstructured: Unstructured.io (layout detection, OCR)
    - marker_pdf: Marker-PDF (deep learning, high quality)
    - paddle_ocr: PaddleOCR (OCR, multi-language)
    - pandoc: Pandoc (fast, requires text-based PDFs)

Usage examples:
    # Convert all PDFs with all converters
    python -m workers.pdf_to_md.main --converter all

    # Convert with a specific converter
    python -m workers.pdf_to_md.main --converter markitdown

    # Convert with custom paths
    python -m workers.pdf_to_md.main --converter marker_pdf \\
        --input-dir ./my_pdfs --output-dir ./output

    # Convert with verbose logging
    python -m workers.pdf_to_md.main --converter paddle_ocr --log-level DEBUG

    # Force re-conversion of existing files
    python -m workers.pdf_to_md.main --converter markitdown --no-skip-existing
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from . import get_converter, get_all_converters, list_converters
from .utils import setup_logging, get_pdf_files, format_duration


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace.

    Example:
        >>> args = parse_args()
        >>> print(args.converter)
        'all'
    """
    parser = argparse.ArgumentParser(
        description="Convert PDF files to Markdown using various converters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Convert all PDFs with all converters
    python -m workers.pdf_to_md.main --converter all

    # Convert with MarkItDown only
    python -m workers.pdf_to_md.main --converter markitdown

    # Convert with custom paths and debug logging
    python -m workers.pdf_to_md.main --converter unstructured \\
        --input-dir ./pdfs --output-dir ./markdown --log-level DEBUG
        """
    )

    parser.add_argument(
        "--converter",
        choices=["all"] + list_converters(),
        default="all",
        help="Converter to use (default: all)"
    )

    parser.add_argument(
        "--input-dir",
        default="data/pdfs",
        help="Directory containing PDF files (default: data/pdfs)"
    )

    parser.add_argument(
        "--output-dir",
        default="data/md",
        help="Base directory for output files (default: data/md)"
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip files that already have output (default: True)"
    )

    parser.add_argument(
        "--no-skip-existing",
        action="store_false",
        dest="skip_existing",
        help="Force re-conversion of existing files"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--single-file",
        type=str,
        default=None,
        help="Convert a single PDF file instead of a directory"
    )

    return parser.parse_args()


def convert_with_single_converter(
    converter_name: str,
    pdf_files: list[Path],
    output_dir: str,
    skip_existing: bool,
    log_level: str
) -> dict:
    """
    Convert PDF files using a single converter.

    Args:
        converter_name: Name of the converter to use.
        pdf_files: List of PDF file paths.
        output_dir: Base output directory.
        skip_existing: Whether to skip existing output files.
        log_level: Logging level.

    Returns:
        Dictionary with conversion statistics.

    Example:
        >>> stats = convert_with_single_converter(
        ...     "markitdown",
        ...     [Path("doc1.pdf"), Path("doc2.pdf")],
        ...     "data/md",
        ...     skip_existing=True,
        ...     log_level="INFO"
        ... )
        >>> print(stats)
        {'converted': 2, 'skipped': 0, 'failed': 0}
    """
    logger = setup_logging(log_level)
    stats = {"converted": 0, "skipped": 0, "failed": 0}

    try:
        converter = get_converter(converter_name, log_level=log_level)
    except ImportError as e:
        logger.error(f"Failed to load converter '{converter_name}': {e}")
        stats["failed"] = len(pdf_files)
        return stats

    if not converter.is_available():
        logger.error(f"Converter '{converter_name}' is not available (missing dependencies)")
        stats["failed"] = len(pdf_files)
        return stats

    logger.info(f"Starting conversion with {converter_name} ({len(pdf_files)} files)")

    for pdf_file in tqdm(pdf_files, desc=converter_name, unit="file"):
        try:
            result = converter.convert_file(
                str(pdf_file),
                output_dir,
                skip_existing=skip_existing
            )
            if result is None:
                stats["skipped"] += 1
            else:
                stats["converted"] += 1
        except Exception as e:
            logger.error(f"Failed to convert {pdf_file.name}: {e}")
            stats["failed"] += 1

    return stats


def convert_with_all_converters(
    pdf_files: list[Path],
    output_dir: str,
    skip_existing: bool,
    log_level: str
) -> dict:
    """
    Convert PDF files using all available converters.

    Args:
        pdf_files: List of PDF file paths.
        output_dir: Base output directory.
        skip_existing: Whether to skip existing output files.
        log_level: Logging level.

    Returns:
        Dictionary mapping converter names to their statistics.

    Example:
        >>> all_stats = convert_with_all_converters(
        ...     [Path("doc.pdf")],
        ...     "data/md",
        ...     skip_existing=True,
        ...     log_level="INFO"
        ... )
        >>> for name, stats in all_stats.items():
        ...     print(f"{name}: {stats['converted']} converted")
    """
    logger = setup_logging(log_level)
    all_stats = {}

    converter_names = list_converters()
    logger.info(f"Converting with all converters: {', '.join(converter_names)}")

    for converter_name in converter_names:
        logger.info(f"\n{'=' * 50}")
        logger.info(f"Converter: {converter_name}")
        logger.info(f"{'=' * 50}")

        stats = convert_with_single_converter(
            converter_name,
            pdf_files,
            output_dir,
            skip_existing,
            log_level
        )
        all_stats[converter_name] = stats

    return all_stats


def print_summary(stats: dict, duration: float) -> None:
    """
    Print a summary of the conversion results.

    Args:
        stats: Dictionary of conversion statistics.
        duration: Total duration in seconds.

    Example:
        >>> print_summary(
        ...     {"markitdown": {"converted": 5, "skipped": 2, "failed": 0}},
        ...     duration=120.5
        ... )
    """
    print("\n" + "=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)

    total_converted = 0
    total_skipped = 0
    total_failed = 0

    for converter_name, converter_stats in stats.items():
        converted = converter_stats.get("converted", 0)
        skipped = converter_stats.get("skipped", 0)
        failed = converter_stats.get("failed", 0)

        total_converted += converted
        total_skipped += skipped
        total_failed += failed

        status = "OK" if failed == 0 else "ERRORS"
        print(f"  {converter_name:15} | Converted: {converted:3} | "
              f"Skipped: {skipped:3} | Failed: {failed:3} | {status}")

    print("-" * 60)
    print(f"  {'TOTAL':15} | Converted: {total_converted:3} | "
          f"Skipped: {total_skipped:3} | Failed: {total_failed:3}")
    print(f"\nTotal time: {format_duration(duration)}")
    print("=" * 60)


def main() -> int:
    """
    Main entry point for the PDF to Markdown converter.

    Returns:
        Exit code (0 for success, 1 for errors).

    Example:
        >>> # From command line:
        >>> # python -m workers.pdf_to_md.main --converter markitdown

        >>> # Programmatically:
        >>> exit_code = main()
    """
    args = parse_args()
    logger = setup_logging(args.log_level)

    start_time = time.time()

    # Get PDF files
    if args.single_file:
        pdf_files = [Path(args.single_file)]
        if not pdf_files[0].exists():
            logger.error(f"File not found: {args.single_file}")
            return 1
    else:
        try:
            pdf_files = get_pdf_files(args.input_dir)
        except FileNotFoundError as e:
            logger.error(str(e))
            return 1

    if not pdf_files:
        logger.warning(f"No PDF files found in {args.input_dir}")
        return 0

    logger.info(f"Found {len(pdf_files)} PDF files")

    # Run conversion
    if args.converter == "all":
        stats = convert_with_all_converters(
            pdf_files,
            args.output_dir,
            args.skip_existing,
            args.log_level
        )
    else:
        stats = {
            args.converter: convert_with_single_converter(
                args.converter,
                pdf_files,
                args.output_dir,
                args.skip_existing,
                args.log_level
            )
        }

    duration = time.time() - start_time

    # Print summary
    print_summary(stats, duration)

    # Check for failures
    total_failed = sum(s.get("failed", 0) for s in stats.values())
    return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
