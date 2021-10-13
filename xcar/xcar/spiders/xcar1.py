import scrapy


class Xcar1Spider(scrapy.Spider):
    name = 'xcar1'
    allowed_domains = ['xcar.com.cn']
    start_urls = "https://www.xcar.com.cn/bbs/#R"

    @classmethod
    def update_settings(cls, settings):
        settings.setdict(
            getattr(cls, 'custom_debug_settings' if getattr(cls, 'is_debug', False) else 'custom_settings', None) or {},
            priority='spider')

    is_debug = True
    custom_debug_settings = {
        'MYSQL_SERVER': '192.168.1.94',
        'MYSQL_USER': "dataUser94",
        'MYSQL_PWD': "94dataUser@2020",
        'MYSQL_PORT': 3306,
        'MYSQL_DB': 'usedcar_update',
        'MYSQL_TABLE': '',
        'MONGODB_SERVER': '127.0.0.1',
        'MONGODB_PORT': 27017,
        'MONGODB_DB': 'xcar',
        'MONGODB_COLLECTION': '',
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0,
        'LOG_LEVEL': 'DEBUG',
        'RETRY_HTTP_CODES': [400, 403, 404, 408],
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
    }


    brand_list = ['名爵', '荣威', '上海', '大众', '上汽大通MAXUS', '别克', '凯迪拉克', '雪佛兰', '宝骏', '五菱', '斯柯达']

    def __init__(self, **kwargs):
        super(Xcar1Spider, self).__init__()
        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"}
        self.counts = 0




    def parse(self, response):
        pass
