import scrapy
from ..items import DoubanItem

class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response):
        move_list= response.xpath('//div[@class=‘hd’]/a/span[1]/text()')
        for i_item in move_list:
            douban_item =DoubanItem()
            douban_item['']
