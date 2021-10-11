# -*- coding: utf-8 -*-
import logging
import os
import random
import re
import sys
import time

import scrapy

# 爬虫名
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from ..items import CheHang168_item

website = 'chehang168'


# 必须有自己的中间件  切与其他的没有关系
class GuazicarSpider(scrapy.Spider):
    name = website
    start_urls = "http://www.chehang168.com/index.php?c=index&m=allBrands"
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": random.uniform(2, 3),
        "DOWNLOADER_MIDDLEWARES": {
            'guazi.che168_proxy.CheHang168Middleware': 180,
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,  # 关闭默认下载器
        },
        "COOKIES_ENABLED": True,
        "REDIRECT_ENABLED": True,
        # "REDIRECT_ENABLED = False"

    }

    def __init__(self, **kwargs):
        settings.set("WEBSITE", website)
        settings.set("MYSQLDB_DB", "usedcar_update")
        super(GuazicarSpider, self).__init__(**kwargs)

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, meta={'dont_redirect': True}, dont_filter=True)

    #  车系和url 解析
    def parse(self, response):
        # print(1111111111111111111111111111111111111111111111111111111111111111111)
        brand_name = response.xpath("//ul[@class='cyxx_wrap_ull pt_1']//a/text()").extract()
        brand_url = response.xpath("//ul[@class='cyxx_wrap_ull pt_1']//a/@href").extract()
        for i in range(len(brand_name))[3:4]:
            yield response.follow(url=brand_url[i], meta={"brand": brand_name[i], 'dont_redirect': True},
                                  callback=self.get_family, dont_filter=True)

    # 进行翻页操作
    def get_family(self, response):
        logging.log(msg='获取famliy_name----------------------------', level=logging.INFO)
        family_list = response.xpath("//div[@class='sx_tiaojian cyxx_div_ull']/div")
        for i in family_list[0:1]:
            family_name = i.xpath("./label/text()").extract_first()
            for series in i.xpath("./ul/li")[0:1]:
                series_name = series.xpath("./a/text()").extract_first()
                series_url = series.xpath("./a/@href").extract_first() + "&pricetype=0&page=1"
                response.meta.update({"series_name": series_name, "family_name": family_name, "page": 1})
                # print(response.meta)
                yield response.follow(url=series_url, meta=response.meta, callback=self.next_page_parse,
                                      dont_filter=True)

    def next_page_parse(self, response):
        # 获取列表看是否有数据  没有没有数据就return
        print(response.url)
        car_list = response.xpath("//div[@class='cheyuan_list']/ul[2]//li")
        # print(response.xpath("//div[@class='cheyuan_list']/ul[2]//li").extract())
        # print(len(car_list))
        print(car_list)
        if len(car_list) == 0:
            print(response.text)

            return
        else:
            for car in car_list:
                item = CheHang168_item()
                item["brand"] = response.meta["brand"]
                item["series_name"] = response.meta["series_name"]
                item["family_name"] = response.meta["family_name"]
                item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item["url"] = car.xpath(".//h3/a/@href").extract_first()
                item["post_time"] = car.xpath(".//p[@class='c3']/cite[1]/text()").extract_first()

                item["salesdesc"] = car.xpath(".//h3/a/text()").extract_first()
                try:
                    item["price"] = car.xpath(".//span[@class='pr']/b/text()").extract_first().strip()
                except:
                    item["price"] = ''
                try:
                    item["guide_price"] = car.xpath(".//b[@class='price_txt']/text()").extract_first().strip()
                except:
                    item["guide_price"] = ''
                item["store"] = car.xpath(".//p[@class='c3']/a/text()").extract_first()
                item["chengjiao_number"] = car.xpath(".//cite[contains(text(),'成交')]/text()").extract_first()
                if item["chengjiao_number"] != None:
                    item["chengjiao_number"] = item["chengjiao_number"].split("：")[1].strip("单")
                item["car_location"] = car.xpath(".//cite[contains(text(),'车源所')]/text()").extract_first()
                if item["car_location"] != None:
                    item["car_location"] = item["car_location"].split("：")[1]
                # 规格
                item["specification"] = car.xpath(".//p[@class='c1']/text()").extract_first()
                item["remark"] = car.xpath(".//p[@class='c2']/text()").extract_first()
                try:
                    item["car_id"] = re.findall(r'uid=(.*)&id=(.*)', item["url"])[0][1]
                except:
                    item["car_id"] = None
                try:
                    item["statusplus"] = item["url"] + str(item["price"]) + str(item["guide_price"])
                except:
                    item["statusplus"] = item["url"]+item["store"]
                    # print(item)
                # yield item

            response.meta["page"] = response.meta["page"] + 1
            url = response.url.split("page=")[0] + 'page={}'.format(response.meta["page"])
            print(url,'*50')
            yield scrapy.Request(url=url, meta=response.meta, callback=self.next_page_parse,
                                 dont_filter=True)
