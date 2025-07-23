import os
import json
import random
import datetime
import http.cookies
from playwright_stealth import Stealth

CAPTCHA_THRESHOLD = 3  # Reset cookies after this many CAPTCHA hits
PROXY_REUSE_LIMIT = 5  # Number of requests per proxy before switching

class ProxyUserAgentAndCaptchaMiddleware:
    """Handles proxy rotation, user‑agent spoofing, header rotation and CAPTCHA retry."""

    def __init__(self, agoda_user_agents, chrome_headers, proxies, retry_times):
        self.agoda_user_agents = agoda_user_agents
        self.chrome_headers = chrome_headers
        self.proxies = proxies
        self.retry_times = retry_times
        self.cookie_jar_path = "cookies.json"
        self.cookie_jar = self.load_cookies()
        self.proxy_captcha_count = {}  # Track CAPTCHA frequency per proxy
        self.current_proxy = None
        self.proxy_request_count = 0


    @classmethod
    def from_crawler(cls, crawler):
        # Load proxy list & user‑agents and chrome headers from files
        with open("proxies.txt") as pf:
            proxies = [line.strip() for line in pf if line.strip()]
        with open("user_agents.txt") as uf:
            ua_list = [line.strip() for line in uf if line.strip()]            
        with open("chrome_headers.json", encoding="utf-8") as hf:
            chrome_headers = json.load(hf)            
        # Filter UA list to only ones that exist in the header mapping
        ua_list = [ua for ua in ua_list if ua in chrome_headers]
        
        retry_times = crawler.settings.getint("CAPTCHA_RETRY_TIMES", 3)
        
        return cls(ua_list, chrome_headers, proxies, retry_times)

    def load_cookies(self):
        if os.path.exists(self.cookie_jar_path):
            if os.path.getsize(self.cookie_jar_path) > 0:
                with open(self.cookie_jar_path, "r") as f:
                    return json.load(f)
            else:
                # Log for debug visibility in test mode
                print(f"[COOKIES] '{self.cookie_jar_path}' is empty — starting with fresh jar.")
        return {}

    def save_cookies(self):
        with open(self.cookie_jar_path, "w") as f:
            json.dump(self.cookie_jar, f, indent=2)

    # ----------- REQUEST -------------
    def process_request(self, request, spider):
        """Attach cookies, proxy & headers before sending the request."""
        
        # if spider.settings.getbool("TEST_MODE"):
        #     return None  # Skip proxy/user-agent rotation in test mode
        
        if not self.current_proxy or self.proxy_request_count >= PROXY_REUSE_LIMIT:
            self.current_proxy = random.choice(self.proxies)
            self.proxy_request_count = 0  # Reset count for new proxy
            if spider.settings.getbool("TEST_MODE"):
                spider.logger.info(f"[PROXY] Rotated to new proxy: {self.current_proxy}")

        proxy = self.current_proxy
        self.proxy_request_count += 1 # Count how many times current proxy has been used
        # Proxy is already IP-authenticated, no credential injection needed
        request.meta["proxy"] = proxy

        # Inject cookies if valid
        proxy_data = self.cookie_jar.get(proxy)
        if proxy_data:
            age = datetime.datetime.utcnow() - datetime.datetime.fromisoformat(proxy_data["last_updated"])
            if age.total_seconds() < 86400:  # 24 hours
                cookie_str = "; ".join(f"{k}={v}" for k, v in proxy_data["cookies"].items())
                request.headers["Cookie"] = cookie_str
                
                # ✅ Log cookie string in test mode
                if spider.settings.getbool("TEST_MODE"):
                    spider.logger.info(f"[COOKIES] Injected for proxy {proxy}: {cookie_str}")
            else:
                del self.cookie_jar[proxy]  # expired
                self.save_cookies()
                # Log when cookies are cleared due to expiration
                spider.logger.info(f"[COOKIES] Expired for proxy {proxy}, removed from jar")

        # Domain‑specific headers
        if "agoda.com" in request.url:
            ua = random.choice(self.agoda_user_agents)
            hdr_extra = self.chrome_headers.get(ua, {})
            
            # test whether headers are applied as expected 
            if spider.settings.getbool("TEST_MODE"):
                spider.logger.info(f"[UA] {ua}")
                spider.logger.info(f"[Headers] {hdr_extra}")

            request.headers["User-Agent"] = ua
            request.meta["user_agent"] = ua
            for k, v in hdr_extra.items():
                request.headers[k] = v

        # You could add more domains here with elif blocks

    # ----------- RESPONSE ------------
    def process_response(self, request, response, spider):
        """Save cookies if any, detect CAPTCHA/verify pages and trigger retry with a new proxy/user-agent."""
        
        proxy = request.meta.get("proxy")
        if not proxy:
            spider.logger.warning("[PROXY] No proxy found in request.meta — skipping CAPTCHA and cookie logic.")
            return response
        
        # --- Cookie Saving ---
        set_cookie_headers = response.headers.getlist("Set-Cookie")
        if set_cookie_headers:
            jar = {}
            for header in set_cookie_headers:
                simple_cookie = http.cookies.SimpleCookie()
                simple_cookie.load(header.decode() if isinstance(header, bytes) else header)
                for k, morsel in simple_cookie.items():
                    jar[k] = morsel.value
            self.cookie_jar[request.meta["proxy"]] = {
                "cookies": jar,
                "last_updated": datetime.datetime.utcnow().isoformat()
            }
            self.save_cookies()
        
        # --- CAPTCHA Detection and Proxy Reset Logic ---
        lower = response.text.lower()
        if ("captcha" in lower or "verify" in lower) and request.meta.get("retry_times", 0) < self.retry_times:
            count = self.proxy_captcha_count.get(proxy, 0) + 1
            self.proxy_captcha_count[proxy] = count
            
            spider.logger.warning(f"CAPTCHA detected for proxy {proxy} (hit #{count}) — retrying {request.url}")            
            
            # Reset current proxy on CAPTCHA detection to trigger rotation
            self.current_proxy = None
            self.proxy_request_count = 0
            
            # Reset cookies after n CAPTCHA hits
            if count >= CAPTCHA_THRESHOLD:
                spider.logger.warning(f"⚠️ Clearing cookies for proxy {proxy} after {CAPTCHA_THRESHOLD} CAPTCHA hits")
                self.cookie_jar.pop(proxy, None)
                self.save_cookies()
                self.proxy_captcha_count[proxy] = 0
            
            new_request = request.copy()
            new_request.dont_filter = True  # allow duplicate
            # increment retry counter
            new_request.meta["retry_times"] = request.meta.get("retry_times", 0) + 1
            
            # ✅ Rotate User-Agent
            ua = random.choice(self.agoda_user_agents)
            hdr_extra = self.chrome_headers.get(ua, {})
            new_request.headers["User-Agent"] = ua
            for k, v in hdr_extra.items():
                new_request.headers[k] = v
            new_request.meta["user_agent"] = ua
            
            # Log rotated UA during retry for debugging
            if spider.settings.getbool("TEST_MODE"):
                spider.logger.info(f"[UA ROTATE] New UA after CAPTCHA for proxy {proxy}: {ua}")
            
            return new_request
        
        # --- Successful response → reset CAPTCHA count
        self.proxy_captcha_count[proxy] = 0
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