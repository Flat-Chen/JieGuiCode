import json
import time

from lxml import etree
import pandas as pd
import re

from redis import Redis
from scrapy import signals
from selenium import webdriver
# from scrapy.xlib.pydispatch import dispatcher
from ..items import autohome_img
import scrapy
import logging
from scrapy.conf import settings
from hashlib import md5

website = 'autohome_brand_image'


# redis_cli = Redis(host="192.168.1.249", port=6379, db=2)


# 先循环城市 然后在循环车
class CarSpider(scrapy.Spider):
    name = website
    # start_urls = get_url()
    start_urls = [
        "https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=1%20&brandId=0%20&fctId=0%20&seriesId=0"]
    headers = {'Referer': 'https://car.autohome.com.cn/',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}
    custom_settings = {
        'DOWNLOAD_DELAY': 1.5,
        'CONCURRENT_REQUESTS': 10,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        service_args = ['--load-images=no', '--disk-cache=yes', '--ignore-ssl-errors=true', ]
        self.driver = webdriver.PhantomJS(settings['PHANTOMJS_PATH'], service_args=service_args)
        self.driver.implicitly_wait(settings['PHANTOMJS_TIMEOUT'])
        self.driver.set_page_load_timeout(settings['PHANTOMJS_TIMEOUT'])
        self.driver.set_script_timeout(settings['PHANTOMJS_TIMEOUT'])
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        settings.set("MONGODB_DB", "newcar", priority="cmdline")
        self.counts = 0
        # dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self):
        self.driver.quit()
        print("***********************************************************************************")

    def parse(self, response):
        # print(response)

        url_list = response.xpath("//a/@href").extract()
        brand_name_list = response.xpath("//li//a/text()").extract()
        # print(brand_name_list)
        for index in range(len(url_list)):
            brand_id = re.findall(r"brand-(\d*).html", url_list[index])[0]
            brand_name = brand_name_list[index]
            yield response.follow(url=url_list[index], headers=self.headers, callback=self.stauts_parse,
                                  meta={"brand_id": brand_id, "brand_name": brand_name})

    def stauts_parse(self, response):
        status_list = response.xpath("//div[@class='tab-nav border-t-no']//ul[@data-trigger='click']/li")
        for status1 in status_list:
            status = status1.xpath(".//a/text()").extract_first()
            url = status1.xpath(".//a/@href").extract_first()
            if url == None:
                continue
            yield scrapy.Request(url="https://car.autohome.com.cn" + url, headers=self.headers,
                                 callback=self.car_parse,
                                 meta={"brand_id": response.meta["brand_id"], "status": status,
                                       "brand_name": response.meta["brand_name"]}, dont_filter=True)

    def car_parse(self, response):
        # 下一页
        # response, errors = tidy_document(response.text)

        next_page = response.xpath("//a[contains(text(),'下一页')]/@href").extract_first()
        # print(next_page, "*" * 50)
        if next_page not in ["javascript:void(0)", None]:
            # print(next_page)
            yield scrapy.Request(url="https://car.autohome.com.cn" + next_page, headers=self.headers,
                                 callback=self.car_parse,
                                 meta=response.meta, dont_filter=True)
        series_list = response.xpath("//div[@class='list-cont']")
        for series in series_list:
            item = autohome_img()
            item["brand_id"] = response.meta["brand_id"]
            item["brand_name"] = response.meta["brand_name"]
            item["img"] = series.xpath(".//img/@src").extract_first()
            item["series_id"] = series.xpath("./@data-value").extract_first()
            item["series_name"] = series.xpath(".//div[@class='list-cont-main']/div/a/text()").extract_first()
            item["url"] = response.url
            item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["statusplus"] = item["brand_id"] + item["brand_name"] + item["img"] + str(item["series_name"])
            yield item
            # print(item)