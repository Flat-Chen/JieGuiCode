# -*-coding:utf-8-*-
import json
import logging
import random
import re, time
import requests
import os
from scrapy import signals
from scrapy.conf import settings
from scrapy.http import Headers, TextResponse, Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.proxy import ProxyType
from twisted.internet.error import TimeoutError
from .spiders.autohome_car_forecast2 import CarSpider
from .cookie import get_cookie

user_agent_list = [
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


def get_ug():
    ua = random.choice(user_agent_list)
    return ua


def get_Proxy():
    url = 'http://120.27.216.150:5000'
    headers = {
        'Connection': 'close',
    }
    proxy = requests.get(url, headers=headers, auth=('admin', 'zd123456'), timeout=3).text[0:-6]
    return proxy


class ProxyMiddleware(object):
    def __init__(self):
        self.count = 0
        self.proxy = "http://" + get_Proxy()

    @staticmethod
    def get_Proxy():
        # url = 'http://192.168.2.120:5000'
        url = 'http://120.27.216.150:5000'
        headers = {
            'Connection': 'close',
        }
        proxy = requests.get(url, headers=headers, auth=('admin', 'zd123456'), timeout=3).text[0:-6]
        return proxy

    def process_request(self, request, spider):
        if spider.name not in ["guazi", "youka_price", 'yuantong']:
            if self.count < 2:
                request.meta['proxy'] = self.proxy
                self.count += 1
            else:
                self.proxy = "http://" + get_Proxy()
                self.count = 0
            print('proxy success !')
            logging.log(msg="use           " + self.proxy, level=logging.INFO)
            request.meta['proxy'] = self.proxy
            request.headers['User-Agent'] = get_ug()


    def process_exception(self, request, exception, spider):
        if isinstance(exception, TimeoutError):
            new_ip = "http://" + get_Proxy()
            request.meta['proxy'] = new_ip
            request.headers['User-Agent'] = get_ug()

            return request

    def process_response(self, request, spider, response):
        # print(response.text)
        if response.status in [301, 302]:
            if spider.name == 'autohome_car_forecast2':
                print('处理302页面')
                if response.css('h2::text').get().startswith('Object moved to'):
                    url = 'https://car.autohome.com.cn' + response.css('a::attr(href)').get()
                    car = CarSpider()
                    return Request(url=url, callback=car.stauts_parse, dont_filter=True,)
            else:
                return request

        return response


class Che300ProxyMiddleware(object):

    @staticmethod
    def get_Proxy():
        url = 'http://120.27.216.150:5000'
        headers = {
            'Connection': 'close',
        }
        proxy = requests.get(url, headers=headers, auth=('admin', 'zd123456'), timeout=3).text[0:-6]
        return proxy

    def process_request(self, request, spider):
        if spider.name not in ["guazi", "youka_price", 'yuantong']:
            proxy = "http://" + get_Proxy()
            logging.log(msg="use           " + proxy, level=logging.INFO)
            request.headers['User-Agent'] = get_ug()
            request.meta['proxy'] = proxy

    def process_response(self, request, spider, response):
        data = json.loads(response.text)
        if data["data"] == {}:
            proxy = "http://" + get_Proxy()
            request.headers['User-Agent'] = get_ug()
            request.meta['proxy'] = proxy
            return request
        else:
            return response


class MySeleniumMiddleware1(object):
    def __init__(self):
        service_args = ['--load-images=no', '--disk-cache=yes', '--ignore-ssl-errors=true', ]
        self.driver = webdriver.PhantomJS(settings['PHANTOMJS_PATH'], service_args=service_args)
        # self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(settings['PHANTOMJS_TIMEOUT'])
        self.driver.set_page_load_timeout(settings['PHANTOMJS_TIMEOUT'])
        self.driver.set_script_timeout(settings['PHANTOMJS_TIMEOUT'])

        # chromedriver
        if os.path.exists('/home/home'):
            self.file_path = '/home/home/mywork/stealth.min.js'
        else:
            self.file_path = '/home/machao/stealth.min.js'
        chrome_opts = Options()
        chrome_opts.add_argument('--headless')
        chrome_opts.add_argument('--disable-gpu')
        chrome_opts.add_argument("window-size=1024,768")
        chrome_opts.add_argument("--no-sandbox")
        # chrome_opts.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
        self.browser = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_opts)
        with open(self.file_path, 'r') as f:
            js = f.read()
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': js
        })

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_closed(self):
        # print("-" * 50, "quit")
        self.driver.quit()

    def process_request(self, request, spider):
        if spider.name in [ "autohome_car_forecast_test", ]:
            self.driver.get(request.url)
            # self.driver.get(request.url)
            body = self.driver.page_source
            url = self.driver.current_url
            # driver.quit()
            return TextResponse(body=body, request=request, encoding="utf-8",
                                url=url)
        elif "autohome_newcar" in spider.name and "https://car.autohome.com.cn/config/spec/" in request.url:
            print(r"/\\" * 50)
            self.driver.get(request.url)
            # self.driver.get(request.url)
            body = self.driver.page_source
            url = self.driver.current_url

            return TextResponse(body=body, request=request, encoding="utf-8",
                                url=url)
        elif spider.name == 'xcar':
            self.browser.get(request.url)
            time.sleep(2)
            url = self.browser.current_url
            page_source = self.browser.page_source
            # self.browser.close()
            return TextResponse(
                url=url, body=page_source, encoding='utf-8'    
            )
        elif spider == 'autohome_car_forecast2':
            if 'brand-' in request.url:
                print('渲染页面。。。')
                self.browser.get(request.url)
                time.sleep(0.5)
                url = self.browser.current_url
                page_source = self.browser.page_source
                # self.browser.close()
                return TextResponse(
                    url=url, body=page_source, encoding='utf-8'    
                )


    def process_response(self, request, spider, response):
        if spider.name == 'autohome_car_forecast2':
            if '点击按钮进行验证' in response.text:
                print('模拟浏览器获取页面：', request)
                # self.driver.get(response.url)
                # time.sleep(0.5)
                # body = self.driver.page_source
                # url = self.driver.current_url

                # return TextResponse(body=body, request=request, encoding="utf-8", url=url)
        return response


class autohome_middlewarel(object):
    def __init__(self):
        # print("/" * 50, '__init__')

        service_args = ['--load-images=no', '--disk-cache=yes', '--ignore-ssl-errors=true', ]
        self.driver = webdriver.PhantomJS(settings['PHANTOMJS_PATH'], service_args=service_args)
        # self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(settings['PHANTOMJS_TIMEOUT'])
        self.driver.set_page_load_timeout(settings['PHANTOMJS_TIMEOUT'])
        self.driver.set_script_timeout(settings['PHANTOMJS_TIMEOUT'])

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_closed(self):
        # print("-" * 50, "quit")
        self.driver.quit()

    def process_request(self, request, spider):
        # if "https://car.autohome.com.cn/config/spec/" not in request.url:
        proxy = "http://" + get_Proxy()
        logging.log(msg="use           " + proxy, level=logging.INFO)
        request.headers['User-Agent'] = get_ug()
        request.meta['proxy'] = proxy
        # elif "https://car.autohome.com.cn/config/spec/" in request.url:
        #     # print(r"/\\" * 50)
        #     self.driver.get(request.url)
        #     # self.driver.get(request.url)
        #     body = self.driver.page_source
        #     url = self.driver.current_url
        #     # driver.quit()
        #     return TextResponse(body=body, request=request, encoding="utf-8",
        #                         url=url)


class GuaziCookieMiddleware(object):
    def process_request(self, request, spider):
        if spider.name == "guazi":
            # User_Agent 
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'}
            # print(request.headers)
            proxy = ProxyMiddleware.get_Proxy()
            # logging.log(msg="use           " + proxy, level=logging.INFO)
            # try:
            #     headers = get_cookie(request.url, User_Agent, proxy=proxy)
            # except Exception as e:
            #     logging.log(msg="proxy is lose efficacy 继续使用上一次的cookie   {}".format(e), level=logging.INFO)
            #     return request
            # else:
            #     # print("*" * 50, headers)
            request.headers = Headers(headers)
            request.meta['proxy'] = "https://" + proxy

    def process_response(self, request, spider, response):
        print("-" * 50)
        if response.status == 203:
            print(response.text)
#             User_Agent = {'User-Agent': get_ug()}
#             # print(request.headers)/
#             proxy = ProxyMiddleware.get_Proxy()
#             logging.log(msg="use           " + proxy, level=logging.INFO)
#             try:
#                 headers = get_cookie(request.url, User_Agent, proxy=proxy)
#             except Exception as e:
#                 logging.log(msg="proxy is lose efficacy 继续使用上一次的cookie   {}".format(e), level=logging.INFO)
#                 return request
#             else:
#                 # print("*" * 50, headers)
#                 # print(headers, "*" * 50)    
#                 request.headers = Headers(headers)
#                 request.meta['proxy'] = "https://" + proxy
#                 return request
        return response

