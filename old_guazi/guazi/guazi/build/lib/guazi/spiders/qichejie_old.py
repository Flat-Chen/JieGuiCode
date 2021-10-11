# -*- coding: UTF-8 -*-
import json
import re
import time

import pandas as pd
import redis
import scrapy
import logging
from scrapy.conf import settings
from sqlalchemy import create_engine

from ..items import GuaziItem
import time
from hashlib import md5

import requests
from ..redis_bloom import BloomFilter

website = 'qichejie_old'


class CarSpider(scrapy.Spider):
    name = website
    # start_urls = get_url()
    start_urls = 'http://auction.autostreets.com/onlineauction/{}'
    next_url = "http://auction.autostreets.com/onlineauction/index?pageNumber={}"
    headers = {'Referer': 'http://auction.autostreets.com/',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        "DOWNLOADER_MIDDLEWARES": {
            "guazi.proxy.ProxyMiddleware": 530
        }

    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', 'qichejie', priority='cmdline')
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('MYSQLDB_DB', 'usedcar_update', priority='cmdline')
        self.counts = 0
        self.page = 1

    def get_city_prive(self):
        engine_1 = create_engine('mysql+pymysql://dataUser94:94dataUser@2020@192.168.1.94:3306/usedcar_update?charset=utf8')
        city = pd.read_sql("select	carid from  qichejie_online where outer_score is NULL",
                           con=engine_1)
        return city.values.tolist()

    def start_requests(self):
        car_list = self.get_city_prive()
        for i in car_list:
            url = self.start_urls.format(i[0] )
            yield scrapy.Request(url=url, dont_filter=True, headers=self.headers)

    def deal_time(self, sold_time):
        timeStamp = sold_time / 1000
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
        return otherStyleTime

    def deal_price(self, id):
        headers = {
            "terminal-type": "mobile",
            "os-name": "android",
            "app-name": "autostreets",
        }
        avSid = id
        time.sleep(3)
        a = int(time.time() * 1000)
        sign = "apiKey=865e437f-c1eb-4a84-a9bb-26b134a1fcd0,avSid={},t={}".format(avSid, a)
        redis_md5 = md5(sign.encode("utf-8")).hexdigest()
        url = "https://app.autostreets.com/online/loadCurrentPrice?apiSign={}&t={}&avSid={}".format(redis_md5, a, avSid)
        text = requests.get(url=url, headers=headers, )
        price = text.json()["extras"]["totalPrice"]
        sold_time = self.deal_time(int(text.json()["extras"]["endTime"]))
        return sold_time, price

    def parse(self, response):
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
            if '评星说明' in response.text:
                # new
                item = GuaziItem()

                item["carid"] = re.findall(r"onlineauction/(\d+)", response.url)[0]
                item["car_source"] = "qichejie"
                item["usage"] = response.xpath(
                    "//span[contains(text(),'使用性质')]/../span[2]/text()").extract_first().strip(
                    "\r\n\t\t\t\t\t\t\t\t")
                item["grab_time"] = grap_time
                item["update_time"] = None
                item["post_time"] = None
                item["pagetime"] = None
                item["parsetime"] = grap_time
                item["shortdesc"] = response.xpath(
                    "//div[@class='detailbox-r']//h2[@class='detail-title']/text()").extract_first().replace("\r",
                                                                                                             "").replace(
                    "\n", "").replace("\t", "").strip()
                item["pagetitle"] = response.xpath("//head/title/text()").extract_first().strip("")
                item["url"] = response.url
                item["newcarid"] = None
                item["status"] = 'sold'
                item["brand"] = item["shortdesc"].split(
                    " ")[
                    0]
                print(item['brand'], '*' * 50)
                item["series"] = \
                    item["shortdesc"].split(
                        " ")[
                        1]
                item["factoryname"] = None
                item["modelname"] = None
                item["brandid"] = None
                item["familyid"] = None
                item["seriesid"] = None
                try:

                    item['makeyear'] = re.findall(r"(\d+)款", item["shortdesc"])[0]
                except:
                    item['makeyear'] = None
                item["registeryear"] = response.xpath(
                    "//span[contains(text(),'首次上牌日期')]/../span[2]/text()").extract_first().strip("")
                item["produceyear"] = response.xpath(
                    "//span[contains(text(),'出厂日期')]/../span[2]/text()").extract_first().strip("\r\n\t\t\t\t\t\t\t\t")
                item["body"] = None
                item["bodystyle"] = None

                item["level"] = None
                item["fueltype"] = response.xpath(
                    "//span[contains(text(),'燃料类型')]/../span[2]/text()").extract_first().strip("")
                item["driverway"] = None
                item["output"] = response.xpath(
                    "//span[contains(text(),'排气量')]/../span[2]/text()").extract_first().strip(
                    "\r\n\t\t\t\t\t\t\t\t")
                item["guideprice"] = None
                # 新车指导价46.30万(含税)
                item["guidepricetax"] = None
                item["doors"] = None
                item["emission"] = None
                item["gear"] = None
                item["geartype"] = response.xpath(
                    "//span[contains(text(),'变速箱类型')]/../span[2]/text()").extract_first().strip("")
                item["seats"] = response.xpath("//span[contains(text(),'座位数')]/../span[2]/text()"
                                               ).extract_first().strip("")
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
                item["maxpower"] = response.xpath(
                    "//span[contains(text(),'最大功率')]/../span[2]/text()").extract_first().strip("")
                item["maxps"] = None
                item["frontgauge"] = None
                item["compress"] = None
                item["registerdate"] = response.xpath(
                    "//span[contains(text(),'首次上牌日期')]/../span[2]/text()").extract_first().strip("")
                item["years"] = None
                item["paytype"] = None
                item["sold_date"], item["price1"] = self.deal_price(item["carid"])
                item["pricetag"] = None
                item["mileage"] = response.xpath(
                    "//span[contains(text(),'表显里程')]/../span[2]/text()").extract_first().strip(
                    "\r\n\t\t\t\t\t\t\t\t")
                item["color"] = response.xpath(
                    "//span[contains(text(),'车身颜色')]/../span[2]/text()").extract_first().strip("")
                item["city"] = response.xpath(
                    "//span[contains(text(),'车辆所在地')]/../span[2]/text()").extract_first().strip(
                    "")
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
                item["change_times"] = response.xpath(
                    "//span[contains(text(),'过户次数')]/../span[2]/text()").extract_first().strip().strip("")
                item["insurance1_date"] = response.xpath(
                    "//span[contains(text(),'交强险到期')]/../span[2]/text()").extract_first().strip("\r\n\t\t\t\t\t\t\t\t")
                item["insurance2_date"] = response.xpath(
                    "//span[contains(text(),'商业险到期')]/../span[2]/text()").extract_first().strip("\r\n\t\t\t\t\t\t\t\t")
                item["hascheck"] = None
                item["repairinfo"] = None
                item["yearchecktime"] = response.xpath(
                    "//span[contains(text(),'年检到期')]/../span[2]/text()").extract_first().strip("")
                item["carokcf"] = None
                item["carcard"] = None
                item["carinvoice"] = None
                item["accident_desc"] = None
                item["accident_score"] = None
                item["outer_desc"] = str(dict(
                    zip(response.xpath(
                        "//span[contains(text(),'外观检测')]/../div[@class='sketch-icon-box']//dt/text()").extract(),
                        response.xpath(
                            "//span[contains(text(),'外观检测')]/../div[@class='sketch-icon-box']//dd/text()").extract())))
                item["inner_desc"] = str(dict(
                    zip(response.xpath(
                        "//span[contains(text(),'内饰检测')]/../div[@class='sketch-icon-box']//dt/text()").extract(),
                        response.xpath(
                            "//span[contains(text(),'内饰检测')]/../div[@class='sketch-icon-box']//dd/text()").extract())))
                item["inner_score"] = response.xpath(
                    "//div[@class='dl-auto']//dt[contains(text(),'内饰')]/../dd/text()").extract_first()
                item["safe_desc"] = str(dict(
                    zip(response.xpath(
                        "//span[contains(text(),'骨架检测')]/../div[@class='sketch-icon-box']//dt/text()").extract(),
                        response.xpath(
                            "//span[contains(text(),'骨架检测')]/../div[@class='sketch-icon-box']//dd/text()").extract())))
                item["safe_score"] = response.xpath(
                    "//div[@class='dl-auto']//dt[contains(text(),'骨架')]/../dd/text()").extract_first()
                item["road_desc"] = str(dict(
                    zip(response.xpath(
                        "//span[contains(text(),'工况检测')]/../div[@class='sketch-icon-box']//dt/text()").extract(),
                        response.xpath(
                            "//span[contains(text(),'工况检测')]/../div[@class='sketch-icon-box']//dd/text()").extract())))
                item["road_score"] = response.xpath(
                    "//div[@class='dl-auto']//dt[contains(text(),'工况')]/../dd/text()").extract_first()
                item["lastposttime"] = None
                item["newcartitle"] = None
                item["newcarurl"] = None
                item["img_url"] = response.xpath("//div[@class='bigimgbox']/img/@src").extract_first().strip("")
                item["first_owner"] = None
                item["carno"] = response.xpath(
                    "//span[contains(text(),'车牌号')]/../span[2]/text()").extract_first().strip("\r\n\t\t\t\t\t")
                item["outer_score"] = response.xpath(
                    "//div[@class='dl-auto']//dt[contains(text(),'外观')]/../dd/text()").extract_first()
                item["carnotype"] = None
                item["carddate"] = None
                item["changecolor"] = None
                item["outcolor"] = None
                item["innercolor"] = response.xpath(
                    "//span[contains(text(),'内饰颜色')]/../span[2]/text()").extract_first().strip("")
                item["desc"] = response.xpath("//h2[contains(text(),'车辆简述')]/../p/text()").extract_first().strip("")
                item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + str(11411)
                print(item)
                # print(item)
            else:
                #  old
                item = GuaziItem()
                item["carid"] = re.findall(r"onlineauction/(\d+)", response.url)[0]
                item["car_source"] = "qichejie"
                item["usage"] = response.xpath(
                    "//th[contains(text(),'使用性质')]/../td/text()").extract_first().strip(
                    "")
                item["grab_time"] = grap_time
                item["update_time"] = None
                item["post_time"] = None
                item["pagetime"] = None
                item["parsetime"] = grap_time
                item["shortdesc"] = response.xpath(
                    "//div[@class='detailbox-r']//h2[@class='detail-title']/text()").extract_first().strip("\n").strip(
                    " ")
                item["pagetitle"] = response.xpath("//head/title/text()").extract_first().strip("\n").strip(" ")
                item["url"] = response.url
                item["newcarid"] = None
                item["status"] = 'sold'
                item["brand"] = item["shortdesc"].split(
                    " ")[
                    0]
                print(item['brand'], '*' * 50)
                item["series"] = \
                    item["shortdesc"].split(
                        " ")[
                        1]
                item["factoryname"] = None
                item["modelname"] = None
                item["brandid"] = None
                item["familyid"] = None
                item["seriesid"] = None
                try:

                    item['makeyear'] = re.findall(r"(\d+)款", item["shortdesc"])[0]
                except:
                    item['makeyear'] = None
                item["registeryear"] = response.xpath(
                    "//th[contains(text(),'上牌日期')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["produceyear"] = response.xpath(
                    "//th[contains(text(),'出厂日期')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["body"] = None
                item["bodystyle"] = None

                item["level"] = None
                item["fueltype"] = response.xpath(
                    "//th[contains(text(),'燃料类型')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["driverway"] = None
                item["output"] = response.xpath(
                    "//th[contains(text(),'排气量')]/../td/text()").extract_first().strip(
                    "")
                item["guideprice"] = None
                # 新车指导价46.30万(含税)
                item["guidepricetax"] = None
                item["doors"] = None
                item["emission"] = None
                item["gear"] = None
                item["geartype"] = response.xpath(
                    "//th[contains(text(),'变速箱类型')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["seats"] = None
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
                item["maxpower"] = response.xpath(
                    "//th[contains(text(),'最大功率')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["maxps"] = None
                item["frontgauge"] = None
                item["compress"] = None
                item["registerdate"] = response.xpath(
                    "//th[contains(text(),'上牌日期')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["years"] = None
                item["paytype"] = None
                item["sold_date"], item["price1"] = self.deal_price(item["carid"])
                item["pricetag"] = None
                item["mileage"] = response.xpath(
                    "//th[contains(text(),'表显里程')]/../td/text()").extract_first().replace("\r", "").replace("\n",
                                                                                                            "").replace(
                    "\t", "").strip()
                item["color"] = response.xpath(
                    "//th[contains(text(),'车辆颜色')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["city"] = response.xpath(
                    "//th[contains(text(),'车辆所在地')]/../td/text()").extract_first().strip(
                    "")
                item["prov"] = None
                item["guarantee"] = None
                item["totalcheck_desc"] = response.xpath("//td[@rowspan='6']/p/text()").extract_first().split("：")[1]
                item["totalgrade"] = None
                item["contact_type"] = None
                item["contact_name"] = None
                item["contact_phone"] = None
                item["contact_address"] = None
                item["contact_company"] = None
                item["contact_url"] = None
                item["change_date"] = None
                item["change_times"] = response.xpath(
                    "//th[contains(text(),'过户次数')]/../td/text()").extract_first().strip("\n").strip().strip(" ")
                item["insurance1_date"] = response.xpath(
                    "//th[contains(text(),'交强险有效期')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["insurance2_date"] = None
                item["hascheck"] = None
                item["repairinfo"] = None
                item["yearchecktime"] = response.xpath(
                    "//th[contains(text(),'年审有效期')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["carokcf"] = None
                item["carcard"] = None
                item["carinvoice"] = None
                item["accident_desc"] = None
                item["accident_score"] = None
                item["outer_desc"] = str(dict(
                    zip(response.xpath(
                        "//div[@id='a3']//ul[@class='listul']//del[@title!='']/../../strong/text()").extract(),
                        response.xpath(
                            "//div[@id='a3']//ul[@class='listul']//del[@title!='']/text()").extract())))
                item["inner_desc"] = str(dict(
                    zip(response.xpath(
                        "//div[@id='a4']//ul[@class='listul']//del[@title!='']/../../strong/text()").extract(),
                        response.xpath(
                            "//div[@id='a4']//ul[@class='listul']//del[@title!='']/../../strong/text()").extract())))
                item["inner_score"] = response.xpath("//td[contains(text(),'内饰')]/../td[last()]/text()").extract_first()
                item["safe_desc"] = str(dict(
                    zip(response.xpath(
                        "//div[@id='a2']//ul[@class='listul']//del[@title!='']/../../strong/text()").extract(),
                        response.xpath(
                            "//div[@id='a2']//ul[@class='listul']//del[@title!='']/../../strong/text()").extract())))
                item["safe_score"] = response.xpath(
                    "//td[contains(text(),'启动检查')]/../td[last()]/text()").extract_first()
                item["road_desc"] = str(dict(
                    zip(response.xpath(
                        "//div[@id='a5']//ul[@class='listul']//del[@title!='']/../../strong/text()").extract(),
                        response.xpath(
                            "//div[@id='a5']//ul[@class='listul']//del[@title!='']/../../strong/text()").extract())))
                item["road_score"] = response.xpath("//td[contains(text(),'路试')]/../td[last()]/text()").extract_first()
                item["lastposttime"] = None
                item["newcartitle"] = None
                item["newcarurl"] = None
                item["img_url"] = response.xpath("//div[@class='bigimgbox']/img/@src").extract_first().strip(
                    "\n").strip(" ")
                item["first_owner"] = None
                item["carno"] = response.xpath(
                    "//th[contains(text(),'车牌号')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["outer_score"] = response.xpath("//td[contains(text(),'外观')]/../td[last()]/text()").extract_first()
                item["carnotype"] = None
                item["carddate"] = None
                item["changecolor"] = None
                item["outcolor"] = None
                item["innercolor"] = response.xpath(
                    "//th[contains(text(),'内饰颜色')]/../td/text()").extract_first().strip("\n").strip(" ")
                item["desc"] = response.xpath("//dt[contains(text(),'车辆描述')]/../dd/text()").extract_first().strip(
                    "\n").strip(" ")
                item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + str(11411)
        except:
            log_dict["logType"] = 'ERROR'
            log_dict["logMessage"] = response.url
            logging.log(msg=json.dumps(log_dict, ensure_ascii=False), level=logging.INFO)
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
            logging.log(msg=json.dumps(log_dict, ensure_ascii=False), level=logging.INFO)
            # print(item)
            yield item
