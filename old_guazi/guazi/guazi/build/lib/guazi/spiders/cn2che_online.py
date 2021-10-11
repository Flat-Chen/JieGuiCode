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
website ='cn2che'

class CarSpider(scrapy.Spider):
    name = website
    allowed_domains = ["cn2che.com"]
    start_urls = [
        "http://www.cn2che.com/serial.html",
    ]
    custom_settings = {
        "REDIRECT_ENABLED": True,
        "DOWNLOADER_MIDDLEWARES" : {
        "guazi.proxy.ProxyMiddleware": 530
    }
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0

    def parse(self, response):
        for href in response.xpath('//div[@class="msglist12"]/dl/dd/a[contains(text(),"二手车")]/@href'):
            url = response.urljoin(href.extract())
            print(url)
            yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):
        for href in response.xpath('//ul[@class="carList2"]/li'):
            urlbase = href.xpath("./a/@href").extract_first()
            url = response.urljoin(urlbase)
            yield scrapy.Request(url, callback=self.parse_car)

            next_page = response.xpath('//a[contains(text(),"下一页")]/@href')
            if next_page:
                url = response.urljoin(next_page.extract_first())
                yield scrapy.Request(url, self.parse_list)

    def parse_car(self, response):
        grap_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
        self.counts += 1
        logging.log(msg="download  " + str(self.counts) + "   items",
                    level=logging.INFO)

        status = response.xpath('//li[@id="car_state_text"]/@val')
        if status:
            if int(status.extract_first()) == 1:
                status = "sale"
            else:
                status = "sold"
        else:
            status = "sale"

        price = response.xpath('//strong[@id="price"]/text()')
        price = ".".join(price.re('\d+')) if price else "zero"

        pagetime = response.xpath('//li[@class="sendtime"]/text()')
        pagetime = "-".join(pagetime.re('\d+')) if pagetime else "zero"
        try:
            item = GuaziItem()
            item["carid"] = re.findall(r'(\d+).html', response.url)[0]
            item["car_source"] = "cn2che"
            item["usage"] = response.xpath('//div[@class="Detailed_list"]/div[1]/table/tr[1]/td[2]/text()').extract_first().strip()
            item["grab_time"] = grap_time
            item["update_time"] = re.findall(r'\d+\/\d+\/\d+', response.xpath('//li[contains(text(), "更新时间")]/text()').extract_first())[0]
            item["post_time"] =re.findall(r'\d+\/\d+\/\d+', response.xpath('//li[contains(text(), "更新时间")]/text()').extract_first())[0]
            item["sold_date"] = None
            item["pagetime"] = None
            item["parsetime"] = grap_time
            item["shortdesc"] = response.xpath('//div[@class="datum_right"]/h2/text()').extract_first()
            item["pagetitle"] = response.xpath('head/title/text()').extract_first().strip("")
            item["url"] = response.url
            item["newcarid"] = None
            item["status"] = status
            item["brand"] = re.findall(r'车辆品牌：(.*)', response.xpath('//li[contains(text(), "车辆品牌")]/text()').extract_first())[0]

            item["series"] = re.findall(r'车辆系列：(.*)', response.xpath('//li[contains(text(), "车辆系列")]/text()').extract_first())[0]

            item["factoryname"] =None
            item["modelname"] = None
            item["brandid"] = None
            item["familyid"] = None
            item["seriesid"] = None
            item['makeyear'] =  re.findall(r'(\d{4})[年款]', response.xpath('//div[@class="Detailed"]/h1/text()').extract_first())[0]

            item["registeryear"] = re.findall(r'\d{4}', response.xpath('//li[contains(text(), "上牌时间")]/text()').extract_first())[0]

            item["produceyear"] = None
            item["body"] = None
            item["bodystyle"] =None

            item["level"] = None
            item["fueltype"] =None
            item["driverway"] = None
            item["output"] =  response.xpath("//td[contains(text(),'排量')]/following-sibling::td[1]/text()").extract_first().split('mL')[0].strip()

            item["guideprice"] =None
            # 新车指导价46.30万(含税)
            item["guidepricetax"] = None
            item["doors"] =None
            item["emission"] = response.xpath('//div[@class="Detailed_list"]/div[1]/table/tr[3]/td[4]/text()').extract_first().strip()
            item["gear"] = response.xpath('//div[@class="Detailed_list"]/div[1]/table//tr[2]/td[2]/text()').extract_first().strip()
            item["geartype"] =None

            item["seats"] = None
            item["length"] = None
            item["width"] =None
            item["gearnumber"] = None
            item["weight"] = None
            item["wheelbase"] = None
            item["generation"] = None
            item["fuelnumber"] = None
            item["lwv"] =None
            item["lwvnumber"] = None
            item["maxnm"] = None
            item["maxpower"] = None
            item["maxps"] = None
            item["frontgauge"] =None
            item["compress"] = None
            item["registerdate"] = re.findall(r'\d+\-\d+', response.xpath('//li[contains(text(), "上牌时间")]/text()').extract_first())[0]

            item["years"] = None
            item["paytype"] = None
            item["price1"] = re.findall(r'\d+\.*\d*', response.xpath('//div[@class="Detailed"]/dl/dd/ol/li[1]/strong/text()').extract_first())[0]

            item["pricetag"] = None
            item["mileage"] = re.findall(r'\d+', response.xpath('//div[@class="Detailed"]/dl/dd/ol/li[1]/strong/text()').extract_first())[0]

            item["color"] = response.xpath(
                '//div[@class="Detailed_list"]/div[1]/table/tr[1]/td[6]/text()').extract_first().strip()
            item["city"] =  re.findall(r'.{5}(.*)-.*', response.xpath('//*[@id="jydq"]/text()').extract_first())[0]

            item["prov"] =  re.findall(r'.{5}.*-(.*)', response.xpath('//*[@id="jydq"]/text()').extract_first())[0]

            item["guarantee"] = None
            item["totalcheck_desc"] = None
            item["totalgrade"] = response.xpath(
                '//div[@class="Detailed_list"]/div[1]/table//tr[2]/td[4]/text()').extract_first().strip()
            item["contact_type"] = None
            item["contact_name"] =response.xpath('//*[@id="linkman"]/text()').extract_first()
            item["contact_phone"] = response.xpath('//*[@id="phone"]/text()').extract_first()
            item["contact_address"] = response.xpath('//*[@id="address"]/text()').extract_first()
            item["contact_company"] = None
            item["contact_url"] = None
            item["change_date"] = None
            item["change_times"] = None
            item["insurance1_date"] = response.xpath('//div[@class="Detailed_list"]/div[1]/table/tr[3]/td[2]/text()').extract_first().strip()
            item["insurance2_date"] = None
            item["hascheck"] = None
            item["repairinfo"] =None
            item["yearchecktime"] = response.xpath('//div[@class="Detailed_list"]/div[1]/table//tr[3]/td[6]/text()').extract_first().strip()
            item["carokcf"] = None
            item["carcard"] = None
            item["carinvoice"] = None
            item["accident_desc"] = None
            item["accident_score"] = None
            item["outer_desc"] = None
            item["outer_score"] =  None
            item["inner_desc"] = None
            item["inner_score"] =  None
            item["safe_desc"] = None
            item["safe_score"] = None
            item["road_desc"] = None
            item["road_score"] = None
            item["lastposttime"] = None
            item["newcartitle"] = None
            item["newcarurl"] = None
            item["img_url"] = response.xpath('//dt[@class="chepic"]/ul/li[2]/a/img/@src').extract_first()
            item["first_owner"] = None
            item["carno"] = None
            item["carnotype"] = response.xpath('//table//tr[1]/td[4]/text()').extract_first().strip()
            item["carddate"] = None
            item["changecolor"] = None
            item["outcolor"] = None
            item["innercolor"] = None
            item["desc"] =''.join( response.xpath('//span[@class="describe"]/text()').extract())
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
            # print(item)