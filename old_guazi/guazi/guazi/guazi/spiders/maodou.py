# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.conf import settings
from scrapy.mail import MailSender
import re
import logging

website = 'xcar1'


class CarSpider(scrapy.Spider):
    name = website
    allowed_domains = ["xcar.com.cn"]
    start_urls = [
        "http://newcar.xcar.com.cn/m50122/config.htm"
    ]

    def __init__(self, **kwargs):
        # args
        super(CarSpider, self).__init__(**kwargs)
        # problem report
        self.mailer = MailSender.from_settings(settings)
        self.counts = 0
        self.carnum = 50000
        # Mongo
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MONGODB_DB', 'newcar', priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')

    # family select
    def parse(self, response):
        car = []
        car2=[]
        car_list = response.xpath("//tr/td[1]")
        car_list=car_list.xpath("string(.)").extract()
        for i in car_list:
            car.append(i.split("：")[0].split("\n")[1].strip(" "))
        for i in car:
            if i!="":
                car2.append(i)
        print(car2)
        namelist = ['price', 'an_price', 'bname', 'type_name', 'disl_working_mpower', 'dynamic', 'speed_transtype',
                    'length_width_height', 'door_seat_frame', 'ear', 'mspeed', 'hatime', 'comfuel', 'ypolicy',
                    'length', 'width', 'height', 'wheelbase', 'weight', 'clearance', 'btread', 'ftread', 'frame',
                    'door', 'seat', 'oilbox', 'trunk', 'mtrunk', 'enginetype', 'disl', 'mdisl', 'working', 'cyarrange',
                    'cylinder', 'cylindernum', 'cr', 'valvegear', 'cylinderbore', 'journey', 'cylinderblock',
                    'cylinderhead', 'mhpower', 'mpower', 'mtorque', 'fuel', 'fuelno', 'sfueltype', 'envstand',
                    'stechnology', 'speed', 'transtype', 'tranname', 'drivetype', 'awdtype', 'mdifferentialtype',
                    'carstruc', 'hptype', 'fsustype_text', 'bsustype_text', 'fdifferentiallock', 'mdifferentiallock',
                    'rdifferentiallock', 'fbraketype', 'bbraketype', 'park', 'ftiresize', 'btiresize', 'sparetire',
                    'isdairbag', 'isfhairbag', 'isfsairbag', 'iskairbag', 'pedeairbag', 'isofix', 'istpmonitor',
                    'istpruning', 'isseatbeltti', 'iseanti', 'enginelock', 'iscclock', 'isrekey', 'baws', 'nightwork',
                    'isabs', 'isebd', 'iseba', 'isasr', 'isesp', 'hillassist', 'hdc', 'isuphillassist', 'isandstitch',
                    'deviatewar', 'iskbsus', 'issteesys', 'aba', 'iswindow', 'isarwindow', 'isspround', 'isaluhub',
                    'eletric_sdoor', 'electricdoor', 'rack', 'agrille', 'elecartrunk', 'isleasw', 'isswud', 'ismultisw',
                    'steelectrol', 'steewhmory', 'iswheelhot', 'isswshift', 'isassibc', 'isparkvideo', 'panorcamera',
                    'ispark', 'isascd', 'autcruise', 'isnokeyinto', 'isnokeysys', 'display', 'ishud', 'isleaseat',
                    'sportseat', 'isseatadj', 'isfseatadj', 'reseateletrol', 'iswaistadj', 'shouldersdj', 'thighsdj',
                    'iseseatmem', 'isseathot', 'isseatknead', 'chairmassage', 'secseatbadj', 'secseatfbwadj',
                    'isbseatlay', 'isbseatplay', 'thirdrowseat', 'isfarmrest', 'isbcup', 'isgps', 'isbluetooth',
                    'iscclcd', 'isblcd', 'humancomption', 'interservice', 'istv', 'audio_brand', 'aux', 'ismp3',
                    'isscd', 'ismcd', 'allcd', 'onedvd', 'ismdvd', 'is2audio', 'is4audio', 'is6audio', 'is8audio',
                    'isxelamp', 'isledlamp', 'isjglamp', 'ishfoglamp', 'dayrunlight', 'islampheiadj', 'isautohlamp',
                    'bendauxlig', 'isturnhlamp', 'islampclset', 'interatmlamp', 'isfewindow', 'isgnhand',
                    'ispreventionuv', 'fseat_pglass', 'isermirror', 'ishotrmirror', 'iseprmirror', 'ecm',
                    'ismemorymirror', 'isbssvisor', 'ishbsvisor', 'issvisordr', 'isinswiper', 'rwiper', 'isairc',
                    'isaairc', 'fseat_ac', 'isbsairo', 'istempdct', 'isairfilter', 'iscaricebox', 'other', ]
