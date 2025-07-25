# agoda/utilities/headers/header_templates.py

"""
Platform-specific header templates used during runtime header generation.
These determine user-agent structure, sec-ch headers, and mobile-specific keys.
"""

PLATFORM_TEMPLATES = {
    "Windows": {
        "ua_override": "(Windows NT 10.0; Win64; x64)",
        "platform": '"Windows"',
        "mobile": "?0"
    },
    "macOS": {
        "ua_override": "(Macintosh; Intel Mac OS X 10_15_7)",
        "platform": '"macOS"',
        "mobile": "?0"
    },
    "Android": {
        "ua_override": "(Linux; Android 11; SM-G991B)",
        "platform": '"Android"',
        "mobile": "?1",
        "viewport": [360, 412, 375, 393],
        "memory": [2, 4, 6, 8],
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    },
    "iOS": {
        "ua_override": "(iPhone; CPU iPhone OS 15_5 like Mac OS X)",
        "platform": '"iOS"',
        "mobile": "?1",
        "viewport": [375, 390, 414, 428],
        "memory": [2, 4],
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    }
}
