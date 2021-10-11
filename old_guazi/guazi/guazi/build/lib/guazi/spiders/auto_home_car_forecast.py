import json
import time

from lxml import etree
import pandas as pd
import re

from redis import Redis
from selenium import webdriver

from ..items import autohome
import scrapy
import logging
from scrapy.conf import settings
from hashlib import md5
# from scrapy.xlib.pydispatch import dispatcher
# from scrapy import signals

website = 'autohome_car_forecast'


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
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 3,
        "COOKIES_ENABLED": False,
        "RETRY_TIMES": 8,

    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        settings.set("MONGODB_DB", "newcar", priority="cmdline")
        self.counts = 0


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
        next_page = response.xpath("//a[contains(text(),'下一页')]/@href").extract_first()
        if next_page not in ["javascript:void(0)", None]:
            yield scrapy.Request(url="https://car.autohome.com.cn" + next_page, headers=self.headers,
                                 callback=self.car_parse,
                                 meta=response.meta, dont_filter=True)
        series_list = response.xpath("//div[@class='list-cont']")
        for series in series_list:
            series_id = series.xpath("./@data-value").extract_first()
            Official_guide_price = series.xpath(".//div[@class='main-lever-right']//span/span/text()").extract_first()
            series_name = series.xpath(".//div[@class='list-cont-main']/div/a/text()").extract_first()
            level = "|".join(series.xpath('.//li[contains(text(), "级")]/span/text()').extract())
            body_structure = "|".join(series.xpath(".//li[contains(text(), '车身结构：')]/a/text()").extract())
            engine = "|".join(series.xpath(".//li[3]//a/text()").extract())
            gearbox = "|".join(series.xpath(".//li[4]//a/text()").extract())
            model_list = response.xpath("//div[@id='divSpecList{}']//ul".format(series_id))
            endurance_mileage = "|".join(series.xpath(".//li[contains(text(), '续航里程：')]/span/text()").extract())
            electromotor = "|".join(series.xpath(".//li[contains(text(), '电 动 机')]/span/text()").extract())
            charging_time = "|".join(series.xpath(".//li[contains(text(), '充电时间：')]/span/text()").extract())
            print(series_name, "*" * 50)
            for model in model_list[0:len(model_list)]:
                li_list = model.xpath(".//li")
                for li in li_list:
                    item = autohome()
                    item["endurance_mileage"] = endurance_mileage
                    item["electromotor"] = electromotor
                    item["charging_time"] = charging_time
                    item["familyid"] = series_id
                    item["autohomeid"] = li.xpath("./@data-value").extract_first()
                    item["salesdesc"] = li.xpath(
                        ".//div[@class='interval01-list-cars-infor']/p/a/text()").extract_first()
                    item["guideprice"] = li.xpath(
                        ".//div[@class='interval01-list-guidance']//div/text()").extract_first()
                    item["url"] = li.xpath(".//div[@class='interval01-list-cars-infor']/p/a/@href").extract_first()
                    # print(item["url"])
                    item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item["guideprice_range"] = Official_guide_price
                    item["familyname"] = series_name
                    item["level"] = level
                    item["body_structure"] = body_structure
                    item["engine"] = engine
                    item["geartype"] = gearbox
                    item["brandid"] = response.meta["brand_id"]
                    item["salestatus"] = response.meta["status"]
                    item["brandname"] = response.meta["brand_name"]
                    item["statusplus"] = item["salesdesc"] + item["url"] + str(1551)+time.strftime('%Y-%m-%d %X', time.localtime())
                        # print(item)
                    yield item
                    # print(item)
