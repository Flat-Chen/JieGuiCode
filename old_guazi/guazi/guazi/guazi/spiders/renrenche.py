# -*- coding: UTF-8 -*-
import json
import re
import requests
import scrapy
from fontTools.ttLib import TTFont
from scrapy.conf import settings
from scrapy_redis.spiders import RedisSpider
import time
import logging
import xml.dom.minidom
from ..redis_bloom import BloomFilter
from ..items import GuaziItem

website = 'renrenche'


class CarSpider(scrapy.Spider):
    name = website
    # allowed_domains = ["renrenche.com"]
    start_urls = [
        "https://www.renrenche.com/sh/ershouche/"
    ]

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        self.bf = BloomFilter(key='b1f_' + website)
        settings.set('MYSQLDB_DB', 'usedcar_update', priority='cmdline')
        self.counts = 0
        self.page = 1
        self.id = 'rrcttf38b57967526a33b0a74086976c4bd887'
        self.note = {'1': '2', '4': '3', '7': '7', '8': '5', '3': '4', '9': '9', '5': '8', '2': '1', '0': '0', '6': '6'}
        self.headers = {'Referer': 'https://www.guazi.com/www/',
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], headers=self.headers, dont_filter=True)

    def parse(self, response):
        for href in response.xpath(
                '//div[@class="area-city-letter"]//a[contains(@class,"province-item")]/@href').extract():
            url = 'https://www.renrenche.com{}ershouche/?sort=publish_time&seq=desc'.format(href)
            yield scrapy.Request(url, callback=self.list_parse)

    def list_parse(self, response):
        for href in response.xpath('//li[contains(@class, "list-item")]'):
            datasave1 = href.extract()
            urlbase = href.xpath('a/@href').extract_first()
            url = response.urljoin(urlbase)
            yield scrapy.Request(url, meta={'datasave1': datasave1}, callback=self.parse_car)

        neighbor = response.xpath('//div[contains(text(), "附近城市车辆")]')
        if neighbor:
            return

        next_page = response.xpath('//a[@rrc-event-name="switchright"]/@href').extract_first()
        if 'javascript' not in next_page:
            url2 = response.urljoin(next_page)
            yield scrapy.Request(url2, callback=self.list_parse)

    def parse_car(self, response):
        if response.status == 200:
            self.counts += 1
            logging.log(msg="download  " + str(self.counts) + "  items", level=logging.INFO)

            rr = response.xpath('//*[@id="basic"]/div[1]/p/a[last()]/@class').extract_first()
            print(rr, '----', self.id)
            if rr != self.id:
                try:
                    self.note = self.woff(rr)
                    self.id = rr
                except Exception as e:
                    print('Get RR Fail, ', e)
                    return
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

            # key and status (sold or sale, price,time)
            if response.xpath("//*[@id='sold_button']"):
                status = "sold"
            else:
                status = "sale"

            try:
                # item loader
                item = GuaziItem()
                #
                item["carid"] = re.findall(r'/car/(.*)', response.url)[0]
                item["car_source"] = "renrenche"
                item["usage"] = None
                item["grab_time"] = grap_time
                item["update_time"] = None
                item["post_time"] = response.xpath('//span[contains(text(), "检测时间")]/text()').extract_first()
                item["sold_date"] = None
                item["pagetime"] = grap_time
                item["parsetime"] = grap_time
                # **********************************
                shortdesc = response.xpath('//h1[contains(@class, "title-name")]/text()').extract_first()
                if not shortdesc.strip():
                    shortdesc = response.xpath('//h1[contains(@class, "title-name")]/text()[2]').extract_first()
                item['shortdesc'] = self.transform(shortdesc).strip()

                item["pagetitle"] = response.xpath("//title/text()").extract_first().strip()
                item["url"] = response.url
                item["newcarid"] = None
                item["status"] = status
                item["brand"] = \
                    response.xpath('//p[@class="detail-breadcrumb-tagP"]/a[3]/text()').extract_first().split('二手')[1]
                item["series"] = \
                response.xpath('//p[@class="detail-breadcrumb-tagP"]/a[4]/text()').extract_first().split('二手')[1]
                item["factoryname"] = response.xpath(
                    '//div[@id="js-parms-table"]/table[1]//tr[2]/td[3]/div[2]/text()').extract_first().strip()
                item["modelname"] = None
                item["brandid"] = None
                item["familyid"] = None
                item["seriesid"] = None
                item['makeyear'] = \
                    re.findall(r'(\d{4}[年款])', response.xpath("//title/text()").extract_first())[0]

                # **************************


                item["produceyear"] = response.xpath('//*[contains(text(), "出厂日期")]/following-sibling::*[1]/text()').extract_first().strip()
                item["body"] = response.xpath('//div[contains(text(), "车身结构")]/../div[2]/text()').extract_first().strip()
                item["bodystyle"] = re.findall(r'单厢|两厢|三厢',response.xpath('//div[contains(text(), "车身结构")]/../div[2]/text()').extract_first())[0]

                item["level"] = response.xpath('//div[contains(text(), "车型")]/../div[2]/text()').extract_first().strip()
                item["fueltype"] = response.xpath(
                    '//div[contains(text(), "燃油形式")]/../div[2]/text()').extract_first().strip()
                item["driverway"] = response.xpath(
                    '//div[contains(text(), "驱动方式")]/../div[2]/text()').extract_first().strip()

                item["output"] = response.xpath('//div[contains(text(), "排量")]/../div[2]/text()').extract_first()
                item["guideprice"] =re.findall(r'\d+.\d+万', response.xpath('//div[@class="car-price-new"]/text()').extract_first())[0]
                # 新车指导价46.30万(含税)
                item["guidepricetax"] = response.xpath('//div[@class="new-car-price detail-title-right-tagP"]/span/text()').extract_first()
                item["doors"] = response.xpath(
                    '//div[contains(text(), "车门数")]/following-sibling::div[1]/text()').extract_first().split("：")[0].strip()
                item["emission"] = response.xpath('//*[contains(@class, "car-fluid-standard")]/div/p/strong/text()').extract_first().strip()
                item["gear"] = response.xpath('//div[contains(text(), "变速箱")]/following-sibling::div[1]/text()').extract_first()
                item["geartype"] = response.xpath('//li[@class="kilometre"][2]//strong/text()').extract_first().strip()
                item["seats"] = response.xpath('//div[contains(text(), "座位数")]/following-sibling::div[1]/text()'
                                               ).extract_first().strip()
                item["length"] = response.xpath(
                    '//div[contains(text(), "长度")]/following-sibling::div[1]/text()').extract_first().strip()
                item["width"] = response.xpath(
                    '//div[contains(text(), "宽度")]/following-sibling::div[1]/text()').extract_first().strip()
                item["height"] = response.xpath(
                    '//div[contains(text(), "高度")]/following-sibling::div[1]/text()').extract_first().strip()
                item["gearnumber"] = response.xpath(
                    '//div[contains(text(), "挡位个数")]/following-sibling::div[1]/text()').extract_first().strip()

                item["weight"] = response.xpath(
                    '//div[contains(text(), "整备质量")]/following-sibling::div[1]/text()').extract_first().strip()
                item["wheelbase"] = response.xpath(
                    '//div[contains(text(), "轴距")]/following-sibling::div[1]/text()').extract_first().strip()
                item["generation"] = None
                item["fuelnumber"] = response.xpath(
                    '//div[contains(text(), "燃油标号")]/following-sibling::div[1]/text()').extract_first().strip()

                item["lwv"] = response.xpath(
                    '//div[contains(text(), "气缸排列形式")]/following-sibling::div[1]/text()').extract_first().strip()
                item["lwvnumber"] = response.xpath(
                    '//div[contains(text(), "气缸数")]/following-sibling::div[1]/text()').extract_first().strip()
                item["maxnm"] = response.xpath(
                    '//div[contains(text(), "最大扭矩")]/following-sibling::div[1]/text()').extract_first().strip()
                item["maxpower"] = response.xpath(
                    '//div[contains(text(), "最大功率")]/following-sibling::div[1]/text()').extract_first().strip()

                item["maxps"] = response.xpath(
                    '//div[contains(text(), "最大马力")]/following-sibling::div[1]/text()').extract_first().strip()
                item["frontgauge"] = response.xpath(
                    '//div[contains(text(), "前轮距")]/following-sibling::div[1]/text()').extract_first().strip()
                item["compress"] = response.xpath(
                    '//div[contains(text(), "压缩比")]/following-sibling::div[1]/text()').extract_first().strip()
                # ********************
                registerdate = response.xpath('//*[@id="basic"]//p[contains(text(), "上牌")]/text()').extract_first()
                logging.log(msg=registerdate, level=logging.INFO)
                registerdate = re.findall(r'(.*)上牌', registerdate)[0]
                item['registerdate'] = self.transform(registerdate)

                item["years"] = None
                item["paytype"] = None
                item["price1"] = re.findall(r'\d+\.*\d*',response.xpath('//span[@class="price"]/text()').extract_first())[0]
                item["pricetag"] = None
                # ***********************
                mileage = response.xpath('//li[@class="kilometre"]//strong/text()').extract_first()
                item['mileage'] = self.transform(mileage)
                item["color"] = response.xpath(
                    '//*[contains(text(), "车身颜色")]/following-sibling::*[1]/text()').extract_first().strip()
                item["city"] =re.findall(r'检测城市：(.*)', response.xpath('//span[contains(text(), "检测城市")]/text()').extract_first())[0]
                item["prov"] = None
                # *****************************
                if response.xpath('//span[@class="zhimaicar-icon"]'):
                    item['guarantee'] = '严选车'
                else:
                    item['guarantee'] = '非严选车'

                # **************************
                totalcheck = response.xpath('//*[contains(text(), "综合车况")]/text()')
                if totalcheck:
                    item['totalcheck_desc'] = totalcheck.extract_first().strip()
                else:
                    item['totalcheck_desc'] = response.xpath('//*[@class="test-result"]/text()[2]').extract_first()

                try:
                    totalgrade = response.xpath('//img[contains(@src, "standard")]/@src').extract_first()
                except:

                    item["totalgrade"] = None
                else:
                    item["totalgrade"] = totalgrade
                item["contact_type"] =response.xpath('//ul[@class="owner-info"]/li[1]/text()[1]').extract_first()
                item["contact_name"] = re.findall(r'卖家-(.*)说车',response.xpath('//ul[@class="owner-info"]/h2/text()').extract_first())[0]
                item["contact_phone"] = None
                item["contact_address"] = response.xpath('//ul[@class="owner-info"]/li[2]/text()[1]').extract_first()
                item["contact_company"] = None
                item["contact_url"] = None
                item["change_date"] = None
                item["change_times"] =re.findall(r'\d+', response.xpath('//p[@class="transfer-record"]/strong/text()').extract_first())[0]
                item["insurance1_date"] = response.xpath('//td[contains(text(), "商业险到期时间")]/following-sibling::td[1]/text()').extract_first()
                item["insurance2_date"] = response.xpath('//td[contains(text(), "交强险到期时间")]/following-sibling::td[1]/text()').extract_first()
                item["hascheck"] = None
                item["repairinfo"] = response.xpath(
                    '//td[contains(text(), "是否4S店保养")]/following-sibling::td[1]/text()').extract_first()
                item["yearchecktime"] = response.xpath('//td[contains(text(), "年检到期时间")]/following-sibling::td[1]/text()').extract_first()
                item["carokcf"] = None
                item["carcard"] = None
                item["carinvoice"] = response.xpath('//div[@class="card-table"]/table/tr[2]/td[6]/text()').extract_first()
                item["accident_desc"] = response.xpath('//*[@id="report"]/div/div/div[3]/div[1]/text()[3]').extract_first()
                item["accident_score"] = None
                item["outer_desc"] = response.xpath('//table[@class="span6 col-2 case2"]//tr[1]/td[@class="test-fail-remark"]/text()[1] | //*[@id="gallery"]/div[1]/div[2]/div[1]/p/text()').extract_first()
                item["outer_score"] = None
                item["inner_desc"] =response.xpath('//table[@class="span6 col-2 case2"]//tr[2]/td[@class="test-fail-remark"]/text()[1] | //*[@id="gallery"]/div[1]/div[3]/div[1]/p/text()').extract_first()
                item["inner_score"] = None
                item["safe_desc"] = None
                item["safe_score"] = None
                item["road_desc"] = None
                item["road_score"] = response.xpath('//*[@id="start-report"]/text()[3]').extract_first()
                item["lastposttime"] = None
                item["newcartitle"] = None
                item["newcarurl"] = None
                item["img_url"] = response.xpath("//div[@class='recommend-img-container']/img[@class='main-pic']/@src").extract_first()
                item["first_owner"] = response.xpath(
                    '//div[contains(text(), "进气形式")]/../div[2]/text()').extract_first().strip()
                item["carno"] = response.xpath('//*[@id="car-licensed"]/text()').extract_first()
                item["carnotype"] = None
                item["carddate"] = None
                item["changecolor"] = None
                item["outcolor"] = None
                item["innercolor"] = None
                relt = re.findall(r'\d{4}', item['registerdate'])
                item['registeryear'] = relt[0] if relt else '-'
                item["desc"] = response.xpath('//div[@class="text-about-car-owner"]/p/text()').extract()[0]
                item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])
                print(item)

            except:
                log_dict["logType"] = 'ERROR'
                log_dict["logMessage"] = response.url
                logging.log(msg=json.dumps(log_dict, ensure_ascii=False), level=logging.INFO)
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
                logging.log(msg=json.dumps(log_dict, ensure_ascii=False), level=logging.INFO)
                yield item

            #

    # translate
    def woff(self, id):
        woff_url = 'https://misc.rrcimg.com/ttf/{}.woff'.format(id)
        url = 'http://120.27.216.150:5000'
        proxy = requests.get(url, auth=('admin', 'zd123456')).text[0:-6]
        proxies = {
            "http": "http://{}".format(proxy),
            "https": "http://{}".format(proxy),
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

        response_woff = requests.get(woff_url, headers=headers, proxies=proxies).content

        with open('fonts.woff', 'wb') as f:
            f.write(response_woff)

        onlineFonts = TTFont('fonts.woff')
        onlineFonts.saveXML('test.xml')

        dom = xml.dom.minidom.parse('test.xml')
        root = dom.documentElement
        flect = {'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6', 'seven': '7',
                 'eight': '8',
                 'nine': '9'}
        d = dict()
        for i in range(1, 11):
            temp = root.getElementsByTagName("GlyphID")[i].getAttribute("name")

            k = str(i - 1)
            v = flect[temp]
            d[v] = str(k)

        return d

    def transform(self, value):
        l = list()
        for i in range(len(value)):
            temp = value[i]
            if temp.isdigit():
                l.append(self.note[temp])
            else:
                l.append(value[i])
        return ''.join(l)
