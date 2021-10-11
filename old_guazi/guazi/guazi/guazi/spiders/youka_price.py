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
from ..items import youka_prcie

website = 'youka_price'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://www.365youka.com/truck-foton-web/api/truck/v1/list?pageSize=40&page={}&truckType=1"
    headers = {'Referer': 'https://www.woniuhuoche.com/',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    index = True
    car_url = "https://www.365youka.com/truck-foton-web/api/truck/v1/getTruckDetail?truckId={}"
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
        for i in range(1000):
            if self.index == True:
                url = self.start_urls.format(i + 1)
            else:
                break
            yield scrapy.Request(url=url, headers=self.headers)

    def parse(self, response):
        car_list = json.loads(response.text)["data"]
        if car_list == []:
            self.index = False
        for car in car_list:
            meta = {}
            meta["id"] = car["id"]
            meta["createTime"] = car["createTime"]
            meta["truckTitle"] = car["truckTitle"]
            meta["truckDriveform"] = car["truckDriveform"]
            meta["dayTag"] = car["dayTag"]
            meta["truckPrice"] = car["truckPrice"]
            meta["truckAddress"] = car["truckAddress"]
            meta["contactMobile"] = car["contactMobile"]
            url = self.car_url.format(meta["id"])
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_series, meta=meta)

    def parse_series(self, response):
        # print(response.text)
        car = json.loads(response.text)
        item = youka_prcie()
        item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["id"] = response.meta["id"]
        item["createTime"] = response.meta["createTime"]
        item["truckTitle"] = response.meta["truckTitle"]
        item["truckDriveform"] = response.meta["truckDriveform"]
        item["dayTag"] = response.meta["dayTag"]
        item["truckPrice"] = response.meta["truckPrice"]
        item["truckAddress"] = response.meta["truckAddress"]
        item["contactMobile"] = response.meta["contactMobile"]
        item["provincesName"] = car["data"]["provincesName"]
        item["districtName"] = car["data"]["districtName"]
        item["contactname"] = car["data"]["contactname"]
        item["showmileage"] = car["data"]["showmileage"]
        item["motorName"] = car["data"]["motorName"]
        item["oiltype"] = car["data"]["oiltype"]
        item["environment"] = car["data"]["truckDriveform"].split("/")[-1]

        for i in car["JSONArray"]:
            if i["key"] =="箱体长度":
                item["bodylong"] =i["value"]
            if i["key"] =="是否可过户":
                item["ownership"] = i["value"]
        item["nature"] = car["data"]["carNature"]
        item["type"] = car["data"]["carLevel"]
        item["color"] = car["data"]["color"]
        item["insurance"] = car["data"]["isInsurance"]
        item["year_check"] = car["data"]["inspectionTime"]
        item["city"] = car["data"]["cityName"]
        item["brandName"] = car["data"]["brandName"]
        item["seriesName"] = car["data"]["seriesName"]
        item["modelName"] = car["data"]["modelName"]

        item["statusplus"] = str(car)+str(1)
        # print(item)
        yield item
