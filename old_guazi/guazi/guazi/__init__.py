# # # 修改这部分代码完成需求
# # # import requests
# # # from lxml import etree
# # # from lxml import etree
# # # def get_climate():
# # #     url = 'http://weather.sina.com.cn/'
# # #     headers ={
# # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
# # #     }
# # #     text =requests.get(url=url,headers=headers).text
# # #     # 把数据转换为xml格式
# # #     html =etree.HTML(text)
# # #     # 解析 最低温度
# # #     temp_low_list =html.xpath("//div[@class='blk6_c0_1']/@data-nightmthtemp")[0].split(",")
# # #     # 解析 最高温度
# # #     temp_high_list =html.xpath("//div[@class='blk6_c0_1']/@data-daymthtemp")[0].split(",")
# # #     # 解析 降雨量
# # #     precipitaion =html.xpath("//span[contains(@class,'blk6_i_w')]//span[@class='blk6_i_res']/text()")
# # #     city_weather_list =[]
# # #     for i in range(12):
# # #         item= {'month': i+1,
# # #          'precipitaion': precipitaion[i].strip("mm"),
# # #          'temp_low': temp_low_list[i],
# # #          'temp_high': temp_high_list[i]
# # #          }
# # #         city_weather_list.append(item)
# # #     return city_weather_list
# # # print(get_climate())
# # import re
# #
# # a ='go_to_next_page'
# # def hump2underline(hunp_str):
# #     '''驼峰形式字符串转化为下划线形式'''
# #     #匹配正则
# #     p = re.compile(r'([a-z]|\d)([A-Z])')
# #     sub = re.sub(p,r'\1_\2', hunp_str).upper()#添加下划线，并将其变成小写字母
# #     return sub
# # print(hump2underline(a))
# # def underline2hump(underline_str):
# #     '''下划线转小驼峰'''
# #     sub = re.sub(r'(_\w)', lambda x:x.group(1)[1].upper(), underline_str)#对返回的分组进行遍历，取字母的值，将其大写
# #     return sub
# #
# # print(underline2hump("go_to_next_page"))
import time

import requests
from hashlib import md5

# def deal_price( id):
#     headers = {
#         "terminal-type": "mobile",
#         "os-name": "android",
#         "app-name": "autostreets",
#     }
#     avSid = id
#     a = int(time.time() * 1000)
#     sign = "apiKey=865e437f-c1eb-4a84-a9bb-26b134a1fcd0,avSid={},t={}".format(avSid, a)
#     redis_md5 = md5(sign.encode("utf-8")).hexdigest()
#     url = "https://app.autostreets.com/online/loadCurrentPrice?apiSign={}&t={}&avSid={}".format(redis_md5, a, avSid)
#     text = requests.get(url=url, headers=headers, ).json()
#     return text
# print(deal_price(710775))