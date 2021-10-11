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

from ..items import Woniu_Car_evaluate_Item

website = 'woniu_car_evakuate'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://open.che300.com/api/cv/brand_list"
    headers = {'https': '//www.woniuhuoche.com/truck/api/v1/evaluation/getEvalInfoWithZimu',
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

    # https://www.woniuhuoche.com/truck/api/v1/evaluation/newEvalPrice?brand=%E5%A5%A5%E9%A9%B0%E6%B1%BD%E8%BD%A6&buyDate=2010-1&city=99&customerId=458313&drive=6X2&emission=%E5%9B%BD%E4%BA%94&model=%E8%BD%BD%E8%B4%A7%E8%BD%A6&oiltype=%E6%9F%B4%E6%B2%B9&power=168%E5%8C%B9&price=16.25&province=12&residueRatio=1&series=%E5%A5%A5%E9%A9%B0D%E7%B3%BB&boxLen=&volume=
    # brand: 奥驰汽车
    # buyDate: 2010-1
    # city: 99
    # drive: 6X2
    # emission: 国五
    # model: 载货车
    # oiltype: 柴油
    # power: 168匹
    # price: 16.25
    # province: 12
    # residueRatio: 1 到10
    # series: 奥驰D系
    # boxLen:
    # volume
    def start_requests(self):
        # cityid provid
        city_list = [['236', "22"], ["73", "9"]]
        car_list = pd.read_sql(
            "SELECT brand,driveName,emissionName ,model,oiltype,power,price,series, boxLen,volume ,description from woniu_car_online ",
            con=self.engine, )
        for i in car_list.values.tolist():
            for city in city_list:
                print(city)
                for year in range(int(time.strftime("%Y", time.localtime())) + 1)[2010::]:
                    buyDate = str(year) + time.strftime("-%m", time.localtime())
                    for id in range(10):
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
                            "residueRatio": id + 1,
                            "series": i[7],
                            "boxLen": i[8],
                            "volume": i[9],
                            'description': i[10]
                        }
                        url = "https://www.woniuhuoche.com/truck/api/v1/evaluation/newEvalPrice?brand={}&buyDate={}&city={}&drive={}&emission={}&model={}&oiltype={}&power={}&price={}&province={}&residueRatio={}&series={}&boxLen={}&volume={}".format(
                            meta["brand"], meta["buyDate"], meta["city"], meta["drive"], meta["emission"],
                            meta["model"], meta["oiltype"], meta["power"], meta["price"], meta["province"],
                            meta["residueRatio"], meta["series"], meta["boxLen"], meta["volume"], )
                        print(url)

                        yield scrapy.Request(url=url, headers=self.headers, meta=meta)

    def parse(self, response):
        data = json.loads(response.text)
        data_dict = data["data"]
        item = Woniu_Car_evaluate_Item()
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
        item["residueRatio"] = response.meta["residueRatio"]
        item["series"] = response.meta["series"]
        item["boxLen"] = response.meta["boxLen"]
        item["volume"] = response.meta["volume"]
        item["badMerchantPrice"] = data_dict["merchant"]["badMerchantPrice"]
        item["midMerchantPrice"] = data_dict["merchant"]["midMerchantPrice"]
        item["fineMerchantPrice"] = data_dict["merchant"]["fineMerchantPrice"]
        item["badPersonPrice"] = data_dict["person"]["badPersonPrice"]
        item["midPersonPrice"] = data_dict["person"]["midPersonPrice"]
        item["badPersonPrice"] = data_dict["person"]["badPersonPrice"]
        item["fineOldTruckPrice"] = data_dict["oldTruck"]["fineOldTruckPrice"]
        item["badOldTruckPrice"] = data_dict["oldTruck"]["badOldTruckPrice"]
        item["midOldTruckPrice"] = data_dict["oldTruck"]["midOldTruckPrice"]
        item["seepName"] = data["backup"]["seepName"]
        item["seecName"] = data["backup"]["seecName"]
        item["description"] = response.meta["description"]
        item["statusplus"] = item["description"] + response.url + item["midOldTruckPrice"] + item["badOldTruckPrice"] + \
                             item["fineOldTruckPrice"] + item["badPersonPrice"] + item["midPersonPrice"] + item[
                                 "badPersonPrice"] + item["badMerchantPrice"] + item["midMerchantPrice"] + item[
                                 "fineMerchantPrice"]
        yield item
