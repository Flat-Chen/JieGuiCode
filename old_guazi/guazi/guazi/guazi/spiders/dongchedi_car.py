# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import re
import sys
import time

import scrapy

# 爬虫名
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
# from ..cookie import get_cookie
from ..items import dongchedi

website = 'dongchedi_car'


# 必须有自己的中间件  切与其他的没有关系
class GuazicarSpider(scrapy.Spider):
    name = website
    start_urls = "https://www.dcdapp.com/motor/brand/m/v1/select/series/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://www.dcdapp.com/auto",
    }
    brand_dict = {'2': '奥迪', '80': '阿斯顿·马丁', '51': '阿尔法·罗密欧', '176': 'ARCFOX', '336': 'AUXUN傲旋', '232': '爱驰',
                  '114': 'ALPINA', '211': 'ABT', '113': 'AC Schnitzer', '178': '艾康尼克', '281': 'Apollo', '177': 'Arash',
                  '224': 'Aria', '256': 'AEV ROBOTICS', '312': 'Aurus', '314': 'Agile Automotive', '313': 'ATS',
                  '364': 'Aspark', '3': '奔驰', '4': '宝马', '9': '本田', '12': '别克', '16': '比亚迪', '20': '保时捷', '81': '宝骏',
                  '61': '标致', '47': '宾利', '27': '奔腾', '52': '北京', '68': '北京汽车', '93': '北汽新能源', '78': '北汽制造',
                  '60': '北汽昌河', '94': '北汽幻速', '69': '北汽威旺', '116': '宝沃',
                  '118': '巴博斯', '117': '比速汽车', '175': '北汽道达', '334': '比德文汽车', '240': '北京清行', '263': '博郡汽车', '82': '布加迪',
                  '204': '拜腾', '219': '宾尼法利纳', '254': '宝腾汽车', '226': '保斐利',
                  '346': 'Bollinger', '270': '博世', '315': 'BAC', '35': '长安', '119': '长安欧尚', '8': '长城', '171': '长安轻型车',
                  '210': '长安跨越', '120': '成功汽车', '304': '车驰汽车', '341': 'Cupra', '233': '刺猬汽车', '227': '昶洧',
                  '180': '长江·EV', '217': 'Corbellati', '316': 'Conquest', '228': 'Caterham', '345': 'Canoo', '1': '大众',
                  '70': '东风风行', '37': '东风风神', '54': '道奇', '55': 'DS', '77': '东南', '95': '东风风光', '79': '东风小康',
                  '246': '大乘汽车', '197': '电咖', '91': '东风', '92': '东风风度', '230': '东风·瑞泰特', '121': '大发', '183': 'Dacia',
                  '291': 'Datsun', '337': 'De Tomaso', '294': 'Donkervoort', '257': 'Dianchè', '353': 'Drako',
                  '286': '大迪汽车', '293': 'Elemental', '5': '丰田', '7': '福特', '44': '法拉利', '57': '福田', '56': '菲亚特',
                  '122': '福迪', '123': '福汽启腾', '205': 'Fisker', '229': 'Faraday Future', '317': 'FM Auto', '284': '弗那萨利',
                  '40': '广汽传祺', '242': '广汽新能源', '58': '观致', '237': '广汽集团', '96': 'GMC', '335': '广通客车', '191': '国金汽车',
                  '97': '广汽吉奥', '266': '国机智骏', '124': '光冈', '249': '高合Hiphi', '268': 'GYON', '267': 'GFG Style',
                  '318': 'Ginetta', '321': 'GTA', '271': '格罗夫', '342': '谷歌', '320': 'GLM', '17': '哈弗', '59': '红旗',
                  '53': '海马', '126': '汉腾汽车', '72': '华泰', '99': '华泰新能源', '131': '华颂', '132': '黄海', '125': '海格',
                  '127': '恒天', '128': '华凯', '184': '华骐', '241': '红星汽车', '199': '合众汽车', '343': '汉龙汽车',
                  '220': 'Hennessey', '278': '霍顿', '322': 'Hispano Suiza', '303': '合创', '165': 'Icona',
                  '223': 'Italdesign', '323': 'Inferno', '73': '吉利汽车', '264': '几何汽车', '14': 'Jeep', '31': '捷豹',
                  '32': '江淮', '209': '捷途', '260': '捷达', '74': '金杯', '100': '江铃', '136': '江铃集团新能源', '190': '君马汽车',
                  '140': '金龙', '133': '金旅', '134': '九龙', '258': '钧天汽车', '273': '捷尼赛思', '354': 'Jannarelly',
                  '30': '凯迪拉克', '84': '克莱斯勒', '142': '凯翼', '139': '开瑞', '138': '卡威', '137': '卡升', '141': 'KTM',
                  '148': '开沃汽车', '135': '卡尔森', '259': '开云汽车', '83': '科尼赛克', '253': 'Karma', '287': '凯佰赫',
                  '350': 'Karlmann', '355': '开利', '22': '雷克萨斯', '19': '路虎', '174': '领克', '62': '林肯', '46': '雷诺',
                  '41': '劳斯莱斯', '42': '兰博基尼', '202': '理想汽车', '50': '铃木', '207': '零跑汽车', '76': '猎豹汽车', '85': '路特斯',
                  '101': '力帆汽车', '102': '陆风', '111': '理念', '282': '雷丁', '145': 'Lorinser', '248': '罗夫哈特', '247': '领途汽车',
                  '146': '陆地方舟', '192': '拉达', '298': 'LeSEE', '212': '绿驰', '301': '雷诺三星', '214': '拉共达', '309': '领志',
                  '324': 'LEVC', '325': 'Lucid', '15': '马自达', '34': '名爵', '45': '玛莎拉蒂', '65': 'MINI', '86': '迈凯伦',
                  '349': '迈迈', '272': '迈莎锐', '147': '摩根', '356': '敏安汽车', '296': 'Mazzanti', '261': 'Mole',
                  '297': 'MELKUS', '328': '米高', '327': 'MAGNA', '351': 'Mahindra', '87': '纳智捷', '200': 'NEVS国能汽车',
                  '299': 'nanoFLOWCELL', '363': 'Neuron EV', '38': '讴歌', '238': '欧拉', '357': '欧联', '196': 'Polestar极星',
                  '88': '帕加尼', '280': '佩奇奥', '329': 'Puritalia', '262': 'Piëch', '13': '起亚', '18': '奇瑞', '109': '启辰',
                  '149': '前途', '143': '全球鹰', '236': '乔治·巴顿', '203': '庆铃汽车', '104': '骐铃汽车', '225': '奇点汽车', '265': '清源汽车',
                  '10': '日产', '36': '荣威', '198': '瑞驰', '244': '容大智造', '150': '如虎', '292': 'Rezvani', '213': 'Rimac',
                  '279': 'Rinspeed', '252': 'RIVIAN', '330': 'RENOVO', '358': 'Radical', '23': '斯柯达', '108': '上汽MAXUS',
                  '26': '三菱', '33': '斯巴鲁', '48': 'smart', '157': 'SWM斯威汽车', '163': '双龙', '193': 'SRM鑫源', '235': '思皓',
                  '105': '思铭', '153': '陕汽通家', '365': '上喆汽车', '231': 'SERES', '152': '赛麟', '275': 'Scion',
                  '338': 'Sono Motors', '359': 'Share2Drive', '360': 'SIN CARS', '63': '特斯拉', '159': '腾势',
                  '250': '天际汽车', '216': '塔塔', '221': '泰克鲁斯·腾风', '285': 'TVR', '305': 'Tramontana', '361': 'TOROIDION',
                  '339': 'Ultima', '348': 'Uniti', '289': 'Venturi', '300': 'Vinfast', '288': 'VLF Automotive',
                  '362': 'Vanda Electric', '24': '沃尔沃', '39': '五菱汽车', '66': 'WEY', '112': '蔚来', '185': '威马汽车',
                  '106': '五十铃', '160': '威麟', '162': '潍柴汽车', '161': '威兹曼', '274': '沃克斯豪尔', '222': 'W Motors', '6': '雪佛兰',
                  '11': '现代', '21': '雪铁龙', '251': '星途', '195': '小鹏汽车', '164': '新凯', '344': '星驰', '234': '新特汽车',
                  '306': '谢尔比', '89': '西雅特', '245': '西尔贝', '29': '英菲尼迪', '67': '一汽', '107': '野马汽车', '90': '依维柯',
                  '167': '驭胜', '172': '宇通客车', '173': '御捷', '188': '云度', '194': '裕路', '206': '云雀汽车', '302': '银隆新能源',
                  '308': '远程汽车', '332': 'YAMAHA', '208': '游侠', '307': '英飒', '64': '众泰', '28': '中华', '169': '中兴',
                  '168': '知豆', '170': '之诺', '215': '正道汽车', '218': 'Zenvo'}

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 10,
    }

    def __init__(self, **kwargs):
        settings.set("WEBSITE", website)
        settings.set("MONGODB_DB", "newcar")
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        super(GuazicarSpider, self).__init__(**kwargs)
        self.used_time = {}

    def start_requests(self):
        for i in self.brand_dict:
            for j in range(5):
                yield scrapy.FormRequest(url=self.start_urls, formdata={"offset": str(j),
                                                                        "limit": "50",
                                                                        "is_refresh": "1",
                                                                        "city_name": "上海"
                    , "brand": str(i)}, headers=self.headers, dont_filter=True)

    # 车型
    def parse(self, response):

        series_list = json.loads(response.text)
        series_list = series_list["data"]["series"]
        if series_list == [] or series_list == None:
            return
        for series in series_list:
            brand_id = series["brand_id"]
            series_id = series["concern_id"]
            series_name = series["outter_name"]
            url = "https://m.dcdapp.com/motor/car_page/m/v1/series_all_json/?series_id=" + str(series_id)

            yield scrapy.Request(url=url, headers=self.headers, callback=self.id_parse,
                                 meta={
                                     "brand_id": brand_id,
                                     "series_id": series_id,
                                     "series_name": series_name,
                                     "brand_name": self.brand_dict[str(brand_id)]
                                 })

    def id_parse(self, response):
        data_list = json.loads(response.text)["data"]["car_year_group"]
        for i in data_list:
            for j in i["cars"]:
                if j["type"] != "1037":
                    continue
                item = {}
                item["shortdesc"] = j["info"]["name"]
                item["price"] = j["info"]["price"]
                item["makeyear"] = j["info"]["year"]
                item["car_id"] = j["info"]["id"]
                try:

                    item["official_price"] = j["info"]["official_price"]
                except:
                    item["official_price"] = None
                try:
                    item["dealer_price"] = j["info"]["owner_price_summary"]["naked_price_avg"]
                except:
                    item["dealer_price"] = None
                response.meta.update(item)
                url = "https://m.dcdapp.com/motor/car_page/v1/get_entity/?car_id_list=" + str(item["car_id"])
                yield scrapy.Request(url=url, headers=self.headers, callback=self.car_prase,
                                     meta=response.meta)

    def car_prase(self, response):
        data_list = response.xpath('//tbody//tr[contains(@class,"normal colorful")]')
        data = {}
        for i in data_list:
            key = i.xpath(".//th/div/text()").extract_first().strip()
            value = i.xpath(".//td//div[@class='content']/text()").extract_first().strip()
            if key == "":
                key = "-"
            data.update({key: value})
        item = {}
        item["factory"] = response.xpath(
            "//div[contains(text(),'厂商')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["body"] = response.xpath(
            "//div[contains(text(),'车身结构')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["doors"] = response.xpath(
            "//div[contains(text(),'车门数')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["seat"] = response.xpath(
            "//div[contains(text(),'座位数')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["driver"] = response.xpath(
            "//div[contains(text(),'驱动方式')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["speed"] = response.xpath(
            "//div[contains(text(),'变速箱')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["engine"] = response.xpath(
            "//div[contains(text(),'发动机')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["car_body"] = response.xpath(
            "//div[contains(text(),'车身结构')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["output"] = response.xpath(
            "//div[contains(text(),'排量(L)')]/../../td//div[@class='content']/text()").extract_first().strip()
        try:
            item["air_type"] = response.xpath(
                "//div[contains(text(),'进气方式')]/../../td//div[@class='content']/text()").extract_first().strip()
        except:
            item["air_type"] = None
        item["environmental"] = response.xpath(
            "//div[contains(text(),'环保标准')]/../../td//div[@class='content']/text()").extract_first().strip()
        item["brand_id"] = response.meta["brand_id"]
        item["series_id"] = response.meta["series_id"]
        item["series_name"] = response.meta["series_name"]
        item["brand_name"] = response.meta["brand_name"]
        item["shortdesc"] = response.meta["shortdesc"]
        item["price"] = response.meta["price"]
        item["makeyear"] = response.meta["makeyear"]
        item["car_id"] = response.meta["car_id"]
        item["official_price"] = None
        item["dealer_price"] = None
        item["statusplus"] = response.url + str(item["price"]) + str(item["dealer_price"]) + str(
            item["official_price"]) + str(2115121)
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["config"] = json.dumps(data, ensure_ascii=False)
        yield item
