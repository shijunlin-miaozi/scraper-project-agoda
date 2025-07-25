import logging
import json

logger = logging.getLogger(__name__)


def log_cookies(proxy, cookies):
    if not cookies:
        logger.info(f"[COOKIES] No cookies set for proxy {proxy}")
    else:
        logger.info(f"[COOKIES] Current cookies for proxy {proxy}:")
        for cookie in cookies:
            logger.info(f"  {cookie['name']} = {cookie['value']}")


HEADER_VALIDATION_LOG = "logs/header_validation_debug.txt"
def log_validation_failure(headers, reason):
    try:
        with open(HEADER_VALIDATION_LOG, "a", encoding="utf-8") as f:
            f.write(f"--- INVALID HEADER ({reason}) ---\n")
            f.write(json.dumps(headers, indent=2))
            f.write("\n\n")
    except Exception as e:
        logger.warning(f"Failed to write header validation log: {e}")

