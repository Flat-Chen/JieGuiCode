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

website = 'autohome_newcar_zhu'

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
        super(CarSpider, self).__init__(**kwargs)
        self.mailer = MailSender.from_settings(settings)
        self.counts = 0
        self.carnum = 1010000
        # Mongo
        # settings.set('WEBSITE', website, priority='cmdline')
        settings.set('DOWNLOAD_DELAY', '0', priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MONGODB_DB', 'newcar', priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        self.nationp = dict()
        self.npcounts = 0

        self.headers = {'Referer': 'https://car.autohome.com.cn/',
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
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

    def get_url(self):
        sum = redis_cli.scard('autohome_newcar')
        if sum <= 0:
            return False
        else:
            return redis_cli.smembers('autohome_newcar', )

    def start_requests(self):
        url_dict_list = self.get_url()
        for url_dict in url_dict_list:
            url_dict = str(url_dict, encoding='utf-8')
            url = url_dict.split("*")[0]
            meta = eval(url_dict.split("*")[1])
            print(url, meta)
            yield scrapy.Request(url=url, headers=self.headers, meta=meta)

    def parse(self, response):
        yingshe_dict = {}
        js_text = re.findall(r"<script>(.*?);</script>", response.text)
        for js in js_text:
            if "</style><script>" in js:
                js = js.split("</style><script>")[1]
            code1 = js.replace('\n', '')
            code = self.js_header + code1.replace("})(document)", "") + self.js_end
            js_code = execjs.compile(code)
            a = js_code.call('get_obj')
            yingshe_dict.update(a)
        try:
            config = re.findall(r"var config = (.*?);", response.text)[0]
        except:
            config = None
        try:
            option = re.findall(r"var option = (.*?);", response.text.replace("&nbsp;", "").replace("&amp;", ""))[0]
        except:
            option = None
        try:
            color = re.findall(r"var color = (.*?);", response.text)[0]
            color = eval(color)
        except:
            color = None
        try:
            innercolor = re.findall(r"var innerColor =(.*?);", response.text)[0]
            innercolor = eval(innercolor)
        except:
            innercolor = None
        for i in yingshe_dict:
            config = config.replace(i, yingshe_dict[i])
            option = option.replace(i, yingshe_dict[i])
        config = eval(config)
        option = eval(option)
        config_list = [option, config]
        config_dict = {}
        for aa in config_list:
            for i in aa["result"]:
                try:
                    configtypeitems = aa["result"]["configtypeitems"]
                except:
                    configtypeitems = aa["result"]["paramtypeitems"]
                for gg in configtypeitems:
                    use_dict = {}
                    try:
                        config_end = gg['configitems']
                    except:
                        config_end = gg['paramitems']
                    for ff in config_end:
                        name = ff["name"]
                        for value in ff["valueitems"][0:1]:
                            try:
                                if len(value['sublist']) > 0:
                                    ff = ""
                                    for i in value["sublist"]:
                                        ff = ff + i["subname"] + ","
                                    use_dict.update({name: ff})
                                else:
                                    use_dict.update({name: value["value"]})
                            except:
                                use_dict.update({name: value["value"]})
                        config_dict.update({gg['name']: use_dict})
        color_list = []
        for i in color["result"]["specitems"]:
            for x in i["coloritems"]:
                color_list.append(x["name"])
        innercolor_list = []
        for i in innercolor["result"]["specitems"]:
            for x in i["coloritems"]:
                innercolor_list.append(x["name"])
        item = autohome_newcar()
        item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["configs"] = json.dumps(config_dict, ensure_ascii=False)
        item["brandname"] = response.meta["brandname"]
        item["brandid"] = response.meta["brandid"]
        item["factoryname"] = response.meta["factoryname"]
        item["factoryid"] = response.meta["factoryid"]
        item["familyname"] = response.meta["familyname"]
        item["familyid"] = response.meta["familyid"]
        item["producestatus"] = response.meta["producestatus"]
        item["model"] = response.meta["model"]
        item["autohomeid"] = response.meta["autohomeid"]
        item["shortdesc"] = config_dict['基本参数']["车型名称"]
        item["guideprice"] = config_dict['基本参数']["厂商指导价(元)"]
        item["statusplus"] = response.url + item["configs"] + str(11111111115545551165521511)+str(item["factoryname"])+str(item["familyname"])+str(item["factoryid"])+str(item["familyid"])+str(item["brandname"])+str(item["brandid"])
        item["color"] = str(color_list)
        item["year"] = re.findall(r"(\d+)款", item["shortdesc"])[0]
        item["innercolor"] = str(innercolor_list)
        url = "https://dealer.api.autohome.com.cn/dealerrest/price/GetMinPriceBySpecSimple?specids={}&_appId=cms".format(
            item["autohomeid"])
        yield scrapy.Request(url=url, meta={"item": item}, headers=self.headers, callback=self.deal_prcie)

    def deal_prcie(self, response):
        # print(response.url)
        text = json.loads(response.text)["result"]["list"]
        item = response.meta["item"]
        try:
            item["dealprice"] = text[0]["MinPrice"]
        except:
            item["dealprice"] = None
        yield item
