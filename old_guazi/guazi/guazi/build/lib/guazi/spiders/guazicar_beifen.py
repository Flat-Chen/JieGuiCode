# # -*- coding: utf-8 -*-
# import logging
# import os
# import re
# import sys
# import time
#
# import scrapy
#
# # 爬虫名
# from scrapy import signals
# from scrapy.conf import settings
# from selenium import webdriver
# from pydispatch import dispatcher
# from selenium.webdriver.chrome.options import Options
#
# from ..items import GuaziItem
#
# website = 'guazi1'
#
#
# #  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
# class GuazicarSpider(scrapy.Spider):
#     name = website
#     allowed_domains = ['guazi.com']
#     start_urls = ['https://www.guazi.com/www/buy/']
#
#     def __init__(self, **kwargs):
#         # os.system('killall phantomjs')
#         settings.set("WEBSITE", website)
#         # chrome_options = Options()
#         # chrome_options.add_argument('--headless')
#         # chrome_options.add_argument('--disable-gpu')
#         # prefs = {"profile.managed_default_content_settings.images": 2,
#         #          "profile.managed_default_content_settings.stylesheet": 2
#         #          }
#         # chrome_options.add_experimental_option("prefs", prefs)
#         # 在爬虫中初始化，变为在管道中是用
#         # service_args = ['--load-images=no', '--disk-cache=yes', '--ignore-ssl-errors=true', ]
#         # self.driver = webdriver.PhantomJS(settings['PHANTOMJS_PATH'], service_args=service_args)
#         # # # self.driver = webdriver.Chrome(chrome_options=chrome_options, service_args=service_args)
#         # self.driver.implicitly_wait(settings['PHANTOMJS_TIMEOUT'])
#         # self.driver.set_page_load_timeout(settings['PHANTOMJS_TIMEOUT'])
#         # self.driver.set_script_timeout(settings['PHANTOMJS_TIMEOUT'])  #
#         super(GuazicarSpider, self).__init__(**kwargs)
#         # 传递信息,也就是当爬虫关闭时scrapy会发出一个spider_closed的信息,当这个信号发出时就调用closeSpider函数关闭这个浏览器.
#         # dispatcher.connect(self.closeSpider, signals.spider_closed)
#
#     #
#     # def closeSpider(self, spider):
#     #     if spider.name == "guazi":
#     #         logging.log(msg='spider closed', level=logging.INFO)
#     #         # 当爬虫退出的时关闭浏览器
#     #         self.driver.quit()
#
#     # 车型
#     def parse(self, response):
#         # print(response.text)
#         car_pinpai_list = response.xpath(
#             "//div[@class='dd-all clearfix js-brand js-option-hid-info']//p/a/text()").extract()
#         car_variety_list = response.xpath(
#             "//div[@class='dd-all clearfix js-brand js-option-hid-info']//p/a/@href").extract()
#         for i in range(len(car_variety_list)):
#             yield response.follow(url=car_variety_list[i], callback=self.car_classif,
#                                   meta={"brand": car_pinpai_list[i]})
#
#     # 车系
#     def car_classif(self, response):
#         # print(2222222222)
#         car_chexi_list = response.xpath("//dl[@class='clearfix'][2]//ul//a/@href").extract()
#         car_series_list = response.xpath("//dl[@class='clearfix'][2]//ul//a/text()").extract()
#         # print(car_chexi_list)
#         for i in range(len(car_chexi_list)):
#             response.meta.update({"series": car_series_list[i].strip(" ").strip("\n").strip(" ")})
#             yield response.follow(url=car_chexi_list[i], callback=self.parse_car,
#                                   meta=response.meta)
#
#     #     车+翻页
#     def parse_car(self, response):
#         next_page_url = response.xpath("//ul[@class='pageLink clearfix']/li[last()]/a/@href").extract_first()
#         if response.status == 302:
#             return
#         car_list = response.xpath("//ul[@class='carlist clearfix js-top']/li/a/@href").extract()
#         if car_list == None:
#             return
#         for car_url in car_list:
#             yield response.follow(url=car_url, callback=self.jiexi_car, meta=response.meta)
#         if next_page_url != None:
#             yield response.follow(url=next_page_url[1], callback=self.parse_car, meta=response.meta)
#
#     def jiexi_car(self, response):
#         # print(response.xpath("//div[@class='product-textbox']/h2/text()[1]").extract_first())
#         # print(11111111)
#         # print("*" * 20, response.meta)
#         item = GuaziItem()
#         item["carid"] = re.findall(r'.*/(.*?)\.htm', response.url)[0]
#         item["car_source"] = "guazi"
#         item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         item["update_time"] = None
#         item["post_time"] = response.xpath("//ul[@class='assort clearfix']/li[1]/span/text()").extract_first()
#         item["sold_date"] = None
#         item["pagetime"] = "zero"
#         item["parsetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         item["shortdesc"] = \
#             response.xpath("//div[@class='product-textbox']/h2/text()").extract_first().strip("\n").strip().strip(
#                 "\n")
#         item["pagetitle"] = response.xpath("//title/text()").extract_first().strip("")
#         item["url"] = response.url
#         item["newcarid"] = None
#         item["status"] = "sale"
#         item["brand"] = response.meta["brand"]
#         item["series"] = response.meta["series"]
#         item["factoryname"] = response.xpath("//table[1]/tbody/tr[3]/td[2]/text()").extract_first()
#         item["modelname"] = None
#         item["brandid"] = None
#         item["familyid"] = None
#         item["seriesid"] = None
#         item["body"] = response.xpath("//table[1]/tbody/tr[7]/td[2]/text()").extract_first()
#         title = response.xpath("//title/text()").extract_first()
#         relt = re.findall(r'(\d{4})[年款]', title)
#         if relt:
#             makeyear = '20' + relt[0] if len(relt[0]) == 2 else relt[0]
#             item['makeyear'] = makeyear
#         item["registeryear"] = response.xpath("//li[@class='one']/div/text()").extract_first().split("-")[0]
#         item["produceyear"] = None
#         try:
#             bodystyle = re.findall(r"座(.*?)厢", item["body"])[0]
#         except:
#             bodystyle = None
#         item["bodystyle"] = bodystyle + "厢" if bodystyle != None else None
#         item["level"] = response.xpath("//table[1]/tbody/tr[4]/td[2]/text()").extract_first()
#         item["fueltype"] = response.xpath("//table[2]/tbody/tr[7]/td[2]/text()").extract_first()
#         item["driverway"] = response.xpath("//table[3]/tbody/tr[2]/td[2]/text()").extract_first()
#         item["output"] = response.xpath("//table[2]/tbody/tr[2]/td[2]/text()").extract_first()
#         item["guideprice"] = None
#         # 新车指导价46.30万(含税)
#         item["guidepricetax"] = response.xpath("//span[@class='newcarprice']/text()").extract_first()
#         try:
#             guidepricetax = re.findall(r"新车指导价(.*?)\(", item["guidepricetax"])[0]
#         except:
#             guidepricetax = None
#         item["guidepricetax"] = guidepricetax
#         try:
#             doors = re.findall(r"(\d?)门", item["body"])[0]
#         except:
#             doors = None
#         item["doors"] = doors
#         item["emission"] = response.xpath("//ul[@class='basic-eleven clearfix']/li[4]/div/text()").extract_first()
#         item["gear"] = response.xpath("//table[1]/tbody/tr[6]/td[2]/text()").extract_first()
#         item["geartype"] = response.xpath("//li[@class='five']/div/text()").extract_first()
#         try:
#             seats = re.findall(r"门(\d?)座", item["body"])[0]
#         except:
#             seats = None
#         item["seats"] = seats
#         length_width_height = response.xpath("//table[1]/tbody/tr[8]/td[2]/text()").extract_first().split("/")
#         if length_width_height != "-":
#             item["length"] = length_width_height[0]
#             item["width"] = length_width_height[1]
#             item["height"] = length_width_height[2]
#         else:
#             item["length"] = None
#             item["width"] = None
#             item["height"] = None
#         item["gearnumber"] = None
#         item["weight"] = response.xpath("//table[1]/tbody/tr[11]/td[2]/text()").extract_first()
#         item["wheelbase"] = response.xpath("//table[1]/tbody/tr[9]/td[2]/text()").extract_first()
#         item["generation"] = None
#         item["fuelnumber"] = response.xpath("//table[2]/tbody/tr[8]/td[2]/text()").extract_first()
#         item["lwv"] = response.xpath("//table[2]/tbody/tr[4]/td[2]/text()").extract_first()
#         try:
#             lwvnumber = re.findall(r"L(\d?)", item["lwv"])[0]
#         except:
#             lwvnumber = None
#         item["lwvnumber"] = lwvnumber
#         item["maxnm"] = response.xpath("//table[2]/tbody/tr[6]/td[2]/text()").extract_first()
#         item["maxpower"] = None
#         item["maxps"] = response.xpath("//table[2]/tbody/tr[5]/td[2]/text()").extract_first()
#         item["frontgauge"] = None
#         item["compress"] = None
#         item["registerdate"] = response.xpath("//li[@class='one']/div/text()").extract_first()
#         item["years"] = None
#         item["paytype"] = None
#         item["price1"] = response.xpath("//span[@class='pricestype']/text()").extract_first().strip("¥").strip(" ")
#         item["pricetag"] = None
#         item["mileage"] = response.xpath("//li[@class='two']/div/text()").extract_first()
#         item["usage"] = None
#         item["color"] = None
#         item["city"] = response.xpath("//li[@class='three']/div/text()").extract_first()
#         item["prov"] = None
#         guarantee = response.xpath("//div[@class='product-textbox']/h2/span/text()").extract_first()
#         item["guarantee"] = "严选车" if guarantee == "严选车" else None
#         item["totalcheck_desc"] = response.xpath("//div[@class='test-con']/text()").extract_first().split("\n")
#         totalcheck_desc = ""
#         for i in item["totalcheck_desc"]:
#             totalcheck_desc = totalcheck_desc + i
#         item["totalcheck_desc"] = totalcheck_desc
#         item["totalgrade"] = None
#         item["contact_type"] = None
#         item["contact_name"] = None
#         item["contact_phone"] = None
#         item["contact_address"] = None
#         item["contact_company"] = response.xpath("//table[2]/tbody/tr[9]/td[1]/text()").extract_first()
#         if item["contact_company"] == "电池充电时间":
#             item["contact_company"] = {
#                 "battery_type": response.xpath('//table[2]/tbody/tr[9]/td[2]/text()').extract_first()}
#         else:
#             item["contact_company"] = '{}'
#         item["contact_url"] = None
#         item["change_date"] = None
#         item["change_times"] = response.xpath("//li[@class='seven']/div/text()").extract_first().split("次")[0]
#         item["insurance1_date"] = response.xpath("//li[@class='ten']/div/text()").extract_first()
#         item["insurance2_date"] = response.xpath("//li[@class='last']/div/text()").extract_first().strip(" ")
#         item["hascheck"] = None
#         item["repairinfo"] = None
#         item["yearchecktime"] = response.xpath("//li[@class='nine']/div/text()").extract_first()
#         item["carokcf"] = None
#         item["carcard"] = None
#         item["carinvoice"] = None
#         item["accident_desc"] = None
#         item["accident_score"] = None
#         item["outer_desc"] = None
#         item["outer_score"] = None
#         item["inner_desc"] = None
#         item["inner_score"] = None
#         item["safe_desc"] = None
#         item["safe_score"] = None
#         item["road_desc"] = None
#         item["road_score"] = None
#         item["lastposttime"] = None
#         item["newcartitle"] = None
#         item["newcarurl"] = None
#         item["img_url"] = response.xpath("//ul/li[@class='fl js-bigpic'][1]/img/@src").extract_first()
#         item["first_owner"] = response.xpath("//table[2]/tbody/tr[3]/td[2]/text()").extract_first()
#         item["carno"] = response.xpath("//li[@class='three']/div/text()").extract_first()
#         item["carnotype"] = None
#         item["carddate"] = None
#         item["changecolor"] = None
#         item["outcolor"] = None
#         item["innercolor"] = None
#         item["desc"] = response.xpath("//dd/span/text()").extract()
#         desc = ""
#         for i in item["desc"]:
#             desc = desc + i + "\\"
#         item["desc"] = desc
#         item["statusplus"] = item["url"] + "-¥" + item["price1"] + "-" + item["status"] + "-" + item["pagetime"]
#         yield item
#         # print(item)
