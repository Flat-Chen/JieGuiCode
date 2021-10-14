# import logging
import html
import random
import json
from lxml import etree
import re
import scrapy


class Xcar1Spider(scrapy.Spider):
    name = 'xcar1'
    allowed_domains = ['xcar.com.cn']
    start_urls = ["https://www.xcar.com.cn/bbs/"]
    brand_list = ['名爵', '荣威', '上海', '大众', '上汽大通MAXUS', '别克', '凯迪拉克', '雪佛兰', '宝骏', '五菱', '斯柯达']

    factory = {'名爵': '上汽乘用车',
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
                print(brand, luntan_name_list[i])
                fid_id = re.findall(r"//www.xcar.com.cn/bbs/forumdisplay.php\?fid=(\d*)", luntan_url_list[i])[0]
                url = "https://www.xcar.com.cn/bbs/xbbsapi/forumdisplay/get_thread_list.php?fid={}&orderby=lastpost&page=1".format(
                    fid_id)
                yield response.follow(url=url, headers=self.headers,
                                      callback=self.get_luntan,
                                      meta={"user_car": luntan_name_list[i],
                                            "page": 1,
                                            "fid_id": fid_id,
                                            "brand": brand,
                                            "factory": self.factory[brand]
                                            },)




    #
    def get_luntan(self, response):
        # print(response.meta["brand"], response.meta["user_car"], "*" * 50)
        brand=response.meta["brand"]
        luntan_name_list=response.meta["user_car"]
        fid_id=response.meta["fid_id"]
        response.meta["page"] = response.meta["page"] + 1
        json_data = json.loads(response.text)
        for luntan_list in json_data['data']['data']['thread_list']:
            luntan_id_list=luntan_list['tid']
            url = "http://www.xcar.com.cn/bbs/xbbsapi/forumdisplay/get_thread_list.php?fid={}&orderby=lastpost&page={}".format(
                fid_id, response.meta["page"])
            print(url)
            # yield scrapy.Request(url=url, callback=self.get_luntan, headers=self.headers, meta=response.meta)
            # for luntan_id in luntan_id_list:
            #     url = "http://www.xcar.com.cn/bbs/viewthread.php?tid={}".format(luntan_id)
            #     print(url)
                # valid = self.redis_tools(url)
                # if valid == 0:
                #     logging.log(msg="this http request is repetition", level=logging.INFO)
                #     continue
                # else:
                # yield scrapy.Request(url=url, callback=self.parse_luntan, headers=self.headers,
                #                          meta=response.meta)

    # def parse_luntan(self, response):
    #
    #     content=html.xpath('//div[@class="floor_div floor_div_e"]/div[@id="content"]/div/text()')[0]
    #     user_name=html.xpath('')

    # def get_luntan(self, response):
    #     # user_car = response.meta["luntan_name_list[i]"]
    #     # factory = response.meta["self.factory[brand]"]
    #     print(response.meta["brand"], response.meta["user_car"], "*" * 50)
    #     response.meta["page"] = response.meta["page"] + 1
    #     # print(response.meta)
    #     luntan_id_list = response.text.encode('utf8').decode('unicode_escape').replace(
    #         r'"videos":"{"num":0,"list":[]}",', "")
    #     luntan_id_list = re.findall(r'"tid":(\d*),"subject"', luntan_id_list)
    #     if luntan_id_list == []:
    #         return
    #     else:
    #         url = "http://www.xcar.com.cn/bbs/xbbsapi/forumdisplay/get_thread_list.php?fid={}&orderby=lastpost&page={}".format(
    #             response.meta["fid_id"], response.meta["page"])
    #         yield scrapy.Request(url=url, callback=self.get_luntan, headers=self.headers, meta=response.meta)
    #         for luntan_id in luntan_id_list:
    #             url = "http://www.xcar.com.cn/bbs/viewthread.php?tid={}".format(luntan_id)
    #             valid = self.redis_tools(url)
    #             if valid == 0:
    #                 logging.log(msg="this http request is repetition", level=logging.INFO)
    #                 continue
    #             else:
    #                 yield scrapy.Request(url=url, callback=self.parse_luntan, headers=self.headers,
    #                                      meta=response.meta)





























# def parse(self, response):
#     json_data = json.loads(response.text)
#     for brand_id in json_data['var _cartype'].keys():
#         for forum_list in json_data['var _cartype'][forum_list]:
#             forum_name=forum_list['forumName']
#             forum_id=forum_list['forumId']
#             url='view-source:https://www.xcar.com.cn/bbs/forumdisplay.php?fid={}'.format(forum_id)
#             yield scrapy.Request(url=url, callback=self.,
#                                  meta={
#                                      'forum_name': forum_name,
#                                  })





