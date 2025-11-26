"""
PDF to Markdown Converter Workers.

This package provides multiple converters for converting PDF documents to Markdown format.
Each converter uses a different underlying library and may produce different results
depending on the PDF content.

Available Converters:
    - MarkItDownConverter: Microsoft's MarkItDown library
    - UnstructuredConverter: Unstructured.io library with layout detection
    - MarkerPDFConverter: Marker-PDF with deep learning models
    - PaddleOCRConverter: PaddleOCR with OCR capabilities
    - PandocConverter: Pandoc document converter

Example usage:
    >>> from workers.pdf_to_md import MarkItDownConverter
    >>> converter = MarkItDownConverter()
    >>> markdown = converter.convert("document.pdf")

    >>> from workers.pdf_to_md import get_converter
    >>> converter = get_converter("markitdown")
    >>> result = converter.convert_file("doc.pdf", "output")

    >>> from workers.pdf_to_md import get_all_converters
    >>> for name, converter_class in get_all_converters().items():
    ...     print(f"{name}: {converter_class}")
"""

from typing import Dict, Type, Optional

from .base import BaseConverter

# Lazy imports to avoid loading all dependencies at once
_CONVERTER_REGISTRY: Dict[str, str] = {
    "markitdown": "workers.pdf_to_md.markitdown.MarkItDownConverter",
    "unstructured": "workers.pdf_to_md.unstructured.UnstructuredConverter",
    "marker_pdf": "workers.pdf_to_md.marker_pdf.MarkerPDFConverter",
    "paddle_ocr": "workers.pdf_to_md.paddle_ocr.PaddleOCRConverter",
    "pandoc": "workers.pdf_to_md.pandoc.PandocConverter",
}


def get_converter(name: str, **kwargs) -> BaseConverter:
    """
    Get a converter instance by name.

    Args:
        name: Name of the converter (markitdown, unstructured, marker_pdf,
              paddle_ocr, pandoc).
        **kwargs: Additional arguments passed to the converter constructor.

    Returns:
        Initialized converter instance.

    Raises:
        ValueError: If the converter name is not recognized.
        ImportError: If the converter's dependencies are not installed.

    Example:
        >>> converter = get_converter("markitdown")
        >>> converter = get_converter("paddle_ocr", log_level="DEBUG")
    """
    if name not in _CONVERTER_REGISTRY:
        available = ", ".join(_CONVERTER_REGISTRY.keys())
        raise ValueError(f"Unknown converter: {name}. Available: {available}")

    module_path = _CONVERTER_REGISTRY[name]
    module_name, class_name = module_path.rsplit(".", 1)

    try:
        import importlib
        module = importlib.import_module(module_name)
        converter_class = getattr(module, class_name)
        return converter_class(**kwargs)
    except ImportError as e:
        raise ImportError(
            f"Failed to import converter '{name}'. "
            f"Make sure dependencies are installed: {e}"
        )


def get_all_converters(**kwargs) -> Dict[str, BaseConverter]:
    """
    Get all available converters.

    Attempts to instantiate all converters, skipping those with missing dependencies.

    Args:
        **kwargs: Additional arguments passed to each converter constructor.

    Returns:
        Dictionary mapping converter names to converter instances.

    Example:
        >>> converters = get_all_converters(log_level="INFO")
        >>> for name, converter in converters.items():
        ...     print(f"{name}: {converter.get_description()}")
    """
    converters = {}
    for name in _CONVERTER_REGISTRY:
        try:
            converters[name] = get_converter(name, **kwargs)
        except ImportError:
            pass  # Skip converters with missing dependencies
    return converters


def list_converters() -> list[str]:
    """
    List all registered converter names.

    Returns:
        List of converter names.

    Example:
        >>> names = list_converters()
        >>> print(names)
        ['markitdown', 'unstructured', 'marker_pdf', 'paddle_ocr', 'pandoc']
    """
    return list(_CONVERTER_REGISTRY.keys())


__all__ = [
    "BaseConverter",
    "get_converter",
    "get_all_converters",
    "list_converters",
]
