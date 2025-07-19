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
  → logic added, but not yet tested or verified


## ❌ Not Implemented / Broken

- Error handling for failed hotel lookups (log to `failed_hotels.csv`)
    --> not working (have seen error to write to the file)
- middlewares.py (handle anti-bot measures using proxies adn user_agents)
    --> not tested
- pipelines.py (save output to database)
    --> not tested


## 🧪 Testing Environment

- Local PC with free VPN
- IP blocks happen quickly, limiting testability
- **Next step**: implement paid rotational proxies, expand user-agent/header sets, begin realistic testing


## 📅 Progress Log

### 2025-07-19
- Integrated `playwright-stealth` to reduce bot detection by Agoda
- Applied stealth logic in both `parse_search_results` and `parse_hotel_page` functions
- Not yet tested — needs validation against real CAPTCHA response behavior

### 2025-07-18
- Extracted 79/93 images urls successfully in test case
- Noted repeated IP blocking when testing locally

_Last updated: 2025-07-19_
