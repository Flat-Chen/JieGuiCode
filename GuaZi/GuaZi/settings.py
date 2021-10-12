# Scrapy settings for GuaZi project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'GuaZi'

SPIDER_MODULES = ['GuaZi.spiders']
NEWSPIDER_MODULE = 'GuaZi.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'GuaZi (+http://www.yourdomain.com)'

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
#     'GuaZi.middlewares.GuaziSpiderMiddleware': 200,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'GuaZi.middlewares.ProxyMiddleware': 199,
    'GuaZi.middlewares.UserAgent': 200,
    'GuaZi.middlewares.GuaZiSeleniumMiddleware': 201,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'GuaZi.pipelines.GuaziPipeline': 200,
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

RETRY_HTTP_CODES = [400, 403, 404, 408]
# 是否开启重试
RETRY_ENABLED = True
# 重试次数
RETRY_TIMES = 5

CITY_DICT = {'鞍山': '57',
             '安阳': '109',
             '安庆': '127',
             '安顺': '39',
             '安康': '184',
             '包头': '146',
             '蚌埠': '125',
             '北海': '317',
             '百色': '139',
             '本溪': '286',
             '宝鸡': '178',
             '毕节': '41',
             '亳州': '314',
             '白城': '91',
             '白银': '168',
             '保山': '228',
             '白山': '89',
             '巴中': '281',
             '长春': '84',
             '长沙': '204',
             '常州': '69',
             '长治': '158',
             '赤峰': '148',
             '滁州': '128',
             '承德': '8',
             '常德': '210',
             '崇左': '320',
             '郴州': '211',
             '潮州': '271',
             '楚雄': '236',
             '池州': '315',
             '朝阳': '289',
             '东莞': '24',
             '大连': '56',
             '东营': '117',
             '德州': '308',
             '大庆': '98',
             '大同': '156',
             '德阳': '48',
             '丹东': '59',
             '达州': '53',
             '大理': '237',
             '德宏': '238',
             '定西': '175',
             '大兴安岭': '303',
             '鄂尔多斯': '150',
             '鄂州': '201',
             '恩施': '331',
             '福州': '75',
             '抚顺': '58',
             '阜新': '287',
             '防城港': '318',
             '抚州': '223',
             '贵阳': '36',
             '贵港': '137',
             '广安': '278',
             '广元': '275',
             '固原': '341',
             '哈尔滨': '93',
             '合肥': '123',
             '呼和浩特': '145',
             '惠州': '23',
             '邯郸': '4',
             '菏泽': '338',
             '淮安': '72',
             '衡水': '11',
             '黄冈': '328',
             '河池': '140',
             '淮南': '310',
             '葫芦岛': '64',
             '衡阳': '207',
             '淮北': '311',
             '怀化': '336',
             '红河': '234',
             '贺州': '319',
             '鹤壁': '107',
             '黑河': '101',
             '汉中': '182',
             '黄山': '313',
             '鹤岗': '96',
             '海东': '187',
             '海拉尔': '151',
             '济南': '113',
             '济宁': '304',
             '嘉兴': '29',
             '吉林': '85',
             '揭阳': '272',
             '佳木斯': '100',
             '晋中': '161',
             '锦州': '60',
             '焦作': '106',
             '荆州': '198',
             '九江': '217',
             '景德镇': '215',
             '吉安': '221',
             '鸡西': '95',
             '晋城': '159',
             '酒泉': '173',
             '济源市': '112',
             '金昌': '167',
             '昆明': '225',
             '开封': '293',
             '临沂': '307',
             '洛阳': '104',
             '兰州': '166',
             '柳州': '133',
             '连云港': '71',
             '临汾': '164',
             '六安': '132',
             '聊城': '309',
             '泸州': '47',
             '乐山': '50',
             '辽阳': '62',
             '吕梁': '323',
             '龙岩': '82',
             '来宾': '141',
             '凉山': '54',
             '丽水': '285',
             '漯河': '110',
             '六盘水': '37',
             '娄底': '213',
             '辽源': '87',
             '丽江': '230',
             '临沧': '232',
             '陇南': '324',
             '临夏': '325',
             '临河': '152',
             '绵阳': '49',
             '茂名': '22',
             '梅州': '266',
             '眉山': '279',
             '牡丹江': '302',
             '马鞍山': '126',
             '南京': '65',
             '南宁': '142',
             '南昌': '214',
             '宁波': '27',
             '南通': '70',
             '南阳': '111',
             '南充': '51',
             '宁德': '83',
             '内江': '277',
             '南平': '81',
             '怒江': '239',
             '濮阳': '294',
             '莆田': '77',
             '平顶山': '105',
             '盘锦': '63',
             '萍乡': '216',
             '普洱': '231',
             '攀枝花': '274',
             '平凉': '172',
             '青岛': '114',
             '泉州': '79',
             '钦州': '136',
             '清远': '270',
             '秦皇岛': '3',
             '曲靖': '226',
             '黔南': '44',
             '衢州': '33',
             '黔西南': '42',
             '黔东南': '43',
             '庆阳': '174',
             '七台河': '301',
             '潜江': '203',
             '沈阳': '55',
             '汕头': '19',
             '宿迁': '292',
             '绍兴': '31',
             '绥化': '102',
             '商丘': '297',
             '松原': '90',
             '宿州': '130',
             '上饶': '224',
             '四平': '86',
             '邵阳': '208',
             '遂宁': '276',
             '十堰': '197',
             '三明': '78',
             '韶关': '263',
             '双鸭山': '97',
             '三门峡': '296',
             '朔州': '160',
             '随州': '330',
             '石嘴山': '339',
             '商州': '185',
             '神农架': '333',
             '天津': '14',
             '太原': '155',
             '唐山': '2',
             '泰安': '305',
             '泰州': '291',
             '铁岭': '288',
             '通辽': '149',
             '通化': '88',
             '天水': '169',
             '铜陵': '312',
             '铜仁': '40',
             '铜川': '177',
             '天门': '332',
             '武汉': '194',
             '潍坊': '119',
             '无锡': '66',
             '乌鲁木齐': '241',
             '温州': '28',
             '威海': '120',
             '芜湖': '124',
             '乌兰察布': '153',
             '渭南': '180',
             '梧州': '135',
             '吴忠': '340',
             '乌海': '147',
             '武威': '170',
             '文山市': '233',
             '乌兰浩特': '154',
             '西安': '176',
             '徐州': '68',
             '厦门': '76',
             '新乡': '108',
             '襄阳': '196',
             '咸阳': '179',
             '西宁': '186',
             '许昌': '295',
             '宣城': '316',
             '信阳': '298',
             '孝感': '327',
             '忻州': '163',
             '湘潭': '206',
             '新余': '218',
             '西双版纳': '235',
             '湘西': '337',
             '锡林郭勒': '321',
             '咸安': '329',
             '仙桃': '202',
             '烟台': '118',
             '扬州': '74',
             '盐城': '73',
             '营口': '61',
             '玉林': '138',
             '银川': '165',
             '宜昌': '199',
             '宜宾': '52',
             '运城': '162',
             '榆林': '183',
             '岳阳': '209',
             '阳江': '269',
             '玉溪': '227',
             '宜春': '222',
             '永州': '212',
             '益阳': '335',
             '延边': '92',
             '阳泉': '157',
             '延安': '181',
             '伊春': '99',
             '雅安': '280',
             '鹰潭': '219',
             '伊犁': '252',
             '郑州': '103',
             '中山': '25',
             '淄博': '115',
             '湛江': '264',
             '珠海': '18',
             '漳州': '80',
             '遵义': '38',
             '肇庆': '265',
             '张家口': '7',
             '驻马店': '300',
             '张家界': '334',
             '周口': '299',
             '自贡': '46',
             '株洲': '205',
             '昭通': '229',
             '资阳': '282',
             '舟山': '34',
             '张掖': '171',
             '中卫': '342',
             '安吉': '2089',
             '北京': '12',
             '保定': '6',
             '滨州': '122',
             '成都': '45',
             '重庆': '15',
             '沧州': '9',
             '沧县': '1773',
             '昌吉市': '1441',
             '长寿': '2866',
             '长兴': '2088',
             '大厂': '1737',
             '大冶': '2291',
             '大邑': '596',
             '丹阳': '1581',
             '东阳': '2110',
             '东源': '1207',
             '都江堰': '587',
             '佛山': '20',
             '阜阳': '129',
             '奉节': '2886',
             '涪陵': '2864',
             '广州': '16',
             '赣州': '220',
             '桂林': '134',
             '甘南': '3173',
             '杭州': '26',
             '湖州': '30',
             '黄石': '195',
             '河源': '268',
             '海丰': '1193',
             '合川': '2869',
             '金华': '32',
             '江门': '21',
             '荆门': '198',
             '江津': '2868',
             '莒县': '866',
             '开平': '1199',
             '昆山': '1564',
             '廊坊': '10',
             '灵川': '1306',
             '临海': '391',
             '罗定': '1144',
             '南川': '2871',
             '南康': '1664',
             '齐齐哈尔': '94',
             '黔江': '2865',
             '日照': '306',
             '上海': '13',
             '深圳': '17',
             '苏州': '67',
             '石家庄': '1',
             '汕尾': '267',
             '三河': '1731',
             '石柱': '2889',
             '台州': '35',
             '滕州': '872',
             '桐庐': '2072',
             '綦江': '2859',
             '万州': '2863',
             '温岭': '2036',
             '邢台': '5',
             '邢台县': '1812',
             '云浮': '273',
             '颍上县': '819',
             '永川': '2870',
             '玉环': '2083',
             '枣庄': '116',
             '镇江': '290',
             '增城': '1163',
             '钟祥': '2260',
             '涿州': '1686',
             '邹平': '912'}
# 数据库字段名 : 网页字段名
CONF_DICT = {
    'factoryname': '厂商',
    'guidepricetax': '厂商指导价(万元)',
    'makeyear': '上市时间',
    'fueltype': '能源形式',
    'gear': '变速器描述',
    'bodystyle': '车身形式',
    'body':'车身形式',
    'first_owner': '进气形式',
    'lwv': '气缸排列形式',
    'lwvnumber': '气缸数(个)',
    'maxps': '最大马力(Ps)',
    'maxpower': '最大功率(kW)',
    'maxnm': '最大扭矩(N·m)',
    'fuelnumber': '燃油标号',
    'gearnumber': '挡位个数',
    'wheelbase': '轴距(mm)',
    'height': '高度(mm)',
    'width': '宽度(mm)',
    'length': '长度(mm)',
    'frontgauge': '前轮距(mm)',
    'doors': '车门数(个)',
    'seats': '座位数(个)',
    'weight': '整备质量(kg)',
    'driverway': '驱动方式',


}




# # familyname生产厂家
# factoryname = parameter_dict['厂商']
# # 指导价(含税)
# guidepricetax = parameter_dict['厂商指导价(万元)']
# # 年款
# makeyear=parameter_dict['上市时间']
# # 燃油类型
# fueltype = parameter_dict['能源形式']
# # 变速箱描述
# gear = parameter_dict['变速器描述']
# # 车身类型
# bodystyle = parameter_dict['车身形式']
# # 进气方式
# first_owner=parameter_dict['进气形式']
# # 气缸排列型式
# lwv = parameter_dict['气缸排列形式']
# # 气缸数
# lwvnumber = parameter_dict['气缸数(个)']
# # 最大马力
# maxps = parameter_dict['最大马力(Ps)']
# # 最大功率
# maxpower = parameter_dict['最大功率(kW)']
# # 最大扭矩
# maxnm = parameter_dict['最大扭矩(N·m)']
# # 燃油标号
# fuelnumber = parameter_dict['燃油标号']
# # 档位数
# gearnumber = parameter_dict['挡位个数']
# # 轴距
# wheelbase = parameter_dict['轴距(mm)']
# # 车高
# height = parameter_dict['高度(mm)']
# # 车宽
# width=parameter_dict['宽度(mm)']
# # 车长
# length = parameter_dict['长度(mm)']
# # 前轮距
# frontgauge = parameter_dict['前轮距(mm)']
# # 车门数量
# doors = parameter_dict['车门数(个)']
# # 座位数
# seats = parameter_dict['座位数(个)']
# # 整备质量
# weight = parameter_dict['整备质量(kg)']
# # 驱动类型
# driverway = parameter_dict['驱动方式']
# # 描述
# # desc=