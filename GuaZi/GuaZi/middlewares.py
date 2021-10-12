# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
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
        request.headers.setdefault(
            'User-Agent',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
        )


class GuaZiSeleniumMiddleware(object):
    """
        selenium 动态加载代理ip 、实现点击
    """

    def __init__(self):
        self.count = 0
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        # 去掉提示：Chrome正收到自动测试软件的控制
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_argument('--proxy-server=192.168.2.144:16127')
        ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        chrome_options.add_argument('user-agent=' + ua)
        self.browser = Chrome(options=chrome_options)

        # 擦除浏览器指纹
        with open('stealth.min.js') as f:
            self.clean_js = f.read()

        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": self.clean_js
        })

    def close_spider(self, spider):
        try:
            self.browser.close()
        except:
            pass

    def __del__(self):
        try:
            self.browser.quit()
            self.browser.close()
        except:
            pass

    def process_request(self, request, spider):
        if 'm.guazi.com' in request.url:
            logging.info('！！！！！！用浏览器打开获取渲染后的网页源代码！！！！！')
            # 此处访问要请求的url
            try:
                for i in range(3):
                    self.browser.get(request.url)
                    for i in range(15):
                        time.sleep(0.2)
                        if '正在努力加载' not in self.browser.page_source:
                            break
                    if '正在努力加载' not in self.browser.page_source:
                        break
                url = self.browser.current_url
                body = self.browser.page_source
            except:
                logging.error("加载页面太慢，停止加载，继续下一步操作")
                self.browser.execute_script("window.stop()")
                url = request.url
                body = self.browser.page_source
            return TextResponse(url=url, body=body, encoding="utf-8", request=request)
