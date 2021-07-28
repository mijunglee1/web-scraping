# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RehabmeasuresItem(scrapy.Item):
    measure_name = scrapy.Field()
    field_dict = scrapy.Field()
    diag_conditions = scrapy.Field()
    population = scrapy.Field()
    no_items = scrapy.Field()
    time = scrapy.Field()
    descriptions = scrapy.Field()
    threeup_dict = scrapy.Field()
    stroke_dict = scrapy.Field()


