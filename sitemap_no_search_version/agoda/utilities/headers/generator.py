# agoda/utilities/headers/generator.py

"""
Generates realistic Chrome headers using:
- Pre-generated User-Agents
- GeoIP-based language selection (based on proxy IP or override_country)
- Referer randomization (based on city to simulate user search intent)
- Validation using jsonschema
- Distinct template logic for macOS, Windows, Android, and iOS Chrome clients
"""

import random
import re
import logging
from collections import OrderedDict
from jsonschema import validate, ValidationError

from .user_agents import CACHED_USER_AGENTS, chrome_x_client_data_map
from .referers import generate_referer_from_city
from .schema import HEADER_SCHEMA, validate_sec_ch_ua, validate_sec_ch_platform, validate_sec_fetch_headers
from .geo import get_country_code, COUNTRY_LANGUAGE_MAP
from .header_templates import PLATFORM_TEMPLATES
from ..log_utils import log_validation_failure

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = "en-US"

def generate_headers(ip_address=None, city=None, override_country=None):
    """
    Generate realistic Chrome request headers for a given IP and city.
    If override_country is provided, it overrides IP geo-detection (used during pre-generation).
    """
    country = override_country or (get_country_code(ip_address) if ip_address else None)
    language = COUNTRY_LANGUAGE_MAP.get(country, DEFAULT_LANGUAGE)
    referer = generate_referer_from_city(city) if city else "https://www.agoda.com/"
    sec_fetch_site = "same-origin" if "agoda.com" in referer else "cross-site"

    is_mobile = random.choices([True, False], weights=[0.3, 0.7])[0]
    platform_key = (
        random.choices(["Android", "iOS"], weights=[0.7, 0.3])[0]
        if is_mobile else
        random.choices(["Windows", "macOS"], weights=[0.4, 0.6])[0]
    )

    template = PLATFORM_TEMPLATES[platform_key]
    attempts = 0

    while attempts < 5:
        user_agent = random.choice(CACHED_USER_AGENTS)
        match = re.search(r"Chrome/(\d+)", user_agent)
        chrome_version = match.group(1) if match else str(random.randint(114, 120))

        ua_mod = re.sub(r"\(.*?\)", template["ua_override"], user_agent)

        headers = OrderedDict([
            ("accept-encoding", random.choice(["gzip, deflate, br", "gzip, deflate", "gzip"])),
            ("accept", template.get("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")),
            ("accept-language", language),
            ("priority", "u=0, i"),
            ("sec-ch-ua", f'"Not)A;Brand";v="8", "Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}"'),
            ("sec-ch-ua-mobile", template["mobile"]),
            ("sec-ch-ua-platform", template["platform"]),
            ("sec-fetch-dest", "document"),
            ("sec-fetch-mode", "navigate"),
            ("sec-fetch-site", sec_fetch_site),
            ("sec-fetch-user", "?1"),
            ("upgrade-insecure-requests", "1"),
            ("user-agent", ua_mod),
            ("referer", referer)
        ])

        if is_mobile:
            headers["viewport-width"] = str(random.choice(template["viewport"]))
            headers["device-memory"] = str(random.choice(template["memory"]))
            headers["x-client-data"] = chrome_x_client_data_map.get(
                chrome_version,
                random.choice(list(chrome_x_client_data_map.values()))
            )

        try:
            validate(instance=headers, schema=HEADER_SCHEMA)
        except ValidationError:
            log_validation_failure(headers, "json-schema invalid")
            attempts += 1
            continue

        if validate_sec_ch_ua(headers) and validate_sec_ch_platform(headers) and validate_sec_fetch_headers(headers):
            logger.debug(f"✅ Valid headers for platform {platform_key}: UA = {ua_mod}")
            return headers

        log_validation_failure(headers, "sec-ch mismatch")
        attempts += 1

    logger.error(f"❌ Failed to generate valid headers after {attempts} attempts (country={country}, city={city})")
    raise RuntimeError("Failed to generate valid headers after 5 attempts.")
