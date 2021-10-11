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

from ..items import shiqiao_Car

website = 'shiqiao_car'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    headers = {'Referer': 'https://youche.shiqiaokache.com/',
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
    # https://youche.shiqiaokache.com/auct/customerBulletinModel/getVehParaConfListByType.do?styleId=180322433026068
    def start_requests(self):
        # cityid provid
        car_list = pd.read_sql(
            "SELECT carid from shiqiao_car_base_online ",
            con=self.engine, )
        for i in car_list.values.tolist():
            print(i)
            url = "https://youche.shiqiaokache.com/auct/customerBulletinModel/getVehParaConfListByType.do?styleId={}".format(i[0])
            yield scrapy.Request(url=url, headers=self.headers, )

    def parse(self, response):
        data = json.loads(response.text)["data"]
        item =shiqiao_Car()
        item["grabtime"]=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] =response.url
        configs={}
        for  i in data["configs"]:
            configs.update({i["parameterName"]:i["parameterValue"]})
        item["configs"]=json.dumps(configs,ensure_ascii=False)
        item["carid"]=data["vechileStyle"]["styleId"]
        item["modelid"]=data["vechileStyle"]["modelId"]
        item["styleBulletinModel"]=data["vechileStyle"]["styleBulletinModel"]
        item["mdfUsrId"]=data["vechileStyle"]["mdfUsrId"]
        item["purposeId"]=data["vechileStyle"]["purposeId"]
        item["styleName"]=data["vechileStyle"]["styleName"]
        item["modelName"]=data["vechileStyle"]["modelName"]
        item["crtTm"]=data["vechileStyle"]["crtTm"]
        item["brandid"]=data["vechileStyle"]["makeId"]
        item["crtUsrId"]=data["vechileStyle"]["crtUsrId"]
        item["isTrailer"]=data["vechileStyle"]["isTrailer"]
        item["makeName"]=data["vechileStyle"]["makeName"]
        item["styleDisname"]=data["vechileStyle"]["styleDisname"]
        item["isOutest"]=data["vechileStyle"]["isOutest"]
        item["statusplus"] =str(item["configs"])+response.url
        # print(item)
        yield  item