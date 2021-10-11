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
from ..items import carcheki

website = 'car_cheki'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://www.cheki.com.ng/cars/toyota/4-runner?page={}"
    headers = {'Referer': 'https://www.cheki.com.ng/cars/toyota/4-runner',
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
                yield scrapy.Request(url=url, headers=self.headers,dont_filter=True)

    def parse(self, response):
        car_list = response.xpath("//ul[@class='listing-unit__container']/li")
        if car_list == []:
            self.sign = False
        for car in car_list:
            car_dict = {}
            try:
                car_dict['price'] = car.xpath(".//h2[@class='listing-price']/text()").extract_first()
                car_dict["shortdesc"] = car.xpath(".//span[@class='ellipses']/text()").extract_first()
                car_dict["mileage"] = car.xpath(".//span[contains(text(),'km')]/text()").extract_first()
                car_dict["carid"] = car.xpath("@data-listing-id").extract_first()
                car_dict["url"] = 'https://www.cheki.com.ng'+car.xpath(".//div[@class='card-main']/a[1]/@href").extract_first()
                yield scrapy.Request(url=car_dict['url'], headers=self.headers, callback=self.parse_series, meta=car_dict)
            except:
                pass

    def parse_series(self, response):
        item = carcheki()
        car_dict = response.meta
        item["grabtime"] = time.strftime('%Y-%m-%d %X', time.localtime())
        item["url"] = car_dict["url"]
        item["price"] = car_dict["price"]
        item["shortdesc"] = car_dict["shortdesc"]
        item["mileage"] = car_dict["mileage"]
        item["year"] = response.xpath("//dt[contains(text(),'Year')]/../dd/text()").extract_first()
        item["rank"] = response.xpath("//p[@class='starability-result']/@data-rating").extract_first()
        item["carid"] = car_dict["carid"]
        item["Make"] = response.xpath("//div[@class='bread-crumbs']//section/ul/li[3]/a/text()").extract_first()
        item["Model"] = response.xpath("//div[@class='bread-crumbs']//section/ul/li[4]/a/text()").extract_first()
        desc =response.xpath("//dl[@class='listing-detail__attributes__description smart']//dd")
        item['desc'] =desc.xpath('string(.)').extract_first()
        item["post_time"] =response.xpath("//div[@class='listing-detail__main-heading__posted']/text()").extract_first().strip("-").strip('\n')
        item["REF_ID"] =response.xpath("//div[@class='listing-detail__ref-id']/text()").extract_first().split(':')[1]
        item["Condition"] =response.xpath("//dt[contains(text(),'Condition')]/../dd/text()").extract_first()
        item["BodyType"] =response.xpath("//dt[contains(text(),'Body Type')]/../dd/text()").extract_first()
        item["Colour"] =response.xpath("//dt[contains(text(),'Colour')]/../dd/text()").extract_first()
        item["DriveType"] =response.xpath("//dt[contains(text(),'Drive Type')]/../dd/text()").extract_first()
        item["Transmission"] =response.xpath("//dt[contains(text(),'Transmission')]/../dd/text()").extract_first()
        item["DoorCount"] =response.xpath("//dt[contains(text(),'Door Count')]/../dd/text()").extract_first()
        item["DriveSetup"] =response.xpath("//dt[contains(text(),'Drive Setup')]/../dd/text()").extract_first()
        item["Fuel"] =response.xpath("//dt[contains(text(),'Fuel')]/../dd/text()").extract_first()
        item["statusplus"] = item["url"] + item["price"]
        yield item
        # print(item)