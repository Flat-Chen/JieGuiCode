# -*- coding: utf-8 -*-
import json
import re
import logging
import scrapy
import time
from ..items import DiyidiandongButieItem
from scrapy.conf import settings
import pandas as pd 

website = 'diyidiandong_car'


class KoubeiSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['www.bitauto.com']
    start_urls = ['http://car.d1ev.com/0-10000_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_3_0.html']

    def __init__(self, **kwargs):
        settings.set("WEBSITE", website)
        settings.set("MYSQLDB_DB", "koubei")
        super(KoubeiSpider, self).__init__(**kwargs)
        self.used_time = {}

    def parse(self, response):
        brand_list = response.xpath("//div[@class='li_types']")
        for i in brand_list:
            brand_id = i.xpath(".//@id").extract_first().strip("brand_")
            brand_name = i.xpath(".//div[@class='brand_img']//a/text()").extract_first().strip()
            for j in i.xpath(".//ul[@class='type_list']"):
                factory_name = j.xpath(".//li[@class='li_title']/p/text()").extract_first()
                for z in j.xpath(".//li")[1::]:
                    item = {}
                    item["serise_name"] = z.xpath(".//p/text()").extract_first()
                    item["serise_id"] = z.xpath("./@id").extract_first().strip('series_')
                    item["brand_id"] = brand_id
                    item["brand_name"] = brand_name
                    item["factory_name"] = factory_name
                    url = "http://car.d1ev.com/audi-series-{}/".format(item["serise_id"])
                    yield scrapy.Request(url=url, meta=item, callback=self.parse_family)

    def parse_family(self, response):
        modelid_list = response.xpath("//tbody[@id='sale_all']//tr")
        if len(modelid_list) == 0:
            item = {}
            item["guide_price"] = '暂无报价'
            item["butie_price"] = None
            item["shortdesc"] = None
            item["car_id"] = None

            response.meta.update(item)
            url = "http://car.d1ev.com/car/api/v1000/series/config.do?modelIds=" + str(item["car_id"])
            yield scrapy.Request(url=url, meta=response.meta, callback=self.parse_details)
        else:
            for i in modelid_list:
                item = {}
                item["guide_price"] = i.xpath(".//td[@class='td_price']/text()").extract_first()
                item["butie_price"] = i.xpath(".//td[@class='td_subsidy']/text()").extract_first()
                item["shortdesc"] = i.xpath(".//div[@class='td_wrapper']/span[@class='td_brand']/text()").extract_first()
                cfg_urls = i.xpath(".//div[@class='button--wrapper']/a/@href").getall()
                for cfg_url in cfg_urls:
                    try:
                        item["car_id"] = re.findall(r"peizhi-(\d+)_?", cfg_url)[0]
                        response.meta.update(item)
                        url = "http://car.d1ev.com/car/api/v1000/series/config.do?modelIds=" + str(item["car_id"])

                        yield scrapy.Request(url=url, meta=response.meta, callback=self.parse_details)
                    except IndexError as e:
                        logging.warning(repr(e))


    def parse_details(self, response):
        try:
            data_dict = json.loads(response.text)["data"]
            data = {}
            for i in data_dict:
                for j in i["paramitems"]:
                    try:
                        data.update({j["name"]: j["valueitems"][0]["value"]})
                    except:
                        data.update({j["name"]: None})
        except Exception as e:
            print(repr(e))

        item = DiyidiandongButieItem()
        item["serise_name"] = response.meta["serise_name"]
        item["serise_id"] = response.meta["serise_id"]
        item["brand_id"] = response.meta["brand_id"]
        item["brand_name"] = response.meta["brand_name"]
        item["factory_name"] = response.meta["factory_name"]
        item["guide_price"] = response.meta["guide_price"]
        item["butie_price"] = response.meta["butie_price"]
        item["shortdesc"] = response.meta["shortdesc"]
        item["car_id"] = response.meta["car_id"]
        item["config"] = json.dumps(data, ensure_ascii=False)
        try:
            item["car_body"] = data["车身结构"]
        except:
            item["car_body"] = None
        try:
            item["auto_driver"] = data["自动驾驶级别"]
        except:
            item["auto_driver"] = None
        try:
            item["energy_type"] = data["能源类型"]
        except:
            item["energy_type"] = None
        try:
            item["door"] = data["车门数(个)"]
        except:
            item["door"] = None
        try:
            item["seat"] = data["座位数(个)"]
        except:
            item["seat"] = None
        try:
            item["output"] = data["排量(L)"]
        except:
            item["output"] = None
        try:
            item["environment"] = data["环保标准"]
        except:
            item["environment"] = None
        try:
            item["driver"] = data["驱动方式"]
        except:
            item["driver"] = None
        item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            item["gongxibu"] =data["工信部纯电续航里程(km)"]
        except:
            item["gongxibu"] = None
        try:
            item["air_type"] = data["进气形式"]
        except:
            item["air_type"] = None
        item["url"] = response.url
        item["statusplus"] = response.url + str(item["guide_price"]) + str(item["butie_price"])+str(1)
        # print(item)
        yield item
