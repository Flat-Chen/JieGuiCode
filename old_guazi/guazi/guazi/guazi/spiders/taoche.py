# -*- coding: UTF-8 -*-
import json
import re
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
from ..items import GuaziItem

website = 'taoche'
from ..redis_bloom import BloomFilter

# main
class CarSpider(scrapy.Spider):
    # basesetting
    name = website
    allowed_domains = ["taoche.com"]
    start_urls = [
        # "http://quanguo.taoche.com/robots/?page=1&orderid=5&direction=2#pagetag"
        "https://shanghai.taoche.com/all/"
    ]
    custom_settings = {

    }

    def __init__(self, **kwargs):
        self.headers = {'Referer': 'https://shanghai.taoche.com/all/',
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

        settings.set("WEBSITE", website)
        self.bf = BloomFilter(key='b1f_' + website)
        super(CarSpider, self).__init__(**kwargs)

    def parse(self, response):
        city_list = response.xpath("//div[@class='header-city-province-mian']//li/div/a/@href").extract()
        for city in city_list:
            yield response.follow(url=city, headers=self.headers, callback=self.city_parse)

    def city_parse(self, response):
        if response.css('div.car_list div#container_base'):
            for detail_url in response.css('div.car_list div#container_base li a.title::attr(href)').getall():
                yield scrapy.Request(url=detail_url, callback=self.parse_car)

        next_page = response.xpath('//a[@class="pages-next"]/@href')
        if next_page:
            yield scrapy.Request(url=next_page.get(), callback=self.city_parse, dont_filter=True)


    def parse_car(self, response):
        print(response.css('title::text').get())
        grap_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
            item = GuaziItem()
            item["carid"] = re.findall(r'(\d*)\D*.html', response.url)[0]
            item["car_source"] = "taoche"
            item["usage"] = None
            item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["update_time"] = None

            try:
                item["post_time"] = response.css('input#hidCarPublishTime::attr(value)').get()
            except:
                item['post_time'] = None
            item["sold_date"] = None
            item["pagetime"] = 'zero'
            item["parsetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["shortdesc"] = response.xpath('//div[@class="summary-title"]/h1/span/text()').extract_first()
            item["pagetitle"] = response.xpath("//head/title/text()").extract_first().strip()
            item["url"] = response.url
            item["newcarid"] = response.xpath('//input[@id="hidCarId"]/@value').extract_first()
            item["status"] = "sale"
            item["brand"] = response.xpath(
                '//div[@class="hide-box"]/div[2]/div[1]/ul/li[1]/span/a[1]/text()').extract_first()
            try:
                item["series"] = response.xpath('//li[contains(., "品牌型号")]/span/a/text()').get()
            except:
                item['series'] = None
            item["factoryname"] = None
            item["modelname"] = None
            item["brandid"] = response.xpath('//input[@id="hidBrandId"]/@value').extract_first()
            item["familyid"] = response.xpath('//input[@id="hidSerialId"]/@value').extract_first()
            item["seriesid"] = response.xpath('//input[@id="hidSerialId"]/@value').extract_first()
            try:
                item['makeyear'] = \
                    re.findall(r"(\d+)款", response.xpath('//meta[@name="keywords"]/@content').extract_first())[0]
            except:
                item['makeyear'] = None
            item["registeryear"] = \
                response.xpath(
                    '//div[@class="summary-attrs"]//dt[contains(text(),"上牌时间")]/../dd/text()').extract_first().split(
                    "年")[0]
            item["produceyear"] = None
            item["body"] = response.xpath('//div[@class="hide-box"]/div[2]/div[2]/ul/li[4]/span/text()').extract_first()
            item["bodystyle"] = response.xpath(
                '//div[@class="hide-box"]/div[2]/div[2]/ul/li[4]/span/text()').extract_first()

            item["level"] = response.xpath(
                '//div[@class="hide-box"]/div[2]/div[1]/ul/li[5]/span/a/text()').extract_first().strip("")
            item["fueltype"] = None
            item["driverway"] = response.xpath('//li[contains(.,"驱动方式")]/span/text()').extract_first()
            item["output"] = response.xpath(
                '//div[@class="summary-attrs"]//dt[contains(.,"排量／变速箱")]/../dd/text()').extract_first()
            item["guideprice"] = response.xpath(
                '//div[@class="summary-price-wrap"]/strong[@class="price-this"]/text()').extract_first()
            # 新车指导价46.30万(含税)
            try:
                item["guidepricetax"] = response.xpath("//span[@class='quankuan']/text()").extract_first().split("价")[1]
            except:
                item["guidepricetax"] = None
            try:
                item["doors"] = response.xpath(
                    '//div[@class="hide-box"]/div[2]/div[2]/ul/li[4]/span/text()').extract_first().split("门")[0]
            except:
                item["doors"] = None
            item["emission"] = response.xpath('//li[contains(.,"排量")]/span/a/text()').extract_first()
            item["gear"] = None
            try:
                item["geartype"] = \
                    response.xpath('//dt[contains(text(),"变速箱")]/following-sibling::dd/text()').extract_first().split("/")[1]
            except:
                item["geartype"] = None
            try:
                item["seats"] = \
                    re.findall(r"门(\d*)座", response.xpath('//div[@class="hide-box"]/div[2]/div[2]/ul/li[4]/span/text()'
                                                          ).extract_first())[0]
            except:
                item["seats"] = None
            try:
                item["length"] = response.xpath(
                    '//div[@class="hide-box"]/div[2]/div[2]/ul/li[3]/span/text()').extract_first().split("mm*")[0]
            except:
                item["length"] = None
            try:
                item["width"] = response.xpath(
                    '//div[@class="hide-box"]/div[2]/div[2]/ul/li[3]/span/text()').extract_first().split("mm*")[1]
            except:
                item["width"] = None
            try:
                item["height"] = response.xpath(
                    '//div[@class="hide-box"]/div[2]/div[2]/ul/li[3]/span/text()').extract_first().split("mm*")[2]
            except:
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
            item["registerdate"] = response.xpath(
                '//div[@class="summary-attrs"]//dt[contains(text(),"上牌时间")]/../dd/text()').extract_first()
            item["years"] = None
            item["paytype"] = None
            item["price1"] = response.xpath(
                '//div[@class="summary-price-wrap"]/strong[@class="price-this"]/text()').extract_first().strip("万")
            item["pricetag"] = None
            item["mileage"] = response.xpath(
                '//div[@class="summary-attrs"]//dt[contains(text(),"表显里程")]/../dd/text()').extract_first()
            try:
                item["color"] = re.findall(r"([\u4e00-\u9fa5])色", response.xpath(
                    '//meta[@name="keywords"]/@content').extract_first())[0] + "色"
            except:
                item["color"] = None
            item["prov"] = None
            item["city"] = response.xpath("//div[@class='crumbs-c']/a[2]/text()").extract_first()
            item["guarantee"] = None
            item["totalcheck_desc"] = None
            item["totalgrade"] = None
            item["contact_type"] = response.xpath('//div[@class="hide-box"]/div[2]/div[1]/ul/li[2]/span/text()').extract_first()
            try:
                item["contact_name"] = response.xpath('//input[@id="hidLinkMan"]/@value').extract_first()
            except:
                item["contact_name"] = None
            item["contact_phone"] = None
            item["contact_address"] = None
            item["contact_company"] = None
            item["contact_url"] = None
            item["change_date"] = None
            item["change_times"] = None
            item["insurance1_date"] = response.xpath(
                '//div[@class="col-xs-3 details-information-main"][4]/div/div[2]/div[2]/text()[2]').extract_first()
            item["insurance2_date"] = None
            item["hascheck"] = None
            item["repairinfo"] = response.xpath(
                '//div[@class="col-xs-3 details-information-main"][2]/div/div[2]/div[1]/text()[2]').extract_first()
            item["yearchecktime"] = response.xpath(
                '//div[@class="col-xs-3 details-information-main"][4]/div/div[2]/div[1]/text()[2]').extract_first()
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
            item["img_url"] = None
            item["first_owner"] = None
            item["carno"] = None
            item["carnotype"] = None
            item["carddate"] = None
            item["changecolor"] = None
            item["outcolor"] = None
            item["innercolor"] = None
            item["desc"] = None
            item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + str(item["post_time"])
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
            logging.log(msg=json.dumps(log_dict,ensure_ascii=False), level=logging.INFO)

        yield item
        # print(item)
