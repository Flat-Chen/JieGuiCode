import execjs
import scrapy
from redis import Redis

from ..items import autohome_newcar
import time
from scrapy.conf import settings
from scrapy.mail import MailSender
import logging
import json
import re
import hashlib
from lxml import etree

import sys
import pandas as pd
from sqlalchemy import create_engine

website = 'autohome_newcar_cong'

redis_cli = Redis(host="192.168.1.249", port=6379, db=3)


class CarSpider(scrapy.Spider):
    name = website
    allowed_domains = ["autohome.com.cn"]
    start_urls = [
        "https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=1%20&brandId=0%20&fctId=0%20&seriesId=0"]
    custom_settings = {
        "REDIRECT_ENABLED": True,
        "DOWNLOADER_MIDDLEWARES": {
            "guazi.proxy.autohome_middlewarel": 550
        },
        'CONCURRENT_REQUESTS': 20,
        'DOWNLOAD_DELAY': 0,
        "RETRY_TIMES": 20
    }

    def __init__(self, **kwargs):
        # problem report
        self.index = 0
        super(CarSpider, self).__init__(**kwargs)
        self.mailer = MailSender.from_settings(settings)
        self.counts = 0
        self.carnum = 1010000
        # Mongo
        settings.set('DOWNLOAD_DELAY', '0', priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MONGODB_DB', 'newcar', priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        self.nationp = dict()
        self.npcounts = 0
        self.headers = {'Referer': 'https://car.autohome.com.cn/',
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    def get_data(self):
        engine_huachen = create_engine('mysql+pymysql://root:Datauser@2017@192.168.1.94:3306/txy?charset=utf8')
        sign = pd.read_sql("select * from missing_autohomeid",
                           con=engine_huachen)
        a = sign.to_dict(orient='records')
        for i in a:
            item = {'producestatus': i["producestatus"], 'model': i["salesdesc"], 'autohomeid': i["autohomeid"],
                    'factoryname': i["factoryname"], 'factoryid': i["factoryid"], 'familyname': i["familyname"],
                    'familyid': i["familyid"], 'brandname': i["brandname"], 'brandid': i["brandid"], }
            url = "https://car.autohome.com.cn/config/spec/{}.html#pvareaid=3454541".format(item["autohomeid"])
            print(url)
            self.redis_tools(url + "*" + str(item))

    def redis_tools(self, url):
        valid = redis_cli.sadd("autohome_newcar", url)
        return valid

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], headers=self.headers)

    def parse(self, response):
        html_str = response.text.replace('document.writeln("', '').replace('");', '')
        res = etree.fromstring("<root>" + html_str.strip() + "</root>")
        lis = res.xpath("//li")
        for li in lis:
            meta = {
                "brandname": li.xpath("h3/a/text()")[0],
                "brandid": li.xpath("@id")[0].replace("b", "")
            }
            url = li.xpath("h3/a/@href")[0]
            yield scrapy.Request(url=response.urljoin(url), meta=meta, callback=self.parse_fnf, headers=self.headers,
                             dont_filter=True)

    def parse_fnf(self, response):
        dls = response.xpath("//*[@class='list-dl']")
        for dl in dls:
            factoryname = dl.xpath("dt/a/text()").extract_first()
            furl = dl.xpath("dt/a/@href").extract_first()
            factoryid = re.findall("\-(\d+)\.html", furl)[0]
            family_list = dl.xpath("dd/div[@class='list-dl-text']/a")
            for family in family_list:
                familyname = family.xpath("text()").extract_first()
                family_url = family.xpath("@href").extract_first()
                familyid = re.findall("series\-(\d+)[\-\.].*?html", family_url)[0]
                meta = {
                    "factoryname": factoryname,
                    "factoryid": factoryid,
                    "familyname": familyname.replace(u" (停售)", ""),
                    "familyid": familyid
                }
                yield scrapy.Request(url=response.urljoin(family_url), meta=dict(meta, **response.meta),
                                     callback=self.parse_family, dont_filter=True)

    def parse_family(self, response):
        pss = response.xpath("//*[@class='tab-nav border-t-no']/*[@data-trigger='click']/li")
        for ps in pss:
            if ps.xpath("@class").extract_first() == 'current':
                producestatus = ps.xpath("a/text()").extract_first()
            if ps.xpath("@class").extract_first() != 'current' and ps.xpath("@class").extract_first != 'disabled':
                yield scrapy.Request(url=response.urljoin(ps.xpath("a/@href").extract_first()), meta=response.meta,
                                     callback=self.parse_family2, dont_filter=True)

        next = response.xpath("//a[@class='page-item-next']")
        if next:
            yield scrapy.Request(url=response.urljoin(next.xpath('@href').extract_first()), meta=response.meta,
                                 callback=self.parse_family2, dont_filter=True)

        lis = response.xpath("//*[@class='interval01-list']/li")
        for li in lis:
            model = li.xpath("div/div/p/a/text()").extract_first()
            autohomeid = li.xpath("@data-value").extract_first()
            meta = {
                "producestatus": producestatus,
                "model": model,
                "autohomeid": autohomeid
            }
            url = "https://car.autohome.com.cn/config/spec/{}.html#pvareaid=3454541".format(autohomeid)
            #
            self.redis_tools(url + "*" + str(dict(meta, **response.meta)))

    def parse_family2(self, response):
        pss = response.xpath("//*[@class='tab-nav border-t-no']/*[@data-trigger='click']/li")
        for ps in pss:
            if ps.xpath("@class").extract_first() == 'current':
                producestatus = ps.xpath("a/text()").extract_first()

        next = response.xpath("//a[@class='page-item-next']")
        if next:
            yield scrapy.Request(url=response.urljoin(next.xpath('@href').extract_first()), meta=response.meta,
                                 callback=self.parse_family2, dont_filter=True)

        lis = response.xpath("//*[@class='interval01-list']/li")
        for li in lis:
            model = li.xpath("div/div/p/a/text()").extract_first()
            autohomeid = li.xpath("@data-value").extract_first()
            meta = {
                "producestatus": producestatus,
                "model": model,
                "autohomeid": autohomeid
            }
            url = "https://car.autohome.com.cn/config/spec/{}.html#pvareaid=3454541".format(autohomeid)
            self.redis_tools(url + "*" + str(dict(meta, **response.meta)))
