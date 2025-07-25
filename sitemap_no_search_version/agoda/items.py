
import scrapy

class HotelItem(scrapy.Item):
    # name_original = scrapy.Field()
    # location_original = scrapy.Field()
    name_agoda = scrapy.Field()
    url = scrapy.Field()
    location_agoda = scrapy.Field()
    description = scrapy.Field()
    facilities = scrapy.Field()
    image_urls = scrapy.Field()