import os
import csv
import scrapy
from datetime import datetime
from itertools import islice
from ..items import HotelItem

class AgodaHotelSpider(scrapy.Spider):
    name = "agoda_hotel_spider"

    def open_spider(self, spider):
        self.middleware = getattr(spider.crawler, "middleware_instance", None)
        
        self.failed_hotels_path = "logs/failed_hotels.csv"
        self.failed_hotels = open(self.failed_hotels_path, "a", newline='', encoding="utf-8")
        self.failed_writer = csv.writer(self.failed_hotels)
        
        self.batch_index = self.settings.getint("BATCH_INDEX", 0)
        self.log_timestamp = os.getenv("LOG_TIMESTAMP", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        
        # Write CSV header only if file is empty
        if os.stat(self.failed_hotels_path).st_size == 0:
            self.failed_writer.writerow(["hotel_url", "batch_index", "timestamp", "reason"])

    def close_spider(self, spider):
        self.failed_hotels.close()

    def start_requests(self):
        input_file = self.settings.get("HOTELS_FILE", "sitemap_hotel_urls.csv")
        batch_index = self.settings.getint("BATCH_INDEX", 0)
        batch_size = self.settings.getint("BATCH_SIZE", 1000)

        with open(input_file, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            start = batch_index * batch_size
            end = start + batch_size
            hotels = islice(reader, start, end)  # use islice() for better memory usage

            self.logger.info(f"Processing batch {batch_index} — rows {start} to {end}")

            for row in hotels:
                url = row["hotel_url"]
                yield self.middleware.build_request(
                    url=url,
                    callback=self.parse_hotel_page,
                    errback=self.errback_hotel,
                    # meta={
                    #     "hotel_name": row.get("hotel_name"),
                    #     "true_address": row.get("address")
                    # }
                )

    def errback_hotel(self, failure):
        request = getattr(failure, "request", None)
        hotel_url = request.url if request else "UNKNOWN"
        self.logger.warning(f"[ERRBACK] Failed to fetch {hotel_url}")
        self.failed_writer.writerow([hotel_url, self.batch_index, self.log_timestamp, "Request failed or timeout"])

    def parse_hotel_page(self, response):
        # debug log for the proxy used
        if self.settings.getbool("TEST_MODE"):
            proxy = response.meta.get("proxy_id")
            self.logger.debug(f"[DEBUG] Using proxy: {proxy} for {response.url}")
            
        # detect CAPTCHA using middleware. if triggered, log the URL and skip parsing    
        proxy = response.meta.get("proxy_id")
        if self.middleware and proxy:
            if self.middleware.detect_and_handle_captcha(proxy, response):
                self.logger.warning(f"[SPIDER] CAPTCHA on {response.url}")
                self.failed_writer.writerow([response.url, self.batch_index, self.log_timestamp, "CAPTCHA"])
                return
        
        # hotel_query = response.meta.get("hotel_name", "")
        # known_address = response.meta.get("true_address", "")

        item = HotelItem()
        # item["name_original"] = hotel_query
        # item["location_original"] = known_address
        item["url"] = response.url

        # Agoda hotel name and address
        item["name_agoda"] = response.css("h1[data-selenium='hotel-header-name']::text").get()
        item["location_agoda"] = response.css("span[data-selenium='hotel-address-map']::text").get()

        # Description
        desc = response.css("span[data-element-name='property-short-description']::text").get()
        item["description"] = desc.strip() if desc else None

        # Facilities
        item["facilities"] = response.css("div[data-element-name='atf-top-amenities-item'] p::text").getall()

        # Images (from srcset)
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
