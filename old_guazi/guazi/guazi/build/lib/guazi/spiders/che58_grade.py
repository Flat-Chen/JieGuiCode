import copy
import hashlib
import json
import pymongo
import time

import re

from ..items import che58_grade
import scrapy
from scrapy.conf import settings

website = 'che58_grade'


# 先循环城市 然后在循环车
class CarSpider(scrapy.Spider):
    name = website
    start_urls = [
        "https://product.58che.com/price_list/brand_1_1.shtml"]
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'Sec-Fetch-Dest': 'document',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 15,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        settings.set("MONGODB_DB", "newcar", priority="cmdline")
        self.counts = 0

    def get_SerialID(self):
        """
        1：获取SerialID_set()
        :return:
        """
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection["newcar"]
        collection = db["che58_newcar"]

        a = collection.find({}, {"serier_id": 1, "_id": 0})
        SerialID_set = set()
        for i in a:
            SerialID_set.add(i["serier_id"])
        return list(SerialID_set)

    def start_requests(self):
        series_list = self.get_SerialID()
        for series in series_list:
            url = "https://www.58che.com/app/index.php?callback=jQuery172010403227733493381_1593583694671&lineId={}&c=Ajax_AjaxJDPower&a=getJDPower&rand=1593583695346&_=1593583695346".format(
                series)
            yield scrapy.Request(url=url, headers=self.headers, meta={"serise_id": series})

    def parse(self, response):
        data = json.loads(response.text.strip("jQuery172010403227733493381_1593583694671(").strip(")"))["data"]
        item = {}
        try:
            item["quality_score"] = data["quality_score"]
        except:
            item["quality_score"] = None
        try:
            item["charm_score"] = data["charm_score"]
        except:
            item["charm_score"] = None
        try:
            item["brand_score"] = data["brand_score"]
        except:
            item["brand_score"] = None
        try:
            item["exp_score"] = data["exp_score"]
        except:
            item["exp_score"] = None
        try:
            item["recom_score"] = data["recom_score"]
        except:
            item["recom_score"] = None
        response.meta.update(item)
        url = "https://www.58che.com/{}/review.html".format(response.meta["serise_id"])
        yield scrapy.Request(url=url, headers=self.headers, meta=response.meta, callback=self.car_parse)

    def car_parse(self, response):
        item = che58_grade()
        item["series_id"] = response.meta["serise_id"]
        item["serise_name"] = response.xpath("//div[@class='curmbs']//a[@target='_self']/text()").extract_first()
        item["car_grade"] = "".join(response.xpath("//div[@class='fenshu l']//span/text()").extract()).split("/")[0]
        item["grade"] = json.dumps(dict(zip(response.xpath("//ul[@class='clearfix']/li/a/text()").extract(),
                                            response.xpath("//ul[@class='clearfix']/li/a/p/text()").extract())),
                                   ensure_ascii=False)
        item["rank"] = json.dumps(
            dict(zip(response.xpath("//div[contains(@class,'xgo_cars_hotcar')]//ul//li//a/text()").extract(),
                     response.xpath("//div[contains(@class,'xgo_cars_hotcar')]//ul//li//p/text()").extract())),
            ensure_ascii=False)
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["quality_score"] = response.meta["quality_score"]
        item["charm_score"] = response.meta["charm_score"]
        item["brand_score"] = response.meta["brand_score"]
        item["exp_score"] = response.meta["exp_score"]
        item["recom_score"] = response.meta["recom_score"]
        item['impression'] = str(response.xpath("//li[contains(@class,'yangshi')]/a/text()").extract())
        item['statusplus'] = response.url + item["car_grade"] + item["grade"] + item["rank"] + str(1)
        # print(item)
        yield item