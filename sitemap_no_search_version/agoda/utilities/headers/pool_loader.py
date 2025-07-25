# agoda/utilities/headers/pool_loader.py

"""
Loads pre-generated headers grouped by country.

Used when:
- You want to match proxy IP → country → headers.
- You want full control over what headers are used per proxy session.
"""

import os
import json
import random
import logging

logger = logging.getLogger(__name__)

HEADER_POOL_FILE = "chrome_headers_pool_by_country.json"
_country_header_pool = {}

def load_country_header_pool(path: str = HEADER_POOL_FILE):
    """
    Load the JSON header pool by country into memory.

    Returns:
        dict[str, list[dict]]: Mapping of country code → list of headers.
    """
    global _country_header_pool

    if not os.path.exists(path):
        logger.warning(f"⚠️ Header pool file not found: {path}")
        return {}

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                _country_header_pool = data
                logger.info(f"✅ Loaded header pool from: {path}")
            else:
                logger.warning("⚠️ Header pool file is not a dict.")
    except Exception as e:
        logger.error(f"❌ Failed to load header pool: {e}")
        _country_header_pool = {}

    return _country_header_pool


def get_random_header_by_country(country_code: str):
    """
    Return a random header from the given country pool.

    Args:
        country_code (str): ISO country code (e.g., "FR", "DE")

    Returns:
        dict or None: A random valid header, or None if not available.
    """
    if not _country_header_pool:
        load_country_header_pool()

    headers = _country_header_pool.get(country_code)
    if headers:
        return random.choice(headers)

    logger.warning(f"⚠️ No headers found for country: {country_code}")
    return None


def get_all_countries_in_pool():
    """
    Return a list of all available country codes in the pool.

    Returns:
        list[str]: All country keys.
    """
    if not _country_header_pool:
        load_country_header_pool()
    return list(_country_header_pool.keys())
