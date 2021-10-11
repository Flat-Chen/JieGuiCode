# -*-coding:utf-8-*-
import logging
import re
import requests
from scrapy.conf import settings
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class ProxyMiddleware(object):
    def __int__(self):
        pass

    @staticmethod
    def get_Proxy():
        url = 'http://120.27.216.150:5000'
        proxy = requests.get(url, auth=('admin', 'zd123456')).text[0:-6]
        return proxy

    def process_request(self, request, spider):
        if spider.name != "guazi":
            proxy = self.get_Proxy()
            logging.log(msg="use           " + proxy, level=logging.INFO)
            request.meta['proxy'] = "http://" + proxy


class MySeleniumMiddleware(object):
    def process_request(self, request, spider):
        if spider.name == "guazi":
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
            # prefs = {"profile.managed_default_content_settings.images": 2,
            #          "profile.managed_default_content_settings.stylesheet": 2
            #          }
            # chrome_options.add_experimental_option("prefs", prefs)
            logging.log(msg="访问：{0}".format(request.url), level=logging.INFO)
            proxy = ProxyMiddleware.get_Proxy()
            ip = re.findall(r'(.*):.*', proxy)[0]
            port = re.findall(r'.*:(.*)', proxy)[0]
            chrome_options.add_argument("--proxy-server=http://{}:{}".format(ip, port))
            driver = webdriver.Chrome(chrome_options=chrome_options, )
            driver.implicitly_wait(settings['PHANTOMJS_TIMEOUT'])
            driver.set_page_load_timeout(settings['PHANTOMJS_TIMEOUT'])
            driver.set_script_timeout(settings['PHANTOMJS_TIMEOUT'])  #
            try:
                driver.get(request.url)
            except Exception as e:
                logging.log(msg="bug    %s" % e, level=logging.INFO)
                return
            else:
                body = driver.page_source
                url = driver.current_url
                driver.quit()
                # print(body, url)
                return HtmlResponse(url=url, body=body, encoding="utf-8",
                                    request=request)


    def process_response(self, request, spider, response):
        if response.status != 200:
            return request
        return response
