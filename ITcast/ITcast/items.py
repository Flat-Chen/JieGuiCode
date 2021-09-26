# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ItcastItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 序列号
    serial_number =scrapy.Field();
    # 电影名
    movie_name = scrapy.Field();
    # title = scrapy.Field()
    # info = scrapy.Field()
    # 介绍
    introduce=scrapy.Field();
    # 星级
    star=scrapy.Field();
    # 评级数
    evaluate=scrapy.Field();
    # 描述
    describe=scrapy.Field();
