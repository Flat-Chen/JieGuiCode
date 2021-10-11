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


website ='chewang'

class CarSpider(scrapy.Spider):
    name = website
    allowed_domains = ["carking001.com"]
    start_urls = [
        "http://www.carking001.com/ershouche"
    ]



    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0
    def parse(self, response):
        for href in response.xpath('//ul[@class="carList"]/li'):
            urlbase = href.xpath("a/@href").extract_first()
            url = response.urljoin(urlbase)
            yield scrapy.Request(url, callback= self.parse_car)

        next_page = response.xpath('//a[contains(text(),"下一页")]/@href')
        if next_page:
            url_next = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url_next, self.parse)

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
        if response.status==200 and len(response.xpath('//html').extract_first())>=20000:
            self.counts += 1
            logging.log(msg="download  " + str(self.counts) + "  items", level=logging.INFO)

            # key and status (sold or sale, price,time)
            status = response.xpath('//a[@class="btn_3"]')
            status = "sold" if status else "sale"

            price = response.xpath('//div[@class="car_details_con_2017"]/span/strong/text()').re('\d+.\d+')[0] \
                if response.xpath('//div[@class="car_details_con_2017"]/span/strong/text()').re('\d+.\d+') else "zero"

            datetime = "zero"

            # extra
            info = response.xpath(u'//p[contains(text(), "新车购入价")]/text()').extract()
            if info:
                guidepricetax = re.findall(r'\d+\.\d+', info[0])[0]
                tax = re.findall(u'含(\d+)', info[0])[0]
                guideprice = str(float(guidepricetax) - float(tax)/10000)
            else:
                guideprice =  "zero"
            try:
                item = GuaziItem()
                item["carid"] = response.xpath('//span[@class="fr"]//em/text()').extract_first()
                item["car_source"] = "chewang"
                item["usage"] =None
                item["grab_time"] = grap_time
                item["update_time"] = None
                item["post_time"] = None
                item["sold_date"] = None
                item["pagetime"] = grap_time
                item["parsetime"] = grap_time
                item["shortdesc"] = response.xpath('//div[@class="caBar"]/h3/text()').extract_first()
                item["pagetitle"] = response.xpath("//head/title/text()").extract_first().strip("")
                item["url"] = response.url
                item["newcarid"] = None
                item["status"] = status
                item["brand"] = re.findall(r'([\S]+)\s',response.xpath('//div[@class="car_details_tit_2017"]/h3/text()').extract_first())[0]
                item["series"] = re.findall(r'\s([\S]+)',response.xpath('//div[@class="car_details_tit_2017"]/h3/text()').extract_first())[0]

                item["factoryname"] =response.xpath("//span[contains(text(),'厂商')]/../../td[4]/span/text()").extract_first()
                item["modelname"] = None
                item["brandid"] = None
                item["familyid"] = None
                item["seriesid"] = None
                item['makeyear'] = re.findall(r'\d{4}',response.xpath('//div[@class="tzPdList1 clearfix"]//tr[2]/td[4]/span/text()').extract_first())[0]

                item["registeryear"] = re.findall(r'\d{4}',response.xpath('//div[@class="tx_1 fl"]/p[2]/text()').extract_first())[0]

                item["produceyear"] = None
                item["body"] = response.xpath('//div[@class="tzPdList1 clearfix"]/table/tr[3]/td[2]/span/text()').extract_first()
                item["bodystyle"] =  re.findall(r'\u5ea7(.*)',response.xpath('//div[@class="tzPdList1 clearfix"]/table/tr[3]/td[2]/span/text()').extract_first())[0]

                item["level"] = response.xpath('//span[contains(text(), "\u7ea7\u522b")]/../../td[2]/span/text()').extract_first()
                item["fueltype"] = response.xpath(
                    '//span[contains(text(), "\u71c3\u6599\u5f62\u5f0f")]/../../td[4]/span/text()').extract_first()

                item["driverway"] = response.xpath(
                    '//span[contains(text(), "\u9a71\u52a8\u65b9\u5f0f")]/../../td[4]/span/text()').extract_first()
                item["output"] =  re.findall(r'(\d.\d)L',response.xpath('//div[@class="caBar1_t2"]/p/span[1]/text()').extract_first())[0]

                item["guideprice"] =  guideprice
                # 新车指导价46.30万(含税)
                item["guidepricetax"] =re.findall(r'\d+.\d+',response.xpath('//div[@class="car_details_con_2017"]/div/p/text()').extract_first())[0]

                item["doors"] = response.xpath(
                    "//span[contains(text(),'车门')]/../../td[4]/span/text()").extract_first()
                item["emission"] = response.xpath("//p[contains(text(),'排放标准')]/../h3/text()").extract_first()
                item["gear"] = response.xpath('//span[contains(text(), "变速箱类型")]/text()').extract_first()
                item["geartype"] =re.findall(r'变速箱：(.*)',response.xpath('//div[@class="caBar1_t2"]//span[2]/text()').extract_first())[0]

                item["seats"] = response.xpath("//span[contains(text(),'座位')]/../../td[2]/span/text()").extract_first()
                item["length"] = response.xpath("//span[contains(text(),'高(')]/../../td[4]/span/text()").extract_first().split('×')[0]
                item["width"] =response.xpath("//span[contains(text(),'高(')]/../../td[4]/span/text()").extract_first().split('×')[1]
                item["height"] =response.xpath("//span[contains(text(),'高(')]/../../td[4]/span/text()").extract_first().split('×')[2]

                item["gearnumber"] = response.xpath(
                    '//span[text()="挡位个数"]/../../td[4]/span/text()').extract_first()

                item["weight"] = response.xpath(
                    '//span[contains(text(), "\u6ee1\u8f7d\u8d28\u91cf")]/../../td[4]/span/text()').extract_first()
                item["wheelbase"] = response.xpath(
                    "//span[contains(text(),'轴距')]/../../td[2]/span/text()").extract_first()
                item["generation"] = None
                item["fuelnumber"] = None
                item["lwv"] =response.xpath(
                    "//span[contains(text(),'汽缸排列')]/../../td[2]/span/text()").extract_first()
                item["lwvnumber"] = response.xpath(
                   "//span[contains(text(),'汽缸排列')]/../../td[4]/span/text()").extract_first()
                item["maxnm"] = response.xpath(
                    "//span[contains(text(),'扭矩')]/../../td[2]/span/text()").extract_first()
                item["maxpower"] = response.xpath(
                   "//span[contains(text(),'功率')]/../../td[2]/span/text()").extract_first()
                item["maxps"] = None
                item["frontgauge"] = None
                item["compress"] = None
                item["registerdate"] = response.xpath('//div[@class="tx_1 fl"]/p[2]/text()').extract_first()
                item["years"] = None
                item["paytype"] = None
                item["price1"] = re.findall(r'\d+.\d+',response.xpath('//div[@class="car_details_con_2017"]/span').extract_first())[0]
                item["pricetag"] = None
                item["mileage"] = response.xpath("//p[contains(text(),'行驶')]/../h3/text()").extract_first().strip("万公里")
                item["color"] = response.xpath(
                    "//span[contains(text(),'车身颜色')]/text()").extract_first().split('：')[1]
                item["city"] = re.findall(r'-(\S+)',response.xpath('//div[@class="fl l"]/h3/text()').extract_first())[0]
                item["prov"] = None
                item["guarantee"] = None
                item["totalcheck_desc"] = None
                item["totalgrade"] = None
                item["contact_type"] = None
                item["contact_name"] = None
                item["contact_phone"] = None
                item["contact_address"] =None
                item["contact_company"] = None
                item["contact_url"] = None
                item["change_date"] = None
                item["change_times"] = None
                item["insurance1_date"] = None
                item["insurance2_date"] = None
                item["hascheck"] = None
                item["repairinfo"] = None
                item["yearchecktime"] = response.xpath('//div[@class="tx_2 fl"]/p[2]/text()').extract_first()
                item["carokcf"] = None
                item["carcard"] = None
                item["carinvoice"] = None
                item["accident_desc"] = response.xpath('//*[@class="daBar"]/div[2]/div[1]/span[2]/text()').extract_first()
                item["accident_score"] = None
                item["outer_desc"] = response.xpath('//*[@class="daBar"]/div[2]/div[2]/div[2]/div[1]/span[2]/text()').extract_first()
                item["outer_score"] = None
                item["inner_desc"] = None
                item["inner_score"] = response.xpath('//ul[@class="grade_ul"]/li[2]/div[1]/text()[2]').extract_first()
                item["safe_desc"] = None
                item["safe_score"] = response.xpath('//span[text()="电器设备检测"]/../span[2]/text()').extract_first()
                item["road_desc"] = None
                item["road_score"] = response.xpath('//*[@class="daBar"]/div[2]/div[2]/div[5]/div[1]/span[2]/text()').extract_first()
                item["lastposttime"] = None
                item["newcartitle"] = None
                item["newcarurl"] = None
                item["img_url"] = response.xpath('//div[@class="bigImg"]/img/@src').extract_first()
                item["first_owner"] = response.xpath(
                    '//span[contains(text(), "吸气方式")]/../following-sibling::td[1]/span/text()').extract_first()
                item["carno"] = response.xpath('//div[@class="fl"][5]/h3/text()').extract_first()
                item["carnotype"] = None
                item["carddate"] = None
                item["changecolor"] = None
                item["outcolor"] =re.findall(r'\uff1a(\S+)',response.xpath('//div[@class="caBar1_t2"]/p/span[3]/text()').extract_first())[0]

                item["innercolor"] =re.findall(r'\uff1a(\S+)',response.xpath('//div[@class="caBar1_t2"]/p/span[4]/text()').extract_first())[0]

                item["desc"] =''.join( response.xpath('//div[@class="caBar1_t4"]/p/text()').extract())
                item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])+str(1)
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
