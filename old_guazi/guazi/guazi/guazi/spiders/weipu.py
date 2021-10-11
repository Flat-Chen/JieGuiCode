# -*- coding: UTF-8 -*-
import json
import re
import time
import redis
import scrapy
import logging
from scrapy.conf import settings
from ..items import GuaziItem
from ..redis_bloom import BloomFilter
website = 'weipu'


class CarSpider(scrapy.Spider):
    name = website
    start_urls = 'http://zcp.chevip.com/portal/api/auction_list.htm'
    headers = {'Referer': 'https://www.guazi.com/www/',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    index = True
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,

    }

    def __init__(self, **kwargs):
        self.bf = BloomFilter(key='b1f_' + website)
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0

    def start_requests(self):
        for i in range(100):
            if self.index:
                data = {
                    "user_id": "",
                    "page_size": "12",
                    "order_by": "",
                    "is_desc": "0",
                    "cur_page": str(i + 1),
                    "brand": "",
                    "series": "",
                    "model": "",
                    "bprice": "",
                    "eprice": "",
                    "bmileage": "",
                    "emileage": "",
                    "criterion": "",
                    "bget_license_date": "",
                    "eget_license_date": "",
                    "cartype": "",
                    "has_bid": "",
                    "city_license": "",
                    "city": "",
                    "city_id": "",
                    "bend_time": "",
                    "is_local": "",
                    "eend_time": "",
                    "price": "",
                    "mileage": "",
                    "search_text": "",
                }
                yield scrapy.FormRequest(url=self.start_urls, formdata=data, dont_filter=True, headers=self.headers)
            else:
                return

    def parse(self, response):
        car_list = json.loads(response.text)["list"]
        if car_list == []:
            self.index = False
        else:
            for car in car_list:
                url = car["detail_path"]
                brand = car["brand"]
                city = car["city_name"]
                # end_time
                sold_date = car["end_time"]
                prov = car["licenseCity"]
                shortdesc = car["vehicle_name"]
                series = car["series"]
                post_time = car["start_time"]
                carid = car["auction_id"]
                meta = {
                    "carid": carid,
                    "url": url
                    , "brand": brand,
                    "city": city,
                    "sold_date": sold_date,
                    "prov": prov,
                    "series": series,
                    "shortdesc": shortdesc,
                    "post_time": post_time
                }
                yield scrapy.Request(url=url, callback=self.parse_car, meta=meta, dont_filter=True)

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
        try:
            self.counts += 1
            logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)
            item = GuaziItem()
            item["carid"] = response.meta["carid"]
            item["car_source"] = "weipu"
            item["usage"] = response.xpath("//li[contains(text(),'使用性质')]/i/text()").extract_first()
            item["grab_time"] = grap_time
            item["update_time"] = None
            item["post_time"] = response.meta["post_time"]
            item["sold_date"] = response.meta["sold_date"]
            item["pagetime"] = None
            item["parsetime"] = grap_time
            item["shortdesc"] = response.meta["shortdesc"]
            item["pagetitle"] = None
            item["url"] = response.url
            item["newcarid"] = None
            item["status"] = "sale"
            item["brand"] = response.meta["brand"]
            item["series"] = response.meta["series"]
            item["factoryname"] = None
            item["modelname"] = None
            item["brandid"] = None
            item["familyid"] = None
            item["seriesid"] = None
            try:
                item['makeyear'] = re.findall(r"(\d*)款", response.meta["shortdesc"])[0]
            except:
                item['makeyear'] = None
            item["registeryear"] = None
            item["produceyear"] = None
            item["body"] = None
            item["bodystyle"] = None

            item["level"] = response.xpath("//li[contains(text(),'车辆类别')]/i/text()").extract_first()
            item["fueltype"] = None
            item["driverway"] = None
            item["output"] = response.xpath("//li[contains(text(),'排量')]/i/text()").extract_first()
            item["guideprice"] = response.xpath("//li[contains(text(),'原始购车价')]/i/text()").extract_first()
            # 新车指导价46.30万(含税)
            item["guidepricetax"] = None
            item["doors"] = None
            item["emission"] = response.xpath("//li[contains(text(),'环保标准')]/i/text()").extract_first()
            item["gear"] = None
            item["geartype"] = response.xpath("//li[contains(text(),'变速箱类型')]/i/text()").extract_first()
            item["seats"] = response.xpath("//li[contains(text(),'座位数')]/i/text()").extract_first()
            item["length"] = None
            item["width"] = None
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
            item["registerdate"] = response.xpath("//li[contains(text(),'首次上牌时间')]/i/text()").extract_first()
            item["years"] = None
            item["paytype"] = None
            item["price1"] = response.xpath("//div[@class='d_c f14']/div[1]/span/text()").extract_first().strip()
            item["pricetag"] = None
            item["mileage"] = response.xpath("//li[contains(text(),'表显里程')]/i/text()").extract_first()
            item["color"] = response.xpath(
                "//li[contains(text(),'车身颜色')]/i/text()").extract_first()
            item["city"] = response.meta["city"]
            item["prov"] = response.meta["prov"]
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
            item["change_times"] = response.xpath("//li[contains(text(),'过户次数')]/i/text()").extract_first().strip()
            item["insurance1_date"] = response.xpath("//li[contains(text(),'交强险到期日')]/i/text()").extract_first()
            item["insurance2_date"] = response.xpath("//li[contains(text(),'商业险到期日')]/i/text()").extract_first()
            item["hascheck"] = None
            item["repairinfo"] = None
            item["yearchecktime"] = response.xpath("//li[contains(text(),'年审有效期')]/i/text()").extract_first()
            item["carokcf"] = None
            item["carcard"] = None
            item["carinvoice"] = None
            item["accident_desc"] = None
            item["accident_score"] = None
            item["outer_desc"] = str(response.xpath("//dt[contains(text(),'经查，该车外观有这些问题：')]/../dd/text()").extract_first())
            item["outer_score"] = None
            item["inner_desc"] = str(response.xpath("//dt[contains(text(),'经查，该车内饰及电子设备有这些问题：')]/../dd/text()").extract())
            item["inner_score"] = None
            item["safe_desc"] = None
            item["safe_score"] = None
            item["road_desc"] = None
            item["road_score"] = None
            item["lastposttime"] = None
            item["newcartitle"] = None
            item["newcarurl"] = None
            item["img_url"] = response.xpath('//*[@id="datumimg"]/img/@src').extract_first()
            item["first_owner"] = None
            item["carno"] = response.xpath("//li[contains(text(),'车牌号码')]/i/text()").extract_first().strip()
            item["carnotype"] = None
            item["carddate"] = None
            item["changecolor"] = None
            item["outcolor"] = None
            item["innercolor"] = None
            item["desc"] = None
            item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])+item["sold_date"]+str(5)
        except:
            log_dict["logType"] = 'ERROR'
            log_dict["logMessage"] = response.url
            logging.log(msg=json.dumps(log_dict, ensure_ascii =False), level=logging.INFO)
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
            logging.log(msg=json.dumps(log_dict,ensure_ascii=False), level=logging.INFO)
            yield item
        # print(item)
