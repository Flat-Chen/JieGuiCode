# -*-coding:utf-8-*-
import logging
import random
import re
import requests
import scrapy
from redis import Redis
from scrapy.http import Headers, TextResponse

from .cookie import get_cookie


#  牛牛中间件需要做的事情
# 1 需要初始化一个redis
class CheHang168Middleware(object):
    def __init__(self):
        self.redis_cli = Redis(host="192.168.1.249", port=6379, db=2)
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        ]
        self.used_cookie = ""
        self.request_url = ''

    def get_Proxy(self):
        url = 'http://120.27.216.150:5000'
        headers = {
            'Connection': 'close',
        }
        proxy = requests.get(url, headers=headers, auth=('admin', 'zd123456'), timeout=30).text[0:-6]
        return proxy

    # 获取cookie
    def get_cookie(self):
        self.used_cookie = str(self.redis_cli.srandmember("chehang_168_cookie", 1)[0], encoding='utf-8')
        # self.used_cookie = str(self.redis_cli.srandmember("chehang_168_cookie_test", 1)[0], encoding='utf-8')

    def process_request(self, request, spider):
        # 1 获取cookie  把获取的cookie 赋值给 used_cookie  如果cookie 失效则 删除cookie
        self.request_url = request.url
        self.get_cookie()
        headers = {
            "Referer": "http://www.chehang168.com/index.php",
            "User-Agent": random.choice(self.user_agent_list),
        }
        # proxy = self.get_Proxy()
        logging.log(msg="cookie={},{},".format(self.used_cookie, "*" * 50), level=logging.INFO)
        request.headers = Headers(headers)
        request.cookies = {i.split("=")[0]: i.split("=")[1] for i in self.used_cookie.split(";")}
        # request.meta['proxy'] = "http://" + proxy

    # 删除cookie
    def remove_cookie(self):
        self.redis_cli.srem("chehang_168_cookie", self.used_cookie)
        # a = self.redis_cli.srem("chehang_168_cookie_test", self.used_cookie)
        logging.log(msg="清除cookie----------------------------{}".format(self.used_cookie), level=logging.INFO)
        #
        #
        #
        # cookie)

    def process_response(self, request, spider, response):
        # print( request.headers)
        print(response.status, "+" * 50)
        # print(response.text)
        if "请重新登录" in response.text or "您的注册信息审核不通过" in response.text or "未认证" in response.text or "您需要绑定设备" in response.text:
            # print(response.text)
            # if "http://www.niuniuqiche.com/assets/frontend/application-455e807caf388115b06705ccfe7a7c92f22e2e2f9f1262810cc274619720a015.css" in response.text:
            print(response.url, "失效的url")
            logging.log(msg="-----------this cookie is efficacy---------------", level=logging.INFO)
            #     处理失效的cookie
            self.remove_cookie()
            logging.log(msg="-----------已经杀死cookie---------------", level=logging.INFO)
            print(self.request_url, "已经失效的url 即将从新请求")

            return request
            # return scrapy.Request(url=self.request_url)
            # 需要重新请求这个给这个url 重新配置cookie
            # yield scrapy.Request()
        else:
            return response
