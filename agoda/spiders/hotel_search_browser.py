import scrapy
import csv
from scrapy_playwright.page import PageMethod
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
                            PageMethod("screenshot", path=f"screenshots/{hotel_name}_1result.png"),
                            
                            # click the first listing from auto suggestion box
                            PageMethod("click", 'li[data-selenium="topDestinationListItem"] >> nth=0'),
                            PageMethod("wait_for_timeout", 1000),
                            PageMethod("screenshot", path=f"screenshots/{hotel_name}_2result.png"),
                            
                            # Dismiss cookie banner if present
                            PageMethod(
                                "evaluate",
                                """() => {
                                    const btn = document.querySelector("button[data-element-name='consent-banner-reject-btn']");
                                    if (btn) btn.click();
                                }"""
                            ), 
                            PageMethod("wait_for_timeout", 1000),
                            PageMethod("screenshot", path=f"screenshots/{hotel_name}_3result.png"),
                            
                            # click check-in box to remove the drop-down calendar in case it blocks the search button
                            # PageMethod("click","div[data-selenium='checkInBox']"),
                            # PageMethod("wait_for_timeout", 1000),
                            # PageMethod("screenshot", path=f"screenshots/{hotel_name}_4result.png"),
                            
                            # click search button
                            PageMethod("click","button[data-selenium='searchButton']"),
                            PageMethod("wait_for_timeout", 3000),
                            PageMethod("screenshot", path=f"screenshots/{hotel_name}_5result.png"),
                            
                            # get to result listing page
                            # PageMethod("wait_for_selector", "li.PropertyCard a", timeout=15000),
                            # PageMethod("press", "input[data-selenium='textInput']", "escape"),
                            # PageMethod("click", 'span[data-selenium="suggestion-text-highlight"]'),
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

    def parse_search_results(self, response):
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
                "hotel_query": hotel_query,
                "true_address": response.meta.get("true_address"),
                "dont_retry": False
            },
            callback=self.parse_hotel_page,
            errback=self.errback_search
        )

    def parse_hotel_page(self, response):
        hotel_query = response.meta["hotel_query"]
        known_address = response.meta["true_address"]

        scraped_address = response.css("span[data-selenium='hotel-address-map']::text").get()

        item = HotelItem()
        item["name_original"] = hotel_query
        item["name_agoda"] = response.css("h1[data-selenium='hotel-header-name']::text").get()
        item["url"] = response.url
        item["location_original"] = known_address
        item["location_agoda"] = scraped_address
        item["description"] = response.css("span[data-element-name='property-short-description']::text").get().strip()
        item["facilities"] = response.css("div[data-element-name='atf-top-amenities-item'] p::text").getall()
        item["image_urls"] = response.css("img::attr(src)").re(r'https://ak-d\.agoda\.net/[^"]+')
        yield item