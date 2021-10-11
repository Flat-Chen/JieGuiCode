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
class NiuNiuMiddleware(object):
    def __init__(self):
        self.redis_cli = Redis(host="192.168.1.248", port=6379, db=3)
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
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
        used_cookie = ''
        try:
            cookie_dict = {}
            self.used_cookie = str(self.redis_cli.srandmember("niuniu_cookie", 1)[0], encoding='utf-8')
            for coo in self.used_cookie.split('; '):
                cookie_dict[coo.split('=')[0]] = coo.split('=')[1]

            # print(self.used_cookie, '-' * 50)

            used_cookie = cookie_dict
        except:
            used_cookie = ''
        return used_cookie
        # self.used_cookie = str(self.redis_cli.srandmember("niuniu_cookie_test", 1)[0], encoding='utf-8')

    def process_request(self, request, spider):
        # 1 获取cookie  把获取的cookie 赋值给 used_cookie  如果cookie 失效则 删除cookie
        # print('niuniu_中间件处理请求：', request.url)
        # self.request_url = request.url
        cookie = self.get_cookie()
        # request.cookies = cookie
        headers = {
            "Referer": "http://www.niuniuqiche.com/",
            "User-Agent": random.choice(self.user_agent_list),
        }
        proxy = self.get_Proxy()
        logging.log(msg="cookie={},{},proxy={}".format(cookie, "*" * 50, proxy), level=logging.INFO)
        request.headers = Headers(headers)
        request.meta['proxy'] = "http://" + proxy
        # request.meta['dont_merge_cookies'] = True

    # 删除cookie
    def remove_cookie(self):
        self.redis_cli.srem("niuniu_cookie", self.used_cookie)
        # a = self.redis_cli.srem("niuniu_cookie_test", self.used_cookie)
        logging.log(msg="清除cookie----------------------------{}".format(self.used_cookie), level=logging.INFO)


    def process_response(self, request, spider, response):
        # print('niuniu_中间件处理响应：', response.status, "+" * 50)
        # print(dict(request.headers))
        # return response
        if response.status == 302:
            print(response.text)
            # if "http://www.niuniuqiche.com/assets/frontend/application-455e807caf388115b06705ccfe7a7c92f22e2e2f9f1262810cc274619720a015.css" in response.text:
            print(response.url, "失效的url")
            logging.log(msg="-----------this cookie is efficacy---------------", level=logging.INFO)
            #     处理失效的cookie
            self.remove_cookie()
            logging.log(msg="-----------已经杀死cookie---------------", level=logging.INFO)
            # print(self.request_url,"88888888888888888888888888888888888")
            cookie = self.get_cookie()
            headers = {
                "Referer": "http://www.niuniuqiche.com/",
                "User-Agent": random.choice(self.user_agent_list),
            }
            proxy = self.get_Proxy()
            logging.log(msg="cookie={},{},proxy={}".format(cookie, "*" * 50, proxy), level=logging.INFO)
            request.headers = Headers(headers)
            request.cookies = {"_niu_niu_session": cookie}
            request.meta['proxy'] = "http://" + proxy
            logging.log(msg="----------继续请求{}---------------".format(request.url), level=logging.INFO)
            return request
            # return scrapy.Request(url=self.request_url)
            # 需要重新请求这个给这个url 重新配置cookie
            # yield scrapy.Request()
        else:
            return response
