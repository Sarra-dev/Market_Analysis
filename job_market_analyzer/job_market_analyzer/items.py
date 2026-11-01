# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    titre = scrapy.Field()
    entreprise = scrapy.Field()
    localisation = scrapy.Field()
    date_publication = scrapy.Field()
    experience = scrapy.Field()
    contrat = scrapy.Field()
    description = scrapy.Field()
    competences = scrapy.Field()
    source = scrapy.Field()

