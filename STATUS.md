# Project Status

This file tracks the current status of the Agoda hotel scraper project.


## ✅ Working Features

- Hotel search via input CSV
- Navigation from search input to first result page
- Detail page scraping: name, address, description, facilities
- Playwright integration for dynamic content
- Clicking "See all photos" and extracting high-resolution image urls


## ⚠️ Partially Working / In Progress

- Image extraction: able to extract 80% of the img urls (for example, extracted 79 out of 93 urls in one testing) 
    --> maybe good enough for now
- Stealth integration using `playwright-stealth` to avoid detection  
    → logic integrated and activated in middleware, but stealth effectiveness still unverified
- Proxy/User-Agent middleware (`middlewares.py`)
    → logic in place and integrated (tested in requests), but proxy quality limits stealth effectiveness


## ❌ Not Implemented / Broken

- Error handling for failed hotel lookups (log to `failed_hotels.csv`)
    → not working (have seen error to write to the file)
- pipelines.py (save output to database)
    → not tested


## 🧪 Testing Environment

- Local MacBook Air with IP-authenticated free datacenter proxies (Webshare)
- Playwright + Stealth in use, with Chrome-only user-agent/header pairs for fingerprint consistency
- CAPTCHA detection still frequent — likely due to use of free datacenter proxies (commonly flagged)
- IP-auth proxies successfully integrated via whitelisting (no Proxy-Authorization used)
- **Next step**: upgrade to paid residential proxies or higher-quality datacenter proxies for larger-scale realistic testing


### ⚖️ Trade-off: Browser Variety vs. Stealth Protection
We chose to use Chrome-only User-Agents to match Playwright’s stealth fingerprinting (which emulates Chrome). This limits UA diversity but ensures consistency and lowers fingerprint mismatch risk.

Alternative (not chosen): rotating across browser families (Safari, Firefox) would increase realism, but break stealth logic and increase detection risk.

We may revisit this if blocking increases or we change away from stealth-based defense.


## 📅 Progress Log

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

_Last updated: 2025-07-20_
