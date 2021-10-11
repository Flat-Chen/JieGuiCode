import json
import logging
import re

import requests
import scrapy
from ..items import SouHu
import time
from scrapy.conf import settings

website = 'souhu'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    # start_urls = "https://price.auto.sina.cn/api/salesApi/getHasSaleBrands"
    start_urls = "http://db.auto.sohu.com/home/"
    # //li[@class='close_child']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://auto.sina.com.cn"
    }
    custom_settings = {
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 8,
        "CONCURRENT_REQUESTS": 5
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.counts = 0
        self.carnum = 800000
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        settings.set("MONGODB_DB", "newcar", priority="cmdline")

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, headers=self.headers, )

    def parse(self, response):
        brand_list = response.xpath("//li[@class='close_child']")
        for brand_xpath in brand_list:
            brandid = brand_xpath.xpath(".//h4/a/@id").extract_first().strip("b")
            brand = brand_xpath.xpath(".//h4/a").xpath("string(.)").extract_first().split()[0]

            for factory_xpath in brand_xpath.xpath(".//ul"):
                factory = factory_xpath.xpath(".//li[@class='con_tit']/a").xpath("string(.)").extract_first().split()[0]
                factoryid = factory_xpath.xpath(".//li[@class='con_tit']/a/@id").extract_first().strip("c")
                for chexi in factory_xpath.xpath(".//li")[1::]:
                    serialId = chexi.xpath(".//a/@id").extract_first().strip("m")
                    serialName = chexi.xpath(".//a").xpath("string(.)").extract_first()

                    meta = {
                        "brand": brand,
                        "brandid": brandid,
                        "factory": factory,
                        "factoryid": factoryid,
                        "serialId": serialId,
                        "serialName": serialName,
                    }
                    url = "http://db.auto.sohu.com/model_{}".format(meta["serialId"])
                    yield scrapy.Request(url=url, headers=self.headers, meta=meta,
                                         callback=self.carlist_parse)

    def carlist_parse(self, response):
        car_list = response.xpath("//td[@class='ftdleft']/a")
        for car in car_list:
            car_id = re.findall(r"/(\d)?", car.xpath("./@href").extract_first())[0]
            if car_id == "":
                car_id = re.findall(r"/(\d+)/(\d+)", car.xpath("./@href").extract_first())[0][1]

            meta = {
                "carid": car_id,
                "shortdesc": car.xpath("./text()").extract_first()
            }
            response.meta.update(meta)
            url = "http://db.auto.sohu.com/api/para/data/trim_more_{}.json".format(car_id)
            # print(url,response.meta,'*'*50)
            yield scrapy.Request(url=url, headers=self.headers, meta=response.meta,
                                 callback=self.car_parse)

    #
    def get_price(self, id):
        url = "http://db.auto.sohu.com/autodealer/summary/dealer/trims/priceinfo_{}_310100".format(id)
        try:
            text = requests.get(url=url, headers=self.headers, ).json()["result"][0]
        except:
            text = {
                "trimId": "",
                "locMinPrice": "",
                "surMinPrice": ""
            }
        return text

    #     # 接口
    #     # http: // db.auto.sohu.com / api / para / data / trim_more_147560.json
    def car_parse(self, response):
        text_dict = json.loads(response.text)
        item = SouHu()
        item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        item["url"] = response.url
        item["brand"] = response.meta["brand"]
        item["brandid"] = response.meta["brandid"]
        item["factory"] = response.meta["factory"]
        item["factoryid"] = response.meta["factoryid"]
        item["serialName"] =text_dict["modelName"]
        item["serialId"] = response.meta["serialId"]
        item["autoType"] = text_dict["SIP_T_CONF"]["SIP_C_105"]["v"]
        item["guidePrice"] = text_dict["SIP_T_CONF"]["SIP_C_102"]["v"]
        item["carid"] = response.meta["carid"]
        item["shortdesc"] = response.meta["shortdesc"]
        price = self.get_price(item["carid"])

        item["city_low_price"] = price["locMinPrice"]
        item["nearby_city_price"] = price["surMinPrice"]
        item["body"] = text_dict["SIP_T_CONF"]["SIP_C_106"]["v"]
        item["drivertype"] = text_dict["SIP_T_CONF"]["SIP_C_303"]["v"]
        item["engine"] = text_dict["SIP_T_CONF"]["SIP_C_107"]["v"]
        item["changing_box"] = text_dict["SIP_T_CONF"]["SIP_C_108"]["v"]
        item["oil_wear"] = text_dict["SIP_T_CONF"]["SIP_C_294"]["v"]
        item["baoyang_week"] = text_dict["SIP_T_CONF"]["SIP_C_114"]["v"]
        item["baoyang_price"] = text_dict["SIP_T_CONF"]["SIP_C_304"]["v"]
        item["door"] = text_dict["SIP_T_CONF"]["SIP_C_125"]["v"]
        item["seat"] = text_dict["SIP_T_CONF"]["SIP_C_126"]["v"]
        item["enginetype"] = text_dict["SIP_T_CONF"]["SIP_C_135"]["v"]
        item["output"] = text_dict["SIP_T_CONF"]["SIP_C_136"]["v"]
        item["Airintake"] = text_dict["SIP_T_CONF"]["SIP_C_138"]["v"]
        item["fule"] = text_dict["SIP_T_CONF"]["SIP_C_149"]["v"]
        item["environmental"] = text_dict["SIP_T_CONF"]["SIP_C_155"]["v"]
        item["Transmissiontype"] = text_dict["SIP_T_CONF"]["SIP_C_158"]["v"]
        item["drive"] = text_dict["SIP_T_CONF"]["SIP_C_159"]["v"]
        item["statusplus"] = response.text + "1"
        # yield item
        print(item)
