import random
import logging
from nodriver import Nodriver, NodriverRequest
from agoda.utilities.headers import generate_headers
from agoda.utilities.log_utils import log_cookies

logger = logging.getLogger(__name__)

class NodriverMiddleware:
    def __init__(self, crawler):
        with open("proxies.txt") as f:
            proxies = [line.strip() for line in f if line.strip()]
        self.proxies = proxies
        self.proxy_contexts = {}
        self.proxy_usage = {}
        self.proxy_captcha_count = {}
        self.test_mode = crawler.settings.getbool("TEST_MODE", False)
        self.captcha_threshold_per_proxy = crawler.settings.getint("CAPTCHA_THRESHOLD_PER_PROXY", 3)
        self.proxy_reuse_limit_per_session = crawler.settings.getint("PROXY_REUSE_LIMIT_PER_SESSION", 5)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.middleware_instance = middleware  # 🔗 attach globally
        return middleware

    def get_proxy(self):
        return random.choice(self.proxies)
    
    def get_context_and_headers(self, proxy):
        attempts = 0
        max_attempts = len(self.proxies)
        
        # caps how many proxies to try per request — avoids infinite loop
        while attempts < max_attempts:
            if proxy not in self.proxy_contexts:
                self.proxy_contexts[proxy] = Nodriver(proxy=proxy)
                self.proxy_usage[proxy] = 0

            context = self.proxy_contexts[proxy]
            self.proxy_usage[proxy] += 1

            if self.proxy_usage[proxy] <= self.proxy_reuse_limit_per_session:
                headers = generate_headers()
                
                # log cookies info for debug
                if self.test_mode:
                    cookies = context.page.cookies()
                    log_cookies(proxy, cookies)

                return context, headers

            # Reset session if proxy reuse limit exceeded
            del self.proxy_contexts[proxy]
            self.proxy_usage[proxy] = 0

            proxy = self.get_proxy()
            attempts += 1

        raise RuntimeError("⚠️ Failed to obtain valid proxy context after max attempts.")

    def build_request(self, url, callback=None, meta=None):
        proxy = self.get_proxy()
        context, headers = self.get_context_and_headers(proxy)

        return NodriverRequest(
            url=url,
            context=context,
            headers=headers,
            wait_until="domcontentloaded",
            callback=callback,
            meta={"proxy_id": proxy, **(meta or {})}
        )

    def detect_and_handle_captcha(self, proxy, response):
        lower = response.text.lower()
        if "captcha" in lower or "verify" in lower:
            self.proxy_captcha_count[proxy] = self.proxy_captcha_count.get(proxy, 0) + 1
            
            # log cookies info for debug
            if self.test_mode:
                context = self.proxy_contexts.get(proxy)
                if context:
                    cookies = context.page.cookies()
                    log_cookies(proxy, cookies)
                    
            # triggers context/session reset after N hits
            if self.proxy_captcha_count[proxy] >= self.captcha_threshold_per_proxy:
                self.proxy_captcha_count[proxy] = 0

                # Reset proxy and session context
                if proxy in self.proxy_contexts:
                    del self.proxy_contexts[proxy]
                    self.proxy_usage[proxy] = 0

            logger.warning(f"[CAPTCHA] Detected for proxy {proxy} on {response.url}. No retry scheduled.")
            return True  # Indicate that CAPTCHA was detected

        return False
