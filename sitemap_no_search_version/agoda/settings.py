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
# Use Nodriver for JS-rendered, stealth-enabled HTTP/HTTPS requests
DOWNLOAD_HANDLERS = {
    "http": "nodriver.scrapy.NodriverDownloadHandler",
    "https": "nodriver.scrapy.NodriverDownloadHandler",
}
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 2
COOKIES_ENABLED = False
RETRY_TIMES = 0

# Autothrottle settings
# note it is mostly useful when concurrency >1, so for now it’s passive, its kept for future scaling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# ──────────────────────────────────────────────
# Toggle between test and production
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"


# Input CSV file
HOTELS_FILE = os.getenv("HOTELS_FILE", "sitemap_hotel_urls.csv")

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
            "indent": 2  # 👈 pretty printing
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
required_files = {
    "proxies.txt": "proxies.txt file not found",
    HOTELS_FILE: "HOTELS_FILE not found"
}
if not POSTGRES_USER or not POSTGRES_PASSWORD:
    raise EnvironmentError("Missing: POSTGRES_USER and POSTGRES_PASSWORD")

missing = [msg for path, msg in required_files.items() if not os.path.exists(path)]
if missing:
    raise EnvironmentError("Missing settings/files: " + ", ".join(missing))

# ──────────────────────────────────────────────
# Middleware / Pipeline / Captcha
ITEM_PIPELINES = {
    "agoda.pipelines.HotelDataPipeline": 300,
}
DOWNLOADER_MIDDLEWARES = {
    "agoda.middlewares.NodriverMiddleware": 543,
}
# adjust below values in production mode
CAPTCHA_THRESHOLD_PER_PROXY = 3
PROXY_REUSE_LIMIT_PER_SESSION = 5

