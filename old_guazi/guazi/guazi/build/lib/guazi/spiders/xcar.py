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

website = 'xcar'

class CarSpider(scrapy.Spider):
    name = website
    allowed_domains = ["used.xcar.com.cn"]
    # start_urls = get_url()
    start_urls = 'https://used.xcar.com.cn/'
    parse_url = "http://used.xcar.com.cn/search/2-507-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0/?page=1"
    headers = {
        'referer': 'https://used.xcar.com.cn/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 10,
        # 'RANDOMIZE_DOWNLOAD_DELAY': True,

    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, headers=self.headers, dont_filter=True)

    def parse(self, response):
        count = response.xpath("//span[@class='car_source']/b/text()").extract_first()
        page = int(count) // 40
        for i in range(page + 1)[:]:
            print('当前处理的页数：', i)
            url = "http://used.xcar.com.cn/search/2-507-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0/?page={}".format(str(i))
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_car)

    def parse_car(self, response):
        car_url_list = response.xpath("//ul[@class='cal_ul clearfix']/li/a/@href").extract()
        for url in car_url_list:
            yield response.follow(url=url, callback=self.parse_car_diatl, headers=self.headers)

    def parse_car_diatl(self, response):
        grap_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        self.counts += 1
        logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)
        item = GuaziItem()
        item["carid"] = re.findall(r'/p(\d+?)\.html', response.url)[0]
        item["car_source"] = "xcar"
        item["usage"] = response.xpath('//div[@class="tag_item tag_blue"]/span/text()').extract_first()
        item["grab_time"] = grap_time
        item["update_time"] = None
        item["post_time"] = response.xpath('//div[@class="fr"]/text()').extract_first().split("：")[1]
        item["sold_date"] = None
        item["pagetime"] = None
        item["parsetime"] = grap_time
        item["shortdesc"] = response.xpath('//div[@class="datum_right"]/h1/text()').extract_first()
        item["pagetitle"] = response.xpath("//head/title/text()").extract_first().strip("-爱卡汽车二手车")
        item["url"] = response.url
        item["newcarid"] = re.findall(r"mid: (\d*),", response.text)[0]
        item["status"] = "sale"
        item["brand"] = response.xpath('//div[@class="fl"]//h2/text()').extract_first().split(" ")[0]
        item["series"] = response.xpath('//div[@class="fl"]//h2/text()').extract_first().split(" ")[1]
        item["factoryname"] = response.xpath('//td[text()="品牌"]/following-sibling::td[1]/text()').extract_first()
        item["modelname"] = None
        item["brandid"] = None
        item["familyid"] = None
        item["seriesid"] = None
        for yea in response.xpath("//div[@class='fl']//h2/text()").extract_first().split():
            if re.findall(r'\d{4}款', yea):
                item['makeyear'] = re.findall(r'\d{4}款', yea)[0]
        item["registeryear"] = None
        item["produceyear"] = response.xpath('//td[text()="上市年份"]/following-sibling::td[1]/text()').extract_first()
        item["body"] = response.xpath('//td[text()="车身结构"]/following-sibling::td[1]/text()').extract_first()
        item["bodystyle"] = response.xpath('//td[contains(text(), "车门数")]/../td[2]/text()').extract_first()

        item["level"] = response.xpath('//td[text()="级别"]/following-sibling::td[1]/text()').extract_first()
        item["fueltype"] = response.xpath(
            '//td[contains(text(), "燃料")]/following-sibling::td[1]/text()').extract_first()
        item["driverway"] = response.xpath(
            '//td[contains(text(), "驱动方式")]/following-sibling::td[1]/text()').extract_first()
        item["output"] = response.xpath('//dd[contains(text(), "排量")]/../dt/text()').extract_first()
        item["guideprice"] = response.xpath('//p[@class="cost"]/span[3]/text()').extract_first().split("：")[1]
        # 新车指导价46.30万(含税)
        item["guidepricetax"] = None
        item["doors"] = response.xpath(
            '//td[contains(text(), "车门数")]/following-sibling::td[1]/text()').extract_first().split("：")[0]
        item["emission"] = response.xpath('//dd[contains(text(), "环保标准")]/../dt/text()').extract_first()
        item["gear"] = response.xpath('//td[text()="变速箱"]/following-sibling::td[1]/text()').extract_first()
        item["geartype"] = response.xpath('//dd[contains(text(), "变速箱")]/../dt/text()').extract_first()
        item["seats"] = response.xpath('//td[contains(text(), "座位数")]/following-sibling::td[1]/text()'
                                        ).extract_first()
        item["length"] = response.xpath(
            '//td[contains(text(), "车长")]/following-sibling::td[1]/text()').extract_first().split(
            "/")[0]
        item["width"] = response.xpath(
            '//td[contains(text(), "车宽")]/following-sibling::td[1]/text()').extract_first().split(
            "/")[0]
        item["height"] = response.xpath(
            '//td[contains(text(), "车高")]/following-sibling::td[1]/text()').extract_first().split(
            "/")[0]
        item["gearnumber"] = response.xpath(
            '//td[contains(text(), "挡位个数")]/following-sibling::td[1]/text()').extract_first()

        item["weight"] = response.xpath('//td[contains(text(), "车重")]/following-sibling::td[1]/text()').extract_first()
        item["wheelbase"] = response.xpath(
            '//td[contains(text(), "轴距")]/following-sibling::td[1]/text()').extract_first()
        item["generation"] = None
        item["fuelnumber"] = response.xpath(
            '//td[contains(text(), "燃油标号")]/following-sibling::td[1]/text()').extract_first()
        item["lwv"] = response.xpath('//td[contains(text(), "气缸排列形式")]/following-sibling::td[1]/text()').extract_first()
        item["lwvnumber"] = response.xpath(
            '//td[contains(text(), "汽缸数")]/following-sibling::td[1]/text()').extract_first()
        item["maxnm"] = response.xpath('//td[contains(text(), "最大扭矩")]/following-sibling::td[1]/text()').extract_first()
        item["maxpower"] = response.xpath(
            '//td[contains(text(), "最大功率")]/following-sibling::td[1]/text()').extract_first()
        item["maxps"] = response.xpath('//td[contains(text(), "最大马力")]/following-sibling::td[1]/text()').extract_first()
        item["frontgauge"] = response.xpath(
            '//td[contains(text(), "前轮距")]/following-sibling::td[1]/text()').extract_first()
        item["compress"] = response.xpath(
            '//td[contains(text(), "压缩比")]/following-sibling::td[1]/text()').extract_first()
        item["registerdate"] = response.xpath('//dd[contains(text(), "上牌时间")]/../dt/text()').extract_first()
        item["years"] = None
        item["paytype"] = None
        item["price1"] = response.xpath('//p[@class="cost"]/span/b/text()').extract_first().strip("￥")
        item["pricetag"] = None
        item["mileage"] = response.xpath('//dd[contains(text(), "表显里程")]/../dt/text()').extract_first()
        item["color"] = response.xpath(
            '//div[@class="tag_mian"]/div[2]/table/tbody/tr[2]/td[4]/span/text()').extract_first()
        item["city"] = response.xpath('//div[@class="fl"]/a[2]/text()').extract_first().strip("二手车")
        item["prov"] = response.xpath(
            '//div[@class="tag_mian"]/div[2]/table/tbody/tr[1]/td[2]/span/text()').extract_first()
        item["guarantee"] = None
        try:
            totalcheck_desc = response.xpath(
                '//div[@class="ensure"]/span[@class="full"]/text()').extract_first().split("/")[0]
        except Exception as  e:
            print(repr(e))
            item["totalcheck_desc"] = None
        else:
            item["totalcheck_desc"] = totalcheck_desc
        try:
            totalgrade = response.xpath('//div[@class="WoM_left"]/p/b/text()').extract_first().split("\n")[0]
        except:

            item["totalgrade"] = None
        else:
            item["totalgrade"] = totalgrade
        item["contact_type"] = None
        item["contact_name"] = None
        item["contact_phone"] = None
        item["contact_address"] = response.xpath('//div[@class="location"]/text()').extract_first()
        item["contact_company"] = None
        item["contact_url"] = None
        item["change_date"] = None
        item["change_times"] = None
        item["insurance1_date"] = response.xpath('//dd[contains(text(), "保险有限期")]/../dt/text()').extract_first()
        item["insurance2_date"] = None
        item["hascheck"] = None
        item["repairinfo"] = response.xpath(
            '//div[@class="tag_mian"]/div[2]/table/tbody/tr[2]/td[6]/span/text()').extract_first()
        item["yearchecktime"] = response.xpath('//dd[contains(text(), "年检有限期")]/../dt/text()').extract_first()
        item["carokcf"] = None
        item["carcard"] = None
        item["carinvoice"] = None
        item["accident_desc"] = None
        item["accident_score"] = None
        item["outer_desc"] = None
        item["outer_score"] = response.xpath('//ul[@class="grade_ul"]/li[1]/div[1]/text()[2]').extract_first()
        item["inner_desc"] = None
        item["inner_score"] = response.xpath('//ul[@class="grade_ul"]/li[2]/div[1]/text()[2]').extract_first()
        item["safe_desc"] = None
        item["safe_score"] = None
        item["road_desc"] = None
        item["road_score"] = response.xpath('//ul[@class="grade_ul"]/li[6]/div[1]/text()[2]').extract_first()
        item["lastposttime"] = None
        item["newcartitle"] = None
        item["newcarurl"] = None
        item["img_url"] = response.xpath('//*[@id="datumimg"]/img/@src').extract_first()
        item["first_owner"] = response.xpath(
            '//td[contains(text(), "进气形式")]/following-sibling::td[1]/text()').extract_first()
        item["carno"] = response.xpath('//dd[contains(text(), "上牌地")]/../dt/text()').extract_first()
        item["carnotype"] = None
        item["carddate"] = None
        item["changecolor"] = None
        item["outcolor"] = None
        item["innercolor"] = None
        item["desc"] = response.xpath('//div[@class="describe"]/p/text()').extract()
        item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])

        yield item
        # print(item)