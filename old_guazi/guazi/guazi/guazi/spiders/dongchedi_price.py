# -*- coding: utf-8 -*-
import json
import logging
import os
import pymongo
import random
import re
import sys
import time

import pandas as pd
import scrapy

# 爬虫名
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from sqlalchemy import create_engine

from ..items import dongchedi

website = 'dongchedi_price'


# 必须有自己的中间件  切与其他的没有关系
class GuazicarSpider(scrapy.Spider):
    name = website
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://www.dcdapp.com/auto",
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 10,
    }

    def __init__(self, **kwargs):
        settings.set("WEBSITE", website)
        settings.set("MONGODB_DB", "newcar")
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        super(GuazicarSpider, self).__init__(**kwargs)
        self.used_time = {}
        self.city_list = [
            "北京",
            "重庆",
            "武汉",
            "上海",
            "天津",
            "苏州",
            "广州",
            "成都",
            "西安",
            "深圳",
            "杭州",
            "南京",
        ]

    def get_SerialID(self):
        """
        1：获取SerialID_set()
        :return:
        """
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection["newcar"]
        collection = db["dongchedi_car"]

        a = collection.find({}, {"series_id": 1, "_id": 0})
        SerialID_set = set()
        for i in a:
            SerialID_set.add(i["series_id"])
        return list(SerialID_set)

    def start_requests(self):
        data_list = self.get_SerialID()
        for i in data_list:
            for j in self.city_list:
                item = {
                    "city": j,
                    "series_id": i
                }
                url = "https://m.dcdapp.com/motor/car_page/m/v1/series_all_json/?series_id={}&city_name={}&device_id=0&req_type=all&recommend_count=6&data_from=m_station&m_station_dealer_price_v=1&show_city_price=1".format(
                    i, j)
                yield scrapy.FormRequest(url=url, headers=self.headers, meta=item)

    # 车型
    def parse(self, response):

        data_list = json.loads(response.text)["data"]["car_year_group"]
        for i in data_list:
            for j in i["cars"]:
                if j["type"] != "1037":
                    continue
                item = {}
                try:
                    item["series_id"] = response.meta["series_id"]
                    item["city"] = response.meta["city"]
                    item["dealer_prov"] = j["info"]["price_info"]["dealer_prov"]
                    item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item["url"] = response.url
                    item["shortdesc"] = j["info"]["name"]
                    item["price"] = j["info"]["price"]
                    item["makeyear"] = j["info"]["year"]
                    item["car_id"] = j["info"]["id"]
                    # 车主
                    item["official_price"] = j["info"]["owner_price_summary"]["naked_price_avg"]
                    # 经销商
                    item["dealer_price"] = j["info"]["dealer_price"]
                    item["statusplus"] =str(item["car_id"])+str(   item["city"] )+str( item["official_price"])+str( item["dealer_price"] )+str(111)
                except:
                    pass
                else:
                    # print(item)
                    yield  item