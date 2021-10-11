# brand: 奥驰汽车
# model: 载货车
# series: 奥驰A系
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
from ..items import car45

website = 'car45'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://buy.cars45.com/cars?limit=100&page={}"
    headers = {'Referer': 'https://buy.cars45.com/cars',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(GuazicarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MYSQLDB_DB', "koubei", priority='cmdline')
        self.sign = True

    def start_requests(self):
        for i in range(1000):
            url = self.start_urls.format(i + 1)
            if self.sign == False:
                return
            else:
                yield scrapy.Request(url=url, headers=self.headers)

    def parse(self, response):
        car_list = response.xpath("//div[contains(@class,'col-12 col-lg-4 col-md-6')]")
        if car_list == []:
            self.sign = False
        for car in car_list:
            car_dict = {}
            car_dict['price'] = car.xpath(".//h5[@class='price']/text()").extract_first().replace("\r\n", '').replace(
                "\n", '').replace("\r", '').replace("\t", '').strip(" ")
            car_dict["shortdesc"] = car.xpath(".//h4/text()").extract_first().replace("\r\n", '').replace(
                "\n", '').replace("\r", '').replace("\t", '').strip(" ")
            car_dict["mileage"] = car.xpath(".//p[1]//span[@class='intersemibold']/text()").extract_first()
            car_dict["year"] = car.xpath(".//p[2]//span[@class='intersemibold']/text()").extract_first()
            car_dict["rank"] = car.xpath(".//div[@data-toggle='tooltip']/text()").extract_first()
            car_dict["carid"] = car.xpath(".//p[3]//span[@class='intersemibold']/text()").extract_first()
            car_dict["used"] = car.xpath(".//p[@class='text-small car-origion']/text()").extract_first()
            car_dict["url"] = car.xpath(".//a[@tabindex='0']/@href").extract_first()
            yield scrapy.Request(url=car_dict['url'], headers=self.headers, callback=self.parse_series, meta=car_dict)

    def parse_series(self, response):
        item = car45()
        car_dict = response.meta
        item["grabtime"] = time.strftime('%Y-%m-%d %X', time.localtime())
        item["url"] = car_dict["url"]
        item["price"] = car_dict["price"]
        item["shortdesc"] = car_dict["shortdesc"]
        item["mileage"] = car_dict["mileage"]
        item["year"] = car_dict["year"]
        item["rank"] = car_dict["rank"]
        item["carid"] = car_dict["carid"]
        item["used"] = car_dict["used"]
        item["Make"] = response.xpath("//label[contains(text(),'Make')]/../span/text()").extract_first().replace("\r\n",
                                                                                                                 '').replace(
            "\n", '').replace("\r", '').replace("\t", '').strip(" ")
        item["Model"] = response.xpath("//label[contains(text(),'Model')]/../span/text()").extract_first().replace(
            "\r\n", '').replace(
            "\n", '').replace("\r", '').replace("\t", '').strip(" ")
        item["Location"] = response.xpath(
            "//label[contains(text(),'Location')]/../span/text()").extract_first().replace("\r\n", '').replace(
            "\n", '').replace("\r", '').replace("\t", '').strip(" ")
        item["Transmission"] = response.xpath(
            "//label[contains(text(),'Transmission')]/../span/text()").extract_first().replace("\r\n", '').replace(
            "\n", '').replace("\r", '').replace("\t", '').strip(" ")
        try:
            item["SellingCondition"] = response.xpath(
                "//label[contains(text(),'Condition')]/../span/text()").extract_first().replace("\r\n", '').replace(
                "\n", '').replace("\r", '').replace("\t", '').strip(" ")
        except:
            item["SellingCondition"] = None
        try:
            item["Colour"] = response.xpath(
                "//label[contains(text(),'Colour')]/../span/text()").extract_first().replace("\r\n", '').replace(
                "\n", '').replace("\r", '').replace("\t", '').strip(" ")
        except:
            item["Colour"] = None
        item["statusplus"] = item["url"] + item["price"]
        yield item
