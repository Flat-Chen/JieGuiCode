# # -*- coding: utf-8 -*-
# import scrapy
# from ..items import AutohomeItem_price
# import time
# from scrapy.conf import settings
# # from scrapy.mail import MailSender
# import logging
# import json
# import re
# import hashlib
#
# from hashlib import md5
#
# website = 'autohome_price_c_2019'
#
#
# # website ='autohome_price'
#
#
# class CarSpider(scrapy.Spider):
#     name = website
#     allowed_domains = ["autohome.com.cn"]
#     start_urls = 'http://dealer.autohome.com.cn/Ajax?actionName=GetAreasAjax&ajaxProvinceId=0&ajaxCityId=0&ajaxBrandid=0&ajaxManufactoryid=0&ajaxSeriesid=0'
#     custom_settings = {
#         "CONCURRENT_REQUESTS": 5
#         , "DOWNLOAD_DELAY": 1,
#
#     }
#
#     def __init__(self, **kwargs):
#         # args
#         super(CarSpider, self).__init__(**kwargs)
#         # problem report
#         # self.mailer = MailSender.from_settings(settings)
#         self.counts = 0
#         self.carnum = 3000000
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
#             "Referer": "https://dealer.autohome.com.cn/"
#         }
#         # Mongo
#         settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
#         settings.set('MONGODB_DB', 'network', priority='cmdline')
#         settings.set('MONGODB_COLLECTION', website, priority='cmdline')
#
#     def start_requests(self):
#         yield scrapy.Request(url=self.start_urls,headers=self.headers)
#         # get region list
#
#     def parse(self, response):
#         # print(response.text)
#         # list value
#         # print(response.xpath('//pre/text()' ).extract_first())
#         jsonlist = json.loads(response.xpath('//pre/text()').extract_first())
#         # jsonlist =json.loads(response.text)
#         # print(jsonlist)
#         for region in jsonlist['AreaInfoGroups'][0:1]:
#             for prov in region['Values'][0:1]:
#                 provdata = dict()
#                 provdata['Key'] = prov['FirstChar']
#                 provdata['prov_ID'] = prov['Id']
#                 provdata['prov_Name'] = prov['Name']
#                 provdata['prov_Pinyin'] = prov['Pinyin']
#                 provdata['prov_Count'] = prov['Count']
#                 for city in prov['Cities']:
#                     citydata = dict()
#                     citydata['city_ID'] = city['Id']
#                     citydata['city_Name'] = city['Name']
#                     citydata['city_Pinyin'] = city['Pinyin']
#                     citydata['city_Count'] = city['Count']
#                     citydata = dict(citydata, **provdata)
#                     url = 'http://dealer.autohome.com.cn/' + city['Pinyin']
#                     # print(url)
#                     yield scrapy.Request(url=url,
#                                          meta={'citydata': citydata},
#                                          callback=self.parse_brand,headers=self.headers)
#                     # get region list
#
#     # get brand
#     def parse_brand(self, response):
#         for brand in response.xpath("//ul[@class='filter-box']//li[contains(@class,'data-brand-item')]//a[@class='item']"):
#             brandname = brand.xpath('text()').extract_first()
#             brandid = brand.xpath('@href').extract_first().split("/")[3]
#             branddata = {'brandname': brandname, 'brandid': brandid}
#             print(branddata)
#             # urlbase = brand.xpath('@href').extract_first()
#             # url = response.urljoin(urlbase)
#             # yield scrapy.Request(url,
#             #                      meta={'citydata': response.meta['citydata'], 'branddata': branddata},
#             #                      callback=self.parse_network,headers=self.headers)
#
#     def parse_network(self, response):
#         # print(response.url)
#         for shop in response.xpath('//li[@class="list-item"]'):
#             # // dealer.autohome.com.cn / 100587 /  # pvareaid=2113600
#             shopid = shop.xpath('.//a/@href').re('\d+')[0]
#             url = "http://dealer.autohome.com.cn/" + str(shopid) + "/price.html"
#             # print url
#             yield scrapy.Request(url,
#                                  meta={'citydata': response.meta['citydata'], 'branddata': response.meta['branddata']},
#                                  callback=self.parse_carinfo,headers=self.headers)
#
#         # 下一页跳转
#         next = response.xpath("//a[@class='disable']")
#         logging.log(msg=str(next), level=logging.INFO)
#         if next:
#             next_pageurl = next.xpath("@href").extract_first()
#             yield scrapy.Request(response.urljoin(next_pageurl),
#                                  meta={'citydata': response.meta['citydata'], 'branddata': response.meta['branddata']},
#                                  callback=self.parse_network)
#
#         # *********************************************************************************************************************
#         ascnum = int(response.xpath('//span[@class= "num data-dealer-count"]/text()').extract_first())
#         maxpage = int(ascnum/15)+1
#         url_to_list = response.url.split("/")
#         for pageindex in range(2, maxpage+1):
#             url_to_list[-4] = str(pageindex)
#             list_to_url = "/".join(url_to_list)
#             logging.log(msg=list_to_url, level=logging.INFO)
#             yield scrapy.Request(response.urljoin(list_to_url),
#                                  meta={'citydata': response.meta['citydata'], 'branddata': response.meta['branddata']},
#                                  callback=self.parse_network,headers=self.headers)
#
#         page = re.findall(r"\d+",re.findall(r"pageIndex=\d+",response.url)[0])[0]\
#             if re.findall(r"pageIndex=\d+",response.url) else "-"
#         if page!="-":
#             pagenext=int(page)+1
#             if pagenext <= maxpage:
#                 next_pageurl = re.sub("pageIndex=\d+", "pageIndex=" + str(pagenext), response.url)
#                 #print next_pageurl
#                 yield scrapy.Request(next_pageurl,meta={'citydata': response.meta['citydata'],'branddata': response.meta['branddata']},callback=self.parse_network)
#
#         # **************************************************************************************************************************
#         #判断是否有综合经销商站点
#         kindnext = response.xpath('//div[@class="tab"]/a[@class="nav"]/@href').extract_first()
#         if kindnext:
#             if not (kindnext.find('kindId=2') == -1):
#                 url = response.urljoin(kindnext)
#                 # print url
#                 yield scrapy.Request(url,meta={'citydata': response.meta['citydata'],'branddata': response.meta['branddata']},callback=self.parse_network,headers=self.headers)
#
#     def parse_carinfo(self, response):
#         # logging.log(msg = str(response.xpath('//div[@class="brandtree-cont"]/dl/dd')) + "$$$$$$$$$$" + "parse_carinfo" + response.url, level=logging.INFO)
#         for tmp in response.xpath('//div[@class="brandtree-cont"]/dl/dd'):
#             contenturl = "http://dealer.autohome.com.cn" + tmp.xpath('a/@href').extract_first()
#             # print 'contenturl',contenturl
#             yield scrapy.Request(contenturl,
#                                  meta={'citydata': response.meta['citydata'], 'branddata': response.meta['branddata']},
#                                  callback=self.parse_netinfo,headers=self.headers)
#
#     def parse_netinfo(self, response):
#         print(response.url, "*" * 50)
#         item = AutohomeItem_price()
#         ####normal infor
#         item['grabtime'] = time.strftime('%Y-%m-%d %X', time.localtime())
#         item['website'] = website
#         ####metadata:
#         # city
#         item['Key'] = response.meta['citydata']['Key']
#         item['prov_ID'] = response.meta['citydata']['prov_ID']
#         item['prov_Name'] = response.meta['citydata']['prov_Name']
#         item['prov_Pinyin'] = response.meta['citydata']['prov_Pinyin']
#         item['prov_Count'] = response.meta['citydata']['prov_Count']
#         item['city_ID'] = response.meta['citydata']['city_ID']
#         item['city_Name'] = response.meta['citydata']['city_Name']
#         item['city_Pinyin'] = response.meta['citydata']['city_Pinyin']
#         item['city_Count'] = response.meta['citydata']['city_Count']
#         # brand
#         item['brandname'] = response.meta['branddata']['brandname']
#         item['brandid'] = response.meta['branddata']['brandid']
#         # factory
#         item['factoryname'] = response.xpath("//div[@class='carprice-title']/a/text()").extract_first()
#         # / 3848 / f_63.html
#         factoryid = response.xpath("//div[@class='carprice']//div[@class='carprice-title']/a/@href").extract_first()
#         print(factoryid, r"/\\" * 50, )
#         item['factoryid'] = re.findall(r'_(\d+)', factoryid)[1]
#         # storeinfo
#         item['shopname'] = response.xpath("//div[@class='breadnav']/p/a[2]/text()").extract_first()
#         item['shopid'] = response.xpath("//div[@class='breadnav']/p/a[2]/@href").extract_first().strip('/')
#         item['tel'] = response.xpath('//span[@class="dealer-api-phone"]/text()').extract_first()
#         item['saleregion'] = response.xpath('//span[@class="dealer-api-phone"]/../i[2]/@title').extract_first()
#         # car detail info
#         for tmp in response.xpath('//dt[@class="fn-clear"]'):
#             item['picurl'] = tmp.xpath('div[@class="pic"]/a/img/@src').extract_first()
#             item['vehilename'] = tmp.xpath('div[@class="name"]/p/a/text()').extract_first()
#             item['salespricerange'] = tmp.xpath('div[@class="name"]/p/span/text()').extract_first().strip()
#             item['guidepricerange'] = ".".join(
#                 re.findall(r'\d+-?\d+', tmp.xpath('div[@class="name"]/p/span/text()').extract()[1].strip()))
#             item['vehilenameid'] = tmp.xpath('div[@class="name"]/p/a/@href').extract_first()
#         for tmp in response.xpath('//table[@class="list-table"]/tr[contains(td/@class, "txt-left")]'):
#             item['salesdesc'] = tmp.xpath('td/a/text()').extract_first()
#             item['salesdescid'] = re.findall(r'spec_\d+', tmp.xpath('td/a/@href').extract_first())[0].replace('spec_',
#                                                                                                               '')
#             item['guideprice'] = tmp.xpath('td/p[@class="grey-999"]/text()').extract_first()
#             item['guidesalesprice'] = tmp.xpath('td/p[@class="grey-999 text-line"]/text()').extract_first()
#             item['salesprice'] = tmp.xpath('td/div/a/text()').extract_first().replace(' ', '') \
#                 if tmp.xpath('td/div/a/text()') else "-"
#             if item['salesprice'] == "-":
#                 item['salesprice'] = tmp.xpath('td/div/a[2]/text()').extract_first().replace(' ', '') \
#                     if tmp.xpath('td/div/a[2]/text()') else "-"
#
#             item['url'] = "http://dealer.autohome.com.cn" + tmp.xpath('td/a/@href').extract_first()
#             status = tmp.xpath('td/a/@href').extract_first() + time.strftime('%Y-%m', time.localtime(time.time()))
#             # item['status']=hashlib.md5(status).hexdigest()
#             item['status'] = status
#             print(item)
#             # yield item
