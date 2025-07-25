# agoda/utilities/headers/geo.py

"""
GeoIP2 lookup for IP address → country code resolution.
Used for regional language/header customization.
"""

import geoip2.database
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

GEOIP_DB_PATH = "agoda/utilities/GeoLite2-Country.mmdb"

try:
    GEOIP_READER = geoip2.database.Reader(GEOIP_DB_PATH)
except Exception as e:
    logger.warning(f"⚠️ Failed to load GeoIP database: {e}")
    GEOIP_READER = None

@lru_cache(maxsize=1000)
def get_country_code(ip_address):
    try:
        if GEOIP_READER:
            response = GEOIP_READER.country(ip_address)
            return response.country.iso_code
    except Exception as e:
        logger.warning(f"🌐 GeoIP lookup failed for {ip_address}: {e}")
    return None
