# -*- coding: utf-8 -*-

# Scrapy settings for guazi project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import datetime

BOT_NAME = 'guazi'
WEBSITE = "guazi"
SPIDER_MODULES = ['guazi.spiders']
NEWSPIDER_MODULE = 'guazi.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = ''

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 10

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Referer': 'https://www.guazi.com/www/',
#     "Cookie": "antipas=161S12s2q1612121418487577",
#     "User-Agent": "Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1"
# }
# #

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'guazi.proxy.MySeleniumMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/MySeleniumMiddleware1
# topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'guazi.middlewares.GuaziDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 关闭默认下载器
    'guazi.proxy.GuaziCookieMiddleware': 550,
    # "guazi.proxy.Che300ProxyMiddleware": 540,
    "guazi.proxy.MySeleniumMiddleware1": 531,
    "guazi.proxy.ProxyMiddleware": 530,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'guazi.pipelines.GuaziPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# 248
# PHANTOMJS_PATH = "/usr/local/phantomjs/bin/phantomjs"
PHANTOMJS_PATH = "/usr/bin/phantomjs"

# 241
# PHANTOMJS_PATH = "/usr/bin/phantomjs"
# PHANTOMJS_PATH = "/usr/local/chromedriver/chromedrivezr"
# PHANTOMJS_PATH = r"E:\phantomjs-2.1.1-windows\phantomjs.exe"
PHANTOMJS_TIMEOUT = 10
MYSQL_SERVER = "192.168.1.94"
MYSQL_PORT = '3306'
MYSQLDB_PASS = "94dataUser@2020"
MYSQLDB_USER = "dataUser94"
MYSQLDB_DB = "usedcar_update"

REDIS_SERVER = '192.168.1.92'
REDIS_PORT = 6379
REDIS_DB = 1
MONGODB_SERVER = '192.168.1.94'
# MONGODB_SERVER = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_DB = 'usedcar'
MONGODB_COLLECTION = "che300"
CrawlCar_Num = 200000
REDIRECT_ENABLED = False
DOWNLOAD_TIMEOUT = 15
