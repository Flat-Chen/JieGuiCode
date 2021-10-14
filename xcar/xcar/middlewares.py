# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# from scrapy import signals
#
# # useful for handling different item types with a single interface
# from itemadapter import is_item, ItemAdapter
#
#
# class XcarSpiderMiddleware:
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the spider middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_spider_input(self, response, spider):
#         # Called for each response that goes through the spider
#         # middleware and into the spider.
#
#         # Should return None or raise an exception.
#         return None
#
#     def process_spider_output(self, response, result, spider):
#         # Called with the results returned from the Spider, after
#         # it has processed the response.
#
#         # Must return an iterable of Request, or item objects.
#         for i in result:
#             yield i
#
#     def process_spider_exception(self, response, exception, spider):
#         # Called when a spider or process_spider_input() method
#         # (from other spider middleware) raises an exception.
#
#         # Should return either None or an iterable of Request or item objects.
#         pass
#
#     def process_start_requests(self, start_requests, spider):
#         # Called with the start requests of the spider, and works
#         # similarly to the process_spider_output() method, except
#         # that it doesn’t have a response associated.
#
#         # Must return only requests (not items).
#         for r in start_requests:
#             yield r
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
#
#
# class XcarDownloaderMiddleware:
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the downloader middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_request(self, request, spider):
#         # Called for each request that goes through the downloader
#         # middleware.
#
#         # Must either:
#         # - return None: continue processing this request
#         # - or return a Response object
#         # - or return a Request object
#         # - or raise IgnoreRequest: process_exception() methods of
#         #   installed downloader middleware will be called
#         return None
#
#     def process_response(self, request, response, spider):
#         # Called with the response returned from the downloader.
#
#         # Must either;
#         # - return a Response object
#         # - return a Request object
#         # - or raise IgnoreRequest
#         return response
#
#     def process_exception(self, request, exception, spider):
#         # Called when a download handler or a process_request()
#         # (from other downloader middleware) raises an exception.
#
#         # Must either:
#         # - return None: continue processing this exception
#         # - return a Response object: stops process_exception() chain
#         # - return a Request object: stops process_exception() chain
#         pass
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)


import logging
import time

import requests
from scrapy import signals
import random
# useful for handling different item types with a single interface
# from itemadapter import is_item, ItemAdapter

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy import signals
from selenium import webdriver
from scrapy.http import HtmlResponse, TextResponse
from selenium.webdriver import Chrome, ActionChains, FirefoxProfile
from selenium.webdriver.chrome.options import Options
from twisted.internet.error import TimeoutError, TCPTimedOutError


class ProxyMiddleware(object):
    def __init__(self):
        self.count = 0
        self.proxy = "http://" + getProxy()

    def process_exception(self, request, exception, spider):
        if isinstance(exception, TimeoutError):
            self.proxy = "http://" + getProxy()
            request.meta['proxy'] = self.proxy
            return request

    def process_request(self, request, spider):
        proxy = getProxy()
        request.meta['proxy'] = "http://" + proxy


def getProxy():
    s = requests.session()
    s.keep_alive = False
    url_list = ['http://192.168.2.120:5000']
    # random.shuffle(url_list)
    url = url_list[0]
    headers = {
        'Connection': 'close',
    }
    proxy = s.get(url, headers=headers, auth=('admin', 'zd123456')).text[0:-6]
    return proxy


class UserAgent(UserAgentMiddleware):
    def process_request(self, request, spider):
        ua = random.choice(user_agent_list)
        request.headers.setdefault('User-Agent', ua)


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




# class GuaZiSeleniumMiddleware(object):
#     """
#         selenium 动态加载代理ip 、实现点击
#     """
#
#
    #     # 擦除浏览器指纹
    #     try:
    #         with open('stealth.min.js') as f:
    #             self.clean_js = f.read()
    #     except:
    #         with open('/home/stealth.min.js') as f:
    #             self.clean_js = f.read()
    #
    #     self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #         "source": self.clean_js
    #     })
    #
    # def close_spider(self, spider):
    #     try:
    #         self.browser.close()
    #     except:
    #         pass
    #
    # def __del__(self):
    #     try:
    #         self.browser.quit()
    #         self.browser.close()
    #     except:
    #         pass
    #
    # def process_request(self, request, spider):
    #     if 'm.guazi.com' in request.url:
    #         # logging.info('！！！！！！用浏览器打开获取渲染后的网页源代码！！！！！')
    #         # 此处访问要请求的url
    #         try:
    #             for i in range(3):
    #                 self.browser.get(request.url)
    #                 for i in range(15):
    #                     time.sleep(0.2)
    #                     if '正在努力加载' not in self.browser.page_source:
    #                         break
    #                 if '正在努力加载' not in self.browser.page_source:
    #                     break
    #             url = self.browser.current_url
    #             body = self.browser.page_source
    #         except:
    #             logging.error("加载页面太慢，停止加载，继续下一步操作")
    #             self.browser.execute_script("window.stop()")
    #             url = request.url
    #             body = self.browser.page_source
    #         return TextResponse(url=url, body=body, encoding="utf-8", request=request)
