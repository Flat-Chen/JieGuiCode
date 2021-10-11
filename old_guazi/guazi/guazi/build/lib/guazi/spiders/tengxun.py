import scrapy

from scrapy_splash import SplashRequest


class TencentStockSpider(scrapy.Spider):
    name = "TencentStock"

    def start_requests(self):
        urls = [
            'http://stock.qq.com/l/stock/ywq/list20150423143546.htm',
        ]

        for url in urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5})
            # yield scrapy.Request(url,)

    def parse(self, response):
        print(response.xpath("//h3/a/text()").extract())
