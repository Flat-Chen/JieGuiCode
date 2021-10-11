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

# 爬虫名
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from sqlalchemy import create_engine

from ..items import Che300_Big_Car_Item

website = 'che300_big_car'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://open.che300.com/api/cv/brand_list"
    headers = {'Referer': 'https://m.che300.com',
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
        brand_list = json.loads(response.text)
        for i in brand_list["data"]["list"]:
            brand_id = i["id"]
            brand_name = i["name"]
            meta = {
                "brand_id": brand_id,
                "brand_name": brand_name,
            }
            url = "https://open.che300.com/api/cv/series_list?brand_id={}".format(brand_id)
            yield scrapy.Request(url=url, headers=self.headers, meta=meta, callback=self.parse_series)

    def parse_series(self, response):
        # print(response.text)
        series_list = json.loads(response.text)
        for i in series_list["data"]["list"]:
            series_id = i["id"]
            series_name = i["name"]
            meta = {
                "series_id": series_id,
                "series_name": series_name,
            }
            response.meta.update(meta)
            url = "https://open.che300.com/api/cv/model_list?series_id={}".format(series_id)
            yield scrapy.Request(url=url, headers=self.headers, meta=response.meta, callback=self.parse_model)

    def parse_model(self, response):
        print(response.meta)
        print('parse model: ', response.text)
        model_list = json.loads(response.text)
        for i in model_list["data"]["list"]:
            model_id = i["id"]
            model_name = i["name"]
            meta = {
                "model_id": model_id,
                "model_name": model_name,
                "price": i["price"],
                "discharge_standard": i["discharge_standard"],
                "liter": i["liter"],
                "car_type": i["car_type"],
                "max_year": i["max_year"],
                "min_year": i["min_year"],
            }
            response.meta.update(meta)
            url = "https://open.che300.com/api/cv/model_config?model_id={}".format(model_id)
            yield scrapy.Request(url=url, headers=self.headers, meta=response.meta, callback=self.parse_car)

    def parse_car(self, response):
        car_dict = json.loads(response.text)["data"]

        item = Che300_Big_Car_Item()
        # for car_dict in car_dict_list:
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["brand_id"] = response.meta["brand_id"]
        item["brand_name"] = response.meta["brand_name"]
        item["series_id"] = response.meta["series_id"]
        item["series_name"] = response.meta["series_name"]
        item["model_id"] = response.meta["model_id"]
        item["model_name"] = response.meta["model_name"]
        item["price"] = response.meta["price"]
        item["discharge_standard"] = response.meta["discharge_standard"]
        item["liter"] = response.meta["liter"]
        item["car_type"] = response.meta["car_type"]
        item["max_year"] = response.meta["max_year"]
        item["min_year"] = response.meta["min_year"]
        item["gonggao_type"] = car_dict[0]["基本信息"][0]["公告型号"]
        item["type"] = car_dict[0]["基本信息"][1]["类型"]
        item["driver"] = car_dict[0]["基本信息"][2]["驱动形式"]
        item["wheel"] = car_dict[0]["基本信息"][3]["轴距（mm）"]
        item["long"] = car_dict[0]["基本信息"][4]["车身长度（米）"]
        item["width"] = car_dict[0]["基本信息"][5]["车身宽度（米）"]
        item["hight"] = car_dict[0]["基本信息"][6]["车身高度（米）"]
        item["qwheelbase"] = car_dict[0]["基本信息"][7]["前轮距(mm)"]
        item["hwheelbase"] = car_dict[0]["基本信息"][8]["后轮距(mm)"]
        item["weight"] = car_dict[0]["基本信息"][9]["整车重量（吨）"]
        item["load"] = car_dict[0]["基本信息"][10]["额定载重（吨）"]
        item["zong_weight"] = car_dict[0]["基本信息"][11]["总质量（吨）"]
        item["speed"] = car_dict[0]["基本信息"][12]["最高车速（km/h）"]
        item["production"] = car_dict[0]["基本信息"][13]["产地"]
        item["overhang"] = car_dict[0]["基本信息"][14]["前悬/后悬(mm)"]
        item["angle"] = car_dict[0]["基本信息"][15]["接近角/离去角"]
        item["overturn"] = car_dict[0]["基本信息"][16]["翻转形式"]
        item["ton_level"] = car_dict[0]["基本信息"][17]["吨位级别"]
        item["manufacturers"] = car_dict[0]["基本信息"][18]["生产厂家"]
        item["guide_price"] = car_dict[0]["基本信息"][19]["整车参考价"]
        item["traction"] = car_dict[0]["基本信息"][20]["牵引总质量（吨）"]
        item["engine"] = car_dict[1]["发动机"][0]["发动机"]
        item["lwvnumber"] = car_dict[1]["发动机"][1]["汽缸数"]
        item["fueltype"] = car_dict[1]["发动机"][2]["燃料种类"]
        item["output"] = car_dict[1]["发动机"][3]["排量（L）"]
        item["emission"] = car_dict[1]["发动机"][4]["排放标准"]
        item["maxpower"] = car_dict[1]["发动机"][5]["最大输出功率（kW）"]

        item["maxps"] = car_dict[1]["发动机"][6]["最大马力"]
        item["nm"] = car_dict[1]["发动机"][7]["扭矩（N·m）"]
        item["maxnm"] = car_dict[1]["发动机"][8]["最大扭矩转速（rpm）"]
        item["rated_speed"] = car_dict[1]["发动机"][9]["额定转速（rpm）"]
        item["Engine_form"] = car_dict[1]["发动机"][10]["发动机形式"]
        item["output_ml"] = car_dict[1]["发动机"][11]["排量（ML）"]
        item["box_long"] = car_dict[2]["货箱参数"][0]["货箱长度（米）"]
        item["box_width"] = car_dict[2]["货箱参数"][1]["货箱宽度（米）"]
        item["box_high"] = car_dict[2]["货箱参数"][2]["货箱高度（米）"]
        item["box_type"] = car_dict[2]["货箱参数"][3]["货箱形式"]
        item["people_num"] = car_dict[3]["驾驶室参数"][0]["准乘人数"]
        item["seat_number"] = car_dict[3]["驾驶室参数"][1]["座位排数"]
        item["cage"] = car_dict[3]["驾驶室参数"][2]["驾驶室类型"]
        item["Transmissions"] = car_dict[4]["变速箱"][0]["变速箱"]
        item["qFil_number"] = car_dict[4]["变速箱"][1]["前进挡位数"]
        item["hFil_number"] = car_dict[4]["变速箱"][2]["倒挡数"]
        item["shift_gear"] = car_dict[4]["变速箱"][3]["换挡方式"]
        item["tires_num"] = car_dict[5]["轮胎"][0]["轮胎数"]
        item["tires_specifications"] = car_dict[5]["轮胎"][1]["轮胎规格"]
        item["Brake_form"] = car_dict[6]["制动器"][0]["制动形式"]
        item["tank"] = car_dict[7]["油箱"][0]["油箱容量"]
        item["tank_texture"] = car_dict[7]["油箱"][1]["油箱材质"]
        item["Rear_description"] = car_dict[8]["底盘"][0]["后桥描述"]
        item["rear_speed"] = car_dict[8]["底盘"][1]["后桥速比"]
        item["spring_num"] = car_dict[8]["底盘"][2]["弹簧片数"]
        item["suspension_type"] = car_dict[8]["底盘"][3]["悬架类型"]
        item["chassis_type"] = car_dict[8]["底盘"][4]["底盘型号"]
        item["frame"] = car_dict[8]["底盘"][5]["车架断面"]
        item["clutch"] = car_dict[8]["底盘"][6]["离合器"]
        item["endurance_mileage"] = car_dict[9]["电动机"][0]["续航里程"]
        item["battery_capacity"] = car_dict[9]["电动机"][1]["电池容量(kWh)"]
        item["url"] = response.url
        item["statusplus"] = item["url"] + str(item["price"]) + str(item["guide_price"])
        yield item
