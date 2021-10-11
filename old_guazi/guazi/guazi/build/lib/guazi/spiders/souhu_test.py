# -*- coding: UTF-8 -*-
import json
import re
import time
import redis
import scrapy
import logging

from lxml import etree
from scrapy.conf import settings
from selenium import webdriver

from ..items import GuaziItem
from ..redis_bloom import BloomFilter




website = 'souhu_test'


class CarSpider(scrapy.Spider):
    name = website
    allowed_domains = ["sohu.com"]
    start_urls = ['http://2sc.sohu.com/ah/buycar/', 'http://2sc.sohu.com/bj/buycar/', 'http://2sc.sohu.com/cq/buycar/',
                  'http://2sc.sohu.com/fj/buycar/', 'http://2sc.sohu.com/gd/buycar/', 'http://2sc.sohu.com/gx/buycar/',
                  'http://2sc.sohu.com/guizhou/buycar/', 'http://2sc.sohu.com/gs/buycar/',
                  'http://2sc.sohu.com/hb/buycar/', 'http://2sc.sohu.com/hlj/buycar/', 'http://2sc.sohu.com/hn/buycar/',
                  'http://2sc.sohu.com/hubei/buycar/', 'http://2sc.sohu.com/hunan/buycar/',
                  'http://2sc.sohu.com/hainan/buycar/', 'http://2sc.sohu.com/jl/buycar/',
                  'http://2sc.sohu.com/js/buycar/', 'http://2sc.sohu.com/jx/buycar/', 'http://2sc.sohu.com/ln/buycar/',
                  'http://2sc.sohu.com/nmg/buycar/', 'http://2sc.sohu.com/nx/buycar/', 'http://2sc.sohu.com/qh/buycar/',
                  'http://2sc.sohu.com/shanxi/buycar/', 'http://2sc.sohu.com/sh/buycar/',
                  'http://2sc.sohu.com/sd/buycar/', 'http://2sc.sohu.com/sc/buycar/', 'http://2sc.sohu.com/sx/buycar/',
                  'http://2sc.sohu.com/tj/buycar/', 'http://2sc.sohu.com/xz/buycar/', 'http://2sc.sohu.com/xj/buycar/',
                  'http://2sc.sohu.com/yn/buycar/', 'http://2sc.sohu.com/zj/buycar/']

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0

    def parse(self, response):
        node_list = response.xpath('//div[@class="carShow"]/div')
        for node in node_list:
            urlbase = node.xpath('a[@class="car-link"]/@href').extract_first()
            url = response.urljoin(urlbase)
            yield scrapy.Request(url, callback=self.parse_car)

        next_page = response.xpath('//span[contains(text(),">")]/../@href').extract_first()
        if next_page:
            url = response.urljoin(next_page)
            yield scrapy.Request(url, self.parse)

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
        self.counts += 1
        logging.log(msg="download  " + str(self.counts) + "  items", level=logging.INFO)

        # key and status (sold or sale, price,time)
        status = response.xpath('//div[@class="ask-box"]/a')
        status = "sale" if status else "sold"

        price = response.xpath('//span[@class="car-price"]/text()')
        price = ".".join(price.re('\d+')) if price else "zero"

        datetime = response.xpath('//label[@class="message"]/text()')
        datetime = "-".join(datetime.re('\d+')) if datetime else "zero"

        # extra
        gap = response.xpath('//span[@class="car-price-new"]/text()')
        gap = ".".join(gap.re('\d+')) if price else "zero"
        guideprice = float(price) + float(gap)
        # item loader
        try:
            item = GuaziItem()
            item["carid"] = re.findall(r'carid.*\'(\d+)',
                                       response.xpath('//script[contains(text(),"modelid")]/text()').extract_first())[0]
            item["car_source"] = "souhu"
            item["usage"] = response.xpath('//div[@class="tag_item tag_blue"]/span/text()').extract_first()
            item["grab_time"] = grap_time
            item["update_time"] = None
            item["post_time"] = response.xpath(
                '//ul[@class="info_txt"]/li[contains(text(),"\u53d1\u5e03\u65f6\u95f4")]/strong/text()').extract_first()
            item["sold_date"] = None
            item["pagetime"] = None
            item["parsetime"] = grap_time
            item["shortdesc"] = response.xpath('//div[contains(@class,"car-detail")]/h3/text()').extract_first()
            item["pagetitle"] = response.xpath("//head/title/text()").extract_first().strip("")
            item["url"] = response.url
            item["newcarid"] = re.findall(r'trimmid =(\d*);', response.xpath(
                '//script[contains(text(),"modelid")]/text()').extract_first())[0]

            item["status"] = status
            item["brand"] = \
            re.findall(r'二手\s(.*)，二手', response.xpath('//head/meta[@name="keywords"]/@content').extract_first())[0]

            item["series"] = \
            re.findall(r'二手\s.*，二手\s(.*?)，', response.xpath('//head/meta[@name="keywords"]/@content').extract_first())[
                0]

            item["factoryname"] = None
            item["modelname"] = re.findall(r'entertrimmname.*\'(.*)\'', response.xpath(
                '//script[contains(text(),"modelid")]/text()').extract_first())[0]

            item["brandid"] = re.findall(r'brandid = \'(.*)\'',
                                         response.xpath('//script[contains(text(),"modelid")]/text()').extract_first())[
                0]

            item["familyid"] = re.findall(r'modelid =(\d+);', response.xpath(
                '//script[contains(text(),"modelid")]/text()').extract_first())[0]

            item["seriesid"] = re.findall(r'modelid =(\d+)', response.xpath(
                '//script[contains(text(),"modelid")]/text()').extract_first())[0]

            item['makeyear'] = re.findall(r'modelYear = \'(\d+)\';', response.xpath(
                '//script[contains(text(),"modelid")]/text()').extract_first())[0]

            item["registeryear"] = re.findall(r'firstLicenseDate = \'(.*)\';', response.xpath(
                '//script[contains(text(),"modelid")]/text()').extract_first())[0]

            item["produceyear"] = None
            item["body"] = None
            item["bodystyle"] = None

            item["level"] = None
            item["fueltype"] = None
            item["driverway"] = response.xpath(
                '//tr/td[contains(text(),"\u9a71\u52a8\u65b9\u5f0f")]/../td[2]/text()').extract_first()
            item["output"] = response.xpath('//tr/td[contains(text(),"\u6392\u91cf")]/../td[2]/text()').extract_first()
            item["guideprice"] = str(guideprice)
            # 新车指导价46.30万(含税)
            item["guidepricetax"] = None
            item["doors"] = None
            item["emission"] = response.xpath('//ul[@class="info_txt"]/li[3]/strong/span/text()').extract_first()
            item["gear"] = response.xpath(
                '//tr/td[contains(text(),"\u53d8\u901f\u7bb1\u6863\u4f4d")]/../td[@class="attr-v"]/text()').extract_first()
            item["geartype"] = response.xpath(
                '//tr/td[contains(text(),"\u53d8\u901f\u7bb1")]/../td[@class="attr-v"]/text()').extract_first()
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
            item["maxpower"] = None
            item["maxps"] = None
            item["frontgauge"] = None
            item["compress"] = None
            item["registerdate"] = re.findall(r'firstLicenseDate.*\'(.*)\'', response.xpath(
                '//script[contains(text(),"modelid")]/text()').extract_first())[0]
            item["years"] = None
            item["paytype"] = None
            item["price1"] = \
            re.findall(r'\uffe5.*\u4e07', response.xpath('//span[@class="car-price"]/text()').extract_first())[0]

            item["pricetag"] = None
            item["mileage"] = re.findall(r'mileageStr.*\'(.*)\'',
                                         response.xpath('//script[contains(text(),"modelid")]/text()').extract_first())[
                0]

            item["color"] = response.xpath(
                '//div[@class="col-md-5"]/table[@class="table table-bordered"]//tr[6]/td[2]/text()').extract_first()
            item["city"] = re.findall(r'cityname.*\'(.*)\'',
                                      response.xpath('//script[contains(text(),"modelid")]/text()').extract_first())[0]
            item["prov"] = response.xpath(
                '//div[@class="tag_mian"]/div[2]/table/tbody/tr[1]/td[2]/span/text()').extract_first()
            item["guarantee"] = None
            try:
                totalcheck_desc = response.xpath(
                    '//div[@class="tip-message"]/@title').extract_first()
            except Exception as  e:
                item["totalcheck_desc"] = None
            else:
                item["totalcheck_desc"] = totalcheck_desc
            try:
                totalgrade = response.xpath('//div[@class="WoM_left"]/p/b/text()').extract_first()
            except:

                item["totalgrade"] = None
            else:
                item["totalgrade"] = totalgrade
            item["contact_type"] = None
            item["contact_name"] = response.xpath(
                '//div[@class="col-md-offset-13 col-md-10"]/table/tbody/tr[1]/td[1]/text()').extract_first()
            item["contact_phone"] = response.xpath(
                '//div[@class="col-md-offset-13 col-md-10"]/table/tbody/tr[1]/td[2]/text()').extract_first()
            item["contact_address"] = response.xpath(
                '//div[@class="col-md-offset-13 col-md-10"]/table/tbody/tr[2]/td[1]/text()[2]').extract_first()
            item["contact_company"] = response.xpath(
                '//div[@class="col-md-offset-13 col-md-10"]/table/tbody/tr[1]/td[1]/text()').extract_first()
            item["contact_url"] = re.findall(r'dealerId.*\'(.*)\'', response.xpath(
                '//script[contains(text(),"modelid")]/text()').extract_first())[0]

            item["change_date"] = None
            item["change_times"] = None
            item["insurance1_date"] = response.xpath(
                '//tr/td[contains(text(),"\u4fdd\u9669\u622a\u6b62\u65e5\u671f")]/../td[@class="attr-v"]/text()').extract_first()
            item["insurance2_date"] = response.xpath(
                '//tr/td[contains(text(),"\u5546\u4e1a\u4fdd\u9669\u622a\u6b62\u65e5\u671f")]/../td[@class="attr-v"]/text()').extract_first()
            item["hascheck"] = None
            item["repairinfo"] = None
            item["yearchecktime"] = response.xpath(
                '//tr/td[contains(text(),"\u5e74\u68c0\u622a\u6b62\u65e5\u671f")]/../td[@class="attr-v"]/text()').extract_first()
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
            item["img_url"] = re.findall(r'picUrl.*\'(.*)\'',
                                         response.xpath('//script[contains(text(),"modelid")]/text()').extract_first())[
                0]

            item["first_owner"] = re.findall(r'[LT]', response.xpath(
                '//tr/td[contains(text(),"\u6392\u91cf")]/../td[2]/text()').extract_first())[0]

            item["carno"] = None
            item["carnotype"] = None
            item["carddate"] = None
            item["changecolor"] = None
            item["outcolor"] = None
            item["innercolor"] = None
            item["desc"] = None
            item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + str(11)
            # extract
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
            yield item
