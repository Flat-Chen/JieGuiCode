# #-*- coding: UTF-8 -*-
import json
import re
import time
import scrapy
import logging
from scrapy.conf import settings
from ..items import GuaziItem
from ..redis_bloom import BloomFilter

website = 'hx2car'


class CarSpider(scrapy.Spider):
    name = website
    allowed_domains = ["hx2car.com"]
    start_urls = [
        "https://www.hx2car.com/quanguo/soa1"
    ]

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2.5,
        # 'CONCURRENT_REQUESTS': 4,
        # 'RANDOMIZE_DOWNLOAD_DELAY': True,
    }

    def __init__(self, **kwargs):
        # self.headers = {'Referer': 'https://shanghai.taoche.com/',
        #                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

        settings.set("WEBSITE", website)
        self.bf = BloomFilter(key='b1f_' + website)
        super(CarSpider, self).__init__(**kwargs)

    def parse(self, response):
        for href in response.xpath('//div[@class="city"]/a/@href').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.select2_parse)

    def select2_parse(self, response):
        for href in response.xpath('//div[@class="brand_r"]/a/@href').extract():
            url = response.urljoin(href)
            # print(url)
            yield scrapy.Request(url, callback=self.list_parse)

    def list_parse(self, response):
        for href in response.xpath('//div[@class="Datu_cars"]/div'):
        # for href in response.xpath('//li[@class="carlog"]/a/@href').getall():
            urlbase = href.xpath('./div/a/@href').extract_first()
            url = response.urljoin(urlbase)
            yield scrapy.Request(url, callback=self.parse_car)

        next_page = response.xpath('//a[@class="num"]/@href')
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, self.list_parse)
    #         # print(url)

    def parse_car(self, response):
        # print(response.url)
        # pass
        grap_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_dict = {
            "projectName": "used-car-scrapy",
            "logProgram": website,
            "logProgramPath": "/home/scrapyd/eggs/guazi",
            "logPath": "/home/scrapyd/logs/guazi/{}/".format(website),
            "logTime": grap_time,
            "logMessage": "",
            "logServer": "192.168.1.248",
            "logObjectType": "UsedCarPaChong",
        }
        try:
            item = GuaziItem()
            item["carid"] = re.findall(r'/details/(\d*)', response.url)[0]
            item["car_source"] = "hx2car"
            item["usage"] = response.xpath('//p[contains(text(), "用途")]/../p[1]/text()').extract_first()
            item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["update_time"] = None
            item["post_time"] = response.xpath('//div[@class="title_infoL"]/span/i[1]/text()').extract_first()
            item["sold_date"] = None
            item["pagetime"] = grap_time
            item["parsetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["shortdesc"] = response.xpath('//*[@class="B_title"]/text()').extract_first()
            item["pagetitle"] = response.xpath("//head/title/text()").extract_first().strip("")
            item["url"] = response.url
            item["newcarid"] = re.findall(r'carType:\'(\d+)\'', response.text)[0]
            # print(response.headers)
            # print(item)
        # except Exception as e:
        #     print(repr(e))
            item["status"] = "sale"
            item["brand"] = response.xpath(
                '//div[@class="path"]/a[5]/text()').extract_first().strip('二手')
            item["series"] = response.xpath(
                '//div[@class="path"]/a[6]/text()').extract_first().strip('二手')
            item["factoryname"] = None
            item["modelname"] = None
            item["brandid"] = None
            item["familyid"] = None
            item["seriesid"] = None
            try:
                item['makeyear'] = \
                    re.findall(r"(\d)款", response.xpath('//*[@class="B_title"]/text()').extract_first())[0]
            except:
                item['makeyear'] = None
            item["registeryear"] = \
                response.xpath(
                    '//input[@id="licensing_month"]/@value').extract_first()
            item["produceyear"] = None
            try:
                item["bodystyle"] = \
                    re.findall(r'单厢|两厢|三厢',
                               response.xpath('//span[contains(text(), "车身结构")]/../text()').extract_first())[0]
            except:
                item["bodystyle"] = None
            item["body"] = response.xpath(
                '//span[contains(text(), "车身结构")]/../text()').extract_first()

            item["level"] = response.xpath(
                '//span[contains(text(), "车型")]/../text()').extract_first().strip("")
            item["fueltype"] = response.xpath('//span[contains(text(), "燃油类型")]/../text()').extract_first()
            item["driverway"] = response.xpath(
                '//span[contains(text(), "驱动方式")]/../text()').extract_first()
            item["output"] = response.xpath(
                "//p[contains(text(),'排量')]/../p[1]/text()").extract_first().split('/')[1]
            item["guideprice"] = None
            # 新车指导价46.30万(含税)
            try:
                item["guidepricetax"] = response.xpath('//p[@class="car_check"]/text()').extract_first().split("：")[
                    1].strip('万').strip(r'\n\t\t')
            except:
                item["guidepricetax"] = None
            try:
                item["doors"] = re.findall(r'(\d)门', response.xpath(
                    '//span[contains(text(), "车身结构")]/../text()').extract_first())[0]
            except:
                item["doors"] = None
            item["emission"] = response.xpath("//p[contains(text(),'排量')]/../p[1]/text()").extract_first().split('/')[0]
            item["gear"] = None
            try:
                item["geartype"] = \
                    response.xpath('//span[contains(text(), "变速箱")]/../text()').extract_first()
            except:
                item["geartype"] = None
            try:
                item["seats"] = \
                    re.findall(r"(\d*)座", response.xpath('//span[contains(text(), "车身结构")]/../text()'
                                                         ).extract_first())[0]
            except:
                item["seats"] = None
            try:
                item["length"] = response.xpath(
                    '//span[contains(text(), "长*宽*高")]/../text()').extract_first().split(
                    "*")[0]
            except:
                item["length"] = None
            try:
                item["width"] = response.xpath(
                    '//span[contains(text(), "长*宽*高")]/../text()').extract_first().split(
                    "*")[1]
            except:
                item["width"] = None
            try:
                item["height"] = response.xpath(
                    '//span[contains(text(), "长*宽*高")]/../text()').extract_first().split(
                    "*")[2]
            except:
                item["height"] = None
            item["gearnumber"] = None
            item["weight"] = None
            item["wheelbase"] = None
            item["generation"] = None
            item["fuelnumber"] = None
            item["lwv"] = None
            item["lwvnumber"] = None
            item["maxnm"] = None
            item["maxpower"] = None
            item["maxps"] = None
            item["frontgauge"] = None
            item["compress"] = None
            item["registerdate"] = response.xpath(
                '//input[@id="licensing_month"]/@value').extract_first()
            item["years"] = None
            item["paytype"] = None
            item["price1"] = response.xpath(
                '//*[@id="moneycar"]/text()').extract_first().split('￥')[1].split('万')[0].replace("\r\n", '').replace(
                "\n", '').replace("\xa0", '').replace("\t", '').replace(
                "\u3000", '')
            item["pricetag"] = None
            item["mileage"] = response.xpath(
                '//p[contains(text(), "行驶公里")]/../p[1]/text()').extract_first().strip('万')[0]
            try:
                item["color"] = re.findall(r"([\u4e00-\u9fa5])色", response.xpath(
                    '//span[contains(text(), "颜色")]/../text()').extract_first())[0] + "色"
            except:
                item["color"] = None
            item["prov"] = response.xpath("//div[@class='path']/a[2]/text()").extract_first().split('二手车')[0]
            item["city"] = response.xpath("//div[@class='path']/a[3]/text()").extract_first().split('二手车')[0]
            item["guarantee"] = None
            item["totalcheck_desc"] = None
            item["totalgrade"] = None
            item["contact_type"] = None
            item["contact_name"] = None
            item["contact_phone"] = None
            item["contact_address"] = None
            item["contact_company"] = None
            item["contact_url"] = None
            item["change_date"] = None
            item["change_times"] = None
            item["insurance1_date"] = response.xpath(
                '//span[contains(text(), "保险情况")]/../text()').extract_first().replace("\r\n", '').replace("\n",
                                                                                                          '').replace(
                "\xa0", '').replace("\t", '').replace(
                "\u3000", '')
            item["insurance2_date"] = None
            item["hascheck"] = None
            item["repairinfo"] = response.xpath(
                '//span[contains(text(), "保养情况")]/../text()').extract_first()
            item["yearchecktime"] = response.xpath(
                '//span[contains(text(), "年审情况")]/../text()').extract_first().replace("\r\n", '').replace("\n",
                                                                                                          '').replace(
                "\xa0", '').replace("\t", '').replace(
                "\u3000", '')
            item["carokcf"] = None
            item["carcard"] = None
            item["carinvoice"] = None
            item["accident_desc"] = None
            item["accident_score"] = None
            item["outer_desc"] = None
            item["outer_score"] = None
            item["inner_desc"] = None
            item["inner_score"] = None
            item["safe_desc"] = None
            item["safe_score"] = None
            item["road_desc"] = None
            item["road_score"] = None
            item["lastposttime"] = response.xpath('//div[@class="title_infoL"]/span/i/text()').extract_first()
            item["newcartitle"] = None
            item["newcarurl"] = None
            item["img_url"] = response.xpath('//*[@id="focusBigImg_0"]/img/@src').extract_first()
            item["first_owner"] = None
            item["carno"] = None
            item["carnotype"] = None
            item["carddate"] = None
            item["changecolor"] = None
            item["outcolor"] = None
            item["innercolor"] = None
            item["desc"] = response.xpath('//div[@class="describe"]/text()').extract_first()
            item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + str(item["post_time"])
            print(item)
        except:
            log_dict["logType"] = 'ERROR'
            log_dict["logMessage"] = response.url
            logging.log(msg=json.dumps(log_dict, ensure_ascii=False), level=logging.INFO)
        else:
            log_dict["logType"] = 'INFO'
            log_dict["logMessage"] = "successful"
            log_dict["logObject"] = {
                "field": {
                    "carsource": website,
                    "grab_time": item["grab_time"],
                    "price1": item["price1"],
                    "mileage": item["mileage"],
                    "post_time": item["post_time"],
                    "sold_date": item["sold_date"],
                    "city": item["city"],
                    "registerdate": item["registerdate"]
                },
                "info": {
                    "dataBaseType": "mysql",
                    "dataBaseName": settings["MYSQLDB_DB"],
                    "tableName": website + '_online',
                    "saveStatus": ""
                }
            }
            returndf = self.bf.isContains(item["statusplus"])
            # 1数据存在，0数据不存在
            if returndf == 1:
                log_dict["logObject"]["info"]["saveStatus"] = "true"
            else:
                log_dict["logObject"]["info"]["saveStatus"] = "false"
            logging.log(msg=json.dumps(log_dict, ensure_ascii=False), level=logging.INFO)
            yield item
            # print(item)
