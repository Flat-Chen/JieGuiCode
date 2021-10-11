# import http.client
# import mimetypes
# conn = http.client.HTTPSConnection("youche.shiqiaokache.com")
# #     配置信息
# payload = 'styleId=180322433032045&purpose=22&timestamp=1583480685895&sign=4ee17f7f94500d7c95fcfc36d562634a'
# headers = {
#   'token': 'eyJlbiI6IlhXektoRmUybzJRREFQOVhrWFBTWDYwVCIsInRva2VuIjoiZGFlYTJiMWFlNjY5NGI5Njg2NTkyNmU4YWExMjVmNDMifQ==',
#   'osname': 'Android',
#   'version': '1.8.0',
#   'usrName': '18220345933',
#   'Host': 'youche.shiqiaokache.com',
#   'User-Agent': 'okhttp/3.12.1'
# }
# conn.request("POST", "/app/vehStyle/getDetailParameter.do", payload, headers)
# res = conn.getresponse()
# data = res.read()
# print(data.decode("utf-8"))


# 估价
# import http.client
# import mimetypes
# conn = http.client.HTTPSConnection("youche.shiqiaokache.com")
# payload = 'styleId=180322433032045&modelName=%u5317%u5954V3&userId=200303165711762&provinceId=100081864&styleName=336%u9A6C%u529B%206%D74%20%u6F4D%u67F4%20%u91C7%u57C3%u5B5A%20%u67F4%u6CB9%20%u56FD%u56DB%2012m%B3&makeName=%u5317%u5954%u91CD%u5361&mileage=1&makeId=180322537000004&purposeId=22&purchaseDate=2019-03&carLevel=3&cityId=100248807&modelId=180322434000009&timestamp=1583480201648&sign=d0f0993dd86e05ccf54dc84ec15a6f2d'
# headers = {
#   'token': 'eyJlbiI6IlhXektoRmUybzJRREFQOVhrWFBTWDYwVCIsInRva2VuIjoiZGFlYTJiMWFlNjY5NGI5Njg2NTkyNmU4YWExMjVmNDMifQ==',
#   'osname': 'Android',
#   'version': '1.8.0',
#   'usrName': '18220345933',
#   'Host': 'youche.shiqiaokache.com',
#   'User-Agent': 'okhttp/3.12.1'
# }
# conn.request("POST", "/app/estresult/getByEstResult.do", payload, headers)
# res = conn.getresponse()
# data = res.read()
# print(data.decode("utf-8"))


# 预测
# import http.client
# import mimetypes
# conn = http.client.HTTPSConnection("youche.shiqiaokache.com")
# payload = 'id=200306921046767&timestamp=1583480202646&sign=94436432a07ec8cf7c6db3bdd9bfd41a'
# headers = {
#   'token': 'eyJlbiI6IlhXektoRmUybzJRREFQOVhrWFBTWDYwVCIsInRva2VuIjoiZGFlYTJiMWFlNjY5NGI5Njg2NTkyNmU4YWExMjVmNDMifQ==',
#   'osname': 'Android',
#   'version': '1.8.0',
#   'usrName': '18220345933',
#   'Host': 'youche.shiqiaokache.com',
#   'User-Agent': 'okhttp/3.12.1'
# }
# conn.request("POST", "/app/estresult/shareEstCarInfo.do", payload, headers)
# res = conn.getresponse()
# data = res.read()
# print(data.decode("utf-8"))
#- * -coding: utf - 8 - * -

