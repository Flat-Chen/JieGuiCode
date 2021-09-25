import json

import requests
import scrapy
import pymongo
import re
import pandas as pd
from redis import Redis
from tqdm import tqdm
import execjs
import time


class AutohomeNewcarRecrawlSpider(scrapy.Spider):
    name = 'autohome_newcar_recrawl'
    allowed_domains = ['autohome.com.cn']

    # start_urls = ['http://autohome.com.cn/']
    #
    def __init__(self):
        # redis_cli = Redis(host="192.168.1.249", port=6379, db=3)
        # url_dict_list = redis_cli.smembers('autohome_newcar', )
        # vehicle_list = []
        # brand_item = {}
        # for i in tqdm(url_dict_list):
        #     json_str = str(i, 'utf-8').split('*')[1]
        #     data_json = eval(json_str)
        #     item = {}
        #     item['producestatus'] = data_json['producestatus']
        #     item['model'] = data_json['model']
        #     item['autohomeid'] = data_json['autohomeid']
        #     item['factoryname'] = data_json['factoryname']
        #     item['factoryid'] = data_json['factoryid']
        #     item['familyname'] = data_json['familyname']
        #     item['familyid'] = data_json['familyid']
        #     item['brandname'] = data_json['brandname']
        #     item['brandid'] = data_json['brandid']
        #     item['depth'] = data_json['depth']
        #     vehicle_list.append(item)
        #     brand_item[data_json['autohomeid']] = item
        # self.brand_item = brand_item
        self.js_header = """var style ={
            sheet:{
                insertRule:function(){}
            }
        }
        var document ={
            createElement :function(){ return style}
            ,head:{
                appendChild:function(){}
            }
            ,querySelectorAll :function(){}
        }

        global.window =global
        var window ={
            getComputedStyle :true
        } 

        obj ={}
        !"""
        self.js_end = """    
                function $InsertRuleRun$() {
                for ($index$ = 0; $index$ < $rulePosList$.length; $index$++) {
                    var $tempArray$ = $Split$($rulePosList$[$index$], ',');
                    var $temp$ = '';
                    for ($itemIndex$ = 0; $itemIndex$ < $tempArray$.length; $itemIndex$++) {
                        $temp$ += $ChartAt$($tempArray$[$itemIndex$]) + '';
                    }
                    obj["<span class='"+$GetClassName$($index$).split(".")[1]+"'></span>"] =$temp$
                }
            }
        })(document);
            function get_obj(){
            return obj
            }"""

    def start_requests(self):
        mongo_url = 'mongodb://192.168.1.94:27017/'
        connection = pymongo.MongoClient(mongo_url)
        db = connection['newcar']
        collection = db['autohome_newcar_problemid']
        data = list(collection.find({}, {'_id': 0, 'vehicle_type_id': 1}))
        vehicle_type_id_list = [i['vehicle_type_id'] for i in data]
        vehicle_type_id_list = set(vehicle_type_id_list)
        print(len(vehicle_type_id_list))
        for autohome_id in vehicle_type_id_list:
            url = 'https://car.autohome.com.cn/config/spec/{}.html'.format(autohome_id)
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'autohome_id': autohome_id})

    def parse(self, response):
        autohome_id = response.meta['autohome_id']
        yingshe_dict = {}
        js_text = re.findall(r"<script>(.*?);</script>", response.text)
        for js in js_text:
            if "</style><script>" in js:
                js = js.split("</style><script>")[1]
            code1 = js.replace('\n', '')
            code = self.js_header + code1.replace("})(document)", "") + self.js_end
            js_code = execjs.compile(code)
            a = js_code.call('get_obj')
            yingshe_dict.update(a)
        try:
            config = re.findall(r"var config = (.*?);", response.text)[0]
        except:
            config = None
        try:
            option = re.findall(r"var option = (.*?);", response.text.replace("&nbsp;", "").replace("&amp;", ""))[0]
        except:
            option = None
        try:
            color = re.findall(r"var color = (.*?);", response.text)[0]
            color = eval(color)
        except:
            color = None
        try:
            innercolor = re.findall(r"var innerColor =(.*?);", response.text)[0]
            innercolor = eval(innercolor)
        except:
            innercolor = None
        for i in yingshe_dict:
            config = config.replace(i, yingshe_dict[i])
            option = option.replace(i, yingshe_dict[i])
        config = eval(config)
        option = eval(option)
        config_list = [option, config]
        config_dict = {}
        for aa in config_list:
            for i in aa["result"]:
                try:
                    configtypeitems = aa["result"]["configtypeitems"]
                except:
                    configtypeitems = aa["result"]["paramtypeitems"]
                for gg in configtypeitems:
                    use_dict = {}
                    try:
                        config_end = gg['configitems']
                    except:
                        config_end = gg['paramitems']
                    for ff in config_end:
                        name = ff["name"]
                        for value in ff["valueitems"]:
                            if str(value['specid']) == autohome_id:
                                try:
                                    if len(value['sublist']) > 0:
                                        ff = ""
                                        for i in value["sublist"]:
                                            ff = ff + i["subname"] + ","
                                        use_dict.update({name: ff})
                                    else:
                                        use_dict.update({name: value["value"]})
                                except:
                                    use_dict.update({name: value["value"]})
                        config_dict.update({gg['name']: use_dict})
        color_list = []
        for i in color["result"]["specitems"]:
            for x in i["coloritems"]:
                color_list.append(x["name"])
        innercolor_list = []
        for i in innercolor["result"]["specitems"]:
            for x in i["coloritems"]:
                innercolor_list.append(x["name"])
        item = {}
        item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["configs"] = json.dumps(config_dict, ensure_ascii=False)
        try:
            # item["brandname"] = self.brand_item[autohome_id]["brandname"]
            # item["brandid"] = self.brand_item[autohome_id]["brandid"]
            # item["factoryname"] = self.brand_item[autohome_id]["factoryname"]
            # item["factoryid"] = self.brand_item[autohome_id]["factoryid"]
            # item["familyname"] = self.brand_item[autohome_id]["familyname"]
            # item["familyid"] = self.brand_item[autohome_id]["familyid"]
            # item["producestatus"] = self.brand_item[autohome_id]["producestatus"]
            # item["model"] = self.brand_item[autohome_id]["model"]
            # item["autohomeid"] = self.brand_item[autohome_id]["autohomeid"]
            item["shortdesc"] = config_dict['基本参数']["车型名称"]
            item["guideprice"] = config_dict['基本参数']["厂商指导价(元)"]
            item["statusplus"] = response.url + item["configs"] + str(11111111115545551165521511) + \
                                 str(item["factoryname"]) + str(item["familyname"]) + str(item["factoryid"]) +\
                                 str(item["familyid"]) + str(item["brandname"]) + str(item["brandid"])
        except:
            pass
        item["color"] = str(color_list)
        # try:
        #     item["year"] = re.findall(r"(\d+)款", self.brand_item[autohome_id]["shortdesc"])[0]
        # except:
        #     pass
        item["innercolor"] = str(innercolor_list)
        print(item)
