# -*- coding: UTF-8 -*-
import datetime
import random
import re

import pandas as pd
import requests

import scrapy
from scrapy.conf import settings
from sqlalchemy import create_engine
from pymysql import *
import time
import logging

website = 'qichejie_stauts'


# original
class CarSpider(scrapy.Spider):
    # basesetting
    name = website

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        "REDIRECT_ENABLED": True
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
        self.headers = {

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
        }

    def get_url_list(self):
        huachen_df = pd.read_sql("select id,url from qichejie_online", con=self.engine_huachen)
        return huachen_df.values.tolist()

    def start_requests(self):
        url_list = self.get_url_list()
        for url in url_list:
            start_url = url[1]
            id = url[0]
            yield scrapy.Request(url=start_url, headers=self.headers, meta={'id': id, 'url': start_url},
                                 dont_filter=True)

    def save_data(self, id, mileage):
        print(id,mileage)
        sql = 'update qichejie_online set status = "{}" where id ="{}"'.format(mileage, id)
        print(sql)
        self.cs1.execute(sql)
        # print(sql.format({"liangdian":item["liangdian"]}, item["carid"]))
        logging.log(msg="updata" + str(id) + "success!!!!!!!!", level=logging.INFO)
        self.con.commit()

    def parse(self, response):
        mileage = response.xpath("//p[@class='detail-status-2']/text()").extract_first()
        if mileage ==None:
            mileage = response.xpath("//span[contains(@class,'auction-status')]/text()").extract_first()
        if '流拍' in mileage:
            mileage ='sale'
        else:
            mileage ='sold'
        self.save_data(response.meta["id"], mileage)


    def close_spider(self, spider, ):
        self.cs1.close()
        self.con.close()
