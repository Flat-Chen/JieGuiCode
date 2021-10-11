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

website = 'che300_old'


# redis_cli = Redis(host="192.168.1.249", port=6379, db=2)


# 先循环城市 然后在循环车
class CarSpider(scrapy.Spider):
    name = website
    # start_urls = get_url()
    parse_car_url = "https://dingjia.che300.com/app/CarDetail/getInfo/{}"
    headers = {'Referer': 'https://m.che300.com',
               "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}

    custom_settings = {
        # 'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        "COOKIES_ENABLED": False
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        settings.set('MONGODB_COLLECTION', website, priority='cmdline')
        self.counts = 0

    # def redis_tools(self, url):
    #     redis_md5 = md5(url.encode("utf-8")).hexdigest()
    #     valid = redis_cli.sadd(website, redis_md5)
    #     return valid

    def start_requests(self):
        # 测试500页之后有数据的城市
        # for i in range(300000000):
        for i in range(300000000):
            url = self.parse_car_url.format(i)
            #     yield scrapy.Request(url, headers=self.headers)
            yield scrapy.Request(url=url.format(i),
                                 headers=self.headers, meta={"id": i})

    def parse(self, response):
        try:
            car_dict = json.loads(response.text)["success"]
        except:
            logging.log(msg="this cai is inexistence/------------{}".format(response.meta["id"]), level=logging.INFO)
            return
        else:
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
            try:
                item["match_step"] = car_dict["match_step"]
            except:
                item["match_step"] = None
            item["sold_date"] = car_dict["sold_date"]
            item["tlci_date"] = car_dict["tlci_date"]
            item["car_service"] = car_dict["car_service"]
            item["audit_date"] = car_dict["audit_date"]
            item["next_year_eval_price"] = car_dict["next_year_eval_price"]
            item["residual_value"] = car_dict["residual_value"]
            try:
                item["qg_month"] = car_dict["qg_month"]
            except:
                item["qg_month"] = None
            try:
                item["qg_mile"] = car_dict["qg_mile"]
            except:
                item["qg_mile"] = None
            try:
                item["cr_day"] = car_dict["cr_day"]
            except:
                item["cr_day"] = None
            try:
                item["qa_flag"] = car_dict["qa_flag"]
            except:
                item["qa_flag"] = None
            try:
                item["qa_price"] = car_dict["qa_price"]
            except:
                item["qa_price"] = None
            try:
                item["inspected"] = car_dict["inspected"]
            except:
                item["inspected"] = None
            try:
                item["weight"] = car_dict["weight"]
            except:
                item["weight"] = None
            try:
                item["is_trusted"] = car_dict["is_trusted"]
            except:
                item["is_trusted"] = None
            try:
                item["match_rate"] = car_dict["match_rate"]
            except:
                item["match_rate"] = None
            try:
                item["series_level"] = car_dict["series_level"]
            except:
                item["series_level"] = None
            try:
                item["series_level_gid"] = car_dict["series_level_gid"]
            except:
                item["series_level_gid"] = None
            try:
                item["liter_value"] = car_dict["liter_value"]
            except:
                item["liter_value"] = None
            try:
                item["gear_type_value"] = car_dict["gear_type_value"]
            except:
                item["gear_type_value"] = None
            try:
                item["liter_turbo"] = car_dict["liter_turbo"]
            except:
                item["liter_turbo"] = None
            item["city_name"] = car_dict["city_name"]
            try:
                item["filter_discharge_standard"] = car_dict["filter_discharge_standard"]
            except:
                item["filter_discharge_standard"] = None
            try:
                item["drive_type"] = car_dict["drive_type"]
            except:
                item["drive_type"] = None
            try:
                item["maker_type"] = car_dict["maker_type"]
            except:
                item["maker_type"] = None
            try:
                item["fuel_type"] = car_dict["fuel_type"]
            except:
                item["fuel_type"] = None
            try:
                item["seat_number_code"] = car_dict["seat_number_code"]
            except:
                item["seat_number_code"] = None
            item["price_reduce_offset"] = car_dict["price_reduce_offset"]
            item["price_reduce_rate"] = car_dict["price_reduce_rate"]
            item["price_reduce_count"] = car_dict["price_reduce_count"]
            item["re_eval"] = car_dict["re_eval"]
            try:
                item["duplicated"] = car_dict["duplicated"]
            except:
                item["duplicated"] = None
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
            # print(item)
