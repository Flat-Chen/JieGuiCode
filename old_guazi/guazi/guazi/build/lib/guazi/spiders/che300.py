import json
import time

import pandas as pd
import re

from redis import Redis

from ..items import Che300Item
import scrapy
import logging
from scrapy.conf import settings
from hashlib import md5

website = 'che300'

redis_cli = Redis(host="192.168.1.249", port=6379, db=2)


# 先循环城市 然后在循环车
class CarSpider(scrapy.Spider):
    name = website
    # start_urls = get_url()
    city_id_list = ['13', '43', '71', '99', '127', '155', '182', '209', '235', '259', '281', '299', '316', '330', '343',
                    '353', '363', '1', '4', '14', '44', '72', '100', '128', '156', '183', '210', '236', '28', '58',
                    '86',
                    '114', '142', '170', '197', '224', '249', '271', '292', '309', '326', '340', '23', '53', '81',
                    '109',
                    '137', '165', '192', '219', '245', '21', '51', '79', '107', '135', '163', '190', '217', '243',
                    '266',
                    '288', '305', '322', '336', '20', '50', '78', '106', '134', '162', '189', '216', '242', '265',
                    '287',
                    '304', '321', '335', '347', '357', '367', '373', '378', '382', '386', '24', '54', '82', '110',
                    '138',
                    '166', '193', '220', '246', '268', '290', '307', '324', '338', '349', '359', '369', '375', '396',
                    '19',
                    '49', '77', '105', '133', '161', '188', '215', '241', '264', '286', '303', '320', '334', '18', '48',
                    '76', '104', '132', '160', '187', '214', '240', '263', '285', '302', '319', '333', '346', '356',
                    '366',
                    '17', '47', '75', '103', '131', '159', '186', '213', '239', '262', '284', '301', '318', '332',
                    '345',
                    '355', '365', '372', '10', '40', '68', '96', '124', '152', '179', '206', '232', '256', '278', '297',
                    '314', '5', '35', '63', '91', '119', '147', '174', '201', '227', '252', '274', '15', '45', '73',
                    '101',
                    '129', '157', '184', '211', '237', '260', '282', '11', '41', '69', '97', '125', '153', '180', '207',
                    '233', '257', '279', '298', '315', '9', '39', '67', '95', '123', '151', '178', '205', '231', '8',
                    '38',
                    '66', '94', '122', '150', '177', '204', '230', '255', '277', '296', '313', '329', '32', '62', '90',
                    '118', '146', '173', '200', '226', '251', '273', '294', '311', '30', '60', '88', '116', '144', '26',
                    '56', '84', '112', '140', '168', '195', '222', '22', '52', '80', '108', '136', '164', '191', '218',
                    '244', '267', '289', '306', '323', '337', '348', '358', '368', '374', '379', '383', '387', '6',
                    '36',
                    '64', '92', '120', '148', '175', '202', '228', '253', '275', '3', '27', '57', '85', '113', '141',
                    '169',
                    '196', '223', '248', '270', '16', '46', '74', '102', '130', '158', '185', '212', '238', '261',
                    '283',
                    '300', '317', '331', '344', '354', '364', '2', '29', '59', '87', '115', '143', '171', '198', '31',
                    '61',
                    '89', '117', '145', '172', '199', '225', '250', '272', '293', '310', '327', '341', '351', '361',
                    '370',
                    '376', '380', '384', '388', '390', '392', '393', '395', '397', '25', '55', '83', '111', '139',
                    '167',
                    '194', '221', '247', '269', '291', '308', '325', '339', '350', '360', '12', '42', '70', '98', '126',
                    '154', '181', '208', '234', '258', '280']
    brand_id_list = ['1', '3', '2', '4', '536', '5', '7', '15', '172', '144', '6', '9', '12', '10', '8', '499', '853',
                     '115',
                     '156', '17', '14', '167', '573', '13', '837', '11', '20', '16', '18', '19', '21', '23', '22', '24',
                     '497', '25', '639', '142', '26', '170', '30', '33', '28', '32', '27', '29', '31', '574', '36',
                     '35',
                     '39', '545', '40', '162', '37', '42', '38', '147', '543', '41', '44', '45', '636', '46', '47',
                     '48',
                     '586', '50', '56', '51', '54', '57', '52', '173', '146', '160', '560', '53', '618', '495', '55',
                     '145',
                     '58', '59', '63', '143', '62', '65', '60', '66', '542', '68', '61', '64', '634', '852', '67', '69',
                     '71', '70', '572', '825', '817', '752', '73', '157', '819', '75', '74', '158', '562', '77', '546',
                     '76',
                     '78', '79', '90', '80', '84', '640', '85', '83', '619', '81', '87', '561', '682', '86', '89',
                     '815',
                     '82', '588', '88', '587', '661', '712', '750', '92', '93', '94', '96', '97', '95', '820', '641',
                     '98',
                     '558', '99', '100', '836', '713', '101', '103', '102', '635', '637', '503', '716', '104', '105',
                     '106',
                     '107', '632', '624', '108', '109', '110', '631', '570', '112', '113', '498', '111', '116', '34',
                     '169',
                     '114', '117', '118', '149', '501', '120', '119', '166', '816', '150', '121', '163', '122', '544',
                     '571',
                     '123', '617', '124', '616', '125', '126', '127', '155', '717', '751', '128', '564', '130', '151',
                     '638',
                     '148', '132', '159', '131', '615', '133', '135', '134', '565', '568', '547', '136', '563', '838',
                     '824',
                     '138', '137', '139', '152', '140', '154', '168', '569']
    # 判断 城市是否有足够的车源，如果充足 则循环车系
    brand_city_url = "https://m.che300.com/all_list.htm?carBrand={}&city={}"
    parse_car_url = "https://dingjia.che300.com/app/CarDetail/getInfo/{}"
    headers = {'Referer': 'https://m.che300.com',
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        self.counts = 0

    def redis_tools(self, url):
        redis_md5 = md5(url.encode("utf-8")).hexdigest()
        valid = redis_cli.sadd(website, redis_md5)
        return valid

    def start_requests(self):
        # 测试500页之后有数据的城市
        redis_cli.delete(website)
        for city_id in set(self.city_id_list):
            for brand_id in set(self.brand_id_list):
                yield scrapy.Request(url=self.brand_city_url.format(brand_id, city_id), headers=self.headers,
                                     meta={"city_id": city_id, "brand_id": brand_id, "page": 1})

    def get_car_id(self, car_url_list):
        df = pd.DataFrame(car_url_list, columns=["url"])
        df["id"] = df["url"].str.findall("buycar/x(\d*)")
        return df["id"].tolist()

    def parse(self, response):
        #     首先判断是否有数据，然后在 判断
        car_url_list = response.xpath("//a[@class='carItem']/@href").extract()
        if car_url_list == []:
            return
        else:
            car_id_list = self.get_car_id(car_url_list)
            for car_id in car_id_list:
                url = self.parse_car_url.format(car_id[0])
                valid = self.redis_tools(url)
                if valid == 0:
                    logging.log(msg="this http request is repetition", level=logging.INFO)
                    return
                else:
                    yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_car)
        page = response.meta["page"] + 1
        brand_id = response.meta["brand_id"]
        city_id = response.meta["city_id"]
        url = self.brand_city_url.format(brand_id, city_id) + "&page={}".format(page)
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse,
                             meta={"city_id": city_id, "brand_id": brand_id, "page": page})

    def parse_car(self, response):
        car_dict = json.loads(response.text)["success"]
        item = Che300Item()
        item["we_grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["parse_url"] = response.url
        item["id"] = car_dict["id"]
        item["url"] = car_dict["url"]
        item["city"] = car_dict["city"]
        item["prov"] = car_dict["prov"]
        item["title"] = car_dict["title"]
        item["car_desc"] = car_dict["car_desc"]
        item["brand_id"] = car_dict["brand_id"]
        item["brand_name"] = car_dict["brand_name"]
        item["series_id"] = car_dict["series_id"]
        item["series_name"] = car_dict["series_name"]
        item["model_id"] = car_dict["model_id"]
        item["model_name"] = car_dict["model_name"]
        item["price"] = car_dict["price"]
        item["mile_age"] = car_dict["mile_age"]
        item["register_date"] = car_dict["register_date"]
        item["reg_year"] = car_dict["reg_year"]
        item["gear_type"] = car_dict["gear_type"]
        item["color"] = car_dict["color"]
        item["liter"] = car_dict["liter"]
        item["tel"] = car_dict["tel"]
        item["tel_url"] = car_dict["tel_url"]
        item["contactor"] = car_dict["contactor"]
        item["seller_type"] = car_dict["seller_type"]
        item["dealer_id"] = car_dict["dealer_id"]
        item["dealer_name"] = car_dict["dealer_name"]
        item["car_source"] = car_dict["car_source"]
        item["car_status"] = car_dict["car_status"]
        item["post_time"] = car_dict["post_time"]
        item["grab_time"] = car_dict["grab_time"]
        item["update_time"] = car_dict["update_time"]
        item["model_price"] = car_dict["model_price"]
        item["eval_price"] = car_dict["eval_price"]
        item["vpr"] = car_dict["vpr"]
        item["match_step"] = car_dict["match_step"]
        item["sold_date"] = car_dict["sold_date"]
        item["tlci_date"] = car_dict["tlci_date"]
        item["car_service"] = car_dict["car_service"]
        item["audit_date"] = car_dict["audit_date"]
        item["next_year_eval_price"] = car_dict["next_year_eval_price"]
        item["residual_value"] = car_dict["residual_value"]
        item["qg_month"] = car_dict["qg_month"]
        item["qg_mile"] = car_dict["qg_mile"]
        item["cr_day"] = car_dict["cr_day"]
        item["qa_flag"] = car_dict["qa_flag"]
        item["qa_price"] = car_dict["qa_price"]
        item["inspected"] = car_dict["inspected"]
        item["weight"] = car_dict["weight"]
        item["is_trusted"] = car_dict["is_trusted"]
        item["match_rate"] = car_dict["match_rate"]
        item["series_level"] = car_dict["series_level"]
        item["series_level_gid"] = car_dict["series_level_gid"]
        item["liter_value"] = car_dict["liter_value"]
        item["gear_type_value"] = car_dict["gear_type_value"]
        item["liter_turbo"] = car_dict["liter_turbo"]
        item["city_name"] = car_dict["city_name"]
        item["filter_discharge_standard"] = car_dict["filter_discharge_standard"]
        item["drive_type"] = car_dict["drive_type"]
        item["maker_type"] = car_dict["maker_type"]
        item["fuel_type"] = car_dict["fuel_type"]
        item["seat_number_code"] = car_dict["seat_number_code"]
        item["price_reduce_offset"] = car_dict["price_reduce_offset"]
        item["price_reduce_rate"] = car_dict["price_reduce_rate"]
        item["price_reduce_count"] = car_dict["price_reduce_count"]
        item["re_eval"] = car_dict["re_eval"]
        item["duplicated"] = car_dict["duplicated"]
        item["source_name"] = car_dict["source_name"]
        item["fee_rate"] = car_dict["fee_rate"]
        item["fee_floor"] = car_dict["fee_floor"]
        item["fee_ceiling"] = car_dict["fee_ceiling"]
        item["enable_contact"] = car_dict["enable_contact"]
        item["transfer_time"] = car_dict["transfer_time"]
        item["aux_detail"] = car_dict["aux_detail"]
        item["modelInfo"] = car_dict["modelInfo"]
        item["all_content"] = car_dict
        item["statusplus"] = item["post_time"] + item["city_name"] + str(item["price"]) + str(item["id"]) + item[
            "source_name"]
        yield item
