🧭 Project Overview: sitemap_no_search Strategy

This branch introduces a more stealth-oriented scraping approach for Agoda hotel pages, replacing the previous Playwright-based search method. The original method involved navigating to Agoda’s homepage, entering hotel names in the search bar via Playwright, clicking suggestion box items, and extracting hotel data. However, this approach often triggered CAPTCHA challenges or soft blocks (e.g., no results returned after clicking the search button) due to Agoda's advanced bot detection during search interactions.

To overcome this, the sitemap_no_search method skips search entirely by starting directly from individual hotel page URLs sourced from Agoda’s public sitemap. This dramatically reduces surface area for detection.

We continue to use Scrapy for request scheduling and data extraction, but replace Playwright with Nodriver, which operates in a headless JavaScript context with enhanced stealth capabilities. No clicks or dynamic page interactions are performed — only the initially rendered hotel page content is parsed (e.g., description, facilities, images).

Key features in both old and new approaches:

✅ Rotating residential proxies

✅ Rotating Chrome-based User-Agent and headers

✅ Proxy-session pinning and cookie persistence

✅ CAPTCHA detection and handling (with backoff logic)

This approach is designed for high-scale scraping with reduced risk of blocking.

📌 [Project Status](./STATUS.md)
