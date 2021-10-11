# https://open.che300.com/api/cv/brand_list  品牌 接口
# https://open.che300.com/api/cv/series_list?brand_id=436  车系接口
# https://open.che300.com/api/cv/model_list?series_id=4421   model 接口
# https://open.che300.com/api/cv/model_config?model_id=121187 车结构的接口
# https://open.che300.com/api/cv/evaluate?brand_id=436&series_id=4421&model_id=1211878&prov_id=21&city_id=79&reg_date=2015-01&mile=2 估值接口
# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import re
import sys
import time

import scrapy
import pandas as pd
# 爬虫名
from pymysql import connect
from redis import Redis
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from sqlalchemy import create_engine

from ..items import Che300_Big_Car_evaluate_Item
import hashlib

# ****************************************************************************************
# 每个月 运行之前需要先 删除过滤池
# ****************************************************************************************
website = 'che300_big_car_evaluate'

redis_cli = Redis(host="192.168.1.249", port=6379, db=2)


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
        'CONCURRENT_REQUESTS': 16,
        "COOKIES_ENABLED": False,
        "RETRY_TIMES": 8,
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,  # 关闭默认下载器
            "guazi.proxy.Che300ProxyMiddleware": 530

        }
    }

    def __init__(self, **kwargs):
        self.good_type_list = [
            "111",
            "普通轻型货物",
            "鲜活农产品",
            "水产品",
            "砂石/煤/渣土",
            "大石块",
        ]
        super(GuazicarSpider, self).__init__(**kwargs)
        self.counts = 1
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MYSQLDB_DB', "truck", priority='cmdline')

    def redis_tools(self, url):
        redis_md5 = hashlib.md5(url.encode("utf-8")).hexdigest()
        valid = redis_cli.sadd("che300_big_car_evaluate", redis_md5)
        return valid

    def get_city_prive(self):
        engine_1 = create_engine('mysql+pymysql://baogang:Baogang@2019@192.168.2.120:3306/peoplez?charset=utf8')
        city = pd.read_sql("select cityid,provid from che300_city where provincial_capital=1 ", con=engine_1)
        return city.values.tolist()

    def change_table_name(self):
        # alter table 旧表名 rename 新表名
        # 先判断 新表是否存在 然后在修改

        con = connect(host='192.168.1.94', port=3306, user='dataUser94', password='94dataUser@2020', database='truck',
                      charset='utf8')
        table_time = time.strftime("%Y_%m", time.localtime())
        cs1 = con.cursor()
        index = cs1.execute("show tables like 'che300_big_car_evaluate_online_{}'".format(table_time))
        if int(index) == 1:
            logging.log(msg='表名已经存在 不需要修改-----------------------------------------------------', level=logging.INFO)
            cs1.close()
            con.close()
            return
        else:
            sql = "alter table che300_big_car_evaluate_online rename  to che300_big_car_evaluate_online_{}".format(
                table_time)
            try:
                cs1.execute(sql)
            except:
                logging.log(msg='表名不存在-----------------------------------------------------', level=logging.INFO)
            else:
                logging.log(msg='修改表名成功----------------------------------------------------------------',
                            level=logging.INFO)
            cs1.close()
            con.close()

    def start_requests(self):
        # cityid provid
        # 删除指纹
        # redis_cli.delete("che300_big_car_evaluate")
        # 数据库重新命名
        self.change_table_name()
        city_list = self.get_city_prive()
        car_list = pd.read_sql(
            "SELECT brand_id,series_id,model_id ,min_year,max_year ,'type' from che300_big_car_online",
            con=self.engine, )
        max_year = int(time.strftime("%Y", time.localtime()))
        car_list1 = car_list.values.tolist()
        random.shuffle(car_list1)
        for i in car_list1:
            for city in city_list:
                for year in range(int(max_year) + 1)[int(i[3]):]:
                    mile = (max_year - year) * 2
                    if year == max_year:
                        mile = 0.1
                    if i[5] == '载货车':
                        url = "https://dingjia.che300.com/pro/v1/cv/evaluate?brand_id={}&series_id={}&model_id={}&prov_id={}&city_id={}&reg_date={}&mile={}&tire_used_level=1&goods_type={}"
                        for type in range(5):
                            reg_date = str(year) + time.strftime("-%m", time.localtime())
                            meta = {
                                "brand_id": i[0],
                                "series_id": i[1],
                                "model_id": i[2],
                                "prov_id": int(city[1]),
                                "city_id": int(city[0]),
                                "mile": mile,
                                "reg_date": reg_date,
                                "goods_type": type + 1
                            }
                            # url ="https://dingjia.che300.com/pro/v1/cv/evaluate?brand_id=437&series_id=4422&model_id=1244718&prov_id=1&city_id=1&reg_date=2017-1&mile=2&tire_used_level=1&goods_type=1"
                            url = url.format(
                                meta["brand_id"], meta["series_id"], meta["model_id"], meta["prov_id"], meta["city_id"],
                                meta["reg_date"], meta["mile"], type + 1)
                            logging.log(msg="down -----------------------{}".format(self.counts), level=logging.INFO)
                            self.counts = self.counts + 1
                            valid = self.redis_tools(url)
                            if valid == 0:
                                logging.log(msg="this http request is repetition", level=logging.INFO)
                                continue
                            else:
                                yield scrapy.Request(url=url, meta=meta, headers=self.headers, dont_filter=True)
                    else:
                        url = "https://dingjia.che300.com/pro/v1/cv/evaluate?brand_id={}&series_id={}&model_id={}&prov_id={}&city_id={}&reg_date={}&tire_used_level=1&mile={}"
                        reg_date = str(year) + time.strftime("-%m", time.localtime())
                        meta = {
                            "brand_id": i[0],
                            "series_id": i[1],
                            "model_id": i[2],
                            "prov_id": int(city[1]),
                            "city_id": int(city[0]),
                            "mile": mile,
                            "reg_date": reg_date,
                            "goods_type": None
                        }
                        # url ="https://dingjia.che300.com/pro/v1/cv/evaluate?brand_id=437&series_id=4422&model_id=1244718&prov_id=1&city_id=1&reg_date=2017-1&mile=2&tire_used_level=1&goods_type=1"
                        url = url.format(
                            meta["brand_id"], meta["series_id"], meta["model_id"], meta["prov_id"], meta["city_id"],
                            meta["reg_date"], meta["mile"])
                        logging.log(msg="down -----------------------{}".format(self.counts), level=logging.INFO)
                        self.counts = self.counts + 1
                        valid = self.redis_tools(url)
                        if valid == 0:
                            logging.log(msg="this http request is repetition", level=logging.INFO)
                            continue
                        else:
                            yield scrapy.Request(url=url, meta=meta, headers=self.headers, dont_filter=True)

    def parse(self, response):
        data = json.loads(response.text)
        data_dict = data["data"]["eval_prices"]
        item = Che300_Big_Car_evaluate_Item()
        try:
            item["goods_type"] = self.good_type_list[response.meta["goods_type"]]
        except:
            item["goods_type"] = None
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
        for i in data_dict:
            ci = i["condition"]
            item["{}_dealer_high_buy_price".format(ci)] = i["dealer_high_buy_price"]
            item["{}_dealer_low_buy_price".format(ci)] = i["dealer_low_buy_price"]
            item["{}_dealer_high_sold_price".format(ci)] = i["dealer_high_sold_price"]
            item["{}_dealer_buy_price".format(ci)] = i["dealer_buy_price"]
            item["{}_dealer_low_sold_price".format(ci)] = i["dealer_low_sold_price"]
            item["{}_dealer_sold_price".format(ci)] = i["dealer_sold_price"]

        item["statusplus"] = response.text + item["url"]
        yield item
        # print(item)
