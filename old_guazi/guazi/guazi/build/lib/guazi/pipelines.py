# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import pymongo

import pandas as pd

from sqlalchemy import create_engine
from scrapy.conf import settings
from .redis_bloom import BloomFilter


# price34.22prov3city3mile0.1model1206year2016month10typedealer_price
class GuaziPipeline(object):

    def __init__(self):
        # def __init__(self,settings):
        self.count = 0
        self.engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(settings['MYSQLDB_USER'],
                                                                                         settings['MYSQLDB_PASS'],
                                                                                         settings['MYSQL_SERVER'],
                                                                                         settings['MYSQL_PORT'],
                                                                                         settings['MYSQLDB_DB'], ))

        self.connection = pymongo.MongoClient(
            settings["MONGODB_SERVER"],
            settings["MONGODB_PORT"]
        )
        db = self.connection[settings["MONGODB_DB"]]
        self.collection = db[settings["MONGODB_COLLECTION"]]
        # print("爬取的网站： "  ,settings["WEBSITE"])
        self.bf = BloomFilter(key='b1f_' + settings["WEBSITE"])
        # self.bf = BloomFilter(key='b1f_guazi')

        # self.settings = settings)

    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler.settings)

    def process_item(self, item, spider):
        #  用来去重的键 statusplus
        returndf = self.bf.isContains(item["statusplus"])

        # 1数据存在，0数据不存在
        if returndf == 1:
            logging.log(msg="Car duplication!!!!", level=logging.INFO)
            return item
        else:
            self.count = self.count + 1
            self.bf.insert(item["statusplus"])
            # 如果不在 列表内，存mysql  如果在 存 mongodb
            if spider.name not in ["che300", "che300_old", "autohome_car_forecast", "autohome_car_forecast2","autohome_brand_image",
                                   "autohome_car_forecast_test", "souhu", 'autohome_custom_price2',
                                   'autohome_newcar_zhu', 'che58_newcar', 'che58_grade', "autohome_custom_price2_avg",
                                   "dongchedi_car", "dongchedi_price", "guchewang_chexing"]:
                try:
                    df = pd.DataFrame([item])
                    df.to_sql(name=settings["WEBSITE"] + "_online", con=self.engine, if_exists="append", index=False)
                except Exception as e:
                    logging.log(msg="fail to save  %s" % e, level=logging.INFO)
                else:
                    logging.log(msg="add car in SQL %d" % self.count, level=logging.INFO)
                finally:
                    return item
            else:
                try:
                    self.collection.insert(dict(item))
                except Exception as e:
                    logging.log(msg="fail to save  %s" % e, level=logging.INFO)
                else:
                    logging.log(msg="add car in MONGODB %d" % self.count, level=logging.INFO)
                finally:
                    return item
