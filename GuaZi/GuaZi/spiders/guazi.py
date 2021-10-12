import json
from lxml import etree
import scrapy


class GuaziSpider(scrapy.Spider):
    name = 'guazi'
    allowed_domains = ['guazi.com']

    start_urls = ['https://marketing.guazi.com/marketing/brand/haveTags/all?cityId=-1']

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
        'MYSQL_DB': 'usedcar_update',
        'MYSQL_TABLE': 'guazi_online',
        'MONGODB_SERVER': '127.0.0.1',
        'MONGODB_PORT': 27017,
        'MONGODB_DB': 'guazi',
        'MONGODB_COLLECTION': 'guazi_online',
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0,
        'LOG_LEVEL': 'DEBUG',
        'RETRY_HTTP_CODES': [400, 403, 404, 408],
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
    }

    def parse(self, response):
        json_data = json.loads(response.text)
        for zimu in json_data['data']['brands'].keys():
            for brand_list in json_data['data']['brands'][zimu]:
                brand_name = brand_list['name']
                for family in brand_list['tags']:
                    family_name = family['name']
                    tag = family['url']
                    # print(brand_name, family_name, tag)
                    url = 'https://mapi.guazi.com/car-source/carList/pcList?tag={}&page=1&pageSize=20'.format(tag)
                    yield scrapy.Request(url=url, callback=self.parse_clue_id,
                                         meta={
                                             'brand_name': brand_name,
                                             'family_name': family_name,
                                             'tag': tag
                                         })
                    break
                break
            break

    def parse_clue_id(self, response):
        tag = response.meta['tag']
        brand_name = response.meta['brand_name']
        family_name = response.meta['family_name']
        item = {}
        json_data = json.loads(response.text)
        page = int(json_data['data']['page'])
        total_page = int(json_data['data']['totalPage'])
        print('--------------------------------当前{}页，共{}页-----------------------------'.format(page, total_page))
        # if page < total_page:
        #     next_url = 'https://mapi.guazi.com/car-source/carList/pcList?tag={}&page={}&pageSize=20'.format(tag,
        #                                                                                                     page + 1)
        #     yield scrapy.Request(url=next_url, callback=self.parse_clue_id,
        #                          meta={
        #                              'brand_name': brand_name,
        #                              'family_name': family_name,
        #                              'tag': tag
        #                          })

        for car in json_data['data']['postList']:
            clue_id = car['clue_id']
            try:
                # 取严选车
                guarantee = car['title_tags']['text']
            except:
                guarantee = None
            url = 'https://m.guazi.com/detail?clueId={}'.format(clue_id)
            yield scrapy.Request(url=url, callback=self.parse_index, dont_filter=True,
                                 meta={
                                     'brand_name': brand_name,
                                     'family_name': family_name,
                                     'clue_id': clue_id,
                                     'guarantee': guarantee
                                 })
            break

    def parse_index(self, response):
        brand_name = response.meta['brand_name']
        family_name = response.meta['family_name']
        clue_id = response.meta['clue_id']
        guarantee = response.meta['guarantee']
        html = etree.HTML(str(response.body, encoding="utf-8"))
        print(html.xpath('//h4[@class="car-name"]/text()'))

        # 第一页要取数据的解析
        info_dict = {}
        divs = html.xpath('//div[@class="item"]')
        for div in divs:
            key_name = div.xpath('./p[1]/text()')[0].strip()
            value_name = div.xpath('./p[2]/text()')[0].strip()
            #     print(key_name, value_name)
            info_dict[key_name] = value_name
        # 注册时间
        registeryear=html.xpath('//div[@class="m-car-record__body--top"]/div[@class="item"][1]/p[1]/text()')[0]\
            .strip()
        # 里程
        mileage=html.xpath('//div[@class="m-car-record__body--top"]/div[@class="item"][2]/p[@class="text"]/text()')[0]\
            .strip()
        # 排放标准
        emission=html.xpath('//div[@class="m-car-record__body--top"]/div[@class="item"][3]/p[@class="text"]/text()')[0]\
            .strip()
        # 过户次数
        change_times=info_dict['过户次数']
        # 排量
        output=info_dict['排量']
        # 城市归属地
        city=info_dict['车牌归属地']
        # 变速箱类型
        geartype=info_dict['变速箱']
        # 年检到期时间
        yearchecktime=info_dict['年检到期']
        # 车辆用途
        usage=info_dict['使用性质']
        # 交强险
        insurance1_date=info_dict['交强险到期']
        # 颜色
        color=info_dict['车身颜色']
        # 出厂日期
        produceyear=info_dict['出厂日期']
        # 车源号
        statusplus=info_dict['车源号']
        # 钥匙
        keynumbers=info_dict['钥匙数量']

        url = 'https://m.guazi.com/car-record/v2?clueId={}'.format(clue_id)
        yield scrapy.Request(url=url, callback=self.parse_parameter, dont_filter=True,
                             meta={
                                 'brand_name': brand_name,
                                 'family_name': family_name,
                                 'clue_id': clue_id,
                                 'guarantee': guarantee,
                                 'registeryear':registeryear,
                                 'mileage':mileage,
                                 'emission':emission,
                                 'change_times':change_times,
                                 'output':output,
                                 'city':city,
                                 'geartype':geartype,
                                 'yearchecktime':yearchecktime,
                                 'usage':usage,
                                 'insurance1_date':insurance1_date,
                                 'color':color,
                                 'produceyear':produceyear,
                                 'statusplus':statusplus,
                                 'keynumbers':keynumbers,

                             })

    def parse_parameter(self, response):
        item = {}
        brand_name = response.meta['brand_name']
        family_name = response.meta['family_name']
        clue_id = response.meta['clue_id']
        guarantee = response.meta['guarantee']
        registeryear=response.meta['registeryear']
        mileage=response.meta['mileage']
        emission=response.meta['emission']
        change_times=response.meta['change_times']
        output=response.meta['output']
        city=response.meta['city']
        geartype=response.meta['geartype']
        yearchecktime=response.meta['yearchecktime']
        usage=response.meta['usage']
        insurance1_date=response.meta['insurance1_date']
        color=response.meta['color']
        produceyear=response.meta['produceyear']
        statusplus=response.meta['statusplus']
        keynumbers=response.meta['keynumbers']
        html = etree.HTML(str(response.body, encoding="utf-8"))
        parameter_dict = {}
        configures = html.xpath('//li[@class="list-item__body__row"]')
        for configure in configures:
            key_name1 = configure.xpath('./span[@class="list-item__body__row__title"]/text()')[0].strip()
            try:
                value_name1 = configure.xpath('./div[@class="list-item__body__row__content"]/text()')[0].strip()
            except:
                try:
                    value_name1 = configure.xpath('./div[@class="list-item__body__row__content"]/span/@class')[0]\
                        .replace('list-item__body__row__content--', '')
                except:
                    value_name1 = ''.join(
                        configure.xpath('./div[@class="list-item__body__row__content"]//text()'))\
                        .replace('\n','').replace(
                        ' ', '')
            parameter_dict[key_name1] = value_name1
        # familyname生产厂家
        factoryname = parameter_dict['厂商']
        # 指导价(含税)
        guidepricetax = parameter_dict['厂商指导价(万元)']
        # 年款
        makeyear=parameter_dict['上市时间']
        # 燃油类型
        fueltype = parameter_dict['能源形式']
        # 变速箱描述
        gear = parameter_dict['变速器描述']
        # 车身类型
        bodystyle = parameter_dict['车身形式']
        # 进气方式
        first_owner=parameter_dict['进气形式']
        # 气缸排列型式
        lwv = parameter_dict['气缸排列形式']
        # 气缸数
        lwvnumber = parameter_dict['气缸数(个)']
        # 最大马力
        maxps = parameter_dict['最大马力(Ps)']
        # 最大功率
        maxpower = parameter_dict['最大功率(kW)']
        # 最大扭矩
        maxnm = parameter_dict['最大扭矩(N·m)']
        # 燃油标号
        fuelnumber = parameter_dict['燃油标号']
        # 档位数
        gearnumber = parameter_dict['挡位个数']
        # 轴距
        wheelbase = parameter_dict['轴距(mm)']
        # 车高
        height = parameter_dict['高度(mm)']
        # 车宽
        width=parameter_dict['宽度(mm)']
        # 车长
        length = parameter_dict['长度(mm)']
        # 前轮距
        frontgauge = parameter_dict['前轮距(mm)']
        # 车门数量
        doors = parameter_dict['车门数(个)']
        # 座位数
        seats = parameter_dict['座位数(个)']
        # 整备质量
        weight = parameter_dict['整备质量(kg)']
        # 驱动类型
        driverway = parameter_dict['驱动方式']
        # 描述
        desc=

        item['carid'] = clue_id
        item['car_source'] = 'guazi'
        update_time = None


