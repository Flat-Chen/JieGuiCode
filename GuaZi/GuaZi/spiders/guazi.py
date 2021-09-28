import scrapy


class GuaziSpider(scrapy.Spider):
    name = 'guazi'
    allowed_domains = ['guazi.com']
    start_urls = ['https://www.guazi.com/buy']

    def parse(self, response):
        pass
