# Scrapy settings for xcar project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'xcar'

SPIDER_MODULES = ['xcar.spiders']
NEWSPIDER_MODULE = 'xcar.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'xcar (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'xcar.middlewares.XcarSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'xcar.middlewares.ProxyMiddleware': 200,
    'xcar.middlewares.UserAgent': 201,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'xcar.pipelines.XcarPipeline': 200,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
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
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# RETRY_HTTP_CODES = [400, 403, 404, 408]
# # 是否开启重试
# RETRY_ENABLED = True
# # 重试次数
# RETRY_TIMES = 5


# BRAND_URL = {'名爵': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10014',
#              '荣威': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10044',
#              '上海': '上汽乘用车',
#              '斯柯达': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10006',
#              '大众': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10003',
#              '上汽大通MAXUS': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10125',
#              '别克': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10012',
#              '凯迪拉克': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10064',
#              '雪佛兰': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10016',
#              '宝骏': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10103',
#              '五菱': 'https://www.xcar.com.cn/bbs/forumdisplay.php?fid=10077',}
#   # '名爵', '荣威', '上海', '大众', '上汽大通MAXUS', '别克', '凯迪拉克', '雪佛兰', '宝骏', '五菱', '斯柯达'
# BRAND_DIC = {'名爵': '上汽乘用车',
#              '荣威': '上汽乘用车',
#              '上海': '上汽乘用车',
#              '斯柯达': '上汽大众',
#              '大众': '上汽大众',
#              '上汽大通MAXUS': '上汽大通',
#              '别克': '上汽通用',
#              '凯迪拉克': '上汽通用',
#              '雪佛兰': '上汽通用',
#              '宝骏': '上汽通用五菱',
#              '五菱': '上汽通用五菱',}
# band_series ="名名爵7论坛名爵TF论坛名爵6/名爵6新能源论坛名爵5论坛名爵3SW论坛名爵3论坛名爵论坛名爵锐行论坛名爵HS论坛名爵ZS论坛" \
#                  "MG领航/MG领航PHEV论坛锐腾论坛荣威Ei5论坛荣威MARVEL X论坛荣威E50论坛荣威360论坛荣威W5论坛荣威750论坛荣威550论坛" \
#                  "荣威350论坛荣威950论坛荣威论坛荣威ei6论坛荣威iMAX8论坛荣威R ER6论坛荣威RX3论坛荣威i5论坛荣威新能源论坛荣威i6论坛" \
#                  "荣威鲸论坛荣威RX8论坛荣威RX5论坛荣威e550论坛荣威e950论坛昊锐论坛晶锐论坛斯柯达SUV兄弟汇--柯迪亚克明锐/明锐旅行版论" \
#                  "坛明锐RS论坛柯珞克论坛斯柯达Rapid/昕锐论坛斯柯达速派论坛柯米克论坛斯柯达昕动论坛斯柯达SUV兄弟汇--大众ID.3论坛大众ID.4" \
#                  " X论坛大众ID.6 X论坛大众凌渡论坛高尔论坛辉昂论坛浩纳论坛朗境/朗逸CROSS论坛朗行论坛朗逸论坛Polo/Polo Plus论坛" \
#                  "帕萨特论坛|帕协新桑塔纳论坛途昂论坛途岳论坛途铠论坛途昂X论坛途安论坛途观/途观L/途观X/Tiguan论坛途安L论坛威然论坛" \
#                  "上汽大通MAXUS G10论坛上汽大通MAXUS T系论坛上汽大通MAXUS G50/EUNIQ 5论坛上汽大通MAXUS V80论坛" \
#                  "上汽大通MAXUS D60/EUNIQ 6论坛上汽大通MAXUS D90/D90 Pro论坛上汽大通MAXUS EV30论坛上汽大通MAXUS宝骏论坛" \
#                  "宝骏510论坛宝骏330论坛宝骏530论坛宝骏360论坛宝骏630论坛宝骏310/宝骏310W论坛宝骏730论坛宝骏610论坛宝骏560论坛" \
#                  "乐驰论坛昂科旗论坛昂科拉论坛昂科威论坛Enspire论坛GL8论坛GL6论坛HRV论坛新君威论坛新君越论坛凯越旅行车论坛凯越论坛" \
#                  "林荫大道论坛别克新能源论坛威朗论坛微蓝6论坛英朗论坛阅朗论坛凯迪拉克CT6论坛凯迪拉克XTS论坛凯迪拉克SLS论坛凯迪拉克CT4论坛" \
#                  "凯迪拉克CT5论坛凯迪拉克XT4论坛凯迪拉克XT5论坛凯迪拉克ATS/ATS-L论坛凯迪拉克XT6论坛爱唯欧论坛创界论坛畅巡论坛景程论坛" \
#                  "科沃兹论坛开拓者论坛科鲁兹论坛科帕奇论坛科鲁泽论坛乐风RV论坛乐骋论坛乐风论坛迈锐宝/迈锐宝XL论坛赛欧论坛" \
#                  "探界者论坛沃兰多论坛雪佛兰创酷-trax论坛宏光MINI EV论坛凯捷论坛五菱宏光S3论坛五菱论坛五菱宏光侠论坛五菱荣光小卡论坛" \
#                  "五菱荣光V论坛五菱征程论坛五菱宏光论坛五菱之光论坛五菱星辰论坛"
