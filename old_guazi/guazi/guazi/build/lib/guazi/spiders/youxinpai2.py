# -*- coding: UTF-8 -*-
import json
import re
import time
from ..items import GuaziItem
import requests
import scrapy
import logging
from scrapy.conf import settings
from ..redis_bloom import BloomFilter

website = 'youxinpai2'


class GuazicarSpider(scrapy.Spider):
    name = website
    allowed_domains = ['youxinpai.com']

    def __init__(self, **kwargs):
        settings.set("WEBSITE", website)
        settings.set("MYSQLDB_DB", "people_zb")
        super(GuazicarSpider, self).__init__(**kwargs)
        self.bf = BloomFilter(key='b1f_' + website)
        self.counts = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            "Referer": "http://www.youxinpai.com/index"}

    def start_requests(self):
        url = "http://www.youxinpai.com/halfMinUpdateList"
        data = requests.post(url, headers=self.headers).json()
        carlist = data['data']['data']['auctionHallResponeList']
        for car in carlist:
            url = 'http://www.youxinpai.com/home/trade/detail/{}/{}'.format(car['publishID'], car['crykey'])
            # print(url)
            yield scrapy.Request(url, headers=self.headers)

    def parse(self, response):
        # print(response.xpath('//title/text()').get()

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
        # try:
        self.counts += 1
        logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)
        item = GuaziItem()
        try:
            item["carid"] = re.findall(r'detail/(\d+)', response.url)[0]
        except:
            item['carid'] = None
        item["car_source"] = "youxinpai2"
        item["usage"] = response.xpath('//span[contains(text(), "使用性质")]/following-sibling::span/text()').get().strip()
        item["grab_time"] =  grap_time
        item["update_time"] = response.xpath(
            '//span[@class="MD-widget-tradedetail-template7-action_title-time"]/text()').extract_first()
        item["post_time"] = None
        item["sold_date"] = None
        item["pagetime"] = None
        item["parsetime"] =  grap_time
        item["shortdesc"] = response.xpath('//h1[@class="fl"]/text()').extract_first().strip('\n')
        item["pagetitle"] = response.xpath("//title/text()").extract_first().strip()
        item["url"] = response.url
        item["newcarid"] = None
        item["status"] = None
        try:
            item["brand"] = re.findall(r'(.*?) .*', response.xpath('//title/text()').extract_first())[0]
        except:
            item["brand"] = None
        try:
            item["series"] = re.findall(r'.*? (.*?) .*', response.xpath('//title/text()').extract_first())[0]
        except:
            item["series"] = None
        item["factoryname"] = None
        item["modelname"] = None
        item["brandid"] = None
        item["familyid"] = None
        item["seriesid"] = None
        try:
            item['makeyear'] = re.findall(r"(\d{4}[年款])",
                                            response.xpath("//title/text()").extract_first())[0]
        except:
            item['makeyear'] = None
        item["registeryear"] = None
        item["produceyear"] = response.xpath(
            "//table[@class='MD-widget-tradedetail-template7-proceduresDetail_new-tbl-info']//tbody[1]/tr[2]/td[1]/td/text()").extract_first()
        item["body"] = None
        item["bodystyle"] = None

        item["level"] = None
        item["fueltype"] = None
        item["driverway"] = None
        try:
            item["output"] = re.findall(r"(\d\.\d.*?) .*", response.xpath('//title/text()').extract_first())[0]
        except:
            item["output"] = None

        item["guideprice"] = \
            response.xpath('//th[contains(text(), "原始购车价")]/following-sibling::td/text()').extract_first()
        # 新车指导价46.30万(含税)
        item["guidepricetax"] = None
        item["doors"] = None
        try:
            item["emission"] = response.xpath('//span[contains(text(), "排放标准")]/following-sibling::span/text()').get().strip()
        except:
            item['emission'] = None
        item["gear"] = None
        try:
            item["geartype"] = str(re.findall(r"([自手]动)", response.xpath('//title/text()').extract_first())[0])
        except:
            item["geartype"] = None
        # item["seats"] = response.xpath('//span[@class="MD-widget-tradedetail-template7-action_title-sval"]/text()').getall()[8].strip()
        item["seats"] = response.xpath('//span[contains(text(), "座位数")]/following-sibling::span/text()').get().strip()
        item["length"] = None
        item["width"] = None
        item["height"] = None
        item["gearnumber"] = None
        item["weight"] = response.xpath('//td[contains(text(), "车重")]/following-sibling::td[1]/text()').extract_first()
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
            '//th[contains(text(), "注册日期")]/following-sibling::td[1]/text()').extract_first()
        item["years"] = None
        item["paytype"] = None
        item["price1"] = None
        item["pricetag"] = None
        item["mileage"] = response.xpath('//span[contains(text(), "表显里程")]/following-sibling::span/text()').get().strip()
        item["color"] = response.xpath('//span[contains(text(), "颜色")]/following-sibling::span/text()').get().strip()
        try:
            item["city"] = re.findall(r"【(.*)】", response.xpath('//h1/em/text()').extract_first())[0]
        except:
            item["city"] = None
        try:
            item["prov"] = re.findall(r"province=(.*);city", response.xpath(
                '///meta[5]/@content').extract_first())[0]
        except:
            item["prov"] = None
        item["guarantee"] = None

        item["totalcheck_desc"] = str(response.xpath(
            '//th[contains(text(), "车辆信息")]/../td/text()').extract_first())
        try:
            item["totalgrade"] = str(
                response.xpath('//h3[contains(text(),"车况信息")]/../div/div/ul/li[1]/text()').extract()[0])
        except:
            item["totalgrade"] = str({})
        item["contact_type"] = None
        item["contact_name"] = None
        item["contact_phone"] = None
        item["contact_address"] = None
        item["contact_company"] = None
        item["contact_url"] = None
        item["change_date"] = None
        item["change_times"] = response.xpath("//td[@colspan='4']/text()").extract_first().strip('\n')
        item["insurance1_date"] = response.xpath('//*[text() ="交强险"]/../td[1]/text()').extract_first()
        item["insurance2_date"] = response.xpath('//*[text() ="商业险"]/../td[1]/text()').extract_first()
        item["hascheck"] = None
        item["repairinfo"] = response.xpath(
            '//span[contains(text(),"保养情况")]/../span[2]/text()').extract_first()
        item["yearchecktime"] = response.xpath('//*[text() ="年检到期"]/../td[1]/text()').extract_first()
        item["carokcf"] = response.xpath('//th[contains(text(), "改装说明")]/../td/text()').extract_first()
        item["carcard"] = response.xpath('//img[@id="picPro0"]/@src').extract_first()
        item["carinvoice"] = None
        item["accident_desc"] = response.xpath(
            '//p[@class="MD-widget-tradedetail-template5-condition_new-sub-section-des"]/text()').extract_first()
        try:
            item["accident_score"] = re.findall(r'x(\d)', response.xpath('//*[@id="a7"]/em/i/@class').extract_first())[
                0]
        except:
            item["accident_score"] = None
        item["outer_desc"] = str(response.xpath(
            '//div[text()="外观"]/..//span[@class="MD-widget-tradedetail-template7-flaw-sp MD-widget-tradedetail-template7-flaw-sp-w1 MD-widget-tradedetail-template7-flaw-st1"]//text()').extract())
        item["outer_score"] = response.xpath(
            '//em[@class="MD-widget-tradedetail-template5-outer_new-sec-level"]/text()').extract_first()
        item["inner_desc"] = str(response.xpath(
            '//div[text()="内饰"]/..//span[@class="MD-widget-tradedetail-template7-flaw-sp MD-widget-tradedetail-template7-flaw-sp-w1 MD-widget-tradedetail-template7-flaw-st1"]//text()').extract())
        try:
            item["inner_score"] = re.findall(r'x(\d)', response.xpath('//*[@id="a5"]/em/i/@class').extract_first())[0]
        except:
            item["inner_score"] = None
        item["safe_desc"] = str(response.xpath(
            '//div[text()="骨架"]/..//span[@class="MD-widget-tradedetail-template7-flaw-sp MD-widget-tradedetail-template7-flaw-sp-w1 MD-widget-tradedetail-template7-flaw-st1"]//text()').extract())
        item["safe_score"] = response.xpath(
            '//em[@class="MD-widget-tradedetail-template5-skeleton_new-sec-level"]/text()').extract_first()
        item["road_desc"] = str(response.xpath(
            '//div[@class="MD-widget-tradedetail-template7-flaw-flaw-box"]//span[@class="MD-widget-tradedetail-template7-flaw-sp MD-widget-tradedetail-template7-flaw-sp-w2 MD-widget-tradedetail-template7-flaw-st1"]/text()').extract())
        try:
            item["road_score"] = re.findall(r'x(\d)', response.xpath(
                '//em[@class="MD-widget-tradedetail-template5-electric_new-sec-level MD-widget-tradedetail-template5-electric_new-x-level"]/i/@class').extract_first())[
                0]
        except:
            item["road_score"] = None
        try:
            item["lastposttime"] = \
                re.findall(r"车辆核实员(.*)完成上架", response.xpath('//span[@class="cd_m_vpre_txt"]/text()').extract_first())[0]
        except:
            item["lastposttime"] = None
        item["newcartitle"] = response.xpath('//th[contains(text(), "可见配置")]/../td/text()').extract_first()
        item["newcarurl"] = None
        item["img_url"] = response.xpath('//*[@id="bigImageShow"]/img[1]/@src').extract_first()
        try:
            item["first_owner"] = re.findall(r'\d+\.\d+(.*?) .*', response.xpath(
                '//title/text()').extract_first())[0]
        except:
            item["first_owner"] = None
        try:
            item["carno"] = response.xpath('//span[@class="MD-widget-tradedetail-template7-action_title-sval"]/text()').getall()[-1].strip()
        except:
            item['carno'] = None
        try:
            item["carnotype"] = response.xpath(
                '//span[@class="MD-widget-tradedetail-template7-action_title-sval MD-widget-tradedetail-template7-action_title-c "]/text()').getall()[0].strip()
        except:
            item['carnotype'] = None
        item["carddate"] = None
        item["changecolor"] = None
        item["outcolor"] = response.xpath('//span[contains(text(),"颜色")]/../span[2]/a/text()').extract_first()
        item["innercolor"] = None
        item["desc"] = None
        item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + item["update_time"] + str(4)
        # except Exception as e:
        #     print(repr(e))
        #     log_dict["logType"] = 'ERROR'
        #     log_dict["logMessage"] = response.url
        #     logging.log(msg=json.dumps(log_dict, ensure_ascii =False), level=logging.INFO)
        # else:
        #     log_dict["logType"] = 'INFO'
        #     log_dict["logMessage"] = "successful"
        #     log_dict["logObject"] = {
        #         "field": {
        #             "carsource": website,
        #             "mileage": item["mileage"],
        #             "post_time": item["post_time"],
        #             "sold_date": item["sold_date"],
        #             "city": item["city"],
        #             "registerdate": item["registerdate"]
        #         },
        #         "info": {
        #             "dataBaseType": "mysql",
        #             "dataBaseName": settings["MYSQLDB_DB"],
        #             "tableName": website + '_online',
        #             "saveStatus": ""
        #         }
        #     }
        #     returndf = self.bf.isContains(item["statusplus"])
        #     # 1数据存在，0数据不存在
        #     if returndf == 1:
        #         log_dict["logObject"]["info"]["saveStatus"] = "true"
        #     else:
        #         log_dict["logObject"]["info"]["saveStatus"] = "false"
        #     logging.log(msg=json.dumps(log_dict,ensure_ascii=False), level=logging.INFO)

        yield item
        # print(item)