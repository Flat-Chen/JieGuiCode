# -*- coding: utf-8 -*-
import json
import logging
import os
import re
import sys
import time
from PIL import Image
import tesserocr
import requests
import io
import scrapy

# 爬虫名
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from ..items import GuaziItem
from ..redis_bloom import BloomFilter

website = 'guazi'


#  瓜子二手车COOKIES_ENABLED 为False
#  是用redis-boolom过滤器   不用指定数量，数量的指定一般在__init__中
class GuazicarSpider(scrapy.Spider):
    name = website
    allowed_domains = ['guazi.com']
    start_urls = ['https://www.guazi.com/www/buy/']
    # custom_settings = {"COOKIES_ENABLED": False}

    # is_debug = Trueis_debug
    # custom_debug_settings = {
    #     'MONGODB_COLLECTION': website,
    #     'CONCURRENT_REQUESTS': 2
    #
    # }

    def __init__(self, **kwargs):
        settings.set("WEBSITE", website)
        # settings.set("COOKIES_ENABLED", False)
        self.bf = BloomFilter(key='b1f_' + website)
        super(GuazicarSpider, self).__init__(**kwargs)

    # 车型
    def parse(self, response):
        print(response.request.headers)
        car_pinpai_list = response.xpath(

            "//div[@class='dd-all clearfix js-brand js-option-hid-info']//p/a/text()").extract()
        car_variety_list = response.xpath(
            "//div[@class='dd-all clearfix js-brand js-option-hid-info']//p/a/@href").extract()
        for i in range(len(car_variety_list)):
            yield response.follow(url=car_variety_list[i], callback=self.car_classif,
                                  meta={"brand": car_pinpai_list[i]}, dont_filter=True)

    def get_conten(self, content_str):
        return re.sub("(\r|\n| )", "", content_str)

    # 车系
    def car_classif(self, response):
        # print(2222222222)
        car_chexi_list = response.xpath("//dl[@class='clearfix'][2]//ul//a/@href").extract()
        car_series_list = response.xpath("//dl[@class='clearfix'][2]//ul//a/text()").extract()
        # print(car_chexi_list)
        for i in range(len(car_chexi_list)):
            response.meta.update({"series": car_series_list[i].strip(" ").strip("\n").strip(" ")})
            yield response.follow(url=car_chexi_list[i], callback=self.parse_car,
                                  meta=response.meta, dont_filter=True)

    #     车+翻页
    def parse_car(self, response):
        next_page_url = response.xpath("//ul[@class='pageLink clearfix']/li[last()]/a/@href").extract_first()
        if response.status == 302:
            return
        car_list = response.xpath("//ul[@class='carlist clearfix js-top']/li/a/@href").extract()
        if car_list == None:
            return
        for car_url in car_list:
            yield response.follow(url=car_url, callback=self.jiexi_car, meta=response.meta)
        if next_page_url != None:
            yield response.follow(url=next_page_url[1], callback=self.parse_car, meta=response.meta, dont_filter=True)

    def jiexi_car(self, response):
        grap_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        item = GuaziItem()
        item["carid"] = re.findall(r'.*/(.*?)\.htm', response.url)[0]
        item["car_source"] = "guazi"
        item["grab_time"] = grap_time
        item["update_time"] = None
        # b = re.findall(r"(\d*)年(\d*)月(\d*)日", response.xpath("//p[@class='bottom-text']/text()").extract_first())[0]
        # item["post_time"] = b[0] + "-" + b[1] + "-" + b[2]
        item['post_time'] = None
        print(item["post_time"], "*" * 50)
        item["sold_date"] = None
        item["pagetime"] = "zero"
        item["parsetime"] = grap_time
        item["shortdesc"] = \
            response.xpath("//div[@class='product-textbox']/h1/text()").extract_first().strip("\r\n").strip(
                " ").strip(
                "\r\n")
        item["pagetitle"] = response.xpath("//title/text()").extract_first().strip("")
        item["url"] = response.url
        item["newcarid"] = None
        item["status"] = "sale"
        item["brand"] = response.meta["brand"]
        item["series"] = response.meta["series"].strip("\r").strip(" ")
        item["factoryname"] = response.xpath(
            "//td[contains(text(),'厂商')]/following-sibling::td[1]/text()").extract_first()
        item["modelname"] = None
        item["brandid"] = None
        item["familyid"] = None
        item["seriesid"] = None
        # item["body"] = response.xpath("//table[1]/tbody/tr[7]/td[2]/text()").extract_first()
        item["body"] = None
        title = response.xpath("//title/text()").extract_first()
        relt = re.findall(r'(\d{4})[年款]', title)
        if relt:
            makeyear = '20' + relt[0] if len(relt[0]) == 2 else relt[0]
            item['makeyear'] = makeyear
        item["registerdate"] = response.xpath("//li[@class='one']/div/text()").extract_first()
        register_date = re.findall(r'\d{4}-\d{2}', item['registerdate'])
        if not register_date:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
                }
                img_url = response.css('li.one img::attr(src)').get()
                buffer_ = io.BytesIO(requests.get(img_url, headers=headers).content)
                item['registerdate'] = re.findall(r'\d{4}-\d{2}', tesserocr.image_to_text(Image.open(buffer_)))[0]
            except Exception as e:
                print('请求图片错误：', repr(e))
            finally:
                buffer_.close()  # 释放缓存

        item["registeryear"] = item['registerdate'].split("-")[0]
        item["produceyear"] = None
        # try:
        #     bodystyle = re.findall(r"座(.*?)厢", item["body"])[0]
        # except:
        #     bodystyle = None
        # item["bodystyle"] = bodystyle + "厢" if bodystyle != None else None
        item["bodystyle"] = None
        item["level"] = response.xpath(
            "//td[contains(text(),'级别')]/following-sibling::td[1]/text()").extract_first()
        item["fueltype"] = response.xpath(
            "//td[contains(text(),'燃料类型')]/following-sibling::td[1]/text()").extract_first()
        item["driverway"] = response.xpath(
            "//td[contains(text(),'驱动方式')]/following-sibling::td[1]/text()").extract_first()
        item["output"] = response.xpath(
            "//td[contains(text(),'排量')]/following-sibling::td[1]/text()").extract_first()
        item["guideprice"] = None
        # 新车指导价46.30万(含税)
        item["guidepricetax"] = response.xpath("//span[@class='newcarprice']/text()").extract_first()
        try:
            guidepricetax = re.findall(r"新车指导价(.*?)\(", item["guidepricetax"])[0]
        except:
            guidepricetax = None
        item["guidepricetax"] = guidepricetax
        # try:
        #     doors = re.findall(r"(\d?)门", item["body"])[0]
        # except:
        #     doors = None
        # item["doors"] = doors
        item["doors"] = None
        item["emission"] = response.css("li.four div.typebox::text").get()
        item["gear"] = response.xpath(
            "//td[contains(text(),'变速箱')]/following-sibling::td[1]/text()").extract_first()
        item["geartype"] = response.xpath("//li[@class='five']/div/text()").extract_first()
        # try:
        #     seats = re.findall(r"门(\d?)座", item["body"])[0]
        # except:
        #     seats = None
        # item["seats"] = seats
        item["seats"] = None
        # print(item)
        # length_width_height = \
        #     re.findall(r"<td width='50%' class='td1'>长/宽/高(mm)</td><td width='50%' class='td2'>(.*)</td>",
        #                response.text)
        length_width_height = response.xpath(
            "//div[@class='basic-infor js-basic-infor js-top']//table[1]//tr[7]/td[2]/text()").extract_first()
        try:
            length_width_height = length_width_height.split("/")
        except:
            item["length"] = None
            item["width"] = None
            item["height"] = None
        else:
            if length_width_height != "-":
                item["length"] = length_width_height[0]
                item["width"] = length_width_height[1]
                item["height"] = length_width_height[2]
            else:
                item["length"] = None
                item["width"] = None
                item["height"] = None
            item["gearnumber"] = None
        item["weight"] = response.xpath(
            "//td[contains(text(),'整备质量')]/following-sibling::td[1]/text()").extract_first()
        item["wheelbase"] = response.xpath(
            "//td[contains(text(),'轴距')]/following-sibling::td[1]/text()").extract_first()
        item["generation"] = None
        item["fuelnumber"] = response.xpath(
            "//td[contains(text(),'燃油标号')]/following-sibling::td[1]/text()").extract_first()
        item["lwv"] = response.xpath(
            "//div[@class='detailcontent clearfix js-detailcontent active']//td[contains(text(),'发动机')]/following-sibling::td[1]/text()").extract_first().split("/")[2]
        try:
            lwvnumber = re.findall(r"[[A-Z](\d?)", item["lwv"])[0]
        except:
            lwvnumber = None
        item["lwvnumber"] = lwvnumber
        item["maxnm"] = response.xpath(
            "//td[contains(text(),'最大扭矩')]/following-sibling::td[1]/text()").extract_first()
        item["maxpower"] = None
        item["maxps"] = response.xpath(
            "//td[contains(text(),'最大马力')]/following-sibling::td[1]/text()").extract_first()
        item["frontgauge"] = None
        item["compress"] = None
        item["years"] = None
        item["paytype"] = None
        item["price1"] = response.xpath("//div[@class='price-main']/span/text()").extract_first().strip("万").strip(
            " ")
        item["pricetag"] = None
        item["mileage"] = response.xpath("//li[@class='two']/div/text()").extract_first()
        item["usage"] = None
        item["color"] = None
        item["city"] = response.xpath("//div[@class='left-nav']/a[2]/text()").extract_first().split("二手车")[0]
        item["prov"] = None
        guarantee = response.xpath("//div[@class='product-textbox']//span[@class='labels baomai']/text()").extract_first()
        item["guarantee"] = "严选车" if guarantee == "严选车" else None
        # item["totalcheck_desc"] = response.xpath("//div[@class='test-con']/text()").extract_first().split("\n")
        # totalcheck_desc = ""
        # for i in item["totalcheck_desc"]:
        #     totalcheck_desc = totalcheck_desc + i
        item["totalcheck_desc"] = None
        item["totalgrade"] = None
        item["contact_type"] = None
        item["contact_name"] = None
        item["contact_phone"] = None
        item["contact_address"] = None
        item["contact_company"] = response.xpath("//table[2]/tbody/tr[9]/td[1]/text()").extract_first()
        if item["contact_company"] == "电池充电时间":
            item["contact_company"] = {
                "battery_type": response.xpath('//table[2]/tbody/tr[9]/td[2]/text()').extract_first()}
        else:
            item["contact_company"] = '{}'
        item["contact_url"] = None
        item["change_date"] = None
        item["change_times"] = response.xpath("//li[@class='seven']/div/text()").extract_first().split("次")[0]
        item["insurance1_date"] = response.xpath("//li[@class='ten']/div/text()").extract_first()
        try:
            item["insurance2_date"] = response.xpath("//li[@class='last']/div/text()").extract_first().strip("")
        except:
            item["insurance2_date"] = None
        item["hascheck"] = None
        item["repairinfo"] = None
        item["yearchecktime"] = response.xpath("//li[@class='nine']/div/text()").extract_first()
        item["carokcf"] = None
        item["carcard"] = None
        item["carinvoice"] = None
        item["accident_desc"] = self.get_conten("|".join(response.xpath(
            "//div[@id='accident']/..//span[@class='icon-yellow-error']/../text()").extract()))
        item["accident_score"] = None
        item["outer_desc"] = self.get_conten("|".join(
            response.xpath("//div[@id='surface']//div[@class='appear-ct']/p/text()").extract()))
        item["safe_desc"] = self.get_conten("|".join(
            response.xpath("//div[@id='surface']//span[@class='icon-sanjiao-yellow']/../text()").extract()))
        item["outer_score"] = None
        item["inner_desc"] = None
        item["inner_score"] = None

        dipan = self.get_conten("|".join(response.xpath(
            "//div[@id='underpan']/..//span[@class='icon-yellow-error']/../text()").extract()))
        yisui = self.get_conten("|".join(response.xpath(
            "//div[@id='easyWear']/..//span[@class='icon-yellow-error']/../text()").extract()))
        changyong = self.get_conten("|".join(response.xpath(
            "//div[@id='function']/..//span[@class='icon-yellow-error']/../text()").extract()))
        qidong = self.get_conten("|".join(response.xpath(
            "//div[@id='start']/..//span[@class='icon-yellow-error']/../text()").extract()))

        item["road_desc"] = str({
            "底盘检测": dipan,
            "易损耗部件": yisui,
            "常用功能检测": changyong,
            "启动驾驶检测": qidong,
        })
        item["safe_score"] = None
        item["road_desc"] = None
        item["road_score"] = None
        item["lastposttime"] = None
        item["newcartitle"] = None
        item["newcarurl"] = None
        item["img_url"] = response.xpath("//ul/li[@class='fl js-bigpic'][1]/img/@src").extract_first()
        item["first_owner"] = response.xpath(
            "//td[contains(text(),'进气形式')]/following-sibling::td[1]/text()").extract_first()
        item["carno"] = response.xpath("//li[@class='three']/div/text()").extract_first()
        item["carnotype"] = None
        item["carddate"] = None
        item["changecolor"] = None
        item["outcolor"] = None
        item["innercolor"] = None
        item["desc"] = response.xpath("//dd/span/text()").extract()
        desc = ""
        for i in item["desc"]:
            desc = desc + i + "\\"
        item["desc"] = desc
        try:
            item["statusplus"] = item["url"] + "-¥" + item["price1"] + "-" + item["status"] + "-" + item[
                "pagetime"] + str(item["road_desc"]) + str(item["post_time"]) + guarantee
        except:
            item["statusplus"] = item["url"] + "-¥" + item["price1"] + "-" + item["status"] + "-" + item[
                "pagetime"] + str(item["road_desc"]) + str(item["post_time"]) 

        returndf = self.bf.isContains(item["statusplus"])
        # 1数据存在，0数据不存在
        if returndf == 1:
            have = True
        else:
            have = False
        logging.log(msg='数据是否存在。。%s' % have, level=logging.INFO)

        yield item
        # print(item)