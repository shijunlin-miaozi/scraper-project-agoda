# agoda/utilities/headers/pool_builder.py

"""
Generates a JSON file with prebuilt headers grouped by country.

Each header is generated with:
- Country-specific language
- Realistic Chrome UA and headers
- Distinct template logic for Windows/macOS/Android/iOS
"""

import json
from .generator import generate_headers
from ..geo import COUNTRY_LANGUAGE_MAP
import logging

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT = "chrome_headers_pool_by_country.json"

def generate_header_pool_by_country(countries=None, per_country=20, output_file=DEFAULT_OUTPUT):
    """
    Generate a pool of headers grouped by country.

    Args:
        countries (list): ISO country codes (e.g., ["FR", "DE"]). If None, use keys from COUNTRY_LANGUAGE_MAP.
        per_country (int): Number of headers to generate per country.
        output_file (str): Output JSON filename.
    """
    countries = countries or list(COUNTRY_LANGUAGE_MAP.keys())
    pool = {}

    for country in countries:
        logger.info(f"🌐 Generating headers for country: {country}")
        headers_list = []
        for _ in range(per_country):
            try:
                headers = generate_headers(override_country=country)
                headers_list.append(headers)
            except Exception as e:
                logger.warning(f"⚠️ Failed to generate header for {country}: {e}")
        pool[country] = headers_list

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2)
    logger.info(f"✅ Saved header pool to: {output_file}")
