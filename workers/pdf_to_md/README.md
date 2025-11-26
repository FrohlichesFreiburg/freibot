# PDF to Markdown Converter Worker - Implementation Plan

## Overview

This worker converts PDF files to Markdown format using multiple converter backends.
Each converter produces different results based on the underlying library's capabilities.

## Project Structure

```
workers/pdf_to_md/
├── __init__.py           # Package initialization, exports all converters
├── main.py               # CLI entry point with batch processing
├── base.py               # Abstract base class for converters
├── utils.py              # Logging, file utilities, progress tracking
├── pandoc.py             # pdfminer-based text extraction
├── paddle_ocr.py         # PaddleOCR with multi-language OCR
├── markitdown.py         # Microsoft MarkItDown converter
├── unstructured.py       # Unstructured.io with layout detection
├── marker_pdf.py         # Marker-PDF with deep learning models
└── requirements.txt      # Dependencies for all converters

data/
├── pdfs/                 # Source PDF files (17 files)
└── md/
    ├── pandoc/           # Output from pdfminer
    ├── paddle_ocr/       # Output from PaddleOCR
    ├── markitdown/       # Output from MarkItDown
    ├── unstructured/     # Output from Unstructured
    └── marker_pdf/       # Output from Marker-PDF
```

## Converter Comparison

| Converter    | Speed  | Quality | OCR Support | Tables | Dependencies |
|-------------|--------|---------|-------------|--------|--------------|
| MarkItDown  | Fast   | Medium  | Via Azure   | Basic  | ~50MB        |
| Pandoc      | Fast   | Medium  | No          | No     | ~5MB         |
| Unstructured| Medium | High    | Yes         | Good   | ~500MB       |
| Marker-PDF  | Slow   | High    | Yes         | Good   | ~2GB         |
| PaddleOCR   | Medium | High    | Native      | Basic  | ~2GB         |

## Usage

### Command Line Interface

```bash
# Convert all PDFs with all available converters
python -m workers.pdf_to_md.main --converter all

# Convert with a specific converter
python -m workers.pdf_to_md.main --converter markitdown

# Convert with custom paths
python -m workers.pdf_to_md.main --converter marker_pdf \
    --input-dir ./my_pdfs --output-dir ./output

# Convert with verbose logging
python -m workers.pdf_to_md.main --converter paddle_ocr --log-level DEBUG

# Convert a single file
python -m workers.pdf_to_md.main --converter markitdown \
    --single-file data/pdfs/document.pdf

# Force re-conversion of existing files
python -m workers.pdf_to_md.main --converter markitdown --no-skip-existing
```

### Python API

```python
# Use a specific converter
from workers.pdf_to_md import get_converter

converter = get_converter("markitdown")
markdown = converter.convert("document.pdf")
print(markdown)

# Convert and save to file
result = converter.convert_file("document.pdf", "data/md")
print(f"Saved to: {result}")

# Get all available converters
from workers.pdf_to_md import get_all_converters

converters = get_all_converters()
for name, converter in converters.items():
    print(f"{name}: {converter.get_description()}")
```

## Installation

### Install all dependencies (large, ~5GB):

```bash
pip install -r workers/pdf_to_md/requirements.txt
```

### Install only specific converters:

```bash
# MarkItDown (recommended to start)
pip install markitdown[pdf]

# Pandoc (pdfminer is included with markitdown)
# No additional installation needed

# Unstructured
pip install unstructured[pdf] unstructured-inference

# Marker-PDF
pip install marker-pdf

# PaddleOCR
pip install paddleocr paddlepaddle PyMuPDF
```

## Implementation Steps (Completed)

1. **Base Infrastructure** - utils.py, base.py, __init__.py
2. **MarkItDown Converter** - Microsoft's fast document converter
3. **Unstructured Converter** - Layout detection and OCR
4. **Marker-PDF Converter** - Deep learning models for high quality
5. **PaddleOCR Converter** - Multi-language OCR support
6. **Pandoc Converter** - pdfminer-based text extraction
7. **Main Entry Point** - CLI with argparse
8. **Requirements File** - All dependencies documented
9. **Testing** - Verified with 17 PDF files

## Logging

All conversions are logged to:
- Console (colored output)
- File: `workers/pdf_to_md/conversion.log`

Log format: `[YYYY-MM-DD HH:MM:SS] LEVEL - logger_name - message`

## Notes

- The "pandoc" converter now uses pdfminer.six (not Pandoc binary)
- PaddleOCR and Marker-PDF require significant disk space (~2GB each)
- First run of Marker-PDF downloads model files automatically
- MarkItDown is the fastest and most lightweight option
- For German documents, PaddleOCR with `lang="de"` works best for OCR
