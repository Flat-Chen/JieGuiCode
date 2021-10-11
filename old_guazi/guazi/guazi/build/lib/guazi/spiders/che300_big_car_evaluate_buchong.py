# https://open.che300.com/api/cv/brand_list  品牌 接口
# https://open.che300.com/api/cv/series_list?brand_id=436  车系接口
# https://open.che300.com/api/cv/model_list?series_id=4421   model 接口
# https://open.che300.com/api/cv/model_config?model_id=121187 车结构的接口
# https://open.che300.com/api/cv/evaluate?brand_id=436&series_id=4421&model_id=1211878&prov_id=21&city_id=79&reg_date=2015-01&mile=2 估值接口
# -*- coding: utf-8 -*-
import json
import logging
import os
import re
import sys
import time

import scrapy
import pandas as pd
# 爬虫名
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from sqlalchemy import create_engine

from ..items import Che300_Big_Car_evaluate_Item

website = 'che300_big_car_evaluate_buchong'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://open.che300.com/api/cv/brand_list"
    headers = {'Referer': 'https://m.che300.com',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(settings['MYSQLDB_USER'],
                                                                                settings['MYSQLDB_PASS'],
                                                                                settings['MYSQL_SERVER'],
                                                                                settings['MYSQL_PORT'],
                                                                                "truck"))

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 10,
        "COOKIES_ENABLED": False,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 8,
    }

    def __init__(self, **kwargs):
        super(GuazicarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', "che300_big_car_evaluate", priority='cmdline')
        settings.set('MYSQLDB_DB', "truck", priority='cmdline')

    # https://open.che300.com/api/cv/evaluate?brand_id=436&series_id=4421&model_id=1211878&prov_id=21&city_id=79&reg_date=2015-01&mile=2 估值接口
    # brand_id: 391
    # series_id: 4293
    # model_id: 1223230
    # prov_id: 3
    # city_id: 3
    # reg_date: 2016 - 01
    # mile: 10
    def start_requests(self):
        # cityid provid
        city_list = [[4, 4], [3, 3]]
        car_list = pd.read_sql("SELECT brand_id,series_id,model_id ,min_year,max_year from che300_big_car_evaluate_online_count updated where isok !=1",
                               con=self.engine, )
        for i in car_list.values.tolist():
            for city in city_list:
                for year in range(int(i[4]))[int(i[3]):]:
                    mile = (int(i[4]) - year) * 2
                    reg_date = str(year) + time.strftime("-%m", time.localtime())
                    meta = {
                        "brand_id": i[0],
                        "series_id": i[1],
                        "model_id": i[2],
                        "prov_id": city[1],
                        "city_id": city[0],
                        "mile": mile,
                        "reg_date": reg_date
                    }
                    url = "https://open.che300.com/api/cv/evaluate?brand_id={}&series_id={}&model_id={}&prov_id={}&city_id={}&reg_date={}&mile={}".format(
                        meta["brand_id"], meta["series_id"], meta["model_id"], meta["prov_id"], meta["city_id"],
                        meta["reg_date"], meta["mile"])
                    yield scrapy.Request(url=url, headers=self.headers, meta=meta)

    def parse(self, response):
        data = json.loads(response.text)
        data_dict = data["data"]["eval_prices"]
        item = Che300_Big_Car_evaluate_Item()
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["brand_id"] = response.meta["brand_id"]
        item["series_id"] = response.meta["series_id"]
        item["model_id"] = response.meta["model_id"]
        item["prov_id"] = response.meta["prov_id"]
        item["city_id"] = response.meta["city_id"]
        item["mile"] = response.meta["mile"]
        item["reg_date"] = response.meta["reg_date"]
        item["default_car_condition"] = data["data"]["default_car_condition"]
        item["good_dealer_high_buy_price"] = data_dict[0]["dealer_high_buy_price"]
        item["good_dealer_low_buy_price"] = data_dict[0]["dealer_low_buy_price"]
        item["good_dealer_high_sold_price"] = data_dict[0]["dealer_high_sold_price"]
        item["good_dealer_buy_price"] = data_dict[0]["dealer_buy_price"]
        item["good_dealer_low_sold_price"] = data_dict[0]["dealer_low_sold_price"]
        item["good_dealer_sold_price"] = data_dict[0]["dealer_sold_price"]
        item["excellent_dealer_high_buy_price"] = data_dict[1]["dealer_high_buy_price"]
        item["excellent_dealer_low_buy_price"] = data_dict[1]["dealer_high_buy_price"]
        item["excellent_dealer_high_sold_price"] = data_dict[1]["dealer_low_buy_price"]
        item["excellent_dealer_buy_price"] = data_dict[1]["dealer_buy_price"]
        item["excellent_dealer_sold_price"] = data_dict[1]["dealer_low_sold_price"]
        item["excellent_dealer_low_sold_price"] = data_dict[1]["dealer_sold_price"]
        item["normal_dealer_high_buy_price"] = data_dict[2]["dealer_high_buy_price"]
        item["normal_dealer_low_buy_price"] = data_dict[2]["dealer_high_buy_price"]
        item["normal_dealer_high_sold_price"] = data_dict[2]["dealer_low_buy_price"]
        item["normal_dealer_buy_price"] = data_dict[2]["dealer_buy_price"]
        item["normal_dealer_low_sold_price"] = data_dict[2]["dealer_low_sold_price"]
        item["normal_dealer_sold_price"] = data_dict[2]["dealer_sold_price"]
        item["statusplus"] = response.text + item["url"]
        yield item
        # print(item)
