import copy
import hashlib
import json
import time

import re

from ..items import che58_newcar
import scrapy
from scrapy.conf import settings

website = 'che58_newcar'


# 先循环城市 然后在循环车
class CarSpider(scrapy.Spider):
    name = website
    start_urls = [
        "https://product.58che.com/price_list/brand_1_1.shtml"]
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'Sec-Fetch-Dest': 'document',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 15,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        settings.set("MONGODB_DB", "newcar", priority="cmdline")
        self.counts = 0

    def parse(self, response):
        brand_list = response.xpath("//a[@class='first']/@title").extract()
        brand_id_list = response.xpath("//a[@class='first']/@href").extract()
        brand_dict = dict(zip(brand_list, brand_id_list))
        for i in brand_dict.items():
            brand_id = re.findall("_(\d*)_", i[1])[0]
            url = "https://product.58che.com/index.php?c=Ajax_AjaxFirmCarLine"
            yield scrapy.FormRequest(url=url, formdata={"brandId": brand_id},
                                     meta={"brand_name": i[0], "brand_id": brand_id}, callback=self.parse_fnf,
                                     headers=self.headers,
                                     dont_filter=True)

    def parse_fnf(self, response):
        data = json.loads(response.text)
        for i in data['firmCarLineArr']:
            for j in data['firmCarLineArr'][i]:
                for z in data['firmCarLineArr'][i][j]:
                    factoty_name = data['firmCarLineArr'][i][j]["name"]
                    factoty_id = data['firmCarLineArr'][i][j]["firmId"]
                    if isinstance(data['firmCarLineArr'][i][j]["lineInfo"], dict):
                        for x in data['firmCarLineArr'][i][j]["lineInfo"].items():
                            serier_name = x[1]["name"]
                            factoty_name = factoty_name
                            factoty_id = factoty_id
                            serier_id = x[1]["lineId"]
                            url = "https://product.58che.com" + x[1]["lineUrl"]
                            url_list = []
                            id = url.split("/")[-2]
                            url_list.append({"url": "https://product.58che.com/price_list/{}/page_4.shtml".format(id),
                                             "stat": "停售"})  # 4
                            url_list.append({"url": "https://product.58che.com/price_list/{}/page_2.shtml".format(id),
                                             "stat": "停产在售"})  # 2
                            url_list.append({"url": "https://product.58che.com/price_list/{}/page_3.shtml".format(id),
                                             "stat": "即将上市"})
                            url_list.append({"url": "https://product.58che.com/price_list/{}/page_1.shtml".format(id),
                                             "stat": "在售"})
                            for c in url_list:
                                item = {}
                                item["serier_name"] = serier_name
                                item["factoty_name"] = factoty_name
                                item["factoty_id"] = factoty_id
                                item["serier_id"] = serier_id
                                item["stat"] = c["stat"]
                                item["used_url"] = c["url"]
                                response.meta.update(item)
                                meta = copy.deepcopy(response.meta)
                                print(meta)

                                yield scrapy.Request(url=c["url"], meta=meta, headers=self.headers,
                                                     callback=self.parse_family,dont_filter=True)
                    else:
                        for x in data['firmCarLineArr'][i][j]["lineInfo"]:
                            serier_name = x["name"]
                            factoty_name = factoty_name
                            factoty_id = factoty_id
                            serier_id = x["lineId"]
                            url = "https://product.58che.com/" + x["lineUrl"]
                            url_list = []
                            id = url.split("/")[-2]
                            url_list.append({"url": "https://product.58che.com/price_list/{}/page_4.shtml".format(id),
                                             "stat": "停售"})  # 4
                            url_list.append({"url": "https://product.58che.com/price_list/{}/page_2.shtml".format(id),
                                             "stat": "停产在售"})  # 2
                            url_list.append({"url": "https://product.58che.com/price_list/{}/page_3.shtml".format(id),
                                             "stat": "即将上市"})
                            url_list.append({"url": "https://product.58che.com/price_list/{}/page_1.shtml".format(id),
                                             "stat": "在售"})
                            for c in url_list:
                                item = {}
                                item["serier_name"] = serier_name
                                item["factoty_name"] = factoty_name
                                item["factoty_id"] = factoty_id
                                item["serier_id"] = serier_id
                                item["stat"] = c["stat"]
                                item["used_url"] = c["url"]
                                response.meta.update(item)
                                meta = copy.deepcopy(response.meta)
                                print(meta)
                                yield scrapy.Request(url=c["url"], meta=meta, headers=self.headers,
                                                     callback=self.parse_family,dont_filter=True)

    def parse_family(self, response):
        url_list = response.xpath("//td[@class='marg']/a[1]/@href").extract()
        for url in url_list:
            url = "https:" + url.replace("config", "param")
            yield scrapy.Request(url=url, meta=response.meta, headers=self.headers,
                                 callback=self.parse_family2,dont_filter=True)

    def md5_encryption(self, data):
        # 获取sign
        m = hashlib.md5()
        url_md5 = (data).encode(encoding='utf-8')
        m.update(url_md5)
        url_md5 = m.hexdigest()
        return url_md5
    def parse_family2(self, response):
        canshu_list = response.xpath("//div[@id='peizhi']//td")
        canshu_dict = {}
        for i in canshu_list:
            canshu_key = i.xpath(".//span[1]/text()").extract_first()
            if canshu_key == None:
                canshu_key = i.xpath(".//a/text()").extract_first()
            canshu_value = i.xpath(".//span[2]/text()").extract_first()
            if canshu_key != None:
                canshu_dict.update({canshu_key: canshu_value})
        item = che58_newcar()
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["brand_name"] = response.meta["brand_name"]
        item["brand_id"] = response.meta["brand_id"]
        item["serier_id"] = response.meta["serier_id"]
        item["serier_name"] = response.meta["serier_name"]
        item["factoty_name"] = response.meta["factoty_name"]
        item["factoty_id"] = response.meta["factoty_id"]
        car_stat = response.meta["used_url"].split("/")[-1]
        if '1' in car_stat:
            item["stat"] = "在售"
        elif '2' in car_stat:
            item["stat"] = "停产在售"
        elif '3' in car_stat:
            item["stat"] = "即将上市"
        elif '4' in car_stat:
            item["stat"] = "停售"
        item["model_id"] = re.findall("/(\d*)/param", response.url)[0]
        item["model_name"] = response.xpath("//h3/a/text()").extract_first()
        item["short_desc"] = response.xpath("//h3/a/text()").extract_first()
        item["Dealer_price"] = response.xpath("//span[contains(text(),'经销商报价：')]/../span[2]/text()").extract_first()
        item["guide_price"] = response.xpath("//span[contains(text(),'厂商指导价')]/../span[2]/text()").extract_first()
        item["speed"] = response.xpath("//span[contains(text(),'变速箱：')]/../span[2]/text()").extract_first()
        item["output"] = response.xpath("//span[contains(text(),'排量')]/../span[2]/text()").extract_first()
        item["drive_type"] = response.xpath("//span[contains(text(),'驱动方式')]/../span[2]/text()").extract_first()
        item["doors"] = response.xpath("//span[contains(text(),'车门数')]/../span[2]/text()").extract_first()
        item["seat"] = response.xpath("//span[contains(text(),'座位')]/../span[2]/text()").extract_first()
        item["air_inlet"] = response.xpath("//span[contains(text(),'进气')]/../span[2]/text()").extract_first()
        item["fuel_type"] = response.xpath("//span[contains(text(),'燃油类型')]/../span[2]/text()").extract_first()
        item["body"] = response.xpath("//span[contains(text(),'车身结构')]/../span[2]/text()").extract_first()
        item["makeyear"] = response.xpath("//span[contains(text(),'款型')]/../span[2]/text()").extract_first()
        item["environment"] = json.dumps(canshu_dict, ensure_ascii=False)
        item["statusplus"] = response.url + self.md5_encryption(str(canshu_dict)) + str(3)
        yield item
