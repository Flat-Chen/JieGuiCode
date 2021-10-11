# -*- coding: UTF-8 -*-
import json
import re
import time
import redis
import scrapy
import logging
from scrapy.conf import settings
from ..items import GuaziItem
from ..redis_bloom import BloomFilter
website = 'souche'


class CarSpider(scrapy.Spider):
    name = website
    # start_urls = get_url()
    start_urls = 'https://aolai.souche.com/v1/searchApi/searchCar.json'
    headers = {'Referer': 'https://www.guazi.com/www/',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    index = True
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,

    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0

    def start_requests(self):
        for i in range(1000):
            if self.index:
                data = {
                    "isYiChengGou": "",
                    "keyword": "",
                    "brandCode": "",
                    "seriesCode": "",
                    "price": "",
                    "modelCode": "",
                    "carModel": "",
                    "carAge": "",
                    "mileage": "",
                    "gearboxType": "",
                    "displacement": "",
                    "emissionStandard": "",
                    "bodyColor": "",
                    "carBody": "",
                    "fuelType": "",
                    "seatingCapacity": "",
                    "drivingMode": "",
                    "country": "",
                    "pageNo": str(i + 1),
                    "pageSize": '36',
                    "from": "pc",
                    "cityCode": "",
                    "provinceCode": "",
                    "shopCode": "",
                    "sort": "smartSorting"

                }
                yield scrapy.FormRequest(url=self.start_urls, formdata=data, dont_filter=True, headers=self.headers)
            else:
                return

    def parse(self, response):
        car_list = json.loads(response.text)['data']["items"]
        if car_list == []:
            self.index = False
        else:
            for car in car_list:
                try:
                    level = car["carModel"]
                except:
                    level = None
                meta = {
                    "carid": car["carId"],
                    "url": "https://aolai.souche.com/v1/carDetailsApi/carDetailInfo.json?carId=" + car["carId"],
                    "brand": car["brandName"],
                    "city": car["cityName"],
                    # "sold_date": car[""],
                    # "prov": car[""],
                    "seriesid": car["seriesCode"],
                    "brandid": car["brandCode"],
                    "series": car["seriesName"],
                    "shortdesc": car["modelName"],
                    # "post_time":car[""]
                    "mileage": car["mileageStr"],
                    "registeryear": car["registerYear"],
                    'level':level,
                    "registerdate": car["firstLicensePlateDateStr"],
                    'price': car["salePrice"]
                }
                yield scrapy.Request(url=meta["url"], callback=self.parse_car, meta=meta, dont_filter=True)

    def parse_car(self, response):
        grap_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        car_dict = json.loads(response.text)["data"]
        # print(car_dict)
        self.counts += 1
        logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)
        item = GuaziItem()
        item["carid"] = response.meta["carid"]
        item["car_source"] = "souche"
        item["usage"] = None
        item["grab_time"] = grap_time
        item["update_time"] = None
        try:
            item["post_time"] = '-'.join(re.findall(r'(\d{4})年(\d{2})月(\d{2})日', car_dict['baseCarInfoView']['mileageDescription'])[0])
        except:
            item["post_time"] =None

        item["sold_date"] = None
        item["pagetime"] = None
        item["parsetime"] =grap_time
        item["shortdesc"] = response.meta["shortdesc"]
        item["pagetitle"] = None
        item["url"] = response.url
        item["newcarid"] = None
        item["status"] = "sale"
        item["brand"] = response.meta["brand"]
        item["series"] = response.meta["series"]
        item["factoryname"] = None
        item["modelname"] = None
        item["brandid"] = response.meta["brandid"]
        item["familyid"] = response.meta["seriesid"]
        item["seriesid"] = response.meta["seriesid"]
        try:
            item['makeyear'] = re.findall(r"(\d*)款", response.meta["shortdesc"])[0]
        except:
            item['makeyear'] = None
        item["registeryear"] = response.meta["registeryear"]
        item["produceyear"] = None
        item["body"] = None
        item["bodystyle"] = None

        item["level"] = response.meta["level"]
        item["fueltype"] = None
        item["driverway"] = None
        item["guideprice"] = None
        # 新车指导价46.30万(含税)
        item["guidepricetax"] = car_dict["baseCarInfoView"]["newPriceText"]
        item["doors"] = None
        for i in car_dict["carBaseConfigsView"]:
            if i["title"] == "排放标准":
                item["emission"] = i["value"]
            if i["title"] == '变速箱':
                item["gear"] = i["value"]
            if i["title"] == '排量':
                item["output"] = i["value"]
            if i["title"] == '颜色':
                item["color"] = i["value"]
        for i in car_dict["carBaseStructureConfigView"]["itemValue"]:
            if i["title"] == "长*宽*高(mm)":
                item["length"] = i["value"].split("*")[0]
                item["width"] = i["value"].split("*")[1]
                item["height"] = i["value"].split("*")[2]
            if i["title"] == "轴距(mm)":
                item["wheelbase"] = i["value"]

        item["geartype"] = None
        item["seats"] = None
        item["gearnumber"] = None
        item["weight"] = None
        item["generation"] = None
        item["fuelnumber"] = None
        item["lwv"] = None
        item["lwvnumber"] = None
        item["maxnm"] = None
        item["maxpower"] = None
        item["maxps"] = None
        item["frontgauge"] = None
        item["compress"] = None
        item["registerdate"] = response.meta["registerdate"]
        item["years"] = None
        item["paytype"] = None
        item["price1"] = response.meta["price"]
        item["pricetag"] = None
        item["mileage"] = response.meta["mileage"]
        item["city"] = response.meta["city"]
        item["prov"] = None
        item["guarantee"] = None
        item["totalcheck_desc"] = None

        item["totalgrade"] = None

        item["contact_type"] = None
        item["contact_name"] = None
        item["contact_phone"] = None
        item["contact_address"] = None
        item["contact_company"] = None
        item["contact_url"] = None
        item["change_date"] = None
        item["change_times"] = None
        item["insurance1_date"] = None
        item["insurance2_date"] = None
        item["hascheck"] = None
        item["repairinfo"] = None
        item["yearchecktime"] = None
        item["carokcf"] = None
        item["carcard"] = None
        item["carinvoice"] = None
        item["accident_desc"] = None
        item["accident_score"] = None
        item["outer_desc"] = None
        item["outer_score"] = None
        item["inner_desc"] = None
        item["inner_score"] = None
        item["safe_desc"] = None
        item["safe_score"] = None
        item["road_desc"] = None
        item["road_score"] = None
        item["lastposttime"] = None
        item["newcartitle"] = None
        item["newcarurl"] = None
        item["img_url"] = car_dict["modelImgInfos"][0]["url"]
        item["first_owner"] = None
        item["carno"] = None
        item["carnotype"] = None
        item["carddate"] = None
        item["changecolor"] = None
        item["outcolor"] = None
        item["innercolor"] = None
        item["desc"] = None
        item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + str(5)

        returndf = self.bf.isContains(item["statusplus"])
        # 1数据存在，0数据不存在
        if returndf == 1:
            ishave = True
        else:
            ishave = False
        logging.log(msg='数据是否已经存在： %s' % ishave, level=logging.INFO)
        yield item
        # print(item)