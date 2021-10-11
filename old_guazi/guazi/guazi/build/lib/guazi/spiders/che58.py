# -*- coding: UTF-8 -*-
import base64
import datetime
import json
import re

import requests
import scrapy
from scrapy.conf import settings
from ..items import GuaziItem
import time
import logging
from ..redis_bloom import BloomFilter

website = 'che58'


# original
class CarSpider(scrapy.Spider):
    # basesetting
    name = website
    allowed_domains = ["58.com"]
    start_urls = [
        "https://m.58.com/city.html?"
    ]
    base_url = "https://m.58.com/{}/ershouche/?page={}"
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        "REDIRECT_ENABLED": True
    }
    kanche_url = "https://{}.58.com/ershouche/"
    city_dict = {'全国': 'quanguo', '安达': 'shanda', '阿拉尔': 'ale', '安宁': 'anningshi', '安溪': 'anxixian', '安陆': 'anlu',
                 '安丘': 'anqiu',
                 '鞍山': 'as', '阿勒泰': 'alt', '安阳': 'ay', '安庆': 'anqing', '安康': 'ankang', '阿克苏': 'aks', '阿坝': 'ab',
                 '阿里': 'al', '阿拉善盟': 'alsm', '安顺': 'anshun', '安吉': 'anji', '安岳': 'anyuexian', '白银': 'by', '北京': 'bj',
                 '博罗': 'boluo', '北票': 'beipiao', '北流': 'beiliushi', '博兴': 'boxing', '霸州': 'bazhou', '博白': 'bobaixian',
                 '保定': 'bd', '包头': 'bt', '滨州': 'bz', '宝鸡': 'baoji', '保亭': 'baoting', '白沙': 'baish', '蚌埠': 'bengbu',
                 '本溪': 'benxi', '白城': 'bc', '亳州': 'bozhou', '保山': 'bs', '巴音郭楞': 'bygl', '巴中': 'bazhong', '博尔塔拉': 'betl',
                 '巴彦淖尔市': 'bycem', '白山': 'baishan', '毕节': 'bijie', '百色': 'baise', '北海': 'bh', '宝应县': 'baoyingx',
                 '慈溪': 'cixi', '沧县': 'cangxian', '楚雄': 'cx', '慈利': 'cilixian', '茌平': 'chiping', '常宁': 'changningshi',
                 '赤壁': 'chibishi', '岑溪': 'cenxi', '成都': 'cd', '昌乐': 'changle', '昌邑': 'changyishi', '磁县': 'cixian',
                 '常州': 'cz', '沧州': 'cangzhou', '昌吉': 'changji', '澄迈': 'cm', '赤峰': 'chifeng', '常德': 'changde',
                 '郴州': 'chenzhou', '承德': 'chengde', '昌都': 'changdu', '朝阳': 'cy', '巢湖': 'ch', '池州': 'chizhou',
                 '滁州': 'chuzhou', '潮州': 'chaozhou', '崇左': 'chongzuo', '苍南': 'cangnanxian', '曹县': 'caoxian',
                 '定边': 'dingbian', '东台': 'dongtai', '丹阳': 'danyang', '德清': 'deqing', '东海': 'donghai', '德阳': 'deyang',
                 '大理': 'dali', '东至': 'dongzhi', '敦煌': 'dunhuang', '东阳': 'dongyang', '大竹': 'dazu', '东平': 'dongping',
                 '灯塔': 'dengta', '大悟': 'dawu', '邓州': 'dengzhou', '东明': 'dongming', '东莞': 'dg', '大连': 'dl', '德州': 'dz',
                 '当阳': 'dangyang', '东营': 'dy', '大庆': 'dq', '定州': 'dingzhou', '大兴安岭': 'dxal', '东方': 'df', '定安': 'da',
                 '儋州': 'danzhou', '丹东': 'dandong', '大同': 'dt', '迪庆': 'diqing', '德宏': 'dh', '达州': 'dazhou', '定西': 'dx',
                 '大丰': 'dafeng', '单县': 'shanxian', '恩施': 'es', '鄂州': 'ez', '鄂尔多斯': 'erds', '府谷': 'fugu', '阜阳': 'fy',
                 '丰城': 'fengchengshi', '福安': 'fuanshi', '浮梁': 'fuliangxian', '福鼎': 'fudingshi', '扶余': 'fuyuxian',
                 '分宜': 'fenyi', '范县': 'fanxian', '阜宁': 'funingxian', '凤城': 'fengcheng', '福州': 'fz', '佛山': 'fs',
                 '抚顺': 'fushun', '阜新': 'fx', '抚州': 'fuzhou', '防城港': 'fcg', '肥城': 'feicheng', '广州': 'gz',
                 '赣州': 'ganzhou', '广安': 'ga', '固原': 'guyuan', '广水': 'guangshuishi', '谷城': 'gucheng', '高平': 'gaoping',
                 '格尔木': 'geermushi', '高安': 'gaoan', '桂平': 'guipingqu', '桂阳': 'czguiyang', '固始': 'gushixian',
                 '冠县': 'guanxian', '高唐': 'gaotang', '固安': 'lfguan', '改则': 'gaizexian', '贵阳': 'gy', '桂林': 'gl',
                 '馆陶': 'gt', '贵港': 'gg', '广元': 'guangyuan', '甘孜': 'ganzi', '果洛': 'guoluo', '甘南': 'gn', '广饶': 'guangrao',
                 '公主岭': 'gongzhuling', '广汉': 'guanghanshi', '灌云': 'guanyun', '灌南': 'guannan', '高密': 'gaomi',
                 '海门': 'haimen', '海安': 'haian', '海宁': 'haining', '惠东': 'huidong', '华容': 'huarong', '黄冈': 'hg',
                 '淮南': 'hn', '黄山': 'huangshan', '河池': 'hc', '鹤壁': 'hb', '红河': 'honghe', '海北': 'haibei', '滑县': 'huaxian',
                 '韩城': 'hancheng', '河间': 'hejian', '杭州': 'hz', '黄骅': 'huanghua', '桦甸': 'huadian', '衡东': 'hengdong',
                 '海盐': 'haiyan', '淮滨': 'huaibinxian', '哈尔滨': 'hrb', '海口': 'haikou', '合肥': 'hf', '呼和浩特': 'hu',
                 '惠州': 'huizhou', '衡阳': 'hy', '邯郸': 'hd', '湖州': 'huzhou', '衡水': 'hs', '鹤岗': 'hegang', '黑河': 'heihe',
                 '哈密': 'hami', '汉中': 'hanzhong', '淮安': 'ha', '黄石': 'hshi', '海拉尔': 'hlr', '菏泽': 'heze', '怀化': 'hh',
                 '淮北': 'huaibei', '和田': 'ht', '黄南': 'huangnan', '海西': 'hx', '海东': 'haidong', '呼伦贝尔': 'hlbe',
                 '葫芦岛': 'hld', '河源': 'heyuan', '贺州': 'hezhou', '海南': 'hainan', '和县': 'hexian', '霍邱': 'hq',
                 '汉川': 'hanchuan', '海丰': 'haifengxian', '桓台': 'huantaixian', '靖边': 'jingbian', '金昌': 'jinchang',
                 '晋江': 'jinjiangshi', '建湖': 'jianhu', '靖江': 'jingjiang', '荆门': 'jingmen', '锦州': 'jinzhou', '景德镇': 'jdz',
                 '吉安': 'ja', '嘉善': 'jiashanx', '京山': 'jingshanxian', '鄄城': 'juancheng', '江山': 'jiangshanshi',
                 '嘉鱼': 'jiayuxian', '浚县': 'junxian', '进贤': 'jinxian', '句容': 'jurong', '巨野': 'juye', '金湖': 'jinhu',
                 '江阴': 'jiangyins', '济南': 'jn', '济宁': 'jining', '嘉兴': 'jx', '江门': 'jm', '金华': 'jh', '吉林': 'jl',
                 '揭阳': 'jy', '晋中': 'jz', '济源': 'jiyuan', '九江': 'jj', '焦作': 'jiaozuo', '晋城': 'jincheng',
                 '荆州': 'jingzhou', '佳木斯': 'jms', '鸡西': 'jixi', '嘉峪关': 'jyg', '酒泉': 'jq', '金坛': 'jintan',
                 '姜堰': 'jiangyan', '简阳': 'jianyangshi', '莒县': 'juxian', '开原': 'kaiyuan', '开封': 'kaifeng',
                 '开平': 'kaipingshi', '昆明': 'km', '克拉玛依': 'klmy', '喀什': 'ks', '克孜勒苏': 'kzls', '垦利': 'kl',
                 '昆山': 'szkunshan', '溧阳': 'liyang', '莱芜': 'lw', '六安': 'la', '泸州': 'luzhou', '丽江': 'lj', '龙口': 'longkou',
                 '乐陵': 'leling', '冷水江': 'lengshuijiangshi', '陆丰': 'lufengshi', '涟源': 'lianyuanshi', '临清': 'linqing',
                 '澧县': 'lixian', '柳林': 'liulin', '梨树县': 'lishu', '利津': 'lijin', '滦南': 'luannanxian', '梁山': 'liangshanx',
                 '临邑': 'linyixianq', '老河口': 'laohekou', '鹿邑': 'luyi', '林州': 'linzhou', '兰考': 'lankaoxian',
                 '莱阳': 'laiyang', '临朐': 'linqu', '兰州': 'lz', '洛阳': 'luoyang', '廊坊': 'lf', '临沂': 'linyi', '聊城': 'lc',
                 '连云港': 'lyg', '丽水': 'lishui', '临猗': 'linyixian', '娄底': 'ld', '乐清': 'yueqingcity', '陵水': 'lingshui',
                 '六盘水': 'lps', '吕梁': 'lvliang', '乐山': 'ls', '辽阳': 'liaoyang', '辽源': 'liaoyuan', '拉萨': 'lasa',
                 '临汾': 'linfen', '龙岩': 'ly', '临夏': 'linxia', '柳州': 'liuzhou', '漯河': 'luohe', '临沧': 'lincang',
                 '凉山': 'liangshan', '林芝': 'linzhi', '陇南': 'ln', '来宾': 'lb', '莱州': 'laizhou', '临海': 'linhai',
                 '灵宝': 'lingbaoshi', '乐平': 'lepingshi', '龙海': 'longhai', '醴陵': 'liling', '孟津': 'mengjinqu',
                 '梅河口': 'meihekou', '渑池': 'yingchixian', '孟州': 'mengzhou', '弥勒': 'milexian', '绵阳': 'mianyang',
                 '茂名': 'mm', '明港': 'mg', '马鞍山': 'mas', '牡丹江': 'mdj', '梅州': 'mz', '眉山': 'ms', '南安': 'nananshi',
                 '南漳': 'nanzhang', '南充': 'nanchong', '宁国': 'ningguo', '南城': 'nanchengx', '南县': 'nanxian',
                 '宁津': 'ningjin', '宁阳': 'ningyang', '南京': 'nj', '南昌': 'nc', '宁波': 'nb', '南宁': 'nn', '南阳': 'ny',
                 '南通': 'nt', '宁德': 'nd', '内江': 'scnj', '怒江': 'nujiang', '那曲': 'nq', '南平': 'np', '沛县': 'xzpeixian',
                 '邳州': 'pizhou', '攀枝花': 'panzhihua', '平湖': 'pinghushi', '磐石': 'panshi', '平阳': 'pingyangxian',
                 '平邑': 'pingyi', '平顶山': 'pds', '盘锦': 'pj', '萍乡': 'px', '平凉': 'pl', '濮阳': 'puyang', '莆田': 'pt',
                 '普洱': 'pe', '蓬莱': 'penglai', '启东': 'qidong', '钦州': 'qinzhou', '曲靖': 'qj', '祁阳': 'qiyang',
                 '祁东': 'qidongxian', '迁西': 'qianxixian', '淇县': 'qixianq', '渠县': 'qux', '齐河': 'qihe', '沁阳': 'qinyang',
                 '清镇': 'qingzhen', '栖霞': 'qixia', '青岛': 'qd', '泉州': 'qz', '秦皇岛': 'qhd', '七台河': 'qth', '琼海': 'qh',
                 '黔西南': 'qxn', '黔南': 'qn', '齐齐哈尔': 'qqhr', '衢州': 'quzhou', '清远': 'qingyuan', '黔东南': 'qdn',
                 '琼中': 'qiongzhong', '庆阳': 'qingyang', '清徐': 'qingxu', '潜江': 'qianjiang', '迁安市': 'qianan',
                 '青州': 'qingzhou', '杞县': 'qixianqu', '如皋': 'rugao', '如东': 'rudong', '日土': 'rituxian', '日照': 'rizhao',
                 '瑞安': 'ruiancity', '日喀则': 'rkz', '荣成': 'rongcheng', '汝州': 'ruzhou', '仁寿': 'renshouxian',
                 '任丘': 'renqiu', '乳山': 'rushan', '仁怀': 'renhuaishi', '上海': 'sh', '深圳': 'sz', '石狮': 'shishi',
                 '寿光': 'shouguang', '松原': 'songyuan', '三亚': 'sanya', '沙洋': 'shayangxian', '随县': 'suixia',
                 '商水': 'shangshui', '上杭': 'shanghangxian', '邵东': 'shaodongxian', '双峰': 'shuangfengxian',
                 '射洪': 'shehongxian', '沙河': 'shaheshi', '邵阳县': 'shaoyangxian', '松滋': 'songzi', '射阳': 'sheyang',
                 '嵊州': 'shengzhou', '沈丘': 'shenqiu', '睢县': 'suixian', '涉县': 'shexian', '苏州': 'su', '沈阳': 'sy',
                 '厦门': 'xm', '石家庄': 'sjz', '汕头': 'st', '宿州': 'suzhou', '绍兴': 'sx', '十堰': 'shiyan', '顺德': 'sd',
                 '三门峡': 'smx', '双鸭山': 'sys', '三沙': 'sansha', '三明': 'sm', '韶关': 'sg', '商丘': 'sq', '沭阳': 'shuyang',
                 '宿迁': 'suqian', '绥化': 'suihua', '邵阳': 'shaoyang', '汕尾': 'sw', '商洛': 'sl', '朔州': 'shuozhou',
                 '石河子': 'shz', '石嘴山': 'szs', '山南': 'sn', '遂宁': 'suining', '上饶': 'sr', '四平': 'sp', '随州': 'suizhou',
                 '神农架': 'snj', '神木': 'shenmu', '泗阳': 'siyang', '泗洪': 'sihong', '三河': 'sanhe', '天长': 'tianchang',
                 '桐乡': 'tongxiang', '泰兴': 'taixing', '天水': 'tianshui', '郯城': 'tancheng', '太康': 'taikang',
                 '通许': 'tongxuxian', '天津': 'tj', '太原': 'ty', '唐山': 'ts', '塔城': 'tac', '泰安': 'ta', '台州': 'tz',
                 '屯昌': 'tunchang', '铜仁': 'tr', '泰州': 'taizhou', '铁岭': 'tl', '吐鲁番': 'tlf', '铜川': 'tc', '图木舒克': 'tmsk',
                 '通辽': 'tongliao', '通化': 'th', '铜陵': 'tongling', '天门': 'tm', '台山': 'taishan', '桐城': 'tongcheng',
                 '滕州': 'tengzhou', '武穴': 'wuxueshi', '温岭': 'wenling', '文山': 'ws', '乌海': 'wuhai', '无为': 'wuweixian',
                 '无棣': 'wudi', '舞钢': 'wugang', '尉氏': 'weishixian', '武汉': 'wh', '汶上': 'wenshang', '温县': 'wenxian',
                 '武义县': 'wuyix', '微山': 'weishan', '无锡': 'wx', '潍坊': 'wf', '乌鲁木齐': 'xj', '温州': 'wz', '威海': 'weihai',
                 '五指山': 'wzs', '文昌': 'wenchang', '万宁': 'wanning', '芜湖': 'wuhu', '梧州': 'wuzhou', '瓦房店': 'wfd',
                 '渭南': 'wn', '五家渠': 'wjq', '吴忠': 'wuzhong', '乌兰察布': 'wlcb', '武威': 'wuwei', '武夷山': 'wuyishan',
                 '武安': 'wuan', '象山': 'xiangshanxian', '新沂': 'xinyishi', '兴化': 'xinghuashi', '西双版纳': 'bn',
                 '孝义': 'xiaoyi', '宣威': 'xuanwushi', '孝昌': 'xiaochang', '襄垣': 'xiangyuanxian', '新安': 'lyxinan',
                 '宣汉': 'xuanhan', '湘阴': 'xiangyin', '西安': 'xa', '莘县': 'shenxian', '盱眙': 'xuyi', '香河': 'xianghe',
                 '新昌': 'xinchang', '新野': 'xinye', '响水': 'xiangshui', '徐州': 'xz', '湘潭': 'xiangtan', '襄阳': 'xf',
                 '新乡': 'xx', '信阳': 'xy', '仙桃': 'xiantao', '咸阳': 'xianyang', '邢台': 'xt', '孝感': 'xiaogan', '西宁': 'xn',
                 '许昌': 'xc', '忻州': 'xinzhou', '宣城': 'xuancheng', '兴安盟': 'xam', '新余': 'xinyu', '湘西': 'xiangxi',
                 '咸宁': 'xianning', '锡林郭勒': 'xl', '新泰': 'xintai', '雄安新区': 'xionganxinqu', '项城': 'xiangchengshi',
                 '玉田': 'yutianxian', '扬中': 'yangzhong', '宜都': 'yidou', '阳江': 'yj', '永州': 'yongzhou', '玉林': 'yulin',
                 '攸县': 'zzyouxian', '沅江': 'yuanjiangs', '禹城': 'yuchengshi', '禹州': 'yuzhou', '永城': 'yongcheng',
                 '永安': 'yongan', '余江': 'yujiang', '郓城': 'hzyc', '云梦': 'yunmeng', '宜城': 'yichengshi', '永兴': 'yongxing',
                 '宜阳': 'lyyiyang', '阳谷': 'yanggu', '沂南': 'yinanxian', '沂源': 'yiyuanxian', '伊川': 'yichuan',
                 '永春': 'yongchunxian', '烟台': 'yt', '余姚': 'yuyao', '扬州': 'yz', '宜昌': 'yc', '盐城': 'yancheng', '岳阳': 'yy',
                 '阳春': 'yangchun', '阳泉': 'yq', '延安': 'yanan', '鄢陵': 'yanling', '伊春': 'yich', '银川': 'yinchuan',
                 '延边': 'yanbian', '鹰潭': 'yingtan', '玉溪': 'yx', '运城': 'yuncheng', '宜春': 'yichun', '营口': 'yk', '榆林': 'yl',
                 '宜宾': 'yb', '雅安': 'ya', '玉树': 'ys', '伊犁': 'yili', '益阳': 'yiyang', '云浮': 'yf', '永新': 'yxx',
                 '义乌': 'yiwu', '燕郊': 'lfyanjiao', '永康': 'yongkang', '玉环': 'yuhuan', '偃师': 'yanshiqu',
                 '肇东': 'shzhaodong', '诸暨': 'zhuji', '长兴': 'changxing', '遵化市': 'zunhua', '肇州': 'zhaozhou',
                 '长岭': 'changlingxian', '资兴': 'zixing', '钟祥': 'zhongxiangshi', '樟树': 'zhangshu', '长宁': 'changningx',
                 '漳浦': 'zhangpu', '泽州': 'zezhou', '长沙': 'cs', '重庆': 'cq', '长春': 'cc', '郑州': 'zz', '珠海': 'zh',
                 '张家口': 'zjk', '中山': 'zs', '淄博': 'zb', '株洲': 'zhuzhou', '枝江': 'zhijiang', '漳州': 'zhangzhou',
                 '湛江': 'zhanjiang', '肇庆': 'zq', '枣庄': 'zaozhuang', '舟山': 'zhoushan', '章丘': 'zhangqiu', '赵县': 'zx',
                 '诸城': 'zc', '遵义': 'zunyi', '镇江': 'zj', '周口': 'zk', '正定': 'zd', '驻马店': 'zmd', '中国香港': 'hk',
                 '中国台湾': 'tw', '庄河': 'pld', '自贡': 'zg', '张家界': 'zjj', '资阳': 'zy', '长治': 'changzhi', '长葛': 'changge',
                 '中国澳门': 'am', '昭通': 'zt', '中卫': 'zw', '张掖': 'zhangye', '张北': 'zhangbei', '邹平': 'zouping',
                 '邹城': 'zoucheng', '涿州': 'zhuozhou', '招远': 'zhaoyuan', '枣阳': 'zaoyang', '长垣': 'changyuan'}

    def __init__(self, **kwargs):
        # args
        super(CarSpider, self).__init__(**kwargs)
        settings.set('WEBSITE', website, priority='cmdline')
        self.bf = BloomFilter(key='b1f_' + website)
        # setting
        self.counts = 0
        self.headers = {

            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36",
            "Referer": "https://m.58.com/city.html"
        }
        self.headers1 = {

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            "Referer": "https://shanda.58.com"

        }

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], headers=self.headers)

    def parse(self, response):
        city_list = response.xpath("//ul[@class='city_lst']/li")
        dict = {}
        for i in city_list:
            city = i.xpath("./a/text()").extract_first()
            city_url = "https:" + i.xpath("./a/@href").extract_first().split("https:")[0] + 'ershouche'
            city_base = "https://{}.58.com/ershouche/".format(re.findall(r"m.58.com/(.*)/ershouche", city_url)[0])
            dict.update({city: re.findall(r"m.58.com/(.*)/ershouche", city_url)[0]})
            # meta = {"city": city, "city_base": city_base, "page": 1},
            # print(meta)
            yield scrapy.Request(url=city_url, headers=self.headers,
                                 meta={"city": city, "city_base": city_base, "page": 1},
                                 callback=self.car_list_parse, dont_filter=True)
        # print(dict)

    def car_list_parse(self, response):
        # print(response.meta)
        index = response.xpath("//ul[@class='infos sborder']/li/a/@href").extract()
        if index == []:
            return
        response.meta["page"] = response.meta["page"] + 1
        car_list = re.findall(r'"allInfoList":(.*),"currCount"', response.text)[0]
        car_list = eval(car_list.replace('true', 'True').replace("false", 'False'))
        for i in car_list:
            try:
                kanche = i['infoMap']['displocal']['localName']
            except:
                kanche = '全国'
            url = i['infoMap']['url']
            response.meta.update({"kanche": kanche})
            yield scrapy.Request(url=url, headers=self.headers, callback=self.car_parse, meta=response.meta,
                                 dont_filter=True)
        url = self.base_url.format(self.city_dict[response.meta["city"]], response.meta["page"])

        yield scrapy.Request(url=url, headers=self.headers, callback=self.car_list_parse, meta=response.meta)

    #     https://bj.58.com/ershouche/39627873788055x.shtml?
    def car_parse(self, response):
        url = response.url
        print(response.url, "-" * 50)
        id = re.findall(r"/(\d+)x.shtml", url)[0]
        response.meta.update({"id": id})
        #  kanche_url = "https://{}.58.com/ershouche/"
        car_list = []
        car_url = self.kanche_url.format(self.city_dict[response.meta["kanche"]]) + "{}x.shtml".format(id)
        car_list.append(car_url)
        for url in car_list:
            response.meta.update({"url": url})
            yield scrapy.Request(url=url, headers=self.headers1, meta=response.meta, callback=self.detail_parse,
                                 dont_filter=True)

    # def get_car_msg(self, id):
    #     url = "https://cheapi.58.com/api/getCarPCSpecDetailConf/{}".format(id)
    #     car_list = requests.get(url=url, headers=self.headers1, timeout=15).json()["result"]
    #     car_msg_dict = {}
    #     print(url, "*" * 77)
    #     print(car_list)
    #     for i in car_list:
    #         car_msg_dict.update({i["lable"]: i["value"]})
    #     return car_msg_dict

    def deal_font(self):
        import re

        from fontTools.ttLib import TTFont
        # window
        # font = TTFont('../che58.ttf')  # 打开本地的ttf文件
        # linux
        font = TTFont('/home/home/che58_font/che58.ttf')
        bestcmap = font['cmap'].getBestCmap()
        newmap = dict()
        for key in bestcmap.keys():
            # print(bestcmap[key])
            # print(hex(key))
            value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1
            key = hex(key).replace(r'0x', r'\u').encode('utf-8').decode('unicode_escape')
            newmap[key] = str(value)
        return newmap

    def detail_parse(self, response):
        if '访问过于频' in response.text:
            yield scrapy.Request(url=response.meta['url'], headers=self.headers1, meta=response.meta, dont_filter=True)
            return
        if '你要找的页面不在这个' in response.text:
            return
        grap_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        item = GuaziItem()
        item["carid"] = response.meta["id"]
        item["car_source"] = "che58"
        item["usage"] = None
        item["grab_time"] = grap_time
        item["update_time"] = None
        try:
            item["post_time"] = response.xpath('//div[@class="info-service-youxuan_desc"]/text()').get().split('：')[1]
        except:
            item["post_time"] = response.xpath("//span[@class='info-post-date']/text()").extract_first()
        item["sold_date"] = None
        item["pagetime"] = None
        item["parsetime"] = grap_time
        item["shortdesc"] = response.xpath("//h1[@class='info-title']/text()").extract_first()
        item["pagetitle"] = response.xpath("//title/text()").extract_first().strip("")
        item["url"] = response.url
        try:
            item["newcarid"] = re.findall(r' "chexingValue": "(\d+)",', response.text)[0]
        except:
            item["newcarid"] = None

        item["status"] = "sale"
        item["brand"] = response.xpath("//h1[@class='info-title']/text()").extract_first().split(" ")[0]
        item["series"] = response.xpath("//h1[@class='info-title']/text()").extract_first().split(" ")[1]
        item["factoryname"] = None
        item["modelname"] = None
        item["brandid"] = None
        item["familyid"] = re.findall(r""" "chexiValue": '(\d+)',""", response.text)[0]
        item["seriesid"] = re.findall(r""" "chexiValue": '(\d+)',""", response.text)[0]
        item['makeyear'] = re.findall(r""" (\d+)款 """, item["shortdesc"])[0]
        item["registeryear"] = \
            response.xpath("//span[contains(text(),'上牌时间')]/../span[2]/text()").extract_first().strip().split("年")[
                0]
        try:
            dat = re.findall(r'<span class="info-meta_val">([.\d]+?)</span>', response.text, re.S)[0].strip()
        except:
            dat = '.'
        item['registerdate'] = dat.replace('.', '年') + '月'
        item["produceyear"] = None
        item["body"] = None
        item["bodystyle"] = None

        item["level"] = None
        item["driverway"] = None
        try:
            item["guideprice"] = \
            response.xpath("//a[@class='info-price_newcar']/text()").extract_first().split("：")[1]
        except:
            item["guideprice"] = None
        # 新车指导价46.30万(含税)
        item["guidepricetax"] = None
        item["doors"] = response.xpath(
            "//span[contains(text(),'车门数')]/../span[2]/text()").extract_first()
        item["gear"] = None
        item["geartype"] = response.xpath("//span[contains(text(),'变速箱')]/../span[2]/text()").extract_first()
        item["gearnumber"] = None

        item["generation"] = None

        item["lwvnumber"] = None
        item["maxps"] = None
        item["frontgauge"] = None
        item["compress"] = None
        
        item["years"] = None
        item["paytype"] = None
        mileage = response.xpath("//div[@class='info-price']/em/text()").extract_first()
        font_ttf_base64 = re.findall(r"base64,(.*?)'", response.text)[0]
        base64_ttf = base64.b64decode(font_ttf_base64)
        # window
        # with open("../che58.ttf", "bw") as f:
        # linux
        with open("/home/home/che58_font/che58.ttf", "bw") as f:

            f.write(base64_ttf)
            # self.save_data(response.meta["id"], mileage)
        font_dict = self.deal_font()
        for i in range(len(mileage)):
            if mileage[i] in font_dict:
                mileage = mileage.replace(mileage[i], font_dict[mileage[i]])
        item["price1"] = mileage
        item["pricetag"] = None
        item["mileage"] = response.xpath(
            "//div[@class='info-confs']//span[contains(text(),'表显里程')]/../span[2]/text()").extract_first().split(
            '万公里')[0]
        try:
            item['color'] = re.findall(r'_(.*?)_[\d\.]+万_', response.xpath('//title/text()').get())[0]
        except:
            item["color"] = None
        # try:
        #     item['city'] = response.xpath('//div[@class="info-adress"]/text()').get().split('市')[0]
        # except:
        #     item["city"] = response.meta["city"]
        item["city"] = item['pagetitle'].split('_')[-1]
        item["prov"] = None
        item["guarantee"] = None
        item["totalcheck_desc"] = None
        item["totalgrade"] = None
        type = str(response.xpath("//div[@class='shop-wx_desc']/text()").extract())
        if type == []:

            item["contact_type"] = '个人'
        else:
            item["contact_type"] = '店铺'
        item["contact_name"] = response.xpath("//span[@class='usr_nickname']/text()").extract_first()
        item["contact_phone"] = None
        item["contact_address"] = response.xpath("//div[@class='info-adress']/text()").extract_first()
        item["contact_company"] = response.xpath("//h2[@class='shop_title']/text()").extract_first()
        item["contact_url"] = None
        item["change_date"] = None
        item["change_times"] = None
        item["insurance1_date"] = response.xpath(
            "//span[contains(text(),'交强险到期')]/../span[2]/text()").extract_first()
        item["insurance2_date"] = response.xpath(
            "//span[contains(text(),'商业险到期')]/../span[2]/text()").extract_first()
        item["hascheck"] = None
        item["repairinfo"] = None
        item["yearchecktime"] = response.xpath('//dd[contains(text(), "年检到期")]/../dt/text()').extract_first()
        item["carokcf"] = None
        item["carcard"] = None
        item["carinvoice"] = None
        item["accident_desc"] = None
        item["accident_score"] = None
        item["outer_desc"] = None
        item["outer_score"] = None
        item["inner_desc"] = None
        item["inner_score"] = None
        item["safe_desc"] = None
        item["safe_score"] = None
        item["road_desc"] = None
        item["road_score"] = None
        item["lastposttime"] = None
        item["newcartitle"] = None
        item["newcarurl"] = None
        item["img_url"] = response.xpath("//img[@class='c-slide-video_poster']/@src").extract_first()
        item["first_owner"] = None
        item["carno"] = None
        item["carnotype"] = None
        item["carddate"] = None
        item["changecolor"] = None
        item["outcolor"] = None
        item["innercolor"] = None
        item["desc"] = response.xpath("//dd[@class='info-usr-desc_cont'][1]/text()").extract_first()
        item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])
        
        returndf = self.bf.isContains(item["statusplus"])
        # 1数据存在，0数据不存在
        if returndf == 1:
            ishave = True
        else:
            ishave = False
        logging.log(msg='数据是否已经存在： %s' % ishave, level=logging.INFO)
        url = "https://cheapi.58.com/api/getCarPCSpecDetailConf/{}".format(item["newcarid"])

        yield scrapy.Request(url=url, headers=self.headers, callback=self.msg_parse, meta={"item": item})

    # #
    def msg_parse(self, response):
        item = response.meta['item']
        car_list = json.loads(response.text)["result"]
        car_dict = {}
        for i in car_list:
            car_dict.update({i["lable"]: i["value"]})
        item["fueltype"] = car_dict["燃料类型"]
        item["output"] = car_dict["本车排量"]
        item["emission"] = car_dict["排放标准"]
        item["seats"] = car_dict["座位数"]
        if "*" not in car_dict["长*宽*高"]:
            car_dict["长*宽*高"] = "-*-*-"
        item["length"] = car_dict["长*宽*高"].split(
            "*")[0]
        item["width"] = car_dict["长*宽*高"].split("*")[1]
        item["height"] = car_dict["长*宽*高"].split("*")[2]
        item["gearnumber"] = None

        item["weight"] = car_dict["整备质量 (kg)"]
        item["wheelbase"] = car_dict["轴距 (mm)"]

        item["generation"] = None
        item["fuelnumber"] = car_dict["燃料标记"]

        item["lwv"] = car_dict["气缸"]
        item["lwvnumber"] = None
        item["maxnm"] = car_dict["最大扭矩"]
        item["maxpower"] = car_dict["最大功率"]
        yield item
        # print(item)