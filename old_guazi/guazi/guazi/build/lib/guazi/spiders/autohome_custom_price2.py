# -*- coding: utf-8 -*-
"""

C2017-40

"""
import execjs
import scrapy
import re
import time

from scrapy import Selector
from pymysql import connect
from scrapy.mail import MailSender
from ..items import  AutohomeCustomPriceItem
from scrapy.conf import settings

website = 'autohome_custom_price2'


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

        # yield scrapy.Request("https://jiage.autohome.com.cn/price/carlist/p-28763", callback=self.parse_list, dont_filter=True)

        mysqldb = connect("192.168.1.94", "dataUser94", "94dataUser@2020", "newcar_test", port=3306)
        dbc = mysqldb.cursor()

        sql = "select autohomeid from autohomeall"
        dbc.execute(sql)
        res = dbc.fetchall()

        for row in res:
            url = "https://jiage.autohome.com.cn/price/carlist/p-%s-1-0-0-0-0-1-110100" % row[0]
            yield scrapy.Request(url=url, meta={"autohomeid": row[0], 'page': 1}, callback=self.parse_list)
    
    # 清洗价格混淆加密源码
    def cleaned(self, html):
        html = re.sub(r'<script>.*?</script>', '', html, re.S)
        html = re.sub(r'<style.*?</style>', '', html, re.S)
        html = re.sub(r'<span class="hs_kw.*?</span>', '-', html, re.S)
        return html
    
    # 执行 js 获取价格
    def get_price(self, js):
        code1 = js.replace('\n', '')
        code = self.js_header + code1.replace("})(document)", "") + self.js_end
        js_code = execjs.compile(code)
        a = js_code.call('get_obj')
        print('执行js返回对象：', a)
        return a

    def parse_list(self, response):
        nums = response.xpath("//span[@class='athm-title-nums-dettail']/text()").extract_first()
        if int(nums) > response.meta['page'] * 10:
            print("$$$$$$$$$$$$$$next page$$$$$$$$$$$$$$")
            response.meta['page'] = response.meta['page'] + 1
            next_num = response.meta['page'] + 1
            url = re.sub(r"-1-0-0-0-0-(.*?)-110100", r"-1-0-0-0-0-{}-110100".format(next_num), response.url)
            yield scrapy.Request(url=url, meta=response.meta, callback=self.parse_list)
        else:
            print("$$$$$$$$$$$$$$no next page$$$$$$$$$$$$$$")

        brand_and_family = response.xpath("//div[@class='athm-sub-nav__car__name']/a/span/text()").extract()
        price_boxes = response.xpath("//*[@class='car-lists']")
        for i, box in enumerate(price_boxes):
            item = AutohomeCustomPriceItem()

            item['grabtime'] = time.strftime('%Y-%m-%d %X', time.localtime())
            item['url'] = response.url
            item['username'] = box.xpath('//a[@class="car-lists-item-use-name-detail "]/text()').getall()[i]
            item['autohomeid'] = response.meta["autohomeid"]
            item['userid'] = box.xpath('//a[@class="car-lists-item-use-name-detail "]/@href').re(r"\d+")[0]
            item['fapiao'] = box.xpath('//a[@class="mark-receipt"]/text()').get()

            item['car_model'] = "".join(brand_and_family) + box.xpath(
                '//*[@class="car-lists-item-top-middle"]/p/text()').getall()[i]

            # naked_price
            naked_price_js = box.xpath(
                ".//span[contains(text(),'裸车价')]/following-sibling::span//span[@class='luochejia-num']/script[1]/text()").get()
            naked_price_text = box.xpath(".//span[contains(text(),'裸车价')]/following-sibling::span//span[@class='luochejia-num']").get()
            res0 = Selector(text=self.cleaned(naked_price_text))
            text0 = ''.join(res0.xpath('//span[@class="luochejia-num"]/text()').getall())
            naked_price_values = list(self.get_price(naked_price_js).values())
            if naked_price_values:
                for val in naked_price_values if naked_price_values[0] == ',' else reversed(naked_price_values):
                    text0 = text0.replace('-', str(val), 1)
            item['naked_price'] = text0

            # total_price
            total_price_js = box.xpath(
                ".//span[contains(text(),'购车全款')]/following-sibling::span//span[@class='quankuan-num']/script[1]/text()").get()
            total_price_text = box.xpath(".//span[contains(text(),'购车全款')]/following-sibling::span//span[@class='quankuan-num']").get()
            res1 = Selector(text=self.cleaned(total_price_text))
            text1 = ''.join(res1.xpath('//span[@class="quankuan-num"]/text()').getall())
            total_price_values = list(self.get_price(total_price_js).values())
            if total_price_values:
                for val in total_price_values if total_price_values[0] == ',' else reversed(total_price_values):
                    text1 = text1.replace('-', str(val), 1)
            item['total_price'] = text1
            
            # guide_price
            guide_price_js = box.xpath(
                './/span[contains(text(),"厂商指导价")]/..//span[@class="list-details"]//span[@class="luochejia-num"]/script[1]/text()').extract_first()
            guide_price_text = box.xpath(".//span[contains(text(),'厂商指导价')]/following-sibling::span//span[@class='luochejia-num']").get()
            res2 = Selector(text=self.cleaned(guide_price_text))
            text2 = ''.join(res2.xpath('//span[@class="luochejia-num"]/text()').getall())
            guide_price_values = list(self.get_price(guide_price_js).values())
            if guide_price_values:
                for val in guide_price_values if guide_price_values[0] == ',' else reversed(guide_price_values):
                    text2 = text2.replace('-', str(val), 1)
            item['guide_price'] = text2

            # 购置税
            tax_js = box.xpath(
                ".//span[contains(text(),'购置税')]/following-sibling::span/script[1]/text()").get()
            tax_text = box.xpath(".//span[contains(text(),'购置税')]/following-sibling::span").get()
            res3 = Selector(text=self.cleaned(tax_text))
            text3 = ''.join(res3.xpath('//span[@class="list-details"]/text()').getall())
            tax_values = list(self.get_price(tax_js).values())
            if tax_values:
                for val in tax_values if tax_values[0] == ',' else reversed(tax_values):
                    text3 = text3.replace('-', str(val), 1)
            item['tax'] = text3

            # 交强险
            jiaoqiangxian_js = box.xpath(
                ".//span[contains(text(),'交强险')]/following-sibling::span/script[1]/text()").get()
            jiaoqiangxian_text = box.xpath(".//span[contains(text(),'交强险')]/following-sibling::span").get()
            res4 = Selector(text=self.cleaned(jiaoqiangxian_text))
            text4 = ''.join(res4.xpath('//span[@class="list-details"]/text()').getall())
            jiaoqiangxian_values = list(self.get_price(jiaoqiangxian_js).values())
            if jiaoqiangxian_values:
                for val in jiaoqiangxian_values if jiaoqiangxian_values[0] == ',' else reversed(jiaoqiangxian_values):
                    text4 = text4.replace('-', str(val), 1)
            item['jiaoqiangxian'] = text4

            # 车船使用税
            chechuanshui_js = box.xpath(
                ".//span[contains(text(),'车船使用税')]/following-sibling::span/script[1]/text()").get()
            chechuanshui_text = box.xpath(".//span[contains(text(),'车船使用税')]/following-sibling::span").get()
            res5 = Selector(text=self.cleaned(chechuanshui_text))
            text5 = ''.join(res5.xpath('//span[@class="list-details"]/text()').getall())
            chechuanshui_values = list(self.get_price(chechuanshui_js).values())
            if chechuanshui_values:
                for val in chechuanshui_values if chechuanshui_values[0] == ',' else reversed(chechuanshui_values):
                    text5 = text5.replace('-', str(val), 1)
            item['chechuanshui'] = text5

            # 商业险
            shangyexian_js = box.xpath(
                ".//span[contains(text(),'商业险')]/following-sibling::span/script[1]/text()").get()
            shangyexian_text = box.xpath(".//span[contains(text(),'商业险')]/following-sibling::span").get()
            res6 = Selector(text=self.cleaned(shangyexian_text))
            text6 = ''.join(res6.xpath('//span[@class="list-details"]/text()').getall())
            shangyexian_values = list(self.get_price(shangyexian_js).values())
            if shangyexian_values:
                for val in shangyexian_values if shangyexian_values[0] == ',' else reversed(shangyexian_values):
                    text6 = text6.replace('-', str(val), 1)
            item['shangyexian'] = text6

            # 上牌费
            shangpaifei_js = box.xpath(
                ".//span[contains(text(),'上牌费')]/following-sibling::span/script[1]/text()").get()
            shangpaifei_text = box.xpath(".//span[contains(text(),'上牌费')]/following-sibling::span").get()
            res6 = Selector(text=self.cleaned(shangpaifei_text))
            text6 = ''.join(res6.xpath('//span[@class="list-details"]/text()').getall())
            shangpaifei_values = list(self.get_price(shangpaifei_js).values())
            if shangpaifei_values:
                for val in shangpaifei_values if shangpaifei_values[0] == ',' else reversed(shangpaifei_values):
                    text6 = text6.replace('-', str(val), 1)
            item['shangpaifei'] = text6

            item['pay_mode'] = box.xpath(".//span[contains(text(),'付款方式')]/../span[2]/text()").extract_first()
            item['buy_date'] = box.xpath(".//p[@class='bought-time']/time/text()").extract_first()
            item['buy_location'] = box.xpath("//span[@class='bought-location']/text()").extract_first()
            item['dealer'] =None
            item['dealerid'] = None
            item['tel'] =None
            item['dealer_addr'] =None
            item['star_level'] =None
            item['service_level'] =None
            # item['cutting_skill'] = "".join(box.xpath('li/div[2]/ol/li[11]/span[2]//text()').extract())
            item['cutting_skill'] = "-"
            item['statusplus'] = str(item['autohomeid']) + "-" + str(item['userid']) + "-" + str(
                item['buy_location']) + "-" + str(item['buy_date']) + "-" + str(item['naked_price']) + time.strftime(
                '%Y-%m', time.localtime())+str(1)

            # print(item)
            yield item
