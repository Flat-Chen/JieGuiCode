# https://www.woniuhuoche.com/truck/api/v1/evaluation/getEvalInfoWithZimu  品牌 车系
# https://www.woniuhuoche.com/truck/api/v2/truck/getCityWithZimu?content= 城市接口
# https://www.woniuhuoche.com/truck/api/v1/evaluation/getEvalInfos?brand=%E5%A5%A5%E9%A9%B0%E6%B1%BD%E8%BD%A6&model=%E8%BD%BD%E8%B4%A7%E8%BD%A6&series=%E5%A5%A5%E9%A9%B0A%E7%B3%BB 车型
# brand: 奥驰汽车
# model: 载货车
# series: 奥驰A系
import json
import logging
import os
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
from ..items import Wo_Niu_Car_Item

website = 'woniu_car'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://www.woniuhuoche.com/truck/api/v1/evaluation/getEvalInfoWithZimu"
    headers = {'Referer': 'https://www.woniuhuoche.com/',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(GuazicarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MYSQLDB_DB', "truck", priority='cmdline')

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, headers=self.headers)

    def parse(self, response):
        car_list = json.loads(response.text)
        for i in car_list["data"]:
            model = i["model"]
            for x in i["data"]:
                for z in x["data"]:
                    brand = z["brand"]
                    for y in z["seriesList"]:
                        series = y
                        meta = {
                            "model": model,
                            "brand": brand,
                            "series": series,
                        }
                        url = "https://www.woniuhuoche.com/truck/api/v1/evaluation/getEvalInfos?brand={}&model={}&series={}".format(
                            brand, model, series)
                        # print(meta)
                        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_series, meta=meta)

    def parse_series(self, response):
        # print(response.text)
        series_list = json.loads(response.text)
        for i in series_list["data"]:
            item = Wo_Niu_Car_Item()
            item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["url"] = response.url
            item["model"] = response.meta["model"]
            item["brand"] = response.meta["brand"]
            item["series"] = response.meta["series"]
            item["boxLen"] = i["boxLen"]
            item["description"] = i["description"]
            item["driveId"] = i["driveId"]
            item["driveName"] = i["driveName"]
            item["emissionId"] = i["emissionId"]
            item["emissionName"] = i["emissionName"]
            item["id"] = i["id"]
            item["lowPrice"] = i["lowPrice"]
            item["oilType"] = i["oilType"]
            item["oilTypeName"] = i["oilTypeName"]
            item["power"] = i["power"]
            item["price"] = i["price"]
            item["volume"] = i["volume"]
            item["statusplus"] = item["brand"] + item["series"] + item["model"] + item["description"] + str(
                item["price"])
            # print(item)
            yield item
