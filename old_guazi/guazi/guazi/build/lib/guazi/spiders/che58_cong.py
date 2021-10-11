# -*- coding: UTF-8 -*-
import datetime
import re

import requests
import scrapy
from redis import Redis
from scrapy.conf import settings
from ..items import GuaziItem
import time
import logging

website = 'che58_cong'

redis_cli = Redis(host="192.168.1.249", port=6379, db=3)

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
        'CONCURRENT_REQUESTS': 8,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        "REDIRECT_ENABLED": True
    }
    kanche_url = "https://{}.58.com/ershouche/"
    city_dict = {'shanda': '安达', 'ale': '阿拉尔', 'anningshi': '安宁', 'anxixian': '安溪', 'anlu': '安陆', 'anqiu': '安丘', 'as': '鞍山', 'alt': '阿勒泰', 'ay': '安阳', 'anqing': '安庆', 'ankang': '安康', 'aks': '阿克苏', 'ab': '阿坝', 'al': '阿里', 'alsm': '阿拉善盟', 'anshun': '安顺', 'anji': '安吉', 'anyuexian': '安岳', 'by': '白银', 'bj': '北京', 'boluo': '博罗', 'beipiao': '北票', 'beiliushi': '北流', 'boxing': '博兴', 'bazhou': '霸州', 'bobaixian': '博白', 'bd': '保定', 'bt': '包头', 'bz': '滨州', 'baoji': '宝鸡', 'baoting': '保亭', 'baish': '白沙', 'bengbu': '蚌埠', 'benxi': '本溪', 'bc': '白城', 'bozhou': '亳州', 'bs': '保山', 'bygl': '巴音郭楞', 'bazhong': '巴中', 'betl': '博尔塔拉', 'bycem': '巴彦淖尔市', 'baishan': '白山', 'bijie': '毕节', 'baise': '百色', 'bh': '北海', 'baoyingx': '宝应县', 'cixi': '慈溪', 'cangxian': '沧县', 'cx': '楚雄', 'cilixian': '慈利', 'chiping': '茌平', 'changningshi': '常宁', 'chibishi': '赤壁', 'cenxi': '岑溪', 'cd': '成都', 'changle': '昌乐', 'changyishi': '昌邑', 'cixian': '磁县', 'cz': '常州', 'cangzhou': '沧州', 'changji': '昌吉', 'cm': '澄迈', 'chifeng': '赤峰', 'changde': '常德', 'chenzhou': '郴州', 'chengde': '承德', 'changdu': '昌都', 'cy': '朝阳', 'ch': '巢湖', 'chizhou': '池州', 'chuzhou': '滁州', 'chaozhou': '潮州', 'chongzuo': '崇左', 'cangnanxian': '苍南', 'caoxian': '曹县', 'dingbian': '定边', 'dongtai': '东台', 'danyang': '丹阳', 'deqing': '德清', 'donghai': '东海', 'deyang': '德阳', 'dali': '大理', 'dongzhi': '东至', 'dunhuang': '敦煌', 'dongyang': '东阳', 'dazu': '大竹', 'dongping': '东平', 'dengta': '灯塔', 'dawu': '大悟', 'dengzhou': '邓州', 'dongming': '东明', 'dg': '东莞', 'dl': '大连', 'dz': '德州', 'dangyang': '当阳', 'dy': '东营', 'dq': '大庆', 'dingzhou': '定州', 'dxal': '大兴安岭', 'df': '东方', 'da': '定安', 'danzhou': '儋州', 'dandong': '丹东', 'dt': '大同', 'diqing': '迪庆', 'dh': '德宏', 'dazhou': '达州', 'dx': '定西', 'dafeng': '大丰', 'shanxian': '单县', 'es': '恩施', 'ez': '鄂州', 'erds': '鄂尔多斯', 'fugu': '府谷', 'fy': '阜阳', 'fengchengshi': '丰城', 'fuanshi': '福安', 'fuliangxian': '浮梁', 'fudingshi': '福鼎', 'fuyuxian': '扶余', 'fenyi': '分宜', 'fanxian': '范县', 'funingxian': '阜宁', 'fengcheng': '凤城', 'fz': '福州', 'fs': '佛山', 'fushun': '抚顺', 'fx': '阜新', 'fuzhou': '抚州', 'fcg': '防城港', 'feicheng': '肥城', 'gz': '广州', 'ganzhou': '赣州', 'ga': '广安', 'guyuan': '固原', 'guangshuishi': '广水', 'gucheng': '谷城', 'gaoping': '高平', 'geermushi': '格尔木', 'gaoan': '高安', 'guipingqu': '桂平', 'czguiyang': '桂阳', 'gushixian': '固始', 'guanxian': '冠县', 'gaotang': '高唐', 'lfguan': '固安', 'gaizexian': '改则', 'gy': '贵阳', 'gl': '桂林', 'gt': '馆陶', 'gg': '贵港', 'guangyuan': '广元', 'ganzi': '甘孜', 'guoluo': '果洛', 'gn': '甘南', 'guangrao': '广饶', 'gongzhuling': '公主岭', 'guanghanshi': '广汉', 'guanyun': '灌云', 'guannan': '灌南', 'gaomi': '高密', 'haimen': '海门', 'haian': '海安', 'haining': '海宁', 'huidong': '惠东', 'huarong': '华容', 'hg': '黄冈', 'hn': '淮南', 'huangshan': '黄山', 'hc': '河池', 'hb': '鹤壁', 'honghe': '红河', 'haibei': '海北', 'huaxian': '滑县', 'hancheng': '韩城', 'hejian': '河间', 'hz': '杭州', 'huanghua': '黄骅', 'huadian': '桦甸', 'hengdong': '衡东', 'haiyan': '海盐', 'huaibinxian': '淮滨', 'hrb': '哈尔滨', 'haikou': '海口', 'hf': '合肥', 'hu': '呼和浩特', 'huizhou': '惠州', 'hy': '衡阳', 'hd': '邯郸', 'huzhou': '湖州', 'hs': '衡水', 'hegang': '鹤岗', 'heihe': '黑河', 'hami': '哈密', 'hanzhong': '汉中', 'ha': '淮安', 'hshi': '黄石', 'hlr': '海拉尔', 'heze': '菏泽', 'hh': '怀化', 'huaibei': '淮北', 'ht': '和田', 'huangnan': '黄南', 'hx': '海西', 'haidong': '海东', 'hlbe': '呼伦贝尔', 'hld': '葫芦岛', 'heyuan': '河源', 'hezhou': '贺州', 'hainan': '海南', 'hexian': '和县', 'hq': '霍邱', 'hanchuan': '汉川', 'haifengxian': '海丰', 'huantaixian': '桓台', 'jingbian': '靖边', 'jinchang': '金昌', 'jinjiangshi': '晋江', 'jianhu': '建湖', 'jingjiang': '靖江', 'jingmen': '荆门', 'jinzhou': '锦州', 'jdz': '景德镇', 'ja': '吉安', 'jiashanx': '嘉善', 'jingshanxian': '京山', 'juancheng': '鄄城', 'jiangshanshi': '江山', 'jiayuxian': '嘉鱼', 'junxian': '浚县', 'jinxian': '进贤', 'jurong': '句容', 'juye': '巨野', 'jinhu': '金湖', 'jiangyins': '江阴', 'jn': '济南', 'jining': '济宁', 'jx': '嘉兴', 'jm': '江门', 'jh': '金华', 'jl': '吉林', 'jy': '揭阳', 'jz': '晋中', 'jiyuan': '济源', 'jj': '九江', 'jiaozuo': '焦作', 'jincheng': '晋城', 'jingzhou': '荆州', 'jms': '佳木斯', 'jixi': '鸡西', 'jyg': '嘉峪关', 'jq': '酒泉', 'jintan': '金坛', 'jiangyan': '姜堰', 'jianyangshi': '简阳', 'juxian': '莒县', 'kaiyuan': '开原', 'kaifeng': '开封', 'kaipingshi': '开平', 'km': '昆明', 'klmy': '克拉玛依', 'ks': '喀什', 'kzls': '克孜勒苏', 'kl': '垦利', 'szkunshan': '昆山', 'liyang': '溧阳', 'lw': '莱芜', 'la': '六安', 'luzhou': '泸州', 'lj': '丽江', 'longkou': '龙口', 'leling': '乐陵', 'lengshuijiangshi': '冷水江', 'lufengshi': '陆丰', 'lianyuanshi': '涟源', 'linqing': '临清', 'lixian': '澧县', 'liulin': '柳林', 'lishu': '梨树县', 'lijin': '利津', 'luannanxian': '滦南', 'liangshanx': '梁山', 'linyixianq': '临邑', 'laohekou': '老河口', 'luyi': '鹿邑', 'linzhou': '林州', 'lankaoxian': '兰考', 'laiyang': '莱阳', 'linqu': '临朐', 'lz': '兰州', 'luoyang': '洛阳', 'lf': '廊坊', 'linyi': '临沂', 'lc': '聊城', 'lyg': '连云港', 'lishui': '丽水', 'linyixian': '临猗', 'ld': '娄底', 'yueqingcity': '乐清', 'lingshui': '陵水', 'lps': '六盘水', 'lvliang': '吕梁', 'ls': '乐山', 'liaoyang': '辽阳', 'liaoyuan': '辽源', 'lasa': '拉萨', 'linfen': '临汾', 'ly': '龙岩', 'linxia': '临夏', 'liuzhou': '柳州', 'luohe': '漯河', 'lincang': '临沧', 'liangshan': '凉山', 'linzhi': '林芝', 'ln': '陇南', 'lb': '来宾', 'laizhou': '莱州', 'linhai': '临海', 'lingbaoshi': '灵宝', 'lepingshi': '乐平', 'longhai': '龙海', 'liling': '醴陵', 'mengjinqu': '孟津', 'meihekou': '梅河口', 'yingchixian': '渑池', 'mengzhou': '孟州', 'milexian': '弥勒', 'mianyang': '绵阳', 'mm': '茂名', 'mg': '明港', 'mas': '马鞍山', 'mdj': '牡丹江', 'mz': '梅州', 'ms': '眉山', 'nananshi': '南安', 'nanzhang': '南漳', 'nanchong': '南充', 'ningguo': '宁国', 'nanchengx': '南城', 'nanxian': '南县', 'ningjin': '宁津', 'ningyang': '宁阳', 'nj': '南京', 'nc': '南昌', 'nb': '宁波', 'nn': '南宁', 'ny': '南阳', 'nt': '南通', 'nd': '宁德', 'scnj': '内江', 'nujiang': '怒江', 'nq': '那曲', 'np': '南平', 'xzpeixian': '沛县', 'pizhou': '邳州', 'panzhihua': '攀枝花', 'pinghushi': '平湖', 'panshi': '磐石', 'pingyangxian': '平阳', 'pingyi': '平邑', 'pds': '平顶山', 'pj': '盘锦', 'px': '萍乡', 'pl': '平凉', 'puyang': '濮阳', 'pt': '莆田', 'pe': '普洱', 'penglai': '蓬莱', 'qidong': '启东', 'qinzhou': '钦州', 'qj': '曲靖', 'qiyang': '祁阳', 'qidongxian': '祁东', 'qianxixian': '迁西', 'qixianq': '淇县', 'qux': '渠县', 'qihe': '齐河', 'qinyang': '沁阳', 'qingzhen': '清镇', 'qixia': '栖霞', 'qd': '青岛', 'qz': '泉州', 'qhd': '秦皇岛', 'qth': '七台河', 'qh': '琼海', 'qxn': '黔西南', 'qn': '黔南', 'qqhr': '齐齐哈尔', 'quzhou': '衢州', 'qingyuan': '清远', 'qdn': '黔东南', 'qiongzhong': '琼中', 'qingyang': '庆阳', 'qingxu': '清徐', 'qianjiang': '潜江', 'qianan': '迁安市', 'qingzhou': '青州', 'qixianqu': '杞县', 'rugao': '如皋', 'rudong': '如东', 'rituxian': '日土', 'rizhao': '日照', 'ruiancity': '瑞安', 'rkz': '日喀则', 'rongcheng': '荣成', 'ruzhou': '汝州', 'renshouxian': '仁寿', 'renqiu': '任丘', 'rushan': '乳山', 'renhuaishi': '仁怀', 'sh': '上海', 'sz': '深圳', 'shishi': '石狮', 'shouguang': '寿光', 'songyuan': '松原', 'sanya': '三亚', 'shayangxian': '沙洋', 'suixia': '随县', 'shangshui': '商水', 'shanghangxian': '上杭', 'shaodongxian': '邵东', 'shuangfengxian': '双峰', 'shehongxian': '射洪', 'shaheshi': '沙河', 'shaoyangxian': '邵阳县', 'songzi': '松滋', 'sheyang': '射阳', 'shengzhou': '嵊州', 'shenqiu': '沈丘', 'suixian': '睢县', 'shexian': '涉县', 'su': '苏州', 'sy': '沈阳', 'xm': '厦门', 'sjz': '石家庄', 'st': '汕头', 'suzhou': '宿州', 'sx': '绍兴', 'shiyan': '十堰', 'sd': '顺德', 'smx': '三门峡', 'sys': '双鸭山', 'sansha': '三沙', 'sm': '三明', 'sg': '韶关', 'sq': '商丘', 'shuyang': '沭阳', 'suqian': '宿迁', 'suihua': '绥化', 'shaoyang': '邵阳', 'sw': '汕尾', 'sl': '商洛', 'shuozhou': '朔州', 'shz': '石河子', 'szs': '石嘴山', 'sn': '山南', 'suining': '遂宁', 'sr': '上饶', 'sp': '四平', 'suizhou': '随州', 'snj': '神农架', 'shenmu': '神木', 'siyang': '泗阳', 'sihong': '泗洪', 'sanhe': '三河', 'tianchang': '天长', 'tongxiang': '桐乡', 'taixing': '泰兴', 'tianshui': '天水', 'tancheng': '郯城', 'taikang': '太康', 'tongxuxian': '通许', 'tj': '天津', 'ty': '太原', 'ts': '唐山', 'tac': '塔城', 'ta': '泰安', 'tz': '台州', 'tunchang': '屯昌', 'tr': '铜仁', 'taizhou': '泰州', 'tl': '铁岭', 'tlf': '吐鲁番', 'tc': '铜川', 'tmsk': '图木舒克', 'tongliao': '通辽', 'th': '通化', 'tongling': '铜陵', 'tm': '天门', 'taishan': '台山', 'tongcheng': '桐城', 'tengzhou': '滕州', 'wuxueshi': '武穴', 'wenling': '温岭', 'ws': '文山', 'wuhai': '乌海', 'wuweixian': '无为', 'wudi': '无棣', 'wugang': '舞钢', 'weishixian': '尉氏', 'wh': '武汉', 'wenshang': '汶上', 'wenxian': '温县', 'wuyix': '武义县', 'weishan': '微山', 'wx': '无锡', 'wf': '潍坊', 'xj': '乌鲁木齐', 'wz': '温州', 'weihai': '威海', 'wzs': '五指山', 'wenchang': '文昌', 'wanning': '万宁', 'wuhu': '芜湖', 'wuzhou': '梧州', 'wfd': '瓦房店', 'wn': '渭南', 'wjq': '五家渠', 'wuzhong': '吴忠', 'wlcb': '乌兰察布', 'wuwei': '武威', 'wuyishan': '武夷山', 'wuan': '武安', 'xiangshanxian': '象山', 'xinyishi': '新沂', 'xinghuashi': '兴化', 'bn': '西双版纳', 'xiaoyi': '孝义', 'xuanwushi': '宣威', 'xiaochang': '孝昌', 'xiangyuanxian': '襄垣', 'lyxinan': '新安', 'xuanhan': '宣汉', 'xiangyin': '湘阴', 'xa': '西安', 'shenxian': '莘县', 'xuyi': '盱眙', 'xianghe': '香河', 'xinchang': '新昌', 'xinye': '新野', 'xiangshui': '响水', 'xz': '徐州', 'xiangtan': '湘潭', 'xf': '襄阳', 'xx': '新乡', 'xy': '信阳', 'xiantao': '仙桃', 'xianyang': '咸阳', 'xt': '邢台', 'xiaogan': '孝感', 'xn': '西宁', 'xc': '许昌', 'xinzhou': '忻州', 'xuancheng': '宣城', 'xam': '兴安盟', 'xinyu': '新余', 'xiangxi': '湘西', 'xianning': '咸宁', 'xl': '锡林郭勒', 'xintai': '新泰', 'xionganxinqu': '雄安新区', 'xiangchengshi': '项城', 'yutianxian': '玉田', 'yangzhong': '扬中', 'yidou': '宜都', 'yj': '阳江', 'yongzhou': '永州', 'yulin': '玉林', 'zzyouxian': '攸县', 'yuanjiangs': '沅江', 'yuchengshi': '禹城', 'yuzhou': '禹州', 'yongcheng': '永城', 'yongan': '永安', 'yujiang': '余江', 'hzyc': '郓城', 'yunmeng': '云梦', 'yichengshi': '宜城', 'yongxing': '永兴', 'lyyiyang': '宜阳', 'yanggu': '阳谷', 'yinanxian': '沂南', 'yiyuanxian': '沂源', 'yichuan': '伊川', 'yongchunxian': '永春', 'yt': '烟台', 'yuyao': '余姚', 'yz': '扬州', 'yc': '宜昌', 'yancheng': '盐城', 'yy': '岳阳', 'yangchun': '阳春', 'yq': '阳泉', 'yanan': '延安', 'yanling': '鄢陵', 'yich': '伊春', 'yinchuan': '银川', 'yanbian': '延边', 'yingtan': '鹰潭', 'yx': '玉溪', 'yuncheng': '运城', 'yichun': '宜春', 'yk': '营口', 'yl': '榆林', 'yb': '宜宾', 'ya': '雅安', 'ys': '玉树', 'yili': '伊犁', 'yiyang': '益阳', 'yf': '云浮', 'yxx': '永新', 'yiwu': '义乌', 'lfyanjiao': '燕郊', 'yongkang': '永康', 'yuhuan': '玉环', 'yanshiqu': '偃师', 'shzhaodong': '肇东', 'zhuji': '诸暨', 'changxing': '长兴', 'zunhua': '遵化市', 'zhaozhou': '肇州', 'changlingxian': '长岭', 'zixing': '资兴', 'zhongxiangshi': '钟祥', 'zhangshu': '樟树', 'changningx': '长宁', 'zhangpu': '漳浦', 'zezhou': '泽州', 'cs': '长沙', 'cq': '重庆', 'cc': '长春', 'zz': '郑州', 'zh': '珠海', 'zjk': '张家口', 'zs': '中山', 'zb': '淄博', 'zhuzhou': '株洲', 'zhijiang': '枝江', 'zhangzhou': '漳州', 'zhanjiang': '湛江', 'zq': '肇庆', 'zaozhuang': '枣庄', 'zhoushan': '舟山', 'zhangqiu': '章丘', 'zx': '赵县', 'zc': '诸城', 'zunyi': '遵义', 'zj': '镇江', 'zk': '周口', 'zd': '正定', 'zmd': '驻马店', 'hk': '中国香港', 'tw': '中国台湾', 'pld': '庄河', 'zg': '自贡', 'zjj': '张家界', 'zy': '资阳', 'changzhi': '长治', 'changge': '长葛', 'am': '中国澳门', 'zt': '昭通', 'zw': '中卫', 'zhangye': '张掖', 'zhangbei': '张北', 'zouping': '邹平', 'zoucheng': '邹城', 'zhuozhou': '涿州', 'zhaoyuan': '招远', 'zaoyang': '枣阳', 'changyuan': '长垣'}


    def __init__(self, **kwargs):
        # args
        super(CarSpider, self).__init__(**kwargs)
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
    def get_url(self):
        sum =redis_cli.scard('che58:key')
        if sum <=0:
            return False
        else:
            return  redis_cli.spop("che58:key")
    def start_requests(self):
        url =self.get_url()
        yield scrapy.Request(url=url, headers=self.headers)


    def detail_parse(self, response):
        print(response.url)
        item = GuaziItem()
        item["carid"] = response.meta["id"]
        item["car_source"] = "che58"
        item["usage"] = None
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["update_time"] = None
        item["post_time"] = response.xpath("//span[@class='info-post-date']/text()").extract_first()
        item["sold_date"] = None
        item["pagetime"] = None
        item["parsetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["shortdesc"] = response.xpath("//h1[@class='info-title']/text()").extract_first()
        item["pagetitle"] = response.xpath("//title/text()").extract_first().strip("")
        item["url"] = response.url
        try:
            item["newcarid"] = re.findall(r' "chexingValue": "(\d+)",', response.text)[0]
        except:
            item["newcarid"] =None

        car_dict = self.get_car_msg(item["newcarid"])
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
            response.xpath("//span[contains(text(),'上牌时间')]/../span[2]/text()").extract_first().strip().split("年")[0]
        item["produceyear"] = None
        item["body"] = None
        item["bodystyle"] = None

        item["level"] = None
        item["fueltype"] = car_dict["燃料类型"]
        item["driverway"] = None
        item["output"] = car_dict["本车排量"]
        item["guideprice"] = response.xpath("//a[@class='info-price_newcar']/text()").extract_first().split("：")[1]
        # 新车指导价46.30万(含税)
        item["guidepricetax"] = None
        item["doors"] = response.xpath(
            "//span[contains(text(),'车门数')]/../span[2]/text()").extract_first()
        item["emission"] = car_dict["排放标准"]
        item["gear"] = None
        item["geartype"] = response.xpath("//span[contains(text(),'变速箱')]/../span[2]/text()").extract_first()
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
        item["maxps"] = None
        item["frontgauge"] = None
        item["compress"] = None
        item["registerdate"] = response.xpath(
            "//span[contains(text(),'上牌时间')]/../span[2]/text()").extract_first().strip()

        item["years"] = None
        item["paytype"] = None
        item["price1"] = response.xpath("//em[@class='info-price_usedcar']/text()").extract_first()
        item["pricetag"] = None
        item["mileage"] = response.xpath("//div[@class='info-confs']//span[contains(text(),'表显里程')]/../span[2]/text()").extract_first().split('万公里')[0]
        item["color"] = None
        item["city"] = response.meta["city"]
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
        item["insurance1_date"] = response.xpath("//span[contains(text(),'交强险到期')]/../span[2]/text()").extract_first()
        item["insurance2_date"] = response.xpath("//span[contains(text(),'商业险到期')]/../span[2]/text()").extract_first()
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
        item["desc"] = response.xpath("//dd[@class='info-usr-desc_cont'][1]/text()").extract()
        item["statusplus"] = response.url + "-None-sale-" + str(item["price1"])
        # print(item)
        yield item
