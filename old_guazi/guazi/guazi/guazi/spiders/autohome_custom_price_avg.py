# -*- coding: utf-8 -*-
"""

C2017-40

"""
import execjs
import scrapy
from pymysql import connect

import time
from scrapy.mail import MailSender
import re
from ..items import AutohomeCustomPriceItem1
from scrapy.conf import settings

website = 'autohome_custom_price2_avg'


class CarSpider(scrapy.Spider):
    name = website
    start_urls = [
        "https://www.autohome.com.cn/beijing/"
    ]

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.mailer = MailSender.from_settings(settings)
        self.counts = 0
        self.carnum = 800000

        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MONGODB_DB', 'carbusiness', priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')

        super(CarSpider, self).__init__()

        self.js_header = """var style ={
            sheet:{
                insertRule:function(){}
            }
        }
        var document ={
            createElement :function(){ return style}
            ,head:{
                appendChild:function(){}
            }
            ,querySelectorAll :function(){}
        }

        global.window =global
        var window ={
            getComputedStyle :true
        } 

        obj ={}
        !"""
        self.js_end = """    
                function $InsertRuleRun$() {
                for ($index$ = 0; $index$ < $rulePosList$.length; $index$++) {
                    var $tempArray$ = $Split$($rulePosList$[$index$], ',');
                    var $temp$ = '';
                    for ($itemIndex$ = 0; $itemIndex$ < $tempArray$.length; $itemIndex$++) {
                        $temp$ += $ChartAt$($tempArray$[$itemIndex$]) + '';
                    }
                    obj["<span class='"+$GetClassName$($index$).split(".")[1]+"'></span>"] =$temp$
                }
            }

        })(document);
            function get_obj(){
            return obj
            }"""

    def parse(self, response):
        # # yield scrapy.Request("https://jiage.autohome.com.cn/price/carlist/p-28763", callback=self.parse_list, dont_filter=True)

        mysqldb = connect("192.168.1.94", "dataUser94", "94dataUser@2020", "newcar_test", port=3306)
        dbc = mysqldb.cursor()

        sql = "select autohomeid from autohomeall"
        dbc.execute(sql)
        res = dbc.fetchall()
        for row in res:
            url = "https://jiage.autohome.com.cn/price/carlist/p-%s-1-0-0-0-0-1-110100" % row[0]
            yield scrapy.Request(url=url, meta={"autohomeid": row[0], 'page': 1}, callback=self.parse_list)

    def get_price(self, js):
        code1 = js.replace('\n', '')
        code = self.js_header + code1.replace("})(document)", "") + self.js_end
        js_code = execjs.compile(code)
        a = js_code.call('get_obj')
        return a

    def parse_list(self, response):
        item = AutohomeCustomPriceItem1()
        item['grab_time'] = time.strftime('%Y-%m-%d %X', time.localtime())
        item['url'] = response.url
        item["autohomeid"] = response.meta["autohomeid"]
        try:
            guide_price_js = response.xpath(
                "//p[contains(text(),'车主裸车平均价')]/../span[@class='red']//script[1]//text()").extract_first()
            item["Naked_car_price"] = list(self.get_price(guide_price_js).values())[0]
        except:
            item["Naked_car_price"] =None
        try:

            guide_price_js = response.xpath(
                "//p[contains(text(),'车主裸车平均价')]/../span[@class='red']//script[1]//text()").extract_first()
            item["owner_car_price"] = list(self.get_price(guide_price_js).values())[0]
        except:
            item["owner_car_price"] = None

        item['statusplus'] = str(item['autohomeid']) + str(item["Naked_car_price"] )+ str(item["owner_car_price"])
        # yield item
        print(item)