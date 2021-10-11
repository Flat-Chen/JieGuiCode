# -*- coding: UTF-8 -*-
import json
import re
import time
from urllib import parse

import redis
import scrapy
import logging
from scrapy.conf import settings
from ..items import GuaziItem
from ..redis_bloom import BloomFilter

website = 'dafengche'


class CarSpider(scrapy.Spider):
    name = website
    start_urls = 'https://lol.souche.com/carsourcelistaction/getCarSourceList.json?pn=0&brand_code=%7B%22series%22%3A%5B%5D%2C%22brand%22%3A%5B%22{}%22%5D%2C%22modelType%22%3A%5B%5D%7D&appType=merchant&size=100&province_code=&car_source=%5B%225%22%5D'
    next_url = 'https://lol.souche.com/carsourcelistaction/getCarSourceList.json?pn={}&brand_code=%7B%22series%22%3A%5B%5D%2C%22brand%22%3A%5B%22{}%22%5D%2C%22modelType%22%3A%5B%5D%7D&appType=merchant&size=100&province_code=&car_source=%5B%225%22%5D'

    headers = {
        'user-agent': 'Android_18962',
        'Authorization': 'Token token=02_6HTf_Nre89vAZx0',
        'Content-Type': 'application/x-www-form-urlencoded',

        'Cookie': '_security_token=02_NHCH_Nre89vAZx0'
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        "DOWNLOADER_MIDDLEWARES": {
            "guazi.proxy.ProxyMiddleware": 530
        }

    }

    def __init__(self, **kwargs):
        self.bf = BloomFilter(key='b1f_' + website)
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        self.counts = 0
        self.car_dict = {'brand-859': 'AC Schnitzer', 'brand-856': 'ALPINA', 'brand-984': 'AUXUN傲旋', 'brand-15': '奥迪',
                         'brand-548': '安凯客车', 'brand-882': '安驰', 'brand-959': '爱驰', 'brand-12': '阿尔法·罗密欧',
                         'brand-13': '阿斯顿·马丁', 'brand-22': '保时捷', 'brand-30': '别克', 'brand-23': '北京',
                         'brand-534': '北京汽车', 'brand-24': '北汽制造', 'brand-546': '北汽威旺', 'brand-570': '北汽幻速',
                         'brand-512': '北汽新能源', 'brand-35': '北汽昌河', 'brand-870': '北汽道达', 'brand-966': '博郡汽车',
                         'brand-26': '奔腾', 'brand-25': '奔驰', 'brand-821': '宝沃', 'brand-20': '宝马', 'brand-18': '宝骏',
                         'brand-916': '宝骐汽车', 'brand-822': '宾仕盾', 'brand-31': '宾利', 'brand-1018-n': '巴博斯',
                         'brand-33': '布加迪', 'brand-27': '本田', 'brand-29': '标致', 'brand-28': '比亚迪', 'brand-953': '比德文汽车',
                         'brand-829': '比速汽车', 'brand-980': '铂驰', 'brand-516': '成功汽车', 'brand-948': '车驰汽车',
                         'brand-165': '长城', 'brand-164': '长安', 'brand-526': '长安欧尚', 'brand-874': '长安跨越',
                         'brand-875': '长安轻型车', 'brand-544': 'DS', 'brand-45': '东南', 'brand-44': '东风',
                         'brand-888': '东风·瑞泰特', 'brand-911': '东风商用', 'brand-524': '东风小康', 'brand-817': '东风风光',
                         'brand-506': '东风风度', 'brand-522': '东风风神', 'brand-574': '东风风行', 'brand-906': '大乘汽车',
                         'brand-41': '大众', 'brand-500': '大发', 'brand-806': '大宇', 'brand-808': '大迪', 'brand-849': '电咖',
                         'brand-884': '达契亚', 'brand-923': '迪马', 'brand-42': '道奇', 'brand-49': '丰田', 'brand-885': '伏尔加',
                         'brand-823': '富奇', 'brand-847': '房车', 'brand-46': '法拉利', 'brand-508': '福汽启腾', 'brand-53': '福特',
                         'brand-54': '福田', 'brand-52': '福迪', 'brand-48': '菲亚特', 'brand-820': '菲斯克', 'brand-921': '飞碟汽车',
                         'brand-3': 'GMC', 'brand-580': '光冈', 'brand-965': '国机智骏', 'brand-886': '国金汽车',
                         'brand-56': '广汽传祺', 'brand-71': '广汽吉奥', 'brand-887': '广汽新能源', 'brand-903': '广汽集团',
                         'brand-1001-n': '观致', 'brand-987': 'HYCAN合创', 'brand-814': '华凯', 'brand-64': '华普',
                         'brand-65': '华泰', 'brand-979': '华泰新能源', 'brand-741': '华颂', 'brand-907': '华骐',
                         'brand-530': '哈弗', 'brand-57': '哈飞', 'brand-955': '弘安新能源', 'brand-564': '恒天', 'brand-59': '悍马',
                         'brand-804': '汉江', 'brand-835': '汉腾汽车', 'brand-961': '汉龙汽车', 'brand-465': '海格',
                         'brand-58': '海马', 'brand-62': '红旗', 'brand-892': '红星汽车', 'brand-68': '黄海', 'brand-74': 'Jeep',
                         'brand-554': '九龙', 'brand-985': '几何汽车', 'brand-72': '吉利汽车', 'brand-869': '君马汽车',
                         'brand-78': '捷豹', 'brand-950': '捷达', 'brand-893': '捷途', 'brand-861': '杰克Jayco',
                         'brand-75': '江淮', 'brand-543': '江铃客车', 'brand-76': '江铃汽车', 'brand-841': '江铃集团新能源',
                         'brand-986': '金冠汽车', 'brand-552': '金旅', 'brand-79': '金杯', 'brand-812': '金程', 'brand-528': '金龙',
                         'brand-922': '钧天', 'brand-983': 'Karma', 'brand-562': 'KTM', 'brand-86': '克莱斯勒',
                         'brand-866': '凯佰赫', 'brand-556': '凯翼', 'brand-84': '凯迪拉克', 'brand-917': '凯马',
                         'brand-862': '卡升', 'brand-576': '卡威', 'brand-538': '卡尔森', 'brand-568': '开沃汽车',
                         'brand-82': '开瑞', 'brand-540': '科尼赛克', 'brand-908': 'LITE', 'brand-860': 'LOCAL MOTORS',
                         'brand-88': '兰博基尼', 'brand-94': '力帆汽车', 'brand-91': '劳斯莱斯', 'brand-832': '拉达',
                         'brand-96': '林肯', 'brand-166': '猎豹汽车', 'brand-502': '理念', 'brand-927': '理想汽车',
                         'brand-867': '罗伦士', 'brand-913': '罗夫哈特', 'brand-805': '罗孚', 'brand-828': '老爷车',
                         'brand-95': '莲花汽车', 'brand-518': '路特斯', 'brand-99': '路虎', 'brand-97': '铃木',
                         'brand-819': '陆地方舟', 'brand-98': '陆风', 'brand-920': '零跑汽车', 'brand-863': '雷丁',
                         'brand-92': '雷克萨斯', 'brand-93': '雷诺', 'brand-850': '领克', 'brand-914': '领途汽车',
                         'brand-879': 'MARUSSIA', 'brand-109': 'MG', 'brand-108': 'MINI', 'brand-988': '摩托车',
                         'brand-572': '摩根', 'brand-103': '玛莎拉蒂', 'brand-1016-n': '美亚', 'brand-514': '迈凯伦',
                         'brand-104': '迈巴赫', 'brand-930': '迈莎锐', 'brand-977': '迈迈', 'brand-102': '马自达',
                         'brand-954': '南车时代', 'brand-915': '哪吒汽车', 'brand-826': '尼奥普兰', 'brand-111': '纳智捷',
                         'brand-114': '欧宝', 'brand-902': '欧拉', 'brand-558': '欧朗', 'brand-113': '讴歌',
                         'brand-894': 'Polestar', 'brand-864': '帕加尼', 'brand-824': '帕卡德', 'brand-815': '乔治·巴顿',
                         'brand-816': '全球鹰', 'brand-896': '前途', 'brand-520': '启辰', 'brand-118': '奇瑞',
                         'brand-909': '庆铃汽车', 'brand-119': '起亚', 'brand-542': '骐铃汽车', 'brand-504': '如虎',
                         'brand-891': '容大智造', 'brand-121': '日产', 'brand-890': '瑞驰新能源', 'brand-123': '瑞麒',
                         'brand-122': '荣威', 'brand-881': 'Scion', 'brand-956': 'SHELBY', 'brand-10': 'smart',
                         'brand-872': 'SRM鑫源', 'brand-831': 'SWM斯威汽车', 'brand-126': '三菱', 'brand-982': '上喆',
                         'brand-1004-n': '上汽MAXUS', 'brand-536': '世爵', 'brand-131': '双环', 'brand-132': '双龙',
                         'brand-825': '思派朗', 'brand-958': '思皓', 'brand-578': '思铭', 'brand-134': '斯巴鲁',
                         'brand-135': '斯柯达', 'brand-838': '斯达泰克', 'brand-124': '萨博', 'brand-813': '赛麟',
                         'brand-802': '陕汽通家', 'brand-929': '天际汽车', 'brand-809': '天马', 'brand-827': '泰卡特',
                         'brand-510': '特斯拉', 'brand-566': '腾势', 'brand-837': 'WEY', 'brand-811': '万丰',
                         'brand-550': '五十铃', 'brand-148': '五菱汽车', 'brand-145': '威兹曼', 'brand-873': '威马汽车',
                         'brand-144': '威麟', 'brand-146': '沃尔沃', 'brand-978': '潍柴汽车', 'brand-560': '潍柴英致',
                         'brand-858': '瓦滋UAZ', 'brand-851': '蔚来', 'brand-918': '小鹏汽车', 'brand-807': '新凯',
                         'brand-904': '新特汽车', 'brand-928': '星途', 'brand-151': '现代', 'brand-150': '西雅特',
                         'brand-154': '雪佛兰', 'brand-155': '雪铁龙', 'brand-156': '一汽', 'brand-981': '一汽凌河',
                         'brand-853': '云度', 'brand-810': '云雀汽车', 'brand-157': '依维柯', 'brand-897': '宇通客车',
                         'brand-852': '御捷', 'brand-161': '永源', 'brand-158': '英菲尼迪', 'brand-898': '裕路',
                         'brand-949': '远程汽车', 'brand-1005-n': '野马汽车', 'brand-947': '银隆新能源', 'brand-834': '驭胜',
                         'brand-170': '中兴', 'brand-167': '中华', 'brand-926': '中华太空', 'brand-582': '中欧汽车',
                         'brand-803': '中顺', 'brand-833': '之诺', 'brand-172': '众泰', 'brand-865': '征服Conquest',}
        # 'brand-532': '知豆', 'brand-912': '重汽', 'brand-924': '重汽王牌'}

    def start_requests(self):
        for i in self.car_dict:
            url = self.start_urls.format(i)
            yield scrapy.Request(method='POST', url=url, headers=self.headers,
                                 meta={'page': 0, 'brand_id': i, "brand_name": self.car_dict[i]}, dont_filter=True)

    def parse(self, response):
        data = json.loads(response.text)
        print(data)
        car_data = data['data']['items']
        if car_data == []:
            return
        response.meta['page'] = response.meta['page'] + 1
        url = self.next_url.format(response.meta['page'], response.meta['brand_id'])
        yield scrapy.Request(method='POST', url=url, headers=self.headers, meta=response.meta, dont_filter=True,
                             callback=self.parse)
        for i in car_data:
            url = 'http://lol.souche.com/carsourcedetailaction/getCarBaseInfo.json?car_id={}&appType=merchant'.format(
                i['id'])
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_car, meta=response.meta)

    def parse_car(self, response):
        car_data = json.loads(response.text)['data']
        print(car_data)
        grap_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_dict = {
            "projectName": "used-car-scrapy",
            "logProgram": website,
            "logProgramPath": "/home/scrapyd/eggs/guazi",
            "logPath": "/home/scrapyd/logs/guazi/{}/".format(website),
            "logTime": grap_time,
            "logMessage": "",
            "logServer": "192.168.1.248",
            "logObjectType": "UsedCarPaChong",
        }
        try:
            self.counts += 1
            logging.log(msg="download   " + str(self.counts) + "  items", level=logging.INFO)
            item = GuaziItem()
            item["carid"] = car_data['id']
            item["car_source"] = "dafengche"
            item["usage"] = car_data['purpose']
            item["grab_time"] = grap_time
            item["update_time"] = None
            item["post_time"] = car_data['update_time']
            item["sold_date"] = None
            item["pagetime"] = None
            item["parsetime"] = grap_time
            item["shortdesc"] = car_data['name']
            item["pagetitle"] = None
            item["url"] = response.url
            item["newcarid"] = None
            item["status"] = "sale"
            item["brand"] = car_data['brand_code']
            item["series"] = car_data['series_name']
            item["factoryname"] = None
            item["modelname"] = car_data['model_name']
            item["brandid"] = car_data['brand_code']
            item["familyid"] = None
            item["seriesid"] = ['series_code']
            try:
                item['makeyear'] = re.findall(r"(\d*)款", response.meta["shortdesc"])[0]
            except:
                item['makeyear'] = None
            item["registeryear"] = None
            item["produceyear"] = None
            item["body"] = None
            item["bodystyle"] = None

            item["level"] = None
            item["fueltype"] = None
            item["driverway"] = None
            item["output"] = car_data['volume']
            item["guideprice"] = car_data['new_car_price']
            # 新车指导价46.30万(含税)
            item["guidepricetax"] = None
            item["doors"] = None
            item["emission"] = car_data['emissions']
            item["gear"] = None
            item["geartype"] = car_data['gearbox']
            item["seats"] = None
            item["length"] = None
            item["width"] = None
            item["height"] = None
            item["gearnumber"] = None
            item["weight"] = None
            item["wheelbase"] = None
            item["generation"] = None
            item["fuelnumber"] = None
            item["lwv"] = None
            item["lwvnumber"] = None
            item["maxnm"] = None
            item["maxpower"] = None
            item["maxps"] = None
            item["frontgauge"] = None
            item["compress"] = None
            item["registerdate"] = car_data['first_license_plate_date']
            item["years"] = None
            item["paytype"] = None
            item["price1"] = car_data['sale_price']
            item["pricetag"] = None
            item["mileage"] = car_data['mileage']
            item["color"] = car_data['color']
            item["city"] = car_data['check_city']
            item["prov"] = car_data['check_province']
            item["guarantee"] = None
            item["totalcheck_desc"] = None

            item["totalgrade"] = None

            item["contact_type"] = None
            item["contact_name"] = None
            item["contact_phone"] = None
            item["contact_address"] = None
            item["contact_company"] = None
            item["contact_url"] = None
            item["change_date"] = None
            item["change_times"] = None
            item["insurance1_date"] = None
            item["insurance2_date"] = None
            item["hascheck"] = None
            item["repairinfo"] = None
            item["yearchecktime"] = None
            item["carokcf"] = None
            item["carcard"] = None
            item["carinvoice"] = None
            item["accident_desc"] = None
            item["accident_score"] = None
            item["outer_desc"] = None
            item["outer_score"] = None
            item["inner_desc"] = None
            item["inner_score"] = None
            item["safe_desc"] = None
            item["safe_score"] = None
            item["road_desc"] = None
            item["road_score"] = None
            item["lastposttime"] = None
            item["newcartitle"] = None
            item["newcarurl"] = None
            item["img_url"] = car_data['imgs'][0]
            item["first_owner"] = None
            item["carno"] = car_data['phone']
            item["carnotype"] = None
            item["carddate"] = None
            item["changecolor"] = None
            item["outcolor"] = None
            item["innercolor"] = None
            item["desc"] = car_data['car_describe']
            item["statusplus"] = response.url + "-None-sale-" + str(item["price1"]) + str(6)
        except:
            log_dict["logType"] = 'ERROR'
            log_dict["logMessage"] = response.url
            logging.log(msg=json.dumps(log_dict, ensure_ascii=False), level=logging.INFO)
        else:
            log_dict["logType"] = 'INFO'
            log_dict["logMessage"] = "successful"
            log_dict["logObject"] = {
                "field": {
                    "carsource": website,
                    "grab_time": item["grab_time"],
                    "price1": item["price1"],
                    "mileage": item["mileage"],
                    "post_time": item["post_time"],
                    "sold_date": item["sold_date"],
                    "city": item["city"],
                    "registerdate": item["registerdate"]
                },
                "info": {
                    "dataBaseType": "mysql",
                    "dataBaseName": settings["MYSQLDB_DB"],
                    "tableName": website + '_online',
                    "saveStatus": ""
                }
            }
            returndf = self.bf.isContains(item["statusplus"])
            # 1数据存在，0数据不存在
            if returndf == 1:
                log_dict["logObject"]["info"]["saveStatus"] = "true"
            else:
                log_dict["logObject"]["info"]["saveStatus"] = "false"
            logging.log(msg=json.dumps(log_dict, ensure_ascii=False), level=logging.INFO)
            yield item
