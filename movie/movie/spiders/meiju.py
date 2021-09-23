import scrapy
from movie.items import MovieItem


class MeijuSpider(scrapy.Spider):
    name = 'meiju'
    allowed_domains = ['meijutt.tv']
    start_urls = ['http://m.meijutt.tv/new100.html']

    def parse(self, response):
        # print(response.text)
        movies = response.xpath('//ul[@class="class="fn-clear""]/li')
        for each_move in movies:
            # print(each_move)
            item = MovieItem()
            item['name'] = each_move.xpath('.//a/@title').extract()
            # yield item
            print(item)
