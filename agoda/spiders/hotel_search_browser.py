import scrapy
import csv
from scrapy_playwright.page import PageMethod
from playwright_stealth import Stealth
from ..items import HotelItem

class AgodaSearchSpider(scrapy.Spider):
    name = "agoda_search_browser"
    custom_settings = {
        "RETRY_TIMES": 0 # adjust this for production mode
    }

    def open_spider(self, spider):
        self.failed_hotels = open("failed_hotels.csv", "w", newline='', encoding="utf-8")
        self.failed_writer = csv.writer(self.failed_hotels)
        self.failed_writer.writerow(["hotel_name", "reason"])

    def close_spider(self, spider):
        if hasattr(self, "failed_hotels"):
            self.failed_hotels.close()

    async def start(self):
        input_file = self.settings.get("HOTELS_FILE")
        batch_index = self.settings.getint("BATCH_INDEX", 0)
        batch_size = self.settings.getint("BATCH_SIZE", 1000)

        with open(input_file, newline='', encoding="utf-8") as f:
            reader = list(csv.DictReader(f, delimiter=","))
            start = batch_index * batch_size
            end = start + batch_size
            
            # Log the batch range
            self.logger.info(f"Running batch {batch_index} — rows {start} to {end}")
            
            hotels = reader[start:end]
            for row in hotels:
                hotel_name = row["hotel_name"]
                true_address = row["address"]
                city = row["city_name"]
                search_prompt = f'{hotel_name}, {city}'

                yield scrapy.Request(
                    url="https://www.agoda.com/",
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            # enter search prompt(format: hotel name, city) into search input box
                            PageMethod("fill", "input[data-selenium='textInput']", search_prompt),
                            PageMethod("wait_for_timeout", 1000),
                            # PageMethod("screenshot", path=f"screenshots/{hotel_name}_1result.png"),
                            
                            # click the first listing from auto suggestion box
                            PageMethod("click", 'li[data-selenium="topDestinationListItem"] >> nth=0'),
                            PageMethod("wait_for_timeout", 1000),
                            # PageMethod("screenshot", path=f"screenshots/{hotel_name}_2result.png"),
                            
                            # Dismiss cookie banner if present
                            PageMethod(
                                "evaluate",
                                """() => {
                                    const btn = document.querySelector("button[data-element-name='consent-banner-reject-btn']");
                                    if (btn) btn.click();
                                }"""
                            ), 
                            PageMethod("wait_for_timeout", 1000),
                            # PageMethod("screenshot", path=f"screenshots/{hotel_name}_3result.png"),
                            
                            # click search button
                            PageMethod("click","button[data-selenium='searchButton']"),
                            PageMethod("wait_for_timeout", 3000),
                            # PageMethod("screenshot", path=f"screenshots/{hotel_name}_4result.png"),
                            
                        ],
                        "hotel_query": hotel_name,
                        "true_address": true_address,
                        "dont_retry": False
                    },
                    callback=self.parse_search_results,
                    errback=self.errback_search
                )

    def errback_search(self, failure):
        hotel_query = failure.request.meta.get("hotel_query", "UNKNOWN")
        self.logger.warning(f"[ERRBACK] Request failed for hotel: {hotel_query}")
        if hasattr(self, "failed_writer"):
            self.failed_writer.writerow([hotel_query, "Request failed or timeout"])

    async def parse_search_results(self, response):
        page = response.meta.get("playwright_page")
        if page:
            # Apply stealth to the browser context
            stealth = Stealth()
            await stealth.apply_stealth_async(page.context)

            # debug fingerprint detection
            val = await page.evaluate("""
            () => ({
                webdriver: navigator.webdriver,
                languages: navigator.languages,
                plugins: navigator.plugins.length,
                chromeRuntime: !!(window.chrome && window.chrome.runtime)
            })
            """)
            self.logger.info(f"[STEALTH DEBUG] {val}")
            # expected output:
                # {
                # 'webdriver': False,
                # 'languages': ['en-US', 'en'],
                # 'plugins': 2,        # Or any number > 0
                # 'chromeRuntime': True
                # }

        hotel_query = response.meta["hotel_query"]
        first_result = response.css("li.PropertyCard a::attr(href)").get()
        if not first_result:
            self.logger.warning(f"[NOT FOUND] No listing found for hotel: {hotel_query}")
            self.failed_writer.writerow([hotel_query, "No listing found"])
            return

        yield response.follow(
            response.urljoin(first_result),
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "img"),  # wait for initial page load
                    PageMethod("click", 'button[data-element-name="hotel-mosaic-see-all-photos"]'),
                    # PageMethod("wait_for_timeout", 2000),  # waits 2 seconds
                    PageMethod("wait_for_selector", "img"),  # wait again for images to load after click
                ],
                "hotel_query": hotel_query,
                "true_address": response.meta.get("true_address"),
                "dont_retry": False
            },
            callback=self.parse_hotel_page,
            errback=self.errback_search
        )

    async def parse_hotel_page(self, response):
        page = response.meta.get("playwright_page")
        if page:
            # Apply stealth again for this new page context
            stealth = Stealth()
            await stealth.apply_stealth_async(page.context)
            
            # debug fingerprint detection
            val = await page.evaluate("""
            () => ({
                webdriver: navigator.webdriver,
                languages: navigator.languages,
                plugins: navigator.plugins.length,
                chromeRuntime: !!(window.chrome && window.chrome.runtime)
            })
            """)
            self.logger.info(f"[STEALTH DEBUG] {val}")
            
        hotel_query = response.meta["hotel_query"]
        known_address = response.meta["true_address"]

        item = HotelItem()
        item["name_original"] = hotel_query
        item["name_agoda"] = response.css("h1[data-selenium='hotel-header-name']::text").get()
        item["url"] = response.url
        item["location_original"] = known_address
        item["location_agoda"] = response.css("span[data-selenium='hotel-address-map']::text").get()
        item["description"] = response.css("span[data-element-name='property-short-description']::text").get().strip()
        item["facilities"] = response.css("div[data-element-name='atf-top-amenities-item'] p::text").getall()

        # New image extraction logic
        image_sources = (
            "pix8.agoda.net/hotelImages",
            "pix8.agoda.net/property",
            "bstatic.com/xdata/images/hotel/"
        )
        image_urls = []
        for img in response.css("img"):
            srcset = img.attrib.get("srcset")
            if srcset and any(src in srcset for src in image_sources):
                largest = srcset.split(",")[-1].strip().split(" ")[0]
                full_url = response.urljoin(largest)
                image_urls.append(full_url)
        item["image_urls"] = image_urls
        
        yield item