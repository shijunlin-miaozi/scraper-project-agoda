# agoda/utilities/headers/schema.py

"""
Header validation schema and functions.
Used to ensure Chrome-like headers conform to expected fields.
"""

import re

HEADER_SCHEMA = {
    "type": "object",
    "properties": {
        "accept": {"type": "string"},
        "accept-language": {"type": "string"},
        "priority": {"type": "string"},
        "sec-ch-ua": {"type": "string"},
        "sec-ch-ua-mobile": {"type": "string"},
        "sec-ch-ua-platform": {"type": "string"},
        "sec-fetch-dest": {"type": "string"},
        "sec-fetch-mode": {"type": "string"},
        "sec-fetch-site": {"type": "string"},
        "sec-fetch-user": {"type": "string"},
        "upgrade-insecure-requests": {"type": "string"},
        "user-agent": {"type": "string"},
        "viewport-width": {"type": "string"},
        "device-memory": {"type": "string"},
        "x-client-data": {"type": "string"},
        "referer": {"type": "string"}
    },
    "required": [
        "accept", "accept-language", "priority", "sec-ch-ua", "sec-ch-ua-mobile",
        "sec-ch-ua-platform", "sec-fetch-dest", "sec-fetch-mode", "sec-fetch-site",
        "sec-fetch-user", "upgrade-insecure-requests", "user-agent", "referer"
    ]
}

def validate_sec_ch_ua(headers):
    match = re.search(r"Chrome/(\d+)", headers.get("user-agent", ""))
    chrome_version = match.group(1) if match else None
    expected = f'"Chromium";v="{chrome_version}"' if chrome_version else None
    return expected and expected in headers.get("sec-ch-ua", "")

def validate_sec_ch_platform(headers):
    ua = headers.get("user-agent", "")
    platform = headers.get("sec-ch-ua-platform", "")
    if "Windows" in ua:
        return "Windows" in platform
    if "Macintosh" in ua:
        return "macOS" in platform
    return False

def validate_sec_fetch_headers(headers):
    return (
        headers.get("sec-fetch-mode") == "navigate"
        and headers.get("sec-fetch-dest") == "document"
        and headers.get("sec-fetch-site") in {"none", "same-origin", "cross-site"}
    )
