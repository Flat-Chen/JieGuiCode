# import logging
# import random
#
# import pymongo
import hashlib
# import json
# import re
#
# import requests
# import scrapy
# from redis import Redis
#
# from ..items import Che300
# from scrapy.conf import settings
# import time
#
# website = 'che300_price_daily_update_test'
# redis_cli = Redis(host="192.168.1.249", port=6379, db=3)
#
#
# class CarSpider(scrapy.Spider):
#     name = website
#     start_url = "https://m.che300.com/partner/result.php?prov=3&city=3&brand={}&series={}&model={}&registerDate={}&mileAge=0.1&intention=0&partnerId=wechat_01&unit=1&sld=sh"
#     custom_settings = {
#         "RETRY_ENABLED": True,
#         "RETRY_TIMES": "8",
#         "CONCURRENT_REQUESTS": 10
#     }
#
#     # allowed_domains = ['api.app.yiche.com']
#
#     def __init__(self, **kwargs):
#         super(CarSpider, self).__init__(**kwargs)
#         # 一共多少量车
#         self.counts = 0
#         #  布隆过滤器，定义的大概数量
#         self.carnum = 3000000
#         #         Mongod 配置
#         # MONGODB_DB = 'carbaojia'
#         settings.set("MONGODB_COLLECTION", website, priority='cmdline')
#         settings.set("MONGODB_DB", 'usedcar_evaluation', priority='cmdline')
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
#             "Referer": "https://m.che300.com/wechat_01",
#         }
#
#     def redis_tools(self, url):
#         redis_md5 = hashlib.md5(url.encode("utf-8")).hexdigest()
#         valid = redis_cli.sadd("che300_price_daily_update_test", redis_md5)
#         return valid
#
#     def get_SerialID(self):
#         """
#         1：获取SerialID_set()
#         :return:
#         """
#         connection = pymongo.MongoClient(
#             settings['MONGODB_SERVER'],
#             settings['MONGODB_PORT']
#         )
#         db = connection["usedcar_evaluation"]
#         collection = db["che300_app_modelinfo2"]
#
#         a = collection.find({}, {"sid": 1, "bid": 1, "id": 1, "min_reg_year": 1, "max_reg_year": 1, "_id": 0})
#         return a
#
#     # brand: 5
#     # series: 14254
#     # model: 1234997
#     # registerDate: 2019-12
#     def start_requests(self):
#         """
#         1: 构造url，sign
#         2：读取SerialID 这部是构造url 的重要一步
#         :return:
#         """
#         # 1 获取SerialID_set
#         # redis_cli.delete("che300_price_daily_update_test")
#         car_msg_list = list(self.get_SerialID())
#         random.shuffle(car_msg_list)
#         logging.log(msg="down -----------------------{}".format(len(car_msg_list)), level=logging.INFO)
#
#         for car in car_msg_list:
#             #         解析年份
#             for year in range(int(car["max_reg_year"]) + 1)[int(car["min_reg_year"])::]:
#                 for i in range(12):
#                     registerDate = str(year) + "-" + str(i + 1)
#                     meta = {
#                         "brand": car["bid"],
#                         "series": car["sid"],
#                         "model": car["id"],
#                         "registerDate": registerDate,
#                         "city": 3,
#                         "prov": 3,
#                         "mile": 0.1
#                     }
#                     url = self.start_url.format(car["bid"], car["sid"], car["id"], registerDate)
#                     # print(url)
#                     logging.log(msg="down -----------------------{}".format(self.counts), level=logging.INFO)
#                     self.counts = self.counts + 1
#                     valid = self.redis_tools(url)
#                     if valid == 0:
#                         logging.log(msg="this http request is repetition", level=logging.INFO)
#                         return
#                     else:
#                         yield scrapy.Request(url=url, meta=meta, headers=self.headers, dont_filter=True)
#
#     def parse(self, response):
#         item = Che300()
#         item["grabtime"] = time.strftime('%Y-%m-%d %X', time.localtime())
#         item["url"] = response.url
#         item["price1"] = response.xpath("//li[@class='dealer_low_buy_price']/text()").extract_first()
#         item["price2"] = response.xpath("//div[@class='dealer_buy_price']/text()").extract_first()
#         item["price3"] = response.xpath("//li[@class='individual_low_sold_price']/text()").extract_first()
#         item["price4"] = response.xpath("//div[@class='individual_price']/text()").extract_first()
#         item["price5"] = response.xpath("//li[@class='dealer_low_sold_price']/text()").extract_first()
#         item["price6"] = response.xpath("//div[@class='dealer_price']/text()").extract_first()
#         item["price7"] = response.xpath("//li[@class='dealer_high_sold_price']/text()").extract_first()
#         item["brand"] = response.meta["brand"]
#         item["series"] = response.meta["series"]
#         item["salesdescid"] = response.meta["model"]
#         item["regDate"] = response.meta["registerDate"]
#         item["cityid"] = response.meta["city"]
#         item["prov"] = response.meta["prov"]
#         item["mile"] = response.meta["mile"]
#         item["statusplus"] = response.url + str(response.meta)
#         yield item
from redis import Redis

redis_cli = Redis(host="192.168.1.249", port=6379, db=3)
def redis_tools(url):
    redis_md5 = hashlib.md5(url.encode("utf-8")).hexdigest()
    valid = redis_cli.sadd("che300_price_daily_update_test", redis_md5)
    return valid
valid = redis_tools('1')
# 1 不存在
# 0 存在
print(valid)