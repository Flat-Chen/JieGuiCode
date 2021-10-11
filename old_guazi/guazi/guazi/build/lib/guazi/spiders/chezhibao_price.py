# -*- coding: UTF-8 -*-
import base64
import datetime
import random
import re

import pandas as pd
import requests

import scrapy
from scrapy.conf import settings
from sqlalchemy import create_engine
from pymysql import *
from ..items import GuaziItem
import time
import logging
from PIL import Image
import pytesseract

# 上面都是导包，只需要下面这一行就能实现图片文字识别
website = 'chezhibao_price'


# original
class CarSpider(scrapy.Spider):
    # basesetting
    name = website

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        "REDIRECT_ENABLED": True,
        "DOWNLOADER_MIDDLEWARES" : {
        "guazi.proxy.ProxyMiddleware": 530

    }

    }

    def __init__(self, **kwargs):
        # args
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        self.engine_huachen = create_engine(
            'mysql+pymysql://dataUser94:94dataUser@2020@192.168.1.94:3306/usedcar_update?charset=utf8')
        self.con = connect(host="192.168.1.94", port=3306, user="dataUser94",
                           password="94dataUser@2020",
                           database='usedcar_update', charset='utf8')
        self.cs1 = self.con.cursor()

        # setting
        self.counts = 0
        self.headers1 = {

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            "Referer": "https://www.chezhibao.com/"

        }

    def get_url_list(self):
        huachen_df = pd.read_sql("select id,url from chezhibao_online where price1 is null", con=self.engine_huachen)
        return huachen_df.values.tolist()

    def start_requests(self):
        url_list = self.get_url_list()
        for url in url_list:
            start_url = url[1]
            id = url[0]
            # start_url ="https://quanguo.58.com/ershouche/40369562775564x.shtml"
            # id=1
            yield scrapy.Request(url=start_url, headers=self.headers1, meta={'id': id, 'url': start_url})

    def save_data(self, id, mileage):
        sql = 'update chezhibao_online set price1 ={} where id ={}'.format(mileage, id)
        self.cs1.execute(sql)
        # print(sql.format({"liangdian":item["liangdian"]}, item["carid"]))
        logging.log(msg="updata" + str(id) + "success!!!!!!!!", level=logging.INFO)
        self.con.commit()

    def deal_img(self):
        # linux
        a = Image.open('/home/mywork/chezhibao_img/chezhibao_price.jpg')
        # window
        # a = Image.open('./test1.jpg')
        text = pytesseract.image_to_string(a, lang='chi_sim')
        return text.strip("万")

    def parse(self, response):
        img_data = response.xpath("//img[@class='pic_price __big']/@src").extract_first()
        img_data = re.findall(r'data:image/png;base64,(.*)', img_data)[0]
        price_img = base64.b64decode(img_data)
        # window
        # with open("./test1.jpg", "bw") as f:
            # linux
        with open("/home/mywork/chezhibao_img/chezhibao_price.jpg", "bw") as f:
            f.write(price_img)
        price1 = self.deal_img()
        # print(price1)
        self.save_data(response.meta["id"], price1)

    def close_spider(self, spider, ):
        self.cs1.close()
        self.con.close()
