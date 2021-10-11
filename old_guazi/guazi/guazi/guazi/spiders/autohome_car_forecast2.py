import json
import time

from lxml import etree
import pandas as pd
import re

from redis import Redis
from selenium import webdriver

from ..items import autohome
import scrapy
import logging
from scrapy.conf import settings
from hashlib import md5
# from scrapy.xlib.pydispatch import dispatcher
# from scrapy import signals

website = 'autohome_car_forecast2'


# redis_cli = Redis(host="192.168.1.249", port=6379, db=2)


# 先循环城市 然后在循环车
class CarSpider(scrapy.Spider):
    name = website
    # start_urls = get_url()
    start_urls = [
        "https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=1%20&brandId=0%20&fctId=0%20&seriesId=0"]
    headers = {
        'referer': 'https://car.autohome.com.cn/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 3,
        "COOKIES_ENABLED": False,
        "RETRY_TIMES": 8,

    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        settings.set("MONGODB_DB", "newcar", priority="cmdline")
        self.counts = 0


    def parse(self, response):
        url_list = response.xpath("//a/@href").extract()
        brand_name_list = response.xpath("//li//a/text()").extract()
        for index in range(len(url_list)):
            brand_id = re.findall(r"brand-(\d*).html", url_list[index])[0]
            brand_name = brand_name_list[index]
            # 请求停售页面
            url = 'https://car.autohome.com.cn/price/brand-{}-0-3-1.html'.format(brand_id)
            yield response.follow(url=url, headers=self.headers, callback=self.stauts_parse,
                                  meta={"brand_id": brand_id, "brand_name": brand_name}, dont_filter=True)

    def stauts_parse(self, response):
        car_list = response.xpath("//div[@class='list-cont-bg']//div[@class='main-title']/a/@href").getall()
        name_list = response.xpath("//div[@class='list-cont-bg']//div[@class='main-title']/a/text()").getall()
        for i, url in enumerate(car_list):
            headers = {
                'referer': response.url,
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            }
            yield scrapy.Request(url=url, headers=headers, callback=self.sale_parse, meta=response.meta, dont_filter=True)

        nxt_page = response.css('a.page-item-next::attr(href)').getall()
        if nxt_page:
            if nxt_page[0] != 'javascript:void(0)':
                print('下一页： ', nxt_page[0])
                yield response.follow(url=nxt_page[0], headers=self.headers, callback=self.stauts_parse, meta=response.meta, dont_filter=True)

    def sale_parse(self, response):
        if 'class="dropdown"' in response.text:
            url = response.css('div.dropdown a::attr(href)').getall()[-1]
            text = response.css('div.dropdown a::text').getall()[-1]
            if text == '停售':
                headers = {
                    'referer': response.url,
                    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                }
                response.meta['status'] = '停售'
                yield response.follow(url=url, headers=headers, callback=self.car_parse, meta=response.meta, dont_filter=True)
        else:
            print('被重定向到 m.autohome ', response.url)
            # saled = re.findall(r'<!-- 停售信息 -->.*?<!-- end 停售信息 -->', response.text, re.S)[0]
            # print(saled)
            if '停售款' in response.text:
                print('发现停售款。。。')
                response.meta['status'] = '停售'
                yield response.follow(url=response.url, headers=self.headers, callback=self.car_parse, meta=response.meta, dont_filter=True)

            #     for a in response.xpath('//li[@status="40"]/a'):
            #         print(a.css('.::attr(href)').get(), a.css('div.summary-typelist__caption::text').get())


    def car_parse(self, response):
        print(response.meta)
        nav = response.css('div.title').xpath('string(//div[@class="title-nav"])').get().strip().replace('\n', '')
        print('停售年款： ', nav)
        hrefs = response.css('div.modelswrap div.name a::attr(href)').getall()
        series_name = response.css('div.modelswrap div.name a::text').getall()
        price = response.css('div.modelswrap div.price01::text').getall()
        for i in range(len(hrefs)):
            item = autohome()
            item["autohomeid"] = hrefs[i].split('/')[1]
            item["guideprice"] = price[i].strip()
            item["url"] = response.url
            item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["salesdesc"] = series_name[i]
            item["brandid"] = response.meta["brand_id"]
            item["salestatus"] = response.meta["status"]
            item["brandname"] = response.meta["brand_name"]
            item["statusplus"] = item["url"] + str(1551)+time.strftime('%Y-%m-%d %X', time.localtime()) \
                            + str(item["autohomeid"]) + str(item["salestatus"])

            yield item
            # print(item)
