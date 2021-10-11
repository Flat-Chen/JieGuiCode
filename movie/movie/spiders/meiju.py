import scrapy
from movie.items import MovieItem


class MeijuSpider(scrapy.Spider):
    name = 'meiju'
    allowed_domains = ['meijutt.tv']
    start_urls = ['http://m.meijutt.tv/new100.html']

    def parse(self, response):
        movies = response.xpath('//ul[@class="fn-clear"]/li')
        for each_move in movies:
            movie_name = each_move.xpath('.//a/@title').extract_first()
            movie_url_canque = each_move.xpath('.//a/@href').extract_first()
            movie_url = response.urljoin(movie_url_canque)
            yield scrapy.Request(url=movie_url, callback=self.xiangqing_parse, meta={'movie_name': movie_name})

    #     比如还有下一页内容 接着解析
        next_url = '下一页的地址 一般解析出来的是当前url地址+1'
        yield scrapy.Request(url=next_url, callback=self.parse,meta={})

    def xiangqing_parse(self, response):
        item = {}
        movie_name = response.meta['movie_name']
        # print(movie_name)
        xunlei_cili = response.xpath('//div[@class="arconix-toggle-content fn-clear"]//a/@href').extract()
        # print(xunlei_cili)
        item['movie_name'] = movie_name
        item['xunlei_cili'] = xunlei_cili
        yield item