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

from ..items import YouKa_Car_Item

website = 'youka_car_evaluate'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://www.china2cv.com/"
    headers = {'Referer': 'https://www.china2cv.com/',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(settings['MYSQLDB_USER'],
                                                                                settings['MYSQLDB_PASS'],
                                                                                settings['MYSQL_SERVER'],
                                                                                settings['MYSQL_PORT'],
                                                                                "truck"))

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(GuazicarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MYSQLDB_DB', "truck", priority='cmdline')

    # https://www.china2cv.com/truck-foton-web/api/evaluation/v1/newEvalPrice?address=%E9%87%8D%E5%BA%86%E5%B8%82%E9%87%8D%E5%BA%86%E5%B8%82&brand=%E5%A5%A5%E9%A9%B0%E6%B1%BD%E8%BD%A6&buyDate=2010-01&city=236&drive=4X2&emission=%E5%9B%BD%E4%BA%94&mileage=2&model=%E8%87%AA%E5%8D%B8%E8%BD%A6&oiltype=%E6%9F%B4%E6%B2%B9&power=87%E5%8C%B9&price=7.50&province=22&series=%E5%A5%A5%E9%A9%B0T%E7%B3%BB
    # address: 重庆市重庆市
    # brand: 奥驰汽车
    # buyDate: 2010-01
    # city: 236
    # drive: 4X2
    # emission: 国五
    # mileage: 2
    # model: 自卸车
    # oiltype: 柴油
    # power: 87匹
    # price: 7.50
    # province: 22
    # series: 奥驰T系
    def start_requests(self):
        # cityid provid
        city_list = [['236', "22"], ["73", "9"]]
        car_list = pd.read_sql(
            "SELECT brand,driveName,emissionName ,model,oiltype,power,price,series from youka_car_online ",
            con=self.engine, )
        for i in car_list.values.tolist():
            for city in city_list:
                print(city)
                for year in range(int(time.strftime("%Y", time.localtime())) + 1)[2010::]:
                    buyDate = str(year) + time.strftime("-%m", time.localtime())
                    # for id in range(10):
                    meta = {
                        "brand": i[0],
                        "buyDate": buyDate,
                        "city": city[0],
                        "drive": i[1],
                        "emission": i[2],
                        "model": i[3],
                        "oiltype": i[4],
                        "power": i[5],
                        "price": i[6],
                        "province": city[1],
                        "mileage": int(2 * (int(time.strftime("%Y", time.localtime())) - year)),
                        "series": i[7],
                    }
                    url = "https://www.china2cv.com/truck-foton-web/api/evaluation/v1/newEvalPrice?brand={}&buyDate={}&city={}&drive={}&emission={}&model={}&oiltype={}&power={}&price={}&province={}&mileage={}&series={}".format(
                        meta["brand"], meta["buyDate"], meta["city"], meta["drive"], meta["emission"],
                        meta["model"], meta["oiltype"], meta["power"], meta["price"], meta["province"],
                        meta["mileage"], meta["series"], )
                    # print(url)

                    yield scrapy.Request(url=url, headers=self.headers, meta=meta)

    def parse(self, response):
        print(response.url,"*"*50)
        data = json.loads(response.text)
        data_dict = data["data"]
        item = YouKa_Car_Item()
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["brand"] = response.meta["brand"]
        item["buyDate"] = response.meta["buyDate"]
        item["city"] = response.meta["city"]
        item["drive"] = response.meta["drive"]
        item["emission"] = response.meta["emission"]
        item["model"] = response.meta["model"]
        item["oiltype"] = response.meta["oiltype"]
        item["power"] = response.meta["power"]
        item["price"] = response.meta["price"]
        item["province"] = response.meta["province"]
        item["mileage"] = response.meta["mileage"]
        item["series"] = response.meta["series"]
        item["fineMapbuyPrice"] = data_dict["fineMap"]["buyPrice"]
        item["fineMapretailPrice"] = data_dict["fineMap"]["retailPrice"]
        item["ordinaryMapretailPrice"] = data_dict["ordinaryMap"]["retailPrice"]
        item["ordinaryMapbuyPrice"] = data_dict["ordinaryMap"]["buyPrice"]
        item["goodMaperetailPrice"] = data_dict["goodMap"]["retailPrice"]
        item["goodMapbuyPrice"] = data_dict["goodMap"]["buyPrice"]
        item["statusplus"] = response.url + response.text
        yield item
