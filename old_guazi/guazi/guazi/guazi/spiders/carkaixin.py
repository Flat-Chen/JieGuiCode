import json
import time

import pandas as pd
import re

from redis import Redis

from ..items import GuaziItem
import scrapy
import logging
from scrapy.conf import settings
from hashlib import md5
from ..redis_bloom import BloomFilter
website = 'carkaixin'


# 先循环城市 然后在循环车
class CarSpider(scrapy.Spider):
    name = website
    shield = '4cfe8ea820d63af5d1f9bde5b6cf48a9'
    # 判断 城市是否有足够的车源，如果充足 则循环车系
    start_url = 'http://www.kx.cn/prodApi2/cus/MakeDataListXgw'  # 品牌首字母
    brand_url =  'http://www.kx.cn/prodApi2/cus/MakerBrandNameList' # 品牌
    series_url = "http://www.kx.cn/prodApi2/cus/ModelListByMaker"  # 车系  
    year_url = 'http://www.kx.cn/prodApi2/cus/StyleListXgw'  # 年份选项
    car_url = "http://www.kx.cn/prodApi2/cus/TransactionRecordXgw"  # 车id  
    
    headers = {
        'Host': 'www.kx.cn',
        'Origin': 'http://www.kx.cn',
        'Referer': 'http://www.kx.cn/carPrice/carPrice',
        'Content-Type': 'application/json;charset=UTF-8',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        self.bf = BloomFilter(key='b1f_' + website)
        self.counts = 0

    def start_requests(self):
        # 遍历品牌首字母
        brands = ['A', 'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'Q', 'R', 'S', 'T', 'W', 'X', 'Y', 'Z']
        for bra in brands[:1]:
            data = {
                'firstLetter': bra,
            }
            yield scrapy.Request(url=self.start_url, method='POST',headers=self.headers, body=json.dumps(data))

    def parse(self, response):
        brand_data = json.loads(response.text)['data']
        # 获取 brand 名字和baranID
    #     brandid_list = response.xpath("//a/@brandid").extract()
    #     brandname_list = response.xpath("//a/text()").extract()
    #     # print(brandid_list)
    #     # print(brandname_list)
        for itm in brand_data['data']:
            form_dict = {"makeId": itm['makeId']}
            form_dict1 = {"brand_code": itm['makeId'],
                          "brand_name": itm['makeName']}
            yield scrapy.Request(url=self.brand_url, body=json.dumps(form_dict), headers=self.headers, method='POST',
                                     callback=self.series_parse, meta=form_dict1)

    def series_parse(self, response):
        makerbrand_data = json.loads(response.text)['data']

        for itm in makerbrand_data:
            response.meta['maker_brand_name'] = itm['MakerBrandName']
            response.meta['maker_brand_code'] = itm['MakerBrandCode']
            yield scrapy.Request(url=self.series_url, body=json.dumps(itm), headers=self.headers,
                                     method='POST', callback=self.car_parse, meta=response.meta)

    def car_parse(self, response):
        family_data = json.loads(response.text)['data']

        for itm in family_data:
            data = {}
            data['FamilyCode'] = itm['FamilyCode']
            data['FamilyName'] = itm['FamilyName']
            response.meta['family_name'] = itm['FamilyName']
            response.meta['family_code'] = itm['FamilyCode']
            yield scrapy.Request(url=self.year_url, headers=self.headers, method='POST',
                    body=json.dumps(data), callback=self.car_list_parse, meta=response.meta)

    def car_list_parse(self, response):
        # 解析 年款 列表
        style_data = json.loads(response.text)

        if style_data['data']:
            for itm in style_data['data']:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                payload = {
                    "page":1, 
                    "brandNm":response.meta['maker_brand_name'],
                    "seriesNm":response.meta['family_name'],
                    "styleName":itm["styleName"],
                    "regDate":"",
                    "accessTime":current_time,
                    "sign":md5((current_time + self.shield).encode()).hexdigest(),
                }
                response.meta['style_code'] = itm['styleCode']
                response.meta['style_name'] = itm['styleName']
                yield scrapy.Request(url=self.car_url, headers=self.headers, callback=self.car_detail_parse, meta=response.meta, body=json.dumps(payload), method='POST')
        else:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            payload = {
                "page":1, 
                "brandNm":response.meta['maker_brand_name'],
                "seriesNm":response.meta['family_name'],
                "styleName":"",
                "regDate":"",
                "accessTime":current_time,
                "sign":md5((current_time + self.shield).encode()).hexdigest(),
            }
            response.meta['style_name'] = ""
            yield scrapy.Request(url=self.car_url, headers=self.headers, callback=self.car_detail_parse, meta=response.meta, body=json.dumps(payload), method='POST')

    def car_detail_parse(self, response):
        # print('元数据： ', response.meta)
        # print('响应数据 list ： ', json.loads(response.text)['data']['list'])
        data = json.loads(response.text)['data']
        for dt in data['list']:
            carid = dt['carid']
            sign = md5((dt['carid'] + self.shield).encode()).hexdigest()
            car_detail_url = "http://www.kx.cn/carPrice/detail?carid={}&sign={}".format(carid, sign)
            response.meta['cur_page'] = data['currentpage']
            yield scrapy.Request(url=car_detail_url, callback=self.parse_detail, meta=response.meta, headers=self.headers)

        if data['currentpage'] < data['maxpage']:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            payload = {
                "page":data['currentpage'] + 1, 
                "brandNm":response.meta['maker_brand_name'],
                "seriesNm":response.meta['family_name'],
                "styleName":response.meta['style_name'],
                "regDate":"",
                "accessTime":current_time,
                "sign":md5((current_time + self.shield).encode()).hexdigest(),
            }
            response.meta['cur_page'] = data['currentpage'] + 1
            yield scrapy.Request(url=self.car_url, headers=self.headers, callback=self.car_detail_parse, meta=response.meta, body=json.dumps(payload), method='POST')

    def parse_detail(self, response):
        grap_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # print(response.meta)

        item = GuaziItem()

        item["carid"] = re.findall(r"carid=(\d*)", response.url)[0]
        item["car_source"] = "carkaixin"
        item["usage"] = None
        item["grab_time"] =grap_time
        item["update_time"] = None
        item["post_time"] = response.css('p.p2::text').get().split()[0].split('：')[-1]
        item["sold_date"] = None
        item["pagetime"] = None
        item["parsetime"] = grap_time
        item["shortdesc"] = response.xpath("//p[@class='p1']/text()").extract_first().strip()
        item["pagetitle"] = response.xpath("//title/text()").extract_first().strip("")
        item["url"] = response.url
        item["newcarid"] = None
        item["status"] = "sale"
        item["brand"] = response.meta["brand_name"]
        item["series"] = response.meta["family_name"]
        item["factoryname"] = response.meta['maker_brand_name']
        item["modelname"] = None
        item["brandid"] = response.meta["brand_code"]
        item["familyid"] = None
        item["seriesid"] = response.meta["family_code"]
        try:
            item['makeyear'] = response.meta["style_name"].strip('款')
        except:
            item['makeyear'] = None
        item["registeryear"] = None
        item["produceyear"] = None
        item["body"] = None
        item["bodystyle"] = None

        item["level"] = None
        item["fueltype"] = None
        item["driverway"] = None
        item["output"] = None
        item["guideprice"] = None
        # 新车指导价46.30万(含税)
        item["guidepricetax"] = None
        item["doors"] = None
        item["emission"] = None
        item["gear"] = response.xpath(
            "//li//span[contains(text(),'变速箱')]/preceding-sibling::span/text()").extract_first()
        item["geartype"] = None
        item["seats"] =None
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
        item["registerdate"] =response.xpath('//span[contains(text(), "上牌时间")]/preceding-sibling::span/text()').get()
        item["years"] = None
        item["paytype"] = None
        item["price1"] =response.css('span.price::text').get().strip('万')
        item["pricetag"] = None
        item["mileage"] = response.xpath("//li//span[contains(text(),'表显里程')]/preceding-sibling::span/text()").extract_first().strip("公里")
        item["color"] =None
        item["city"] = response.xpath("//span[contains(text(),'牌照归属')]/preceding-sibling::span/text()").extract_first()
        item["prov"] = None
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
        item["insurance1_date"] = None
        item["insurance2_date"] = None
        item["hascheck"] = None
        item["repairinfo"] = None
        item["yearchecktime"] = response.xpath(
            "//li//span[contains(text(),'车检有效期')]/preceding-sibling::span/text()").extract_first()
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
        item["img_url"] = response.xpath("//div[@class='detailContainer flex']/img/@src").extract_first().strip("")
        item["first_owner"] = None
        item["carno"] = response.xpath("//span[contains(text(),'牌照归属')]/preceding-sibling::span/text()").extract_first()
        item["carnotype"] = None
        item["carddate"] = None
        item["changecolor"] = None
        item["outcolor"] = None
        item["innercolor"] = None
        item["desc"] = None
        item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])
    
        returndf = self.bf.isContains(item["statusplus"])
        # 1数据存在，0数据不存在
        if returndf == 1:
            ishave = True
        else:
            ishave = False
        logging.log(msg='数据是否已经存在： %s' % ishave, level=logging.INFO)
        yield item
        # print(item)
