import scrapy
from movie.items import MovieItem


class MeijuSpider(scrapy.Spider):
    name = 'meiju'
    allowed_domains = ['meijutt.tv']
    start_urls = ['http://meijutt.tv/new100.html']

    def parse(self, response):
        # print(response.text)
        movies = response.xpath('//div[@class="top-min top-min-long new100"]/ul/li')
        for each_move in movies:
            print(each_move)
            item = MovieItem()
            item['name'] = each_move.xpath('./h5/a/@title').extract()
            yield item
