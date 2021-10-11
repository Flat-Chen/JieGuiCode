# -*- coding: utf-8 -*-
import logging
import os
import random
import re
import sys
import time
from urllib import parse

import scrapy

# 爬虫名
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
from ..niuniu_proxy import NiuNiuMiddleware
from ..items import NiuNiu_item

website = 'niuniu'


# 必须有自己的中间件  切与其他的没有关系
class GuazicarSpider(scrapy.Spider):
    name = website
    start_urls = "http://www.niuniuqiche.com/v2/sell_cars?brand_name="
    brand_list = set([
            "阿尔法罗密欧", "阿斯顿马丁", "AC Schnitzer", "爱驰", "ALPINA", "安凯客车", "奥迪", "ARCFOX", "巴博斯", 
            "宝骏", "宝马", "保时捷", "宝沃", "北京", "北京汽车", "北京清行", "北汽昌河", "北汽道达", "北汽幻速", 
            "北汽威旺", "北汽新能源", "北汽制造", "奔驰", "奔腾", "本田", "比德文汽车", "比速汽车", "比亚迪", "标致", 
            "别克", "宾利", "宾仕盾", "布加迪", "长安", "长安欧尚", "长安轻型车", "长城", "成功汽车", "大乘汽车", "大众", 
            "道奇", "电咖", "东风", "东风风度", "东风风光", "东风风神", "东风风行", "东风瑞泰特", "东风小康", "东南", "DS", 
            "法拉利", "菲斯科Fisker", "菲亚特", "丰田", "福迪", "福汽启腾", "福特", "福田", "福田乘用车", "GMC", "观致", 
            "广汽传祺", "广汽吉奥", "广汽集团", "广汽新能源", "国机智骏", "国金汽车", "哈飞", "哈弗", "海格", "海马", 
            "悍马", "汉腾汽车", "合众汽车", "恒天", "红旗", "红星汽车", "华凯", "华骐", "华颂", "华泰", "华泰新能源", 
            "黄海", "Icona", "Jeep", "几何汽车", "吉利汽车", "褀智", "江淮", "江铃", "江铃集团新能源", "江铃驭胜", "捷豹", 
            "捷达", "杰克Jayco", "捷途", "金杯", "金龙", "金旅", "九龙", "君马汽车", "钧天", "卡尔森", "卡升", "卡威", 
            "凯佰赫", "凯迪拉克", "开瑞", "开沃汽车", "凯翼", "康迪全球鹰", "克莱斯勒", "科尼赛克", "KTM", "拉达", "兰博基尼", 
            "劳斯莱斯", "雷丁", "雷克萨斯", "雷诺", "力帆汽车", "理念", "理想汽车", "莲花汽车", "猎豹汽车", "林肯", "领克", 
            "铃木", "零跑汽车", "领途汽车", "LOCAL MOTORS", "Lorinser", "陆地方舟", "陆风", "路虎", "路特斯", "罗夫哈特", 
            "玛莎拉蒂", "马自达", "迈巴赫", "迈凯伦", "迈迈", "MG", "MINI", "摩根", "纳智捷", "哪吒汽车", "NEVS国能汽车", 
            "讴歌", "欧拉", "欧朗", "帕加尼", "庞巴迪", "Polestar", "Polestar极星", "启辰", "骐铃汽车", "奇瑞", "起亚", 
            "前途", "乔治巴顿", "庆铃汽车", "日产", "容大智造", "荣威", "如虎", "瑞驰新能源", "赛麟", "三菱", "陕汽通家", 
            "上汽MAXUS", "双环", "双龙", "斯巴鲁", "斯达泰克", "斯柯达", "思铭", "smart", "SRM鑫源", "SWM斯威汽车", "泰卡特", 
            "特斯拉", "腾势", "天际汽车", "瓦滋UAZ", "潍柴英致", "蔚来", "威麟", "威马汽车", "威兹曼", "WEY", "沃尔沃", 
            "五菱汽车", "五十铃", "西雅特", "现代", "小鹏汽车", "新凯", "新特汽车", "鑫源", "星途", "雪佛兰", "雪铁龙", 
            "野马汽车", "一汽", "依维柯", "银隆新能源", "英菲尼迪", "永源", "御捷", "裕路汽车", "宇通客车", "云度", "云雀汽车", 
            "征服Conquest", "知豆", "之诺", "中华", "众泰", "中兴"
        ])

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": random.uniform(2, 3),
        "DOWNLOADER_MIDDLEWARES": {
            # 'guazi.niuniu_proxy.NiuNiuMiddleware': 180,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 关闭默认下载器
            # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
        },
        "COOKIES_ENABLED": True,
        "REDIRECT_ENABLED": False,
        "DUPEFILTER_DEBUG": True

    }

    def __init__(self, **kwargs):
        settings.set("WEBSITE", website + time.strftime("%Y%m%d", time.localtime()))
        settings.set("MYSQLDB_DB", "niuniu")
        super(GuazicarSpider, self).__init__(**kwargs)
        self.niuniu_cookies = NiuNiuMiddleware()

    def start_requests(self):
        random.shuffle(list(self.brand_list))
        for i in list(self.brand_list):
            url = self.start_urls + i
            cookie = self.niuniu_cookies.get_cookie()
            # print(cookie)
            yield scrapy.Request(url=url, dont_filter=True, meta={"brand": i}, cookies=cookie)

    # 车型
    def parse(self, response):
        if response.status != 200:
            self.niuniu_cookies.remove_cookie()
            logging.info('请及时更新Cookie...')
            return

        # 2看车是否超过 2000
        num = response.xpath("//p[@class='result-count']/text()").extract_first()
        print(num)
        # print(response.url)
        # print(response.status)
        try:
            num = int(re.findall(r"共找到(\d*)条资源", num)[0])
        except:
            num = 0
        # 为0 直接跳出
        if num == 0:
            return
        # 直接翻页
        if num <= 2000:
            url = response.url + "&page=1"
            yield scrapy.Request(url=url, callback=self.next_page_parse, meta=response.meta, dont_filter=True)
        if num > 2000:
            # q去重操作
            series_list = response.xpath("//a[@class='filter-item']/text()").extract()
            for series in series_list:
                url = "http://www.niuniuqiche.com/v2/sell_cars?brand_name={}&car_model_name={}".format(
                    parse.quote(response.meta["brand"]), parse.quote(series))
                yield scrapy.Request(url=url, callback=self.next_page_parse, meta=response.meta)

    # 进行翻页操作
    def next_page_parse(self, response):
        logging.log(msg='解析 url---------------', level=logging.INFO)
        car_list = response.xpath("//div[@class='item']")
        for car in car_list:
            item = NiuNiu_item()
            item["brand"] = response.meta["brand"]
            item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            try:
                item["url"] = "http://www.niuniuqiche.com" + car.xpath(
                    ".//div[@class='car-title']/a/@href").extract_first()
            except:
                item["url"] = "-"
            item["post_time"] = car.xpath(".//div[@class='car-publish-time']/text()").extract_first()
            if item["post_time"] != None:
                if ':' in item["post_time"]:
                    item["post_time"] = time.strftime("%Y-%m-%d ", time.localtime()) + item["post_time"]
            else:
                item["post_time"] = '-'
                #     车的小标题
            item["salesdesc"] = car.xpath(".//div[@class='car-title']/a/text()").extract_first()
            # 价格
            item["price"] = car.xpath(".//div[@class='car-info']/div[@class='car-price']/text()").extract_first()
            # 指导价
            try:
                item["guide_price"] = car.xpath(
                    ".//div[@class='car-info']/div[@class='car-guide-price']/text()").extract_first().strip("指导价: ")
            except:
                item["guide_price"] = '-'
            # 车的解释
            item["car_explain"] = car.xpath(".//div[@class='car-subtitle clearfix']/span/text()").extract_first()
            # 店家
            item["procedure"] = car.xpath(".//div[@class='user-info clearfix']/span/a/text()").extract_first()
            # 备注
            item["remark"] = car.xpath(".//div[@class='car-remark clearfix']/p/text()").extract_first()
            # 配置
            item["configuration"] = car.xpath(
                ".//div[@class='car-configuration-remark clearfix']/p/text()").extract_first()
            # item["area"] = car.xpath("").extract_first()

            # item["appearance"] = car.xpath("").extract_first()
            # item["specification"] = car.xpath("").extract_first()
            # item["merchant"] = car.xpath("").extract_first()
            # item["brand"] = response.meta["brand"]
            # 成交量
            try:
                item["deal_sum"] = car.xpath(
                    ".//div[@class='user-info clearfix']/span[3]/text()").extract_first().strip(
                    "|成交量:")
            except:
                item["deal_sum"] = '-'
            item["statusplus"] = str(item["deal_sum"]) + str(item["procedure"]) + str(item["guide_price"]) + str(
                item["salesdesc"]) + str(item["price"]) + str(item["url"]) + str(1111) + time.strftime("%Y-%m-%d",
                                                                                                       time.localtime())
            yield item

        next_page_url = response.xpath("//a[contains(text(),'下一页')]/@href").extract_first()
        if next_page_url == None:
            return
        else:
            yield response.follow(url=next_page_url, callback=self.next_page_parse, meta=response.meta)
        #         解析
