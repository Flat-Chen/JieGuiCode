# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import re
import sys
import time

import scrapy

# 爬虫名
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from ..items import dongchedi2

website = 'dongchedi2'


# 必须有自己的中间件  切与其他的没有关系
class GuazicarSpider(scrapy.Spider):
    name = website
                # https://www.dcdapp.com/motor/discuss_ugc/cheyou_feed_list_v3/v1/
    start_urls = "https://www.dcdapp.com/motor/discuss_ugc/cheyou_feed_list_v3/v1/?motor_id={}&channel=m_web&device_platform=wap&category=dongtai&cmg_flag=dongtai&min_behot_time=&max_behot_time=&max_cursor=&web_id=0&device_id=0&impression_info=%7B%22page_id%22%3A%22page_forum_home%22%2C%22product_name%22%3A%22pc%22%7D&tt_from=load_more"
    seconde_url = "https://www.dcdapp.com/motor/discuss_ugc/cheyou_feed_list_v3/v1/?motor_id={}&channel=m_web&device_platform=wap&category=dongtai&cmg_flag=dongtai&min_behot_time=&max_behot_time=&max_cursor={}&web_id=0&device_id=0&impression_info=%7B%22page_id%22%3A%22page_forum_home%22%2C%22product_name%22%3A%22pc%22%7D&tt_from=load_more"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://www.dcdapp.com/auto",
    }
    brand_dict = {1120028430000000: "蔚来ES6", 630037620000000: "特斯拉Model 3", 160030770000000: "比亚迪唐EV",
                  160035050000000: "比亚迪宋Pro EV",
                  2420035030000000: "广汽AION LX", 360011830000000: "荣威eRX5", 1950028190000000: "小鹏G3",
                  1850019150000000: "威马EX5"
                  }
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 10,
    }

    def __init__(self, **kwargs):
        settings.set("WEBSITE", website)
        settings.set("MYSQLDB_DB", "koubei")
        self.used_time = {}
        super(GuazicarSpider, self).__init__(**kwargs)

    def start_requests(self):
        for i in self.brand_dict:
            url = self.start_urls.format(i)
            yield scrapy.Request(url=url, meta={"series": self.brand_dict[i], "id": i}, headers=self.headers)

        # 进行翻页操作


    def parse(self, response):
        koubei_list = json.loads(response.text)["data"]["list"]
        try:
            self.used_time.update({response.meta["id"]: koubei_list[-1]["info"]["cursor"]})
        except:
            logging.log(msg="达到最后一页了", level=logging.INFO)
            return
        else:
            # 发送请求
            url = self.seconde_url.format(response.meta["id"], self.used_time[response.meta['id']])
            yield scrapy.Request(url=url, meta=response.meta, headers=self.headers,callback=self.parse)
            print(url)
        if koubei_list == [] or koubei_list == None:
            return

        else:
            for koubei in koubei_list[1::]:
                item = dongchedi2()
                item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item["url"] = koubei["info"]["share_info"]["share_url"]
                item["series"] = response.meta["series"]
                item["title"] = koubei["info"]["title"]
                item["content"] = koubei["info"]["content"]
                item["behot_time"] = koubei["info"]["behot_time"]
                item["comment_count"] = koubei["info"]["comment_count"]
                item["read_count"] = koubei["info"]["read_count"]
                item["digg_count"] = koubei["info"]["digg_count"]
                try:
                    item["name"] = koubei["info"]["repost_info"]["name"]
                except:
                    item["name"] = '-'
                try:
                    item["display_car_name"] = koubei["info"]["motor_koubei_info"]["structured_info"][
                        "display_car_name"]
                    item["duration_desc"] = koubei["info"]["motor_koubei_info"]["structured_info"]["duration_desc"]
                    item["bought_time_desc"] = koubei["info"]["motor_koubei_info"]["structured_info"][
                        "bought_time_desc"]
                except:
                    item["display_car_name"] = None
                    item["duration_desc"] = None
                    item["bought_time_desc"] = None
                item["statusplus"] = str(item["url"]) + str(item["read_count"]) + str(item["digg_count"]) + str(
                    item["comment_count"]) + str(item["name"])
                # print(item)
                yield item
