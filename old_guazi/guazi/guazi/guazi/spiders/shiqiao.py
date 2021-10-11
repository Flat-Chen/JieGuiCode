# brand: 奥驰汽车
# model: 载货车
# series: 奥驰A系
import json
import time

import scrapy

# 爬虫名
from scrapy.conf import settings
from ..items import  shiqiao_prcie

website = 'shiqiao_car_base'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://vehest.shiqiaoqiche.com/vehestweb/est/est/estresult/getAllMake.do"
    headers = {'Referer': 'http://www.shiqiaokache.com/',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(GuazicarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MYSQLDB_DB', "truck", priority='cmdline')

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, headers=self.headers)

    def parse(self, response):
        car_list = json.loads(response.text)
        for i in car_list["data"][0:1]:
            brand =i["value"]
            key =i["key"]
            meta= {
               "brand":brand,
                "brandid":key
            }
            url = "https://vehest.shiqiaoqiche.com/vehestweb/est/est/estresult/getModelByMakeId.do?makeId="+str(key)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_series, meta=meta)

    def parse_series(self, response):
        # print(response.text)
        car_list = json.loads(response.text)
        for i in car_list["data"][0:1]:
            model =i["modelname"]
            modelid =i["modelid"]
            meta={
                "model":model ,
                "modelid":modelid ,

            }
            response.meta.update(meta)
            #     https://vehest.shiqiaoqiche.com/vehestweb/est/est/estresult/getCarTypeByModelId.do?modelId=
            url ="https://vehest.shiqiaoqiche.com/vehestweb/est/est/estresult/getCarTypeByModelId.do?modelId={}".format(str(modelid))
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_car, meta=response.meta)
    def parse_car(self,response):
        print(response.meta)
        car_list = json.loads(response.text)
        for  i in car_list["data"]["style"]:
            for car in car_list["data"]["style"][i]:
                item =shiqiao_prcie()
                item["grabtime"] = time.strftime('%Y-%m-%d %X', time.localtime())
                item["url"] = response.url
                item["brandid"] =response.meta["brandid"]
                item["brand"] = response.meta["brand"]
                item["model"] =response.meta["model"]
                item["modelid"] = response.meta["modelid"]
                item["emission"] = car["emissionStandardId"]
                item["power"] = car["engineMaxHorsepower"]
                item["gerrboxBrand"] = car["gerrboxBrand"]
                item["carid"] = car["id"]
                item["styleBulletinModel"] = car["styleBulletinModel"]
                item["styleDisname"] = car["styleDisname"]
                item["styleDriveMode"] = car["styleDriveMode"]
                item["styleName"] = car["styleName"]
                item["stylePurposeId"] = car["stylePurposeId"]
                item["stylePurposeName"] = car["stylePurposeName"]
                item["statusplus"] = str(car)
                print(item)

























