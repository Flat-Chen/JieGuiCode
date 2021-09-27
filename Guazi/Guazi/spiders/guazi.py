import scrapy


class GuaziSpider(scrapy.Spider):
    name = 'guazi'
    allowed_domains = ['guazi.com']
    start_urls = ['https://www.guazi.com/buy']

     #抓取车型,品牌
    def parse(self, response):
        car_pinpai_list=response.xpath(

        )




