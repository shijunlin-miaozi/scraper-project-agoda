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


## ❌ Not Implemented / Broken

- Error handling for failed hotel lookups (log to `failed_hotels.csv`)
    --> not working (have seen error to write to the file)
- middlewares.py (handle anti-bot measures using proxies adn user_agents)
    --> not tested
- pipelines.py (save output to database)
    --> not tested


## Notes

- all the testings on the spider have been done on my pc with free vpn. the IP got blocked frequently. this greatly limits the testing effort. 
- next step is to use paid rotational proxies against anti-bot measures, then conduct more robust testing


_Last updated: 2025-07-18_
