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

website = 'yuantong2'


class CarSpider(scrapy.Spider):
    name = website
    # start_urls = get_url()
    start_urls = ['https://www.ytucar.net/json/car/buy.json?searchType=yishou&aggregateConsignmentFlag=true&index=1',
                  'https://www.ytucar.net/json/car/buy.json?searchType=zaishou&aggregateConsignmentFlag=true&index=1',
                  'https://www.ytucar.net/json/car/buy.json?searchType=yiyuding&aggregateConsignmentFlag=true&index=1']

    headers = {'Referer': 'https://www.ytucar.net/buy.htm',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    index = True
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 20,
        'RANDOMIZE_DOWNLOAD_DELAY': True,

    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', 'yuantong2', priority='cmdline')
        self.bf = BloomFilter(key='b1f_' + website)
        self.counts = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.headers, meta={"page": 1})

    def parse(self, response):
        car_data = json.loads(response.text)["items"]
        if car_data == []:
            return
        else:
            for car in car_data:
                item = {}
                item["brand"] = car["brandName"]
                item["series"] = car["seriesName"]
                item["post_time"] = car["upTime"]
                item["mileage"] = car["mileage"]
                item["modelname"] = car["modelName"]
                item["registerdate"] = car["year"]
                item["guideprice"] = car["newPriceWanStr"]
                item["price1"] = car["price"]
                item["img_url"] = car["bigImage"]
                item["carid"] = car["id"]
                item["city"] = car["cityName"]
                yield scrapy.Request(url="https://www.ytucar.net/car/" + item["carid"], meta={"item": item},
                                     callback=self.parse_car, headers=self.headers)
            response.meta["page"] = response.meta['page'] + 1
            url = response.url.split("index")[0] + "index={}".format(response.meta["page"])
            yield scrapy.Request(url=url, meta=response.meta, callback=self.parse, headers=self.headers)

    def parse_car(self, response):
        grap_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_dict = {
            "projectName": "used-car-scrapy",
            "logProgram": website,
            "logProgramPath": "/home/scrapyd/eggs/guazi",
            "logPath": "/home/scrapyd/logs/guazi/{}/".format(website),
            "logTime": grap_time,
            "logMessage": "",
            "logServer": "192.168.1.248",
            "logObjectType": "UsedCarPaChong",
        }
        try:
            self.counts += 1
            logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)
            item = GuaziItem()
            item["carid"] = response.meta["item"]["carid"]
            item["car_source"] = "yuantong2"
            item["usage"] = None
            item["grab_time"] = grap_time
            item["update_time"] = None
            item["post_time"] = response.meta["item"]["post_time"]
            item["sold_date"] = None
            item["pagetime"] = None
            item["parsetime"] = grap_time
            item["shortdesc"] = response.xpath("//h1//ins/text()").extract_first().strip()
            item["pagetitle"] = None
            item["url"] = response.url
            item["newcarid"] = None
            status = response.xpath("//ins[@class='detail-no']").extract_first()
            if status != '已售':
                status = '未售'
            item["status"] = status
            item["brand"] = response.meta["item"]["brand"]
            item["series"] = response.meta["item"]["series"]
            item["factoryname"] = None
            item["modelname"] = None
            item["brandid"] = None
            item["familyid"] = None
            item["seriesid"] = None
            try:
                item['makeyear'] = re.findall(r"(\d*)款", item["shortdesc"])[0]
            except:
                item['makeyear'] = None
            item["registeryear"] = None
            item["produceyear"] = None
            item["body"] = None
            item["bodystyle"] = response.xpath("//th[contains(text(),'车型')]/../td/text()").extract_first().strip()

            item["level"] = None
            item["fueltype"] = response.xpath("//th[contains(text(),'燃油')]/../td/text()").extract_first().strip()
            item["driverway"] = response.xpath("//th[contains(text(),'驱动方式')]/../td/text()").extract_first().strip()
            item["output"] = response.xpath("//th[contains(text(),'排量')]/../td/text()").extract_first().strip()
            item["guideprice"] = response.meta["item"]["guideprice"]
            # 新车指导价46.30万(含税)
            item["guidepricetax"] = None
            item["doors"] = response.xpath("//th[contains(text(),'车门数')]/../td/text()").extract_first().strip()
            item["emission"] = response.xpath("//th[contains(text(),'排放标准')]/../td/text()").extract_first().strip()
            item["gear"] = response.xpath("//th[contains(text(),'变速箱')]/../td/text()").extract_first().strip()
            item["geartype"] = None
            item["seats"] = response.xpath("//th[contains(text(),'座位数')]/../td/text()").extract_first().strip()
            item["length"] = None
            item["width"] = None
            item["height"] = None
            item["gearnumber"] = None
            item["weight"] = None
            item["wheelbase"] = None
            item["generation"] = None
            item["fuelnumber"] = None
            item["lwv"] = None
            item["lwvnumber"] = None
            item["maxnm"] = None
            item["maxpower"] = None
            item["maxps"] = None
            item["frontgauge"] = None
            item["compress"] = None
            item["registerdate"] = response.meta["item"]["registerdate"].strip('上牌')
            item["years"] = None
            item["paytype"] = None
            item["price1"] = response.meta["item"]["price1"]
            item["pricetag"] = None
            item["mileage"] = response.meta["item"]["mileage"]
            item["color"] = response.xpath("//th[contains(text(),'颜色')]/../td/text()").extract_first()
            item["city"] = response.meta["item"]["city"]
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
            item["insurance1_date"] = response.xpath("//th[contains(text(),'交强险到期')]/../td/text()").extract_first()
            item["insurance2_date"] = response.xpath("//th[contains(text(),'商业险到期')]/../td/text()").extract_first()
            item["hascheck"] = None
            item["repairinfo"] = None
            item["yearchecktime"] = response.xpath("//th[contains(text(),'年检')]/../td/text()").extract_first()
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
            item["img_url"] = response.meta["item"]["img_url"]
            item["first_owner"] = None
            item["carno"] = None
            item["carnotype"] = None
            item["carddate"] = None
            item["changecolor"] = None
            item["outcolor"] = None
            item["innercolor"] = None
            item["desc"] = None
            item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + str(7)

        except:
            log_dict["logType"] = 'ERROR'
            log_dict["logMessage"] = response.url
            logging.log(msg=json.dumps(log_dict, ensure_ascii =False), level=logging.INFO)
        else:
            log_dict["logType"] = 'INFO'
            log_dict["logMessage"] = "successful"
            log_dict["logObject"] = {
                "field": {
                    "carsource": website,
                    "grab_time": item["grab_time"],
                    "price1": item["price1"],
                    "mileage": item["mileage"],
                    "post_time": item["post_time"],
                    "sold_date": item["sold_date"],
                    "city": item["city"],
                    "registerdate": item["registerdate"]
                },
                "info": {
                    "dataBaseType": "mysql",
                    "dataBaseName": settings["MYSQLDB_DB"],
                    "tableName": website + '_online',
                    "saveStatus": ""
                }
            }
            returndf = self.bf.isContains(item["statusplus"])
            # 1数据存在，0数据不存在
            if returndf == 1:
                log_dict["logObject"]["info"]["saveStatus"] = "true"
            else:
                log_dict["logObject"]["info"]["saveStatus"] = "false"
            logging.log(msg=json.dumps(log_dict, ensure_ascii =False), level=logging.INFO)

            yield item
            # print(item)
