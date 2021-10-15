# import logging
import html
import random
import json
import time

from lxml import etree
import re
import scrapy


class Xcar1Spider(scrapy.Spider):
    name = 'xcar1'
    allowed_domains = ['xcar.com.cn']
    start_urls = ["https://www.xcar.com.cn/bbs/"]
    brand_list = ['名爵', '荣威', '上海', '大众', '上汽大通MAXUS', '别克', '凯迪拉克', '雪佛兰', '宝骏', '五菱', '斯柯达']

    band_series = "斯柯达速尊论坛昕锐论明锐旅行版论坛探岳论坛新宝来论坛大众SMV论坛大众ID.4 CROZZ论坛大众二手件交流区大众ID.6 CROZZ论坛大众CC论坛高尔夫论坛高尔夫嘉旅论坛GTI论坛捷达论坛新捷达论坛开迪论坛|兄迪连揽境论坛迈腾论坛新速腾论坛探影论坛探歌论坛探岳GTE论坛蔚领论坛Amarok论坛大众论坛-进口大众Atlas论坛大众R-Model论坛大众蔚揽论坛大众XL1论坛大众EOS论坛大众凯路威论坛大众迈特威论坛大众ARTEON论坛Golf旅行轿车论坛大众新能源论坛高尔夫R论坛辉腾论坛甲壳虫论坛迈腾旅行轿车论坛R36论坛尚酷论坛尚酷R论坛途锐论坛大众up!论坛夏朗论坛昂科雷论坛别克荣御论坛凯迪拉克论坛凯迪拉克SRX论坛凯迪拉克CTS论坛凯迪拉克凯雷德科迈罗论坛斯帕可论坛Traverse论坛雪佛兰SS论坛雪佛兰论坛-进口雪佛兰沃蓝达Volt论"

    @classmethod
    def update_settings(cls, settings):
        settings.setdict(
            getattr(cls, 'custom_debug_settings' if getattr(cls, 'is_debug', False) else 'custom_settings', None) or {},
            priority='spider')

    is_debug = True
    custom_debug_settings = {
        # 'MYSQL_SERVER': '192.168.1.94',
        # 'MYSQL_USER': "dataUser94",
        # 'MYSQL_PWD': "94dataUser@2020",
        # 'MYSQL_PORT': 3306,
        # 'MYSQL_DB': 'saicnqms',
        # 'MYSQL_TABLE': 'luntan_all_copyjg1',
        'MONGODB_SERVER': '127.0.0.1',
        'MONGODB_PORT': 27017,
        'MONGODB_DB': 'xcar',
        'MONGODB_COLLECTION': 'xcar_luntan',
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0,
        'LOG_LEVEL': 'DEBUG',
        'RETRY_HTTP_CODES': [400, 403, 404, 408],
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
    }

    def __init__(self, **kwargs):
        super(Xcar1Spider, self).__init__()
        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"}
        self.counts = 0
        self.carnum = 2000000
        self.factory = {'名爵': '上汽乘用车',
                        '荣威': '上汽乘用车',
                        '上海': '上汽乘用车',
                        '斯柯达': '上汽大众',
                        '大众': '上汽大众',
                        '上汽大通MAXUS': '上汽大通',
                        '别克': '上汽通用',
                        '凯迪拉克': '上汽通用',
                        '雪佛兰': '上汽通用',
                        '宝骏': '上汽通用五菱',
                        '五菱': '上汽通用五菱',
                        }

    # 实现翻页，并且进入下一个循环
    def parse(self, response):
        luntans_url_list = response.xpath("//table")
        random.shuffle(luntans_url_list)
        for luntan_url in luntans_url_list:
            # 品牌的名字
            brand = luntan_url.xpath(".//tbody/tr/td/a/text()").extract_first()
            if brand not in self.brand_list:
                continue
            luntan_url_list = luntan_url.xpath(
                ".//div[@class='t0922_pidiva']/div[@class='t1203_fbox']//a/@href").extract()
            luntan_name_list = luntan_url.xpath(
                ".//div[@class='t0922_pidiva']/div[@class='t1203_fbox']//a/text()").extract()
            for i in range(len(luntan_name_list)):
                if luntan_name_list[i] in self.band_series:
                    continue
                # print(brand, luntan_name_list[i])
                fid_id = re.findall(r"//www.xcar.com.cn/bbs/forumdisplay.php\?fid=(\d*)", luntan_url_list[i])[0]
                url = "https://www.xcar.com.cn/bbs/xbbsapi/forumdisplay/get_thread_list.php?fid={}&orderby=lastpost&page=1".format(
                    fid_id)
                yield response.follow(url=url, headers=self.headers,
                                      callback=self.get_luntan,
                                      meta={
                                          "user_car": luntan_name_list[i],
                                          "page": 1,
                                          "fid_id": fid_id,
                                          "brand": brand,
                                          "factory": self.factory[brand]
                                      }, )

    #
    def get_luntan(self, response):
        # print(response.meta, "*" * 50)
        brand = response.meta["brand"]
        user_car = response.meta["user_car"]
        factory = response.meta["factory"]
        fid_id = response.meta["fid_id"]
        response.meta["page"] = response.meta["page"] + 1
        json_data = json.loads(response.text)
        for luntan_list in json_data['data']['data']['thread_list']:
            luntan_id = luntan_list['tid']

            # print(luntan_id)
            url = "http://www.xcar.com.cn/bbs/xbbsapi/forumdisplay/get_thread_list.php?fid={}&orderby=lastpost&page={}".format(
                fid_id, response.meta["page"])
            # print(url)
            #
            yield scrapy.Request(url=url, callback=self.get_luntan, headers=self.headers, meta={
                "brand": brand,
                "luntan_name_list": user_car,
                "factory": factory
            })


            # print(luntan_id)
            url = "http://www.xcar.com.cn/bbs/viewthread.php?tid={}".format(luntan_id)
            content = response.xpath('//div[@class="floor_div floor_div_e"]/div[@id="content"]/div/text()').extract_first()
            user_name = response.xpath('//div[@class="hover_box"]/div[@class="user"]/a/span[@class="name"]/text()').extract_first()
            try:
                province = response.xpath('//div[@class="clearfix place"]/span[@class="fl province"]/text()').extract_first()
            except:
                province = None
            try:
                region = response.xpat('//div[@class="clearfix place"]/span[@class="fl city"]/text()').extract_first()
            except:
                region = None
            posted_time = response.xpath('//div[@class="time"]/text()').extract_first()
            reply_num = response.xpath('//div[@class="information"]/div[@class="commentNum"]/span/text()').extract_first()
            click_num = response.xpath('//div[@class="information"]/div[@class="preview"]/text()').extract_first()
            content_num = response.xpath(
                '//div[@class="clearfix user_atten"]/div[@class="fl"][3]/span[@class="num"]/text()').extract_first()
            yield scrapy.Request(url=url, callback=self.parse_luntan, headers=self.headers,
                                 meta={
                                     "brand": brand,
                                     "luntan_name_list": user_car,
                                     "factory": factory,
                                     "content": content,
                                     "user_name": user_name,
                                     "reply_num": reply_num,
                                     "province": province,
                                     "region": region,
                                     "posted_time": posted_time,
                                     "click_num": click_num,
                                     "content_num": content_num
                                 })

    def parse_luntan(self, response):
        item = {}
        brand = response.meta["brand"]
        user_car = response.meta["luntan_name_list"]
        factory = response.meta["factory"]
        content = response.meta["content"]
        user_name = response.meta["user_name"]
        reply_num = response.meta["reply_num"]
        province = response.meta["province"]
        region = response.meta["region"]
        posted_time = response.meta["posted_time"]
        click_num = response.meta["click_num"]
        content_num = response.meta["content_num"]

        item["brand"] = brand
        item["information_source"] = 'xcar'
        item["factory"] = factory
        item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["parsetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["content"] = content
        item["url"] = response.url
        item["user_name"] = user_name
        item["posted_time"] = posted_time
        item["user_car"] = user_car
        item["province"] = province
        item["region"] = region
        item["click_num"] = click_num
        item["reply_num"] = reply_num
        item["content_num"] = content_num
        # item["statusplus"] = str(item["user_name"]) + str(item["title"]) + str(item["posted_time"]) + str(
        #     item["province"]) + str(item["brand"]) + str(item["click_num"]) + str(item["reply_num"]) + str(17)
        print(item)
