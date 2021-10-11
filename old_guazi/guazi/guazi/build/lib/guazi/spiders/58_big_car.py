# -*- coding: UTF-8 -*-
import datetime
import re

import requests
import scrapy
from scrapy.conf import settings
from ..items import che58_big_car
import time
import logging

website = 'che58_big_car'


# original
class CarSpider(scrapy.Spider):
    # basesetting
    name = website
    allowed_domains = ["58.com"]
    start_urls = [
        "https://m.58.com/city.html?"
    ]
    base_url = "https://m.58.com/{}/huochec/?page={}"
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        "REDIRECT_ENABLED": True
    }
    kanche_url = "https://{}.58.com/huochec/"
    car_url = 'https://{}.58.com/huochec/{}x.shtml?'
    city_dict = {'安达': 'shanda', '阿拉尔': 'ale', '安宁': 'anningshi', '安溪': 'anxixian', '安陆': 'anlu', '安丘': 'anqiu',
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
        settings.set('MYSQLDB_DB', "truck", priority='cmdline')
        settings.set('WEBSITE', website, priority='cmdline')

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
        for i in city_list[0:5]:
            city = i.xpath("./a/text()").extract_first()
            city_url = "https:" + i.xpath("./a/@href").extract_first().split("https:")[0] + 'huochec'
            city_base = "https://{}.58.com/huochec".format(re.findall(r"m.58.com/(.*)/huochec", city_url)[0])
            dict.update({city: re.findall(r"m.58.com/(.*)/huochec", city_url)[0]})
            yield scrapy.Request(url=city_url, headers=self.headers,
                                 meta={"city": city, "city_base": city_base, "page": 1},
                                 callback=self.car_list_parse)
        # print(dict)

    def car_list_parse(self, response):
        car_list = response.xpath("//ul[@class='seo-infolist']//li")
        index = response.xpath("//ul[@class='seo-infolist']//li//a/@href").extract()
        if index == []:
            return
        response.meta["page"] = response.meta["page"] + 1
        for i in car_list:
            url = i.xpath(".//a/@href").extract_first()
            price = i.xpath(".//b/text()").extract_first()
            response.meta.update({"price": price})
            yield scrapy.Request(url=url, headers=self.headers, callback=self.car_parse, meta=response.meta)
        url = self.base_url.format(self.city_dict[response.meta["city"]], response.meta["page"])
        # yield scrapy.Request(url=url, headers=self.headers, callback=self.car_list_parse, meta=response.meta)

    #     https://bj.58.com/ershouche/39627873788055x.shtml?
    def car_parse(self, response):
        print("-"*50)
        url = response.url
        id = re.findall(r"/(\d+)x.shtml", url)[0]
        city = re.findall(r"com/(.*)/huochec/", url)[0]
        response.meta.update({"id": id, "city": city})
        url = self.car_url.format(city, id)
        yield scrapy.Request(url=url, headers=self.headers1, meta=response.meta, callback=self.detail_parse)

    def detail_parse(self, response):
        print("*" * 50)
        item = che58_big_car()
        if response.xpath("//span[@class='crb_i']/a[@index='3']/text()").extract_first() == '挂车':
            item["carid"] = response.meta["id"]
            item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["url"] = response.url
            item["brandid"] = response.xpath("//input[@id='modelId']/@value").extract_first()
            item["seriesid"] = response.xpath("//input[@id='chexingId']/@value").extract_first()
            item["city"] = response.xpath("//span[@class='crb_i']/a[@index='1']/text()").extract_first()
            item["brand"] = response.xpath("//span[@class='crb_i']/a[@index='4']/text()").extract_first()
            item["series"] = response.xpath("//span[@class='crb_i']/a[@index='5']/text()").extract_first()
            item["price"] = response.meta["price"]
            item["title"] = response.xpath("//title/text()").extract_first()
            item["shortdesc"] = response.xpath("//p[@class='title_p']/text()").extract_first()
            item["mileage"] = response.xpath("//span[contains(text(),'表显里程：')]/../span[2]/text()").extract_first()
            item["des"] = response.xpath("//div[@class='cardes_div']/p/text()").extract_first().strip()
            item["img"] = response.xpath("//div[@class='carimg_list']/img[1]/@src").extract_first()
            item["load"] = response.xpath("//span[contains(text(),'额定载重：')]/../span[2]/text()").extract_first()
            item["yearcheck"] = response.xpath("//span[contains(text(),'年检到期时间')]/../span[2]/text()").extract_first()
            item["makeyear"] = response.xpath(
                "//span[@class='descrp'][contains(text(),'出厂')]/../span[1]/text()").extract_first()
            item["insurance1_date"] = response.xpath(
                "//span[contains(text(),'交强险到期时间：')]/../span[2]/text()").extract_first()
            item["poste_time"] = response.xpath("//span[@class='time']/text()").extract_first()
            item["type"] = response.xpath("//span[@class='crb_i']/a[@index='3']/text()").extract_first()
            item["statusplus"] = response.url + str(item["price"])
        else:
            item["carid"] = response.meta["id"]
            item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["url"] = response.url
            item["brandid"] = response.xpath("//input[@id='modelId']/@value").extract_first()
            item["seriesid"] = response.xpath("//input[@id='chexingId']/@value").extract_first()
            item["city"] = response.xpath("//span[@class='crb_i']/a[@index='1']/text()").extract_first().strip("二手车网")
            item["brand"] = response.xpath("//span[@class='crb_i']/a[@index='4']/text()").extract_first().strip("二手")
            item["series"] = response.xpath("//span[@class='crb_i']/a[@index='5']/text()").extract_first().strip("二手")
            item["price"] = response.meta["price"]
            item["title"] = response.xpath("//title/text()").extract_first()
            item["shortdesc"] = response.xpath("//p[@class='title_p']/text()").extract_first()
            item["mileage"] = response.xpath("//span[contains(text(),'表显里程：')]/../span[2]/text()").extract_first()
            item["des"] = response.xpath("//div[@class='cardes_div']/p/text()").extract_first().strip()
            item["img"] = response.xpath("//div[@class='carimg_list']/img[1]/@src").extract_first()
            item["load"] = response.xpath("//span[contains(text(),'额定载重：')]/../span[2]/text()").extract_first()
            item["yearcheck"] = response.xpath("//span[contains(text(),'年检到期时间')]/../span[2]/text()").extract_first()
            item["makeyear"] = response.xpath(
                "//span[@class='descrp'][contains(text(),'出厂')]/../span[1]/text()").extract_first()
            item["insurance1_date"] = response.xpath(
                "//span[contains(text(),'交强险到期时间：')]/../span[2]/text()").extract_first()
            item["poste_time"] = response.xpath("//span[@class='time']/text()").extract_first()
            item["type"] = response.xpath("//span[@class='crb_i']/a[@index='3']/text()").extract_first()
            item["statusplus"] = response.url + str(item["price"])
        # print(item)
        yield item
