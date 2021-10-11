#-*- coding: UTF-8 -*-

import json
import re
import time
import redis
import scrapy
import logging
from scrapy.conf import settings
from ..items import GuaziItem
from ..redis_bloom import BloomFilter
website ='che273'

class CarSpider(scrapy.Spider):
    name = website
    start_urls = [
        "http://www.273.cn/car/city.html"
    ]



    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0

    def parse(self, response):
        for href in response.xpath('//div[@id="citychange"]/ul[2]/li/dd/span/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, self.parse_list)

    def parse_list(self, response):
        for href in response.xpath('//div[@class="mod-carlist-list"]//div[@data-jslink]'):
            urlbase = href.xpath('@data-jslink').extract_first()
            url = response.urljoin(urlbase)
            yield scrapy.Request(url, callback=self.parse_car)

        next_page = response.xpath('//*[@id="js_page_next"]/@href')
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, self.parse_list)

    def parse_car(self, response):
        self.counts += 1
        logging.log(msg="download   " + str(self.counts) + "   items", level=logging.INFO)

        # key and status (sold or sale, price,time)
        status = response.xpath('//*[@class="tips_shelf"]')
        status = "sold" if status else "sale"
        if status == "sold":
            price = "zero"
        else:
            price = response.xpath('//strong[@class="main_price"]/text()')
            price = price.extract_first() if price else "zero"

        datetime = response.xpath('//div[@class="time"]/span/text()')
        datetime = datetime.extract_first() if datetime else "zero"

        guideprice = response.xpath('//p[contains(text(), "出厂报价")]/strong[1]/text()')
        if guideprice:
            guideprice = guideprice.extract_first()

            tax = response.xpath('//p[contains(text(), "出厂报价")]/strong[2]/text()')
            p1 = re.findall(r'\d+\.\d+', tax.extract_first())[0]
            p2 = re.findall(r'\d+\.\d+', guideprice)[0]
            guidepricetax = str(float(p1) + float(p2)) + u'万'
        else:
            guideprice = '-'
            guidepricetax = '-'
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
        # item loader
        try:
            self.counts += 1
            logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)
            item = GuaziItem()
            item["carid"] = re.findall(r'(\d+).html', response.url)[0]
            item["car_source"] = "che273"
            item["usage"] = response.xpath('//div[@class="sub_content"]/div[@class="font_para"]/ul/li[8]/text()').extract_first()
            item["grab_time"] = grap_time
            item["update_time"] = response.xpath('//div[@class="time"]/span/text()').extract_first()

            item["post_time"] = response.xpath('//div[@class="time"]/span/text()').extract_first()
            item["sold_date"] = None
            item["pagetime"] =  datetime
            item["parsetime"] = grap_time
            item["shortdesc"] = response.xpath('//div[@id="detail_main_info"]/h1/b/text()').extract_first()
            item["pagetitle"] = response.xpath("//title/text()").extract_first().strip("")
            item["url"] = response.url
            item["newcarid"] = None
            item["status"] = status
            item["brand"] = re.findall(r'\u4e8c\u624b(.*)',response.xpath('//div[@class="row clearfix"]/div/a[4]/text()').extract_first())[0]
            item["series"] = re.findall(r'\u4e8c\u624b(.*)',response.xpath('//div[@class="row clearfix"]/div/a[5]/text()').extract_first())[0]

            item["factoryname"] = None
            item["modelname"] = None
            item["brandid"] = None
            item["familyid"] = None
            item["seriesid"] = None
            item['makeyear'] =re.findall(r'(\d{4})\u6b3e',response.xpath('//div[@id="detail_main_info"]/h1/b/text()').extract_first())[0]

            item["registeryear"] = re.findall(r'\d{4}',response.xpath('//div[@class="para para_s"]/ul/li[2]/dl/dd/strong/text()').extract_first())[0]

            item["produceyear"] =None
            item["body"] = None
            item["bodystyle"] = response.xpath('//div[@class="basic_info js_tab_target"]/div[@class="sub_content"]/div/ul/li[7]/text()').extract_first()

            item["level"] = re.findall(r'\u4e8c\u624b(.*)',response.xpath('//div[@class="row clearfix"]/div/a[3]/text()').extract_first())[0]

            item["fueltype"] =None
            item["driverway"] = None
            item["output"] = response.xpath('//div[@class="basic_info js_tab_target"]/div[@class="sub_content"]/div/ul/li[5]/text()').extract_first()
            item["guideprice"] =  guideprice
            # 新车指导价46.30万(含税)
            item["guidepricetax"] =  guidepricetax
            item["doors"] =None
            item["emission"] = response.xpath('//div[@class="para para_s"]/ul/li[3]/dl/dd/strong/text()').extract_first()
            item["gear"] = None
            item["geartype"] = response.xpath('//div[@class="basic_info js_tab_target"]/div[@class="sub_content"]/div/ul/li[4]/text()').extract_first()
            item["seats"] =None
            item["length"] = None
            item["width"] =  None
            item["height"] =  None
            item["gearnumber"] =  None
            item["weight"] =  None
            item["wheelbase"] =  None
            item["generation"] = None
            item["fuelnumber"] =  None
            item["lwv"] =  None
            item["lwvnumber"] =  None
            item["maxnm"] = None
            item["maxpower"] =  None
            item["maxps"] =  None
            item["frontgauge"] = None
            item["compress"] = None
            item["registerdate"] = response.xpath('//div[@class="para para_s"]/ul/li[2]/dl/dd/strong/text()').extract_first()
            item["years"] = None
            item["paytype"] = None
            item["price1"] = response.xpath('//div[@class="price_area"]/p/strong/text()').extract_first()
            item["pricetag"] = None
            item["mileage"] = response.xpath('//div[@class="para para_s"]/ul/li[1]/dl/dd/strong/text()').extract_first()
            item["color"] = response.xpath(
                '//div[@class="sub_content"]/div[@class="font_para"]/ul/li[6]/text()').extract_first()
            item["city"] = re.findall(r'\/(.*)',response.xpath('//div[@class="sub_content"]/div[@class="font_para"]/ul/li[1]/text()').extract_first())[0]

            item["prov"] =  re.findall(r'(.*)\/',response.xpath('//div[@class="sub_content"]/div[@class="font_para"]/ul/li[1]/text()').extract_first())[0]

            item["guarantee"] = None
            item["totalcheck_desc"] = None
            item["totalgrade"] = None
            item["contact_type"] = None
            item["contact_name"] = None
            try:
                item["contact_phone"] = re.findall(r'\d+\-\d+\-\d+',response.xpath('//div[@class="sub_content"]/p/text()').extract_first())[0]
            except:
                item["contact_phone"] =None

            item["contact_address"] = None
            item["contact_company"] = None
            item["contact_url"] = None
            item["change_date"] = None
            item["change_times"] = None
            item["insurance1_date"] = response.xpath('//div[@class="basic_info js_tab_target"]/div[@class="sub_content"]/div/ul/li[11]/text()').extract_first()
            item["insurance2_date"] = response.xpath('//div[@class="basic_info js_tab_target"]/div[@class="sub_content"]/div/ul/li[12]/text()').extract_first()
            item["hascheck"] = None
            item["repairinfo"] = response.xpath(
                '//div[@class="basic_info js_tab_target"]/div[@class="sub_content"]/div/ul/li[9]/text()').extract_first()
            item["yearchecktime"] = response.xpath('//div[@class="font_para"]/ul/li[10]/text()').extract_first()
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
            item["lastposttime"] = None
            item["newcartitle"] = None
            item["newcarurl"] = None
            item["img_url"] = response.xpath('//div[@class="car_photo"]/ul/li/img/@src').extract_first()
            item["first_owner"] = re.findall(r'\d+\.\d+(.*?) .*',response.xpath('//div[@id="detail_main_info"]/h1/b/text()').extract_first())[0]

            item["carno"] = response.xpath('//dd[contains(text(), "上牌地")]/../dt/text()').extract_first()
            item["carnotype"] = None
            item["carddate"] = None
            item["changecolor"] = None
            item["outcolor"] = None
            item["innercolor"] = None
            item["desc"] =''.join( response.xpath('//div[@class="sub_content"]/p/text()').extract())
            item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])
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

            print(item)
