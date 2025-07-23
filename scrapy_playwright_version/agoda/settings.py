import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# ──────────────────────────────────────────────
# Ensure essential folders exist
os.makedirs("logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

# ──────────────────────────────────────────────
# Basic Scrapy settings
BOT_NAME = "agoda"
SPIDER_MODULES = ["agoda.spiders"]
NEWSPIDER_MODULE = "agoda.spiders"

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 1


# ──────────────────────────────────────────────
# Toggle between test and production
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"

# ──────────────────────────────────────────────
# Playwright integration
PLAYWRIGHT_BROWSER_TYPE = "chromium"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
# PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
# Toggle headless mode based on TEST_MODE
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": not TEST_MODE,       # Headful in TEST_MODE, headless in production
    "slow_mo": 500 if TEST_MODE else 0,
    "args": ["--auto-open-devtools-for-tabs"],
}

# Input CSV file
HOTELS_FILE = os.getenv("HOTELS_FILE", "hotels.csv")

# Batch processing
BATCH_INDEX = int(os.getenv("BATCH_INDEX", 0))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))

# Logging
LOG_LEVEL = "INFO"  # or "DEBUG" for development
# LOG_FILE = "logs/batch_{BATCH_INDEX}.log"  # optional fallback file, used when crawling manually (not via launch.sh)

# ──────────────────────────────────────────────
# Test mode overrides
# Used only for local testing (save output as local json file) --> comment it out to save output to database
if TEST_MODE:
    FEEDS = {
        "output/hotels.json": {
            "format": "json",
            "overwrite": True,
            "encoding": "utf8",
        }
    }
    # Optional: disable pipelines in test mode
    # ITEM_PIPELINES = {}

# ──────────────────────────────────────────────
# PostgreSQL DB config from .env
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "agoda")
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")

# ──────────────────────────────────────────────
# Safety check for production credentials
if not TEST_MODE and ("your_user" in POSTGRES_USER or "your_password" in POSTGRES_PASSWORD):
    raise EnvironmentError("❌ Default DB credentials used in production. Please configure .env")

# ──────────────────────────────────────────────
# Validate essential files exist
missing = []
if not POSTGRES_USER or not POSTGRES_PASSWORD:
    missing.append("POSTGRES_USER and POSTGRES_PASSWORD")
if not HOTELS_FILE or not os.path.exists(HOTELS_FILE):
    missing.append("HOTELS_FILE not found")
if not os.path.exists("proxies.txt"):
    missing.append("proxies.txt file not found")
if not os.path.exists("user_agents.txt"):
    missing.append("user_agents.txt file not found")

if missing:
    raise EnvironmentError("Missing settings/files: " + ", ".join(missing))

# ──────────────────────────────────────────────
# Middleware / Pipeline / Captcha
ITEM_PIPELINES = {
    "agoda.pipelines.HotelDataPipeline": 300,
}
DOWNLOADER_MIDDLEWARES = {
    "agoda.middlewares.ProxyUserAgentAndCaptchaMiddleware": 543,
}

CAPTCHA_RETRY_TIMES = 1 # adjust this for production mode

# Register stealth coroutine handler for Playwright pages
# PLAYWRIGHT_PAGE_COROUTINES = "agoda.middlewares.PlaywrightStealthMiddleware"
# debug_pause on headful mode for debug
PLAYWRIGHT_PAGE_COROUTINES = {
    "default": [
        "agoda.middlewares.PlaywrightStealthMiddleware",
        "agoda.playwright_debug.debug_pause",
    ]
}
