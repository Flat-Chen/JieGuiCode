import json
import time

import pymongo
import redis
import scrapy

type_dict = {
    '0': '品牌销量',
    '1': '车型销量',
    '2': '省份销量'
}
# 省份 城市
city_dict = {'["0"]': '全国',
             '["内蒙古:0"]': '内蒙古-内蒙古省所有城市',
             '["内蒙古:阿拉善盟"]': '内蒙古-阿拉善盟',
             '["内蒙古:包头市"]': '内蒙古-包头市',
             '["内蒙古:乌兰察布市"]': '内蒙古-乌兰察布市',
             '["内蒙古:巴彦淖尔市"]': '内蒙古-巴彦淖尔市',
             '["内蒙古:鄂尔多斯市"]': '内蒙古-鄂尔多斯市',
             '["内蒙古:呼和浩特市"]': '内蒙古-呼和浩特市',
             '["内蒙古:呼伦贝尔市"]': '内蒙古-呼伦贝尔市',
             '["内蒙古:锡林郭勒盟"]': '内蒙古-锡林郭勒盟',
             '["内蒙古:通辽市"]': '内蒙古-通辽市',
             '["内蒙古:赤峰市"]': '内蒙古-赤峰市',
             '["内蒙古:兴安盟"]': '内蒙古-兴安盟',
             '["内蒙古:乌海市"]': '内蒙古-乌海市',
             '["青海:0"]': '青海-青海省所有城市',
             '["青海:海西州"]': '青海-海西州',
             '["青海:西宁市"]': '青海-西宁市',
             '["青海:海北州"]': '青海-海北州',
             '["青海:海南州"]': '青海-海南州',
             '["青海:海东市"]': '青海-海东市',
             '["青海:玉树州"]': '青海-玉树州',
             '["青海:果洛州"]': '青海-果洛州',
             '["青海:黄南州"]': '青海-黄南州',
             '["广东:0"]': '广东-广东省所有城市',
             '["广东:珠海市"]': '广东-珠海市',
             '["广东:梅州市"]': '广东-梅州市',
             '["广东:湛江市"]': '广东-湛江市',
             '["广东:中山市"]': '广东-中山市',
             '["广东:云浮市"]': '广东-云浮市',
             '["广东:揭阳市"]': '广东-揭阳市',
             '["广东:惠州市"]': '广东-惠州市',
             '["广东:河源市"]': '广东-河源市',
             '["广东:广州市"]': '广东-广州市',
             '["广东:江门市"]': '广东-江门市',
             '["广东:佛山市"]': '广东-佛山市',
             '["广东:茂名市"]': '广东-茂名市',
             '["广东:潮州市"]': '广东-潮州市',
             '["广东:韶关市"]': '广东-韶关市',
             '["广东:汕头市"]': '广东-汕头市',
             '["广东:清远市"]': '广东-清远市',
             '["广东:汕尾市"]': '广东-汕尾市',
             '["广东:阳江市"]': '广东-阳江市',
             '["广东:东莞市"]': '广东-东莞市',
             '["广东:肇庆市"]': '广东-肇庆市',
             '["广东:深圳市"]': '广东-深圳市',
             '["辽宁:0"]': '辽宁-辽宁省所有城市',
             '["辽宁:锦州市"]': '辽宁-锦州市',
             '["辽宁:抚顺市"]': '辽宁-抚顺市',
             '["辽宁:本溪市"]': '辽宁-本溪市',
             '["辽宁:阜新市"]': '辽宁-阜新市',
             '["辽宁:葫芦岛市"]': '辽宁-葫芦岛市',
             '["辽宁:铁岭市"]': '辽宁-铁岭市',
             '["辽宁:沈阳市"]': '辽宁-沈阳市',
             '["辽宁:营口市"]': '辽宁-营口市',
             '["辽宁:盘锦市"]': '辽宁-盘锦市',
             '["辽宁:鞍山市"]': '辽宁-鞍山市',
             '["辽宁:朝阳市"]': '辽宁-朝阳市',
             '["辽宁:丹东市"]': '辽宁-丹东市',
             '["辽宁:大连市"]': '辽宁-大连市',
             '["辽宁:辽阳市"]': '辽宁-辽阳市',
             '["四川:0"]': '四川-四川省所有城市',
             '["四川:南充市"]': '四川-南充市',
             '["四川:凉山州"]': '四川-凉山州',
             '["四川:成都市"]': '四川-成都市',
             '["四川:宜宾市"]': '四川-宜宾市',
             '["四川:泸州市"]': '四川-泸州市',
             '["四川:巴中市"]': '四川-巴中市',
             '["四川:达州市"]': '四川-达州市',
             '["四川:攀枝花市"]': '四川-攀枝花市',
             '["四川:绵阳市"]': '四川-绵阳市',
             '["四川:眉山市"]': '四川-眉山市',
             '["四川:德阳市"]': '四川-德阳市',
             '["四川:乐山市"]': '四川-乐山市',
             '["四川:雅安市"]': '四川-雅安市',
             '["四川:自贡市"]': '四川-自贡市',
             '["四川:广安市"]': '四川-广安市',
             '["四川:资阳市"]': '四川-资阳市',
             '["四川:遂宁市"]': '四川-遂宁市',
             '["四川:甘孜州"]': '四川-甘孜州',
             '["四川:阿坝州"]': '四川-阿坝州',
             '["四川:广元市"]': '四川-广元市',
             '["四川:内江市"]': '四川-内江市',
             '["广西:0"]': '广西-广西省所有城市',
             '["广西:来宾市"]': '广西-来宾市',
             '["广西:钦州市"]': '广西-钦州市',
             '["广西:玉林市"]': '广西-玉林市',
             '["广西:防城港市"]': '广西-防城港市',
             '["广西:梧州市"]': '广西-梧州市',
             '["广西:桂林市"]': '广西-桂林市',
             '["广西:贺州市"]': '广西-贺州市',
             '["广西:百色市"]': '广西-百色市',
             '["广西:柳州市"]': '广西-柳州市',
             '["广西:贵港市"]': '广西-贵港市',
             '["广西:北海市"]': '广西-北海市',
             '["广西:河池市"]': '广西-河池市',
             '["广西:南宁市"]': '广西-南宁市',
             '["广西:崇左市"]': '广西-崇左市',
             '["安徽:0"]': '安徽-安徽省所有城市',
             '["安徽:六安市"]': '安徽-六安市',
             '["安徽:宿州市"]': '安徽-宿州市',
             '["安徽:淮北市"]': '安徽-淮北市',
             '["安徽:池州市"]': '安徽-池州市',
             '["安徽:亳州市"]': '安徽-亳州市',
             '["安徽:合肥市"]': '安徽-合肥市',
             '["安徽:滁州市"]': '安徽-滁州市',
             '["安徽:安庆市"]': '安徽-安庆市',
             '["安徽:宣城市"]': '安徽-宣城市',
             '["安徽:马鞍山市"]': '安徽-马鞍山市',
             '["安徽:铜陵市"]': '安徽-铜陵市',
             '["安徽:阜阳市"]': '安徽-阜阳市',
             '["安徽:黄山市"]': '安徽-黄山市',
             '["安徽:芜湖市"]': '安徽-芜湖市',
             '["安徽:淮南市"]': '安徽-淮南市',
             '["安徽:蚌埠市"]': '安徽-蚌埠市',
             '["甘肃:0"]': '甘肃-甘肃省所有城市',
             '["甘肃:酒泉市"]': '甘肃-酒泉市',
             '["甘肃:白银市"]': '甘肃-白银市',
             '["甘肃:张掖市"]': '甘肃-张掖市',
             '["甘肃:金昌市"]': '甘肃-金昌市',
             '["甘肃:临夏州"]': '甘肃-临夏州',
             '["甘肃:甘南州"]': '甘肃-甘南州',
             '["甘肃:陇南市"]': '甘肃-陇南市',
             '["甘肃:天水市"]': '甘肃-天水市',
             '["甘肃:庆阳市"]': '甘肃-庆阳市',
             '["甘肃:平凉市"]': '甘肃-平凉市',
             '["甘肃:定西市"]': '甘肃-定西市',
             '["甘肃:兰州市"]': '甘肃-兰州市',
             '["甘肃:嘉峪关市"]': '甘肃-嘉峪关市',
             '["甘肃:武威市"]': '甘肃-武威市',
             '["湖南:0"]': '湖南-湖南省所有城市',
             '["湖南:邵阳市"]': '湖南-邵阳市',
             '["湖南:郴州市"]': '湖南-郴州市',
             '["湖南:娄底市"]': '湖南-娄底市',
             '["湖南:常德市"]': '湖南-常德市',
             '["湖南:怀化市"]': '湖南-怀化市',
             '["湖南:张家界市"]': '湖南-张家界市',
             '["湖南:岳阳市"]': '湖南-岳阳市',
             '["湖南:永州市"]': '湖南-永州市',
             '["湖南:长沙市"]': '湖南-长沙市',
             '["湖南:衡阳市"]': '湖南-衡阳市',
             '["湖南:湘西州"]': '湖南-湘西州',
             '["湖南:益阳市"]': '湖南-益阳市',
             '["湖南:株洲市"]': '湖南-株洲市',
             '["湖南:湘潭市"]': '湖南-湘潭市',
             '["宁夏:0"]': '宁夏-宁夏省所有城市',
             '["宁夏:固原市"]': '宁夏-固原市',
             '["宁夏:中卫市"]': '宁夏-中卫市',
             '["宁夏:银川市"]': '宁夏-银川市',
             '["宁夏:石嘴山市"]': '宁夏-石嘴山市',
             '["宁夏:吴忠市"]': '宁夏-吴忠市',
             '["陕西:0"]': '陕西-陕西省所有城市',
             '["陕西:宝鸡市"]': '陕西-宝鸡市',
             '["陕西:渭南市"]': '陕西-渭南市',
             '["陕西:铜川市"]': '陕西-铜川市',
             '["陕西:商洛市"]': '陕西-商洛市',
             '["陕西:西安市"]': '陕西-西安市',
             '["陕西:安康市"]': '陕西-安康市',
             '["陕西:汉中市"]': '陕西-汉中市',
             '["陕西:榆林市"]': '陕西-榆林市',
             '["陕西:咸阳市"]': '陕西-咸阳市',
             '["陕西:延安市"]': '陕西-延安市',
             '["云南:0"]': '云南-云南省所有城市',
             '["云南:怒江州"]': '云南-怒江州',
             '["云南:迪庆州"]': '云南-迪庆州',
             '["云南:红河州"]': '云南-红河州',
             '["云南:文山州"]': '云南-文山州',
             '["云南:丽江市"]': '云南-丽江市',
             '["云南:西双版纳州"]': '云南-西双版纳州',
             '["云南:楚雄州"]': '云南-楚雄州',
             '["云南:大理州"]': '云南-大理州',
             '["云南:德宏州"]': '云南-德宏州',
             '["云南:昆明市"]': '云南-昆明市',
             '["云南:临沧市"]': '云南-临沧市',
             '["云南:昭通市"]': '云南-昭通市',
             '["云南:保山市"]': '云南-保山市',
             '["云南:玉溪市"]': '云南-玉溪市',
             '["云南:曲靖市"]': '云南-曲靖市',
             '["云南:普洱市"]': '云南-普洱市',
             '["黑龙江:0"]': '黑龙江-黑龙江省所有城市',
             '["黑龙江:齐齐哈尔市"]': '黑龙江-齐齐哈尔市',
             '["黑龙江:大庆市"]': '黑龙江-大庆市',
             '["黑龙江:牡丹江市"]': '黑龙江-牡丹江市',
             '["黑龙江:双鸭山市"]': '黑龙江-双鸭山市',
             '["黑龙江:鸡西市"]': '黑龙江-鸡西市',
             '["黑龙江:黑河市"]': '黑龙江-黑河市',
             '["黑龙江:伊春市"]': '黑龙江-伊春市',
             '["黑龙江:绥化市"]': '黑龙江-绥化市',
             '["黑龙江:哈尔滨市"]': '黑龙江-哈尔滨市',
             '["黑龙江:鹤岗市"]': '黑龙江-鹤岗市',
             '["黑龙江:大兴安岭地区"]': '黑龙江-大兴安岭地区',
             '["黑龙江:佳木斯市"]': '黑龙江-佳木斯市',
             '["黑龙江:七台河市"]': '黑龙江-七台河市',
             '["新疆:0"]': '新疆-新疆省所有城市',
             '["新疆:克拉玛依市"]': '新疆-克拉玛依市',
             '["新疆:阿勒泰地区"]': '新疆-阿勒泰地区',
             '["新疆:哈密地区"]': '新疆-哈密地区',
             '["新疆:和田地区"]': '新疆-和田地区',
             '["新疆:喀什地区"]': '新疆-喀什地区',
             '["新疆:伊犁州"]': '新疆-伊犁州',
             '["新疆:巴州"]': '新疆-巴州',
             '["新疆:吐鲁番地区"]': '新疆-吐鲁番地区',
             '["新疆:吐鲁番市"]': '新疆-吐鲁番市',
             '["新疆:哈密市"]': '新疆-哈密市',
             '["新疆:阿克苏地区"]': '新疆-阿克苏地区',
             '["新疆:新疆县直辖"]': '新疆-新疆县直辖',
             '["新疆:克州"]': '新疆-克州',
             '["新疆:塔城地区"]': '新疆-塔城地区',
             '["新疆:乌鲁木齐市"]': '新疆-乌鲁木齐市',
             '["新疆:昌吉州"]': '新疆-昌吉州',
             '["新疆:博州"]': '新疆-博州',
             '["贵州:0"]': '贵州-贵州省所有城市',
             '["贵州:安顺市"]': '贵州-安顺市',
             '["贵州:毕节市"]': '贵州-毕节市',
             '["贵州:铜仁市"]': '贵州-铜仁市',
             '["贵州:黔南州"]': '贵州-黔南州',
             '["贵州:六盘水市"]': '贵州-六盘水市',
             '["贵州:黔西南州"]': '贵州-黔西南州',
             '["贵州:黔东南州"]': '贵州-黔东南州',
             '["贵州:遵义市"]': '贵州-遵义市',
             '["贵州:贵阳市"]': '贵州-贵阳市',
             '["福建:0"]': '福建-福建省所有城市',
             '["福建:福州市"]': '福建-福州市',
             '["福建:厦门市"]': '福建-厦门市',
             '["福建:南平市"]': '福建-南平市',
             '["福建:三明市"]': '福建-三明市',
             '["福建:泉州市"]': '福建-泉州市',
             '["福建:宁德市"]': '福建-宁德市',
             '["福建:莆田市"]': '福建-莆田市',
             '["福建:龙岩市"]': '福建-龙岩市',
             '["福建:漳州市"]': '福建-漳州市',
             '["天津:0"]': '天津-天津省所有城市',
             '["天津:天津市"]': '天津-天津市',
             '["西藏:0"]': '西藏-西藏省所有城市',
             '["西藏:山南市"]': '西藏-山南市',
             '["西藏:山南地区"]': '西藏-山南地区',
             '["西藏:那曲市"]': '西藏-那曲市',
             '["西藏:昌都市"]': '西藏-昌都市',
             '["西藏:林芝地区"]': '西藏-林芝地区',
             '["西藏:阿里地区"]': '西藏-阿里地区',
             '["西藏:日喀则地区"]': '西藏-日喀则地区',
             '["西藏:拉萨市"]': '西藏-拉萨市',
             '["西藏:昌都地区"]': '西藏-昌都地区',
             '["西藏:日喀则市"]': '西藏-日喀则市',
             '["西藏:林芝市"]': '西藏-林芝市',
             '["西藏:那曲地区"]': '西藏-那曲地区',
             '["江西:0"]': '江西-江西省所有城市',
             '["江西:景德镇市"]': '江西-景德镇市',
             '["江西:赣州市"]': '江西-赣州市',
             '["江西:吉安市"]': '江西-吉安市',
             '["江西:宜春市"]': '江西-宜春市',
             '["江西:萍乡市"]': '江西-萍乡市',
             '["江西:新余市"]': '江西-新余市',
             '["江西:南昌市"]': '江西-南昌市',
             '["江西:上饶市"]': '江西-上饶市',
             '["江西:鹰潭市"]': '江西-鹰潭市',
             '["江西:抚州市"]': '江西-抚州市',
             '["江西:九江市"]': '江西-九江市',
             '["江苏:0"]': '江苏-江苏省所有城市',
             '["江苏:淮安市"]': '江苏-淮安市',
             '["江苏:连云港市"]': '江苏-连云港市',
             '["江苏:常州市"]': '江苏-常州市',
             '["江苏:南通市"]': '江苏-南通市',
             '["江苏:宿迁市"]': '江苏-宿迁市',
             '["江苏:泰州市"]': '江苏-泰州市',
             '["江苏:南京市"]': '江苏-南京市',
             '["江苏:盐城市"]': '江苏-盐城市',
             '["江苏:无锡市"]': '江苏-无锡市',
             '["江苏:镇江市"]': '江苏-镇江市',
             '["江苏:扬州市"]': '江苏-扬州市',
             '["江苏:苏州市"]': '江苏-苏州市',
             '["江苏:徐州市"]': '江苏-徐州市',
             '["山东:0"]': '山东-山东省所有城市',
             '["山东:威海市"]': '山东-威海市',
             '["山东:聊城市"]': '山东-聊城市',
             '["山东:潍坊市"]': '山东-潍坊市',
             '["山东:东营市"]': '山东-东营市',
             '["山东:枣庄市"]': '山东-枣庄市',
             '["山东:莱芜市"]': '山东-莱芜市',
             '["山东:济宁市"]': '山东-济宁市',
             '["山东:泰安市"]': '山东-泰安市',
             '["山东:临沂市"]': '山东-临沂市',
             '["山东:淄博市"]': '山东-淄博市',
             '["山东:滨州市"]': '山东-滨州市',
             '["山东:青岛市"]': '山东-青岛市',
             '["山东:菏泽市"]': '山东-菏泽市',
             '["山东:日照市"]': '山东-日照市',
             '["山东:烟台市"]': '山东-烟台市',
             '["山东:济南市"]': '山东-济南市',
             '["山东:德州市"]': '山东-德州市',
             '["河北:0"]': '河北-河北省所有城市',
             '["河北:衡水市"]': '河北-衡水市',
             '["河北:承德市"]': '河北-承德市',
             '["河北:邢台市"]': '河北-邢台市',
             '["河北:廊坊市"]': '河北-廊坊市',
             '["河北:唐山市"]': '河北-唐山市',
             '["河北:沧州市"]': '河北-沧州市',
             '["河北:保定市"]': '河北-保定市',
             '["河北:张家口市"]': '河北-张家口市',
             '["河北:石家庄市"]': '河北-石家庄市',
             '["河北:邯郸市"]': '河北-邯郸市',
             '["河北:秦皇岛市"]': '河北-秦皇岛市',
             '["吉林:0"]': '吉林-吉林省所有城市',
             '["吉林:四平市"]': '吉林-四平市',
             '["吉林:长春市"]': '吉林-长春市',
             '["吉林:白山市"]': '吉林-白山市',
             '["吉林:白城市"]': '吉林-白城市',
             '["吉林:延边州"]': '吉林-延边州',
             '["吉林:通化市"]': '吉林-通化市',
             '["吉林:吉林市"]': '吉林-吉林市',
             '["吉林:辽源市"]': '吉林-辽源市',
             '["吉林:松原市"]': '吉林-松原市',
             '["浙江:0"]': '浙江-浙江省所有城市',
             '["浙江:湖州市"]': '浙江-湖州市',
             '["浙江:台州市"]': '浙江-台州市',
             '["浙江:杭州市"]': '浙江-杭州市',
             '["浙江:温州市"]': '浙江-温州市',
             '["浙江:绍兴市"]': '浙江-绍兴市',
             '["浙江:丽水市"]': '浙江-丽水市',
             '["浙江:衢州市"]': '浙江-衢州市',
             '["浙江:金华市"]': '浙江-金华市',
             '["浙江:嘉兴市"]': '浙江-嘉兴市',
             '["浙江:宁波市"]': '浙江-宁波市',
             '["浙江:舟山市"]': '浙江-舟山市',
             '["河南:0"]': '河南-河南省所有城市',
             '["河南:平顶山市"]': '河南-平顶山市',
             '["河南:焦作市"]': '河南-焦作市',
             '["河南:郑州市"]': '河南-郑州市',
             '["河南:濮阳市"]': '河南-濮阳市',
             '["河南:洛阳市"]': '河南-洛阳市',
             '["河南:河南省直辖"]': '河南-河南省直辖',
             '["河南:驻马店市"]': '河南-驻马店市',
             '["河南:周口市"]': '河南-周口市',
             '["河南:三门峡市"]': '河南-三门峡市',
             '["河南:商丘市"]': '河南-商丘市',
             '["河南:漯河市"]': '河南-漯河市',
             '["河南:开封市"]': '河南-开封市',
             '["河南:新乡市"]': '河南-新乡市',
             '["河南:安阳市"]': '河南-安阳市',
             '["河南:许昌市"]': '河南-许昌市',
             '["河南:信阳市"]': '河南-信阳市',
             '["河南:南阳市"]': '河南-南阳市',
             '["河南:鹤壁市"]': '河南-鹤壁市',
             '["湖北:0"]': '湖北-湖北省所有城市',
             '["湖北:孝感市"]': '湖北-孝感市',
             '["湖北:武汉市"]': '湖北-武汉市',
             '["湖北:黄石市"]': '湖北-黄石市',
             '["湖北:荆门市"]': '湖北-荆门市',
             '["湖北:随州市"]': '湖北-随州市',
             '["湖北:鄂州市"]': '湖北-鄂州市',
             '["湖北:湖北省直辖"]': '湖北-湖北省直辖',
             '["湖北:咸宁市"]': '湖北-咸宁市',
             '["湖北:恩施州"]': '湖北-恩施州',
             '["湖北:襄阳市"]': '湖北-襄阳市',
             '["湖北:宜昌市"]': '湖北-宜昌市',
             '["湖北:黄冈市"]': '湖北-黄冈市',
             '["湖北:荆州市"]': '湖北-荆州市',
             '["湖北:十堰市"]': '湖北-十堰市',
             '["山西:0"]': '山西-山西省所有城市',
             '["山西:临汾市"]': '山西-临汾市',
             '["山西:吕梁市"]': '山西-吕梁市',
             '["山西:朔州市"]': '山西-朔州市',
             '["山西:长治市"]': '山西-长治市',
             '["山西:晋城市"]': '山西-晋城市',
             '["山西:太原市"]': '山西-太原市',
             '["山西:运城市"]': '山西-运城市',
             '["山西:晋中市"]': '山西-晋中市',
             '["山西:忻州市"]': '山西-忻州市',
             '["山西:阳泉市"]': '山西-阳泉市',
             '["山西:大同市"]': '山西-大同市',
             '["海南:0"]': '海南-海南省所有城市',
             '["海南:海口市"]': '海南-海口市',
             '["海南:三沙市"]': '海南-三沙市',
             '["海南:三亚市"]': '海南-三亚市',
             '["海南:海南省直辖"]': '海南-海南省直辖',
             '["海南:儋州市"]': '海南-儋州市',
             '["北京:0"]': '北京-北京省所有城市',
             '["北京:北京市"]': '北京-北京市',
             '["重庆:0"]': '重庆-重庆省所有城市',
             '["重庆:重庆市"]': '重庆-重庆市',
             '["上海:0"]': '上海-上海省所有城市',
             '["上海:上海市"]': '上海-上海市'
             }
date_list = [
    '2018-09',
    '2018-10',
    '2018-11',
    '2018-12',
    '2019-01',
    '2019-02',
    '2019-03',
    '2019-04',
    '2019-05',
    '2019-06',
    '2019-07',
    '2019-08',
    '2019-09',
    '2019-10',
    '2019-11',
    '2019-12',
    '2020-01',
    '2020-02',
    '2020-03',
    '2020-04',
    '2020-05',
    '2020-06',
    '2020-07',
    '2020-08',
    '2020-09',
    '2020-10',
    '2020-11',
    '2020-12',
    '2021-01',
    '2021-02',
    '2021-03',
    '2021-04',
    '2021-05',
    '2021-06',
    '2021-07',
    '2021-08'
]
model_dict = {
    '["0"]': '全部车型',
    '["轿车:0"]': '轿车-全部轿车',
    '["轿车:微型车"]': '轿车-微型轿车',
    '["轿车:小型车"]': '轿车-小型轿车',
    '["轿车:紧凑型车"]': '轿车-紧凑型轿车',
    '["轿车:中型车"]': '轿车-中型轿车',
    '["轿车:中大型车"]': '轿车-中大型轿车',
    '["SUV:0"]': 'SUV-全部SUV',
    '["SUV:小型SUV"]': 'SUV-小型SUV',
    '["SUV:紧凑型SUV"]': 'SUV-紧凑型SUV',
    '["SUV:中型SUV"]': 'SUV-中型SUV',
    '["SUV:中大型SUV"]': 'SUV-中大型SUV',
    '["SUV:全尺寸SUV"]': 'SUV-全尺寸SUV',
    '["新能源:0"]': '新能源-全部新能源',
    '["新能源:纯电动"]': '新能源-纯电动',
    '["新能源:插电混动"]': '新能源-插电混动',
    '["MPV:0"]': 'MPV-全部MPV',
    '["MPV:小型MPV"]': 'MPV-小型MPV',
    '["MPV:紧凑型MPV"]': 'MPV-紧凑型MPV',
    '["MPV:中型MPV"]': 'MPV-中型MPV',
    '["MPV:大型MPV"]': 'MPV-大型MPV',
}


class YichezhiSpider(scrapy.Spider):
    name = 'yichezhi'
    allowed_domains = ['yichehuoban.cn']

    # start_urls = ['http://yichehuoban.cn/']

    @classmethod
    def update_settings(cls, settings):
        settings.setdict(
            getattr(cls, 'custom_debug_settings' if getattr(cls, 'is_debug', False) else 'custom_settings', None) or {},
            priority='spider')

    is_debug = True
    custom_debug_settings = {
        'MYSQL_SERVER': '192.168.1.94',
        'MYSQL_USER': "dataUser94",
        'MYSQL_PWD': "94dataUser@2020",
        'MYSQL_PORT': 3306,
        'MYSQL_DB': 'yiche',
        'MYSQL_TABLE': 'yichezhi',
        'MONGODB_SERVER': '192.168.2.149',
        'MONGODB_PORT': 27017,
        'MONGODB_DB': 'yiche',
        'MONGODB_COLLECTION': 'yichezhi_rank',
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0,
        'LOG_LEVEL': 'DEBUG',
        'RETRY_HTTP_CODES': [400, 403, 404, 408],
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
    }

    def start_requests(self):
        url = 'http://bb.yichehuoban.cn/ycgt/report/yiCheZhi/getYiCheZhiTableData'
        redis_url = 'redis://192.168.2.149:6379/6'
        r = redis.Redis.from_url(redis_url, decode_responses=True)
        while 1:
            post_data_json = r.blpop('yichezhi:post_data')
            post_data_dict = json.loads(post_data_json[1])

            date = post_data_dict['date']
            area = str(post_data_dict['area']).replace("'", '"')
            try:
                carLevel = str(post_data_dict['carLevel']).replace("'", '"')
            except:
                carLevel = None
            type_code = str(post_data_dict['type'])

            data = {
                "date": date,
                "area": eval(area),
                "carLevel": eval(carLevel),
                "type": eval(type_code)
            }
            meta = {
                'page_type': type_dict[type_code],
                'city': city_dict[area],
                'date': date,
                'model_type': model_dict[carLevel],
                'post_data': data
            }

            yield scrapy.Request(url=url, method='POST', body=json.dumps(data), meta=meta,
                                 dont_filter=True, headers={'Content-Type': 'application/json'})

    def parse(self, response):
        page_type = response.meta['page_type']
        city = response.meta['city']
        date = response.meta['date']
        try:
            model_type = response.meta['model_type']
        except:
            model_type = None
        post_data = response.meta['post_data']
        item = {}
        item['page_type'] = page_type
        item['city'] = city
        item['date'] = date
        item['model_type'] = model_type
        item['post_data'] = post_data
        item['content'] = response.text
        item['grab_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        yield item
