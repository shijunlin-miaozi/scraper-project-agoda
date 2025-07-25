# agoda/utilities/headers/__init__.py

"""
Header generation package for scraping Agoda hotel pages.
Handles realistic User-Agent rotation, header validation,
language detection, referer simulation, and fallback logic.
"""

__version__ = "1.0.0"

# Public API
from .generator import generate_headers, load_header_pool
from .pool_builder import generate_header_pool_by_country

__all__ = ["generate_headers", "load_header_pool", "generate_header_pool_by_country"]

