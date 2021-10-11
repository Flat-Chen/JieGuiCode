import json
import time

import pandas as pd
import re

from redis import Redis

from ..items import CarHome_Item
import scrapy
import logging
from scrapy.conf import settings
from hashlib import md5

website = 'car_home'


# 先循环城市 然后在循环车
class CarSpider(scrapy.Spider):
    name = website
    # start_urls = get_url()
    # 判断 城市是否有足够的车源，如果充足 则循环车系
    start_urls = ["https://product.360che.com/BrandList.html"]
    headers = {'Referer': 'https://product.360che.com/s12/3169_index.html',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}


    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MYSQLDB_DB', "truck", priority='cmdline')

        self.counts = 0

    def parse(self, response):
        #     获取 brand 名字和baranID
        for a in response.xpath('//div[@class="xll_center2_a1_z"]/dl/dd/a/text()').getall():
            print(a)
    #     car_list = response.xpath("//div[@class='xll_center2_a1'or @class='xll_center2_a1 group-area']")
    #     last_brandname = ""
    #     for car in car_list:
    #         # 厂商
    #         factoryname = car.xpath(".//div[@class='xll_center2_a1_y1']/a/text()").extract_first()
    #         factoryid = \
    #             re.findall(r"/b_(\d*).html", car.xpath(".//div[@class='xll_center2_a1_y1']/a/@href").extract_first())[0]
    #         # 品牌
    #         brandname = car.xpath(".//div[@class='xll_center2_a1_z']//dt/a/@title").extract_first()
    #         if brandname == None:
    #             brandname = last_brandname
    #         last_brandname = brandname
    #         familyname1_list = car.xpath(".//div[@class='xll_center2_a1_y2']")
    #         for familyname1_xpath in familyname1_list:
    #             # 车系
    #             familyname = familyname1_xpath.xpath(".//dt/a/text()").extract_first()
    #             familyname_url = familyname1_xpath.xpath(".//dt/a/@href").extract_first()
    #             familynameid = re.findall(r"/(\d*)_index", familyname_url)[0]
    #             meta = {
    #                 "factoryname": factoryname,
    #                 "factoryid": factoryid,
    #                 "brandname": brandname,
    #                 "seriesname": familyname,
    #                 "seriesid": familynameid,
    #             }
    #             # print(meta)
    #             yield response.follow(url=familyname_url, callback=self.series_parse, headers=self.headers, meta=meta)

    # #     https://product.360che.com/index.php?r=ajax/series/get-product&seriesid=1185&subcateid=64
    # def series_parse(self, response):
    #     subcateid_list = response.xpath("//a[@class='header-content']/@href").extract()
    #     subcatename_list = response.xpath("//a[@class='header-content']/h3/text()").extract()
    #     # https://product.360che.com/s4/1185_70_index.html
    #     for i in range(len(subcateid_list)):
    #         subcateid = re.findall(r"_(\d*)_", subcateid_list[i])[0]
    #         subcatename = subcatename_list[i]
    #         response.meta.update({"subcateid": subcateid, 'subcatename': subcatename})
    #         url = "https://product.360che.com/index.php?r=ajax/series/get-product&seriesid={}&subcateid={}".format(
    #             response.meta["seriesid"], subcateid)
    #         yield scrapy.Request(url=url, headers=self.headers, callback=self.car_parse, meta=response.meta)

    # def car_parse(self, response):
    #     url_list = response.xpath("//tr/td[1]/a/@href").extract()
    #     for url in url_list:
    #         yield response.follow(url=url, callback=self.car_list_parse, headers=self.headers, meta=response.meta)

    # def car_list_parse(self, response):
    #     item = CarHome_Item()

    #     item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #     item["url"] = response.url
    #     item["imgurl"] = response.xpath(
    #         "//div[@class='c_n_a_1 main-pic']//img/@src").extract_first()
    #     item["factoryname"] = response.meta["factoryname"]
    #     item["factoryid"] = response.meta["factoryid"]
    #     item["brandname"] = response.meta["brandname"]
    #     item["seriesname"] = response.meta["seriesname"]
    #     item["seriesid"] = response.meta["seriesid"]
    #     item["subcateid"] = response.meta["subcateid"]
    #     item["subcatename"] = response.meta["subcatename"]
    #     item["shortdesc"] = response.xpath(
    #         "//h1[@class='conttan_a_l']/a/text()").extract_first()
    #     print(item["shortdesc"])
    #     try:
    #         item["model"] = re.findall(r'\(.*\)', item["shortdesc"])[0]
    #     except:
    #         item["model"] = None
    #     item["status"] = response.xpath("//div[@class='c_a_t21']/span/text()").extract_first()
    #     item["price"] = response.xpath(
    #         "//font[@class='red']/text()").extract_first()
    #     item["driving"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "驱动形式")).extract_first()
    #     item["maxpower"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "最大马力")).extract_first()
    #     item["emissionstandard"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "排放标准")).extract_first()
    #     item["placeorigin"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "产地")).extract_first()
    #     item["tonlevel"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "吨位级别")).extract_first()
    #     item["enginebrand"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "奔驰")).extract_first()
    #     item["lwvnumber"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "汽缸数")).extract_first()
    #     item["fueltype"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "燃料种类")).extract_first()
    #     item["lwv"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "汽缸排列形式")).extract_first()
    #     item["emission"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "排放标准")).extract_first()
    #     item["maxwork"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "最大输出功率")).extract_first()
    #     item["cab"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "驾驶室")).extract_first()
    #     item["Bridgesuspension"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "驾驶室悬挂")).extract_first()
    #     item["seatrows"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "座位排数")).extract_first()
    #     item["mainseat"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "主驾座椅形式")).extract_first()
    #     item["skylight"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "天窗")).extract_first()
    #     item["tiresnumber"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "轮胎数")).extract_first()
    #     item["ABS"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "ABS防抱死")).extract_first()
    #     item["ASR"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "ASR驱动防滑")).extract_first()
    #     item["fairing"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "导流罩")).extract_first()
    #     item["airconditioner"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "空调调节形式")).extract_first()
    #     item["powerwindow"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "电动车窗")).extract_first()
    #     item["electricrearview"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "后视镜电加热")).extract_first()
    #     item["musicapi"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "外接音源接口")).extract_first()
    #     item["radio"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "收音机")).extract_first()
    #     item["qfoglight"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "前雾灯")).extract_first()
    #     item["nightlight"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "日间行车灯")).extract_first()
    #     item["remotekey"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "遥控钥匙")).extract_first()
    #     item["Electroniclock"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "电子中控锁")).extract_first()
    #     item["cruisecontrol"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "定速巡航")).extract_first()
    #     item["engine"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "发动机：")).extract_first()
    #     item["gearbox"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "变速箱：")).extract_first()
    #     item["Rearaxleratio"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "后桥速比：")).extract_first()
    #     item["carlong"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "车身长度：")).extract_first()
    #     item["carwidth"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "车身宽度：")).extract_first()
    #     item["carhigh"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "车身高度：")).extract_first()
    #     item["carweight"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "整车重量：")).extract_first()
    #     item["totalweight"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "牵引总质量：")).extract_first()
    #     item["maxspeed"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "最高车速：")).extract_first()
    #     item["output"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "排量：")).extract_first()
    #     item["maxnm"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "扭矩：")).extract_first()
    #     item["technicalroute"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "技术路线：")).extract_first()
    #     item["qgears"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "前进挡位")).extract_first()
    #     item["hgears"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "倒挡数：")).extract_first()
    #     item["tyresize"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "轮胎规格：")).extract_first()
    #     item["hbridge"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "前桥描述：")).extract_first()
    #     item["qbridge"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "后桥描述：")).extract_first()
    #     item["hbridgespeed"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "后桥速比：")).extract_first()
    #     item["saddle"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "鞍座：")).extract_first()
    #     item["hwheelbrake"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "后轮制动器：")).extract_first()
    #     item["qwheelbrake"] = response.xpath(
    #         "//div[contains(text(),'{}')]/../following-sibling::td[1]/div/text()".format(
    #             "前轮制动器：")).extract_first()
    #     item["carid"] = re.findall(r'/(\d*)_index.html', response.url)[0]
    #     item["statusplus"] = str(item["url"]) + str(item["price"]) + str(item["shortdesc"]) + str(item["status"]) + str(
    #         item["carid"])
    #     # print(item)
    #     yield item
