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
from ..items import  Wo_Niu_Car_Item

website = 'youka_car'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://www.china2cv.com/truck-foton-web/api/evaluation/v1/PCGetEvalInfoCondition"
    headers = {'Referer': 'https://www.china2cv.com',
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
            for x in i["brandList"]["data"]:
                for z in x["data"]:
                    brand = z["brand"]
                    for y in z["seriesList"]:
                        series_name = y["series_name"]
                        meta = {
                            "model": model,
                            "brand": brand,
                            "series": series_name,
                        }
                        url = "https://www.china2cv.com/truck-foton-web/api/evaluation/v1/getEvalInfos?brand={}&model={}&series={}".format(
                            brand, model, series_name)
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
            # item["boxLen"] = i["boxLen"]
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
            # item["volume"] = i["volume"]
            item["statusplus"] = item["brand"] + item["series"] + item["model"] + item[
                "description"] + str(
                item["price"])+str(1)
            # print(item)
            yield item


