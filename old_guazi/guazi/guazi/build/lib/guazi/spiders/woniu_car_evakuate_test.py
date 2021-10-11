import hashlib
import json
import logging
import os
import random
import re
import sys
import time

import scrapy
import pandas as pd
# 爬虫名
from redis import Redis
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from sqlalchemy import create_engine

from ..items import Woniu_Car_evaluate_Item

website = 'woniu_car_evaluate_all_test'
redis_cli = Redis(host="192.168.1.249", port=6379, db=3)

#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['guazi.com']
    start_urls = "https://open.che300.com/api/cv/brand_list"
    headers = {'https': '//www.woniuhuoche.com/truck/api/v1/evaluation/getEvalInfoWithZimu',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(settings['MYSQLDB_USER'],
                                                                                settings['MYSQLDB_PASS'],
                                                                                settings['MYSQL_SERVER'],
                                                                                settings['MYSQL_PORT'],
                                                                                "truck"))

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(GuazicarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MYSQLDB_DB', "truck", priority='cmdline')

    def redis_tools(self, url):
        redis_md5 = hashlib.md5(url.encode("utf-8")).hexdigest()
        valid = redis_cli.sadd("woniu_car_evaluate_test", redis_md5)
        return valid

    # https://www.woniuhuoche.com/truck/api/v1/evaluation/newEvalPrice?brand=%E5%A5%A5%E9%A9%B0%E6%B1%BD%E8%BD%A6&buyDate=2010-1&city=99&customerId=458313&drive=6X2&emission=%E5%9B%BD%E4%BA%94&model=%E8%BD%BD%E8%B4%A7%E8%BD%A6&oiltype=%E6%9F%B4%E6%B2%B9&power=168%E5%8C%B9&price=16.25&province=12&residueRatio=1&series=%E5%A5%A5%E9%A9%B0D%E7%B3%BB&boxLen=&volume=
    # brand: 奥驰汽车
    # buyDate: 2010-1
    # city: 99
    # drive: 6X2
    # emission: 国五
    # model: 载货车
    # oiltype: 柴油
    # power: 168匹
    # price: 16.25
    # province: 12
    # residueRatio: 1 到10
    # series: 奥驰D系
    # boxLen:
    # volume
    def start_requests(self):
        # cityid provid
        city_list = [[98, 12], [99, 12], [100, 12], [101, 12], [102, 12], [103, 12], [104, 12], [105, 12], [106, 12], [107, 12], [108, 12], [109, 12], [110, 12], [111, 12], [112, 12], [113, 12], [114, 12], [343, 33], [1, 1], [236, 22], [115, 13], [116, 13], [117, 13], [118, 13], [119, 13], [120, 13], [121, 13], [122, 13], [123, 13], [300, 28], [301, 28], [302, 28], [303, 28], [304, 28], [305, 28], [306, 28], [307, 28], [308, 28], [309, 28], [310, 28], [311, 28], [312, 28], [313, 28], [198, 19], [199, 19], [200, 19], [201, 19], [202, 19], [203, 19], [204, 19], [205, 19], [206, 19], [207, 19], [208, 19], [209, 19], [210, 19], [211, 19], [212, 19], [213, 19], [214, 19], [215, 19], [216, 19], [217, 19], [218, 19], [219, 20], [220, 20], [221, 20], [222, 20], [223, 20], [224, 20], [225, 20], [226, 20], [227, 20], [228, 20], [229, 20], [230, 20], [231, 20], [232, 20], [258, 24], [259, 24], [260, 24], [261, 24], [262, 24], [263, 24], [264, 24], [265, 24], [266, 24], [233, 21], [234, 21], [235, 21], [349, 21], [350, 21], [351, 21], [352, 21], [353, 21], [354, 21], [355, 21], [356, 21], [357, 21], [358, 21], [359, 21], [360, 21], [361, 21], [362, 21], [363, 21], [364, 21], [365, 21], [3, 3], [4, 3], [5, 3], [6, 3], [7, 3], [8, 3], [9, 3], [10, 3], [11, 3], [12, 3], [13, 3], [60, 8], [61, 8], [62, 8], [63, 8], [64, 8], [65, 8], [66, 8], [67, 8], [68, 8], [69, 8], [70, 8], [71, 8], [72, 8], [152, 16], [153, 16], [154, 16], [155, 16], [156, 16], [157, 16], [158, 16], [159, 16], [160, 16], [161, 16], [162, 16], [163, 16], [164, 16], [165, 16], [166, 16], [167, 16], [168, 16], [169, 16], [170, 17], [171, 17], [172, 17], [173, 17], [174, 17], [175, 17], [176, 17], [177, 17], [178, 17], [179, 17], [180, 17], [181, 17], [182, 17], [183, 17], [345, 17], [346, 17], [347, 17], [348, 17], [184, 18], [185, 18], [186, 18], [187, 18], [188, 18], [189, 18], [190, 18], [191, 18], [192, 18], [193, 18], [194, 18], [195, 18], [196, 18], [197, 18], [74, 10], [75, 10], [76, 10], [77, 10], [78, 10], [79, 10], [80, 10], [81, 10], [82, 10], [83, 10], [84, 10], [85, 10], [86, 10], [124, 14], [125, 14], [126, 14], [127, 14], [128, 14], [129, 14], [130, 14], [131, 14], [132, 14], [133, 14], [134, 14], [51, 7], [52, 7], [53, 7], [54, 7], [55, 7], [56, 7], [57, 7], [58, 7], [59, 7], [37, 6], [38, 6], [39, 6], [40, 6], [41, 6], [42, 6], [43, 6], [44, 6], [45, 6], [46, 6], [47, 6], [48, 6], [49, 6], [50, 6], [25, 5], [26, 5], [27, 5], [28, 5], [29, 5], [30, 5], [31, 5], [32, 5], [33, 5], [34, 5], [35, 5], [36, 5], [322, 30], [323, 30], [324, 30], [325, 30], [326, 30], [314, 29], [315, 29], [316, 29], [317, 29], [318, 29], [319, 29], [320, 29], [321, 29], [135, 15], [136, 15], [137, 15], [138, 15], [139, 15], [140, 15], [141, 15], [142, 15], [143, 15], [144, 15], [145, 15], [146, 15], [147, 15], [148, 15], [149, 15], [150, 15], [151, 15], [73, 9], [14, 4], [15, 4], [16, 4], [17, 4], [18, 4], [19, 4], [20, 4], [21, 4], [22, 4], [23, 4], [24, 4], [290, 27], [291, 27], [292, 27], [293, 27], [294, 27], [295, 27], [296, 27], [297, 27], [298, 27], [299, 27], [237, 23], [238, 23], [239, 23], [240, 23], [241, 23], [242, 23], [243, 23], [244, 23], [245, 23], [246, 23], [247, 23], [248, 23], [249, 23], [250, 23], [251, 23], [252, 23], [253, 23], [254, 23], [255, 23], [256, 23], [257, 23], [344, 34], [2, 2], [342, 32], [327, 31], [328, 31], [329, 31], [330, 31], [331, 31], [332, 31], [333, 31], [334, 31], [335, 31], [336, 31], [337, 31], [338, 31], [339, 31], [340, 31], [341, 31], [366, 31], [367, 31], [368, 31], [369, 31], [283, 26], [284, 26], [285, 26], [286, 26], [287, 26], [288, 26], [289, 26], [267, 25], [268, 25], [269, 25], [270, 25], [271, 25], [272, 25], [273, 25], [274, 25], [275, 25], [276, 25], [277, 25], [278, 25], [279, 25], [280, 25], [281, 25], [282, 25], [87, 11], [88, 11], [89, 11], [90, 11], [91, 11], [92, 11], [93, 11], [94, 11], [95, 11], [96, 11], [97, 11]]
        random.shuffle(city_list )
        car_list = pd.read_sql(
            "SELECT brand,driveName,emissionName ,model,oiltype,power,price,series, boxLen,volume from woniu_car_online ",
            con=self.engine, )
        for i in car_list.values.tolist():
            for city in city_list:
                print(city)
                for year in range(int(time.strftime("%Y", time.localtime()))+1)[2016::]:
                    buyDate = str(year) + time.strftime("-%m", time.localtime())
                    for id in [0]:
                        meta = {
                            "brand": i[0],
                            "buyDate": buyDate,
                            "city": city[0],
                            "drive": i[1],
                            "emission": i[2],
                            "model": i[3],
                            "oiltype": i[4],
                            "power": i[5],
                            "price": i[6],
                            "province": city[1],
                            "residueRatio": id + 1,
                            "series": i[7],
                            "boxLen": i[8],
                            "volume": i[9],
                        }
                        url = "https://www.woniuhuoche.com/truck/api/v1/evaluation/newEvalPrice?brand={}&buyDate={}&city={}&drive={}&emission={}&model={}&oiltype={}&power={}&price={}&province={}&residueRatio={}&series={}&boxLen={}&volume={}".format(
                            meta["brand"], meta["buyDate"], meta["city"], meta["drive"], meta["emission"],
                            meta["model"], meta["oiltype"], meta["power"], meta["price"], meta["province"],
                            meta["residueRatio"], meta["series"], meta["boxLen"], meta["volume"], )
                        valid = self.redis_tools(url)
                        if valid == 0:
                            logging.log(msg="this http request is repetition", level=logging.INFO)
                            continue
                        else:
                            yield scrapy.Request(url=url, headers=self.headers, meta=meta)

    def parse(self, response):
        data = json.loads(response.text)
        data_dict = data["data"]
        item = Woniu_Car_evaluate_Item()
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["brand"] = response.meta["brand"]
        item["buyDate"] = response.meta["buyDate"]
        item["city"] = response.meta["city"]
        item["drive"] = response.meta["drive"]
        item["emission"] = response.meta["emission"]
        item["model"] = response.meta["model"]
        item["oiltype"] = response.meta["oiltype"]
        item["power"] = response.meta["power"]
        item["price"] = response.meta["price"]
        item["province"] = response.meta["province"]
        item["residueRatio"] = response.meta["residueRatio"]
        item["series"] = response.meta["series"]
        item["boxLen"] = response.meta["boxLen"]
        item["volume"] = response.meta["volume"]
        item["badMerchantPrice"] = data_dict["merchant"]["badMerchantPrice"]
        item["midMerchantPrice"] = data_dict["merchant"]["midMerchantPrice"]
        item["fineMerchantPrice"] = data_dict["merchant"]["fineMerchantPrice"]
        item["badPersonPrice"] = data_dict["person"]["badPersonPrice"]
        item["midPersonPrice"] = data_dict["person"]["midPersonPrice"]
        item["badPersonPrice"] = data_dict["person"]["badPersonPrice"]
        item["fineOldTruckPrice"] = data_dict["oldTruck"]["fineOldTruckPrice"]
        item["badOldTruckPrice"] = data_dict["oldTruck"]["badOldTruckPrice"]
        item["midOldTruckPrice"] = data_dict["oldTruck"]["midOldTruckPrice"]
        item["seepName"] = data["backup"]["seepName"]
        item["seecName"] = data["backup"]["seecName"]
        item["statusplus"] = response.url + item["midOldTruckPrice"] + item["badOldTruckPrice"] + item["fineOldTruckPrice"] + item["badPersonPrice"] + item["midPersonPrice"] + item["badPersonPrice"] + item["badMerchantPrice"]+ item["midMerchantPrice"] + item["fineMerchantPrice"]
        yield item
