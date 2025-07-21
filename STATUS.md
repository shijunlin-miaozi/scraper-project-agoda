# Project Status

This file tracks the current status of the Agoda hotel scraper project.


## ✅ Working Features

- Hotel search via input CSV
- Navigation from search input to first result page
- Detail page scraping: name, address, description, facilities
- Playwright integration for dynamic content
- Clicking "See all photos" and extracting high-resolution image urls
- Headful mode debugging via DevTools pause in TEST_MODE
- Session-level cookie injection and storage via middleware
- Per-proxy reuse logic (N requests per proxy before rotation)


## ⚠️ Partially Working / In Progress

- Image extraction: able to extract 80% of the img urls (for example, extracted 79 out of 93 urls in one testing) 
    --> maybe good enough for now
- Stealth integration using `playwright-stealth` to avoid detection  
    → logic integrated and activated in middleware, but stealth effectiveness still unverified
- Proxy/User-Agent middleware (`middlewares.py`)
    → well integrated, but CAPTCHA rate still high 


## ❌ Not Implemented / Broken

- Error handling for failed hotel lookups (log to `failed_hotels.csv`)
    → not working (have seen error to write to the file)
- pipelines.py (save output to database)
    → not tested


## 🧪 Testing Environment

- MacBook Air with IP-authenticated paid residential proxies (Webshare)
- Playwright + Stealth + Chrome-only user-agent/header pairs for fingerprint consistency
- Cookie injection and persistence across runs enabled
- CAPTCHA detection frequent but auto-handling improved (via cookie reset + proxy rotate)
- Headful mode now available in TEST_MODE for DOM inspection and debugging
- **Next step**: Simulate Natural Browser Behavior More Closely; warmup coroutine; soft block detection


### ⚖️ Trade-off: Browser Variety vs. Stealth Protection
We chose to use Chrome-only User-Agents to match Playwright’s stealth fingerprinting (which emulates Chrome). This limits UA diversity but ensures consistency and lowers fingerprint mismatch risk.

Alternative (not chosen): rotating across browser families (Safari, Firefox) would increase realism, but break stealth logic and increase detection risk.

We may revisit this if blocking increases or we change away from stealth-based defense.


## 📅 Progress Log

### 2025-07-21
- Enabled Playwright headful mode in TEST_MODE for DevTools inspection
- Added debug_pause() coroutine to pause and inspect browser with DevTools
- Implemented session-based cookie management: save/load per proxy, auto-reset on CAPTCHA
- Introduced proxy reuse control: group N requests per proxy before rotating
- Improved debug logging for cookies, proxy count, CAPTCHA hits

### 2025-07-20
- Switched to IP-authenticated proxies due to Playwright’s lack of support for authenticated HTTP proxies
- Moved stealth logic from spider to middleware for cleaner separation of concerns
- Constrained UA rotation to only Chrome-based user agents to match Playwright Stealth’s Chrome fingerprint
- Replaced agoda_headers with structured chrome_headers.json, mapping UAs to realistic headers
- Added 10 free IP-auth datacenter proxies from Webshare to proxies.txt for testing
    ✅ Integration successful
    ⚠️ All requests resulted in CAPTCHA pages — proxies likely flagged

### 2025-07-19
- Integrated `playwright-stealth` to reduce bot detection by Agoda
- Applied stealth logic in both `parse_search_results` and `parse_hotel_page` functions
- Not yet tested — needs validation against real CAPTCHA response behavior

### 2025-07-18
- Extracted 79/93 images urls successfully in test case
- Noted repeated IP blocking when testing locally

_Last updated: 2025-07-21_
