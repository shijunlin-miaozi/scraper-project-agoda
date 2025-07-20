import random
from playwright_stealth import Stealth

class ProxyUserAgentAndCaptchaMiddleware:
    """Handles proxy rotation, user‑agent spoofing, header rotation and CAPTCHA retry."""

    def __init__(self, agoda_user_agents, agoda_headers, proxies, retry_times):
        self.agoda_user_agents = agoda_user_agents
        self.agoda_headers = agoda_headers
        self.proxies = proxies
        self.retry_times = retry_times

    @classmethod
    def from_crawler(cls, crawler):
        # Load proxy list & user‑agents from files
        with open("proxies.txt") as pf:
            proxies = [line.strip() for line in pf if line.strip()]
        with open("user_agents.txt") as uf:
            ua_list = [line.strip() for line in uf if line.strip()]

        # Optional: a dict of additional header sets for Agoda
        agoda_headers = [
            {
                "Accept-Language": "en-GB,en;q=0.9",
                "Referer": "https://www.google.com/",
            },
            {
                "Accept-Language": "de-DE,de;q=0.9",
                "Referer": "https://www.bing.com/",
            }
        ]
        retry_times = crawler.settings.getint("CAPTCHA_RETRY_TIMES", 3)
        return cls(ua_list, agoda_headers, proxies, retry_times)

    # ----------- REQUEST -------------
    def process_request(self, request, spider):
        """Attach proxy & headers before sending the request."""
        
        if spider.settings.getbool("TEST_MODE"):
            return None  # Skip proxy/user-agent rotation in test mode
        
        # Random proxy
        proxy = random.choice(self.proxies)
        request.meta["proxy"] = proxy

        # Domain‑specific headers
        if "agoda.com" in request.url:
            # Choose a UA + header set
            ua = random.choice(self.agoda_user_agents)
            hdr_extra = random.choice(self.agoda_headers)

            request.headers["User-Agent"] = ua
            request.meta["user_agent"] = ua
            for k, v in hdr_extra.items():
                request.headers[k] = v
        # You could add more domains here with elif blocks

    # ----------- RESPONSE ------------
    def process_response(self, request, response, spider):
        """Detect CAPTCHA/verify pages and trigger retry with a new proxy/user-agent."""
        lower = response.text.lower()
        if ("captcha" in lower or "verify" in lower) and request.meta.get("retry_times", 0) < self.retry_times:
            spider.logger.warning("CAPTCHA detected — retrying %s" % request.url)
            new_request = request.copy()
            new_request.dont_filter = True  # allow duplicate
            # increment retry counter
            new_request.meta["retry_times"] = request.meta.get("retry_times", 0) + 1
            # Force new proxy & UA on retry
            new_request.headers.pop("User-Agent", None)
            return new_request
        return response


# -----------------------------
# New stealth middleware class
# -----------------------------
class PlaywrightStealthMiddleware:
    """Automatically applies stealth fingerprinting protection to all Playwright pages."""

    async def __call__(self, page, request):
        stealth = Stealth()
        await stealth.apply_stealth_async(page.context)

        # Optional fingerprint logging for debugging
        val = await page.evaluate("""
        () => ({
            webdriver: navigator.webdriver,
            languages: navigator.languages,
            plugins: navigator.plugins.length,
            chromeRuntime: !!(window.chrome && window.chrome.runtime)
        })
        """)
        # expected output:
            # { 'webdriver': False,
            #   'languages': ['en-US', 'en'],
            #   'plugins': 2,        # Or any number > 0
            #   'chromeRuntime': True}
            
        request.meta["stealth_debug"] = val  # Can log this in parse_ functions if needed
        return page