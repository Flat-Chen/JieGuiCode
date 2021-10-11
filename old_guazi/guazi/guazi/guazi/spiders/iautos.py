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

website ='iautos'

class CarSpider(scrapy.Spider):
    name = website
    allowed_domains = ["iautos.cn"]
    start_urls = [
        "https://so.iautos.cn"
    ]


    def __init__(self, **kwargs):

        super(CarSpider, self).__init__(**kwargs)
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0

    def parse(self, response):
        for href in response.xpath('//div[@class="city-li"]/dl/dd/a/@href').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.list_parse)

    def list_parse(self, response):
        node_list = response.xpath('//ul[contains(@class, "car-box-list")]/li')
        for node in node_list:
            url = node.xpath("a/@href").extract_first()
            yield scrapy.Request(url, callback= self.parse_car)

        # next page
        next_page = response.xpath(u'//div[@class="pages-box"]/a[contains(text(),"下一页")]/@href')
        if next_page:
            urlbase=str(next_page.extract_first())
            urlbase2="http://so.iautos.cn"
            url = urlbase2+urlbase
            yield scrapy.Request(url, self.list_parse)


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
        if response.status == 200:
            # count
            self.counts += 1
            logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)

            # key and status (sold or sale, price,time)
            status = response.xpath('//div[@class="sold-out"]')
            status = "sold" if status else "sale"

            price = response.xpath('//strong[@class="z"]/text()')
            price = str(price.extract_first()) if price else "zero"

            datetime = "zero"

            city = response.xpath('//div[@class="bread-crumbs de-twelve-font"]/a[2]/text()').extract_first()
            city = city.replace('二手车', '')

            brand = response.xpath('//div[@class="bread-crumbs de-twelve-font"]/a[3]/text()').extract_first()
            brand = brand.replace('二手车', '')
            brand = brand.replace(city, '')

            series = response.xpath('//div[@class="bread-crumbs de-twelve-font"]/a[4]/text()').extract_first()
            series = series.replace('二手', '')
            series = series.replace(city, '')

            # item loader


            self.counts += 1
            logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)
            try:
                item = GuaziItem()
                item["carid"] = re.findall(r'\d+', response.url)[0]
                item["car_source"] = "iautos"
                item["usage"] = response.xpath('//*[@id="ycyt"]/@value').extract_first()
                item["grab_time"] =grap_time
                item["update_time"] = None
                item["post_time"] =re.findall(r'(\d{8}).*', response.xpath('//div[@class="bigImage"]//img/@src').extract_first())[0]
                item["sold_date"] = None
                item["pagetime"] = None
                item["parsetime"] = grap_time
                item["shortdesc"] = response.xpath('//div[@class="info-upper"]/h1/span/text()').extract_first()
                item["pagetitle"] = response.xpath("//head/title/text()").extract_first().strip("")
                item["url"] = response.url
                item["newcarid"] = None
                item["status"] = status
                item["brand"] =  brand
                item["series"] =series
                item["factoryname"] = None
                item["modelname"] = None
                item["brandid"] = None
                item["familyid"] = None
                item["seriesid"] = None
                item['makeyear'] = re.findall(r'(\d+)款', response.xpath('//div[@class="info-upper"]/h1/span/text()').extract_first())[0]
                item["registeryear"] = re.findall(r'\d+', response.xpath('//ul[@class="others clean"]/li/p/text()').extract_first())[0]
                item["produceyear"] = None
                item["body"] = None
                item["bodystyle"] = response.xpath('//div[@class="table-wrap clean"]/table[@class="table-r"]/tbody/tr[5]/td/text()').extract_first()

                item["level"] = response.xpath('//div[@class="table-wrap clean"]/table[@class="table-l"]/tbody/tr[3]/td/text()').extract_first()
                item["fueltype"] = response.xpath(
                    '//div[@class="table-wrap clean"]/table[@class="table-r"]/tbody/tr[7]/td/text()').extract_first()
                item["driverway"] = response.xpath(
                    '//div[@class="table-wrap clean"]/table[@class="table-l"]/tbody/tr[6]/td/text()').extract_first()
                item["output"] = response.xpath('//*[contains(text(), "排量")]/../p/text()').extract_first()
                item["guideprice"] = re.findall(r'\d+\.\d+', response.xpath('//div[@class="loan-other"]/p[1]/text()').extract_first())[0]
                # 新车指导价46.30万(含税)
                item["guidepricetax"] = re.findall(r'\d+\.\d+', response.xpath('//span[@class="left-normal"]/text()').extract_first())[0]
                item["doors"] = None
                item["emission"] = response.xpath('//*[contains(text(), "排放")]/../p/text()').extract_first()
                item["gear"] = None
                item["geartype"] = response.xpath('//th[contains(text(), "\u53d8\u901f\u7bb1")]/../td/text()').extract_first()
                item["seats"] = None
                item["length"] =  re.findall(r'\d+', response.xpath('//div[@class="table-wrap clean"]/table[@class="table-r"]/tbody/tr[3]/td/text()').extract_first())[0]
                item["width"] = re.findall(r'\*(.*)\*', response.xpath('//div[@class="table-wrap clean"]/table[@class="table-r"]/tbody/tr[3]/td/text()').extract_first())[0]
                item["height"] =  re.findall(r'\*(\d+$)', response.xpath('//div[@class="table-wrap clean"]/table[@class="table-r"]/tbody/tr[3]/td/text()').extract_first())[0]
                item["gearnumber"] =None
                item["weight"] = None
                item["wheelbase"] =  re.findall(r'\d+', response.xpath('//div[@class="table-wrap clean"]/table[@class="table-r"]/tbody/tr[4]/td/text()').extract_first())[0]
                item["generation"] = None
                item["fuelnumber"] = None
                item["lwv"] =None
                item["lwvnumber"] =None
                try:
                    item["maxnm"] = response.xpath("//th[contains(text(),'扭矩')]/../td/text()").extract_first().strip('N-m')
                except:
                    item["maxnm"] =None
                item["maxpower"] =  response.xpath("//th[contains(text(),'发动机功率')]/../td/text()").extract_first().split('(')[1].strip(')')
                item["maxps"] = response.xpath("//th[contains(text(),'发动机功率')]/../td/text()").extract_first().split('马力')[0]
                item["frontgauge"] = None
                item["compress"] = None

                # **************
                item['registerdate'] = '20' + response.xpath('//*[contains(text(), "上牌时间")]/../p/text()').extract_first()

                item["years"] = None
                item["paytype"] = None
                item["price1"] =response.xpath('//a[@href="{}"]/p[3]/span/b/text()'.format(response.url)).extract_first()
                item["pricetag"] = None
                item["mileage"] =response.xpath('//a[@href="{}"]/p[2]/span[2]/text()'.format(response.url)).extract_first()
                item["color"] = response.xpath(
                    '//*[@id="myColor"]/@value').extract_first()
                item["city"] = city
                item["prov"] =  None

                item["guarantee"] = None
                item["totalcheck_desc"] = None
                item["totalgrade"] = None
                item["contact_type"] = None
                item["contact_name"] = None
                item["contact_phone"] = response.xpath('//div[@class="num de-btn-ico single"]/span/text()').extract_first()
                item["contact_address"] = response.xpath('//div[@class="sub-dealer"]/span/a/text()').extract_first()
                item["contact_company"] = response.xpath('//span[contains(text(), "认证经销商")]/../span[2]/a/text()').extract_first()
                item["contact_url"] = None
                item["change_date"] = None
                try:
                    item["change_times"] = re.findall(r'\d+', response.xpath('//*[contains(text(), "过户")]/text()').extract_first())[0]
                except:

                    item["change_times"] = None

                item["insurance1_date"] = response.xpath('//dd[contains(text(), "保险有限期")]/../dt/text()').extract_first()
                item["insurance2_date"] = None
                item["hascheck"] = None
                item["repairinfo"] = None
                item["yearchecktime"] = None
                item["carokcf"] = None
                item["carcard"] = None
                item["carinvoice"] = None
                item["accident_desc"] = None
                item["accident_score"] = None
                item["outer_desc"] = None
                item["outer_score"] = None
                item["inner_desc"] = None
                item["inner_score"] =None
                item["safe_desc"] = None
                item["safe_score"] = None
                item["road_desc"] = None
                item["road_score"] = None
                item["lastposttime"] = None
                item["newcartitle"] = None
                item["newcarurl"] = None
                item["img_url"] = response.xpath('//ul[@class="car-photo-list"]/li/img/@data-original').extract_first()
                item["first_owner"] = None

                item["carno"] = response.xpath('//div[@class="MD-widget-tradedetail-template7-action_title-flinfo"]//li[11]/span[2]/text()').extract_first()
                item["carnotype"] = None
                item["carddate"] = None
                item["changecolor"] = None
                item["outcolor"] = None
                item["innercolor"] = None
                item["desc"] = '.'.join(response.xpath("//p[@id='see-all']/text()").extract())
                item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])
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





