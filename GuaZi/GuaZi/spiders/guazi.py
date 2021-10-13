import json
import time
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
        'MYSQL_TABLE': 'guazi_online_testjg',
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
                    url = 'https://mapi.guazi.com/car-source/series/getSeriesRaiders?seriesId={}'.format(family['id'])
                    yield scrapy.Request(url=url, callback=self.parse_car_level,
                                         meta={
                                             'brand_name': brand_name,
                                             'family_name': family_name,
                                             'tag': tag
                                         })
                    # break
            #     break
            # break

    def parse_car_level(self, response):
        tag = response.meta['tag']
        brand_name = response.meta['brand_name']
        family_name = response.meta['family_name']
        json_data = json.loads(response.text)
        try:
            car_level = json_data['data']['carSeriesInfo']['carLevel']
        except:
            car_level = None
        url = 'https://mapi.guazi.com/car-source/carList/pcList?tag={}&page=1&pageSize=20'.format(tag)
        yield scrapy.Request(url=url, callback=self.parse_clue_id,
                             meta={
                                 'brand_name': brand_name,
                                 'family_name': family_name,
                                 'tag': tag,
                                 'car_level': car_level
                             })

    def parse_clue_id(self, response):
        tag = response.meta['tag']
        brand_name = response.meta['brand_name']
        family_name = response.meta['family_name']
        car_level = response.meta['car_level']
        json_data = json.loads(response.text)
        page = int(json_data['data']['page'])
        total_page = int(json_data['data']['totalPage'])
        # print('--------------------------------当前{}页，共{}页-----------------------------'.format(page, total_page))
        if page < total_page:
            next_url = 'https://mapi.guazi.com/car-source/carList/pcList?tag={}&page={}&pageSize=20'.format(tag,
                                                                                                            page + 1)
            yield scrapy.Request(url=next_url, callback=self.parse_clue_id,
                                 meta={
                                     'brand_name': brand_name,
                                     'family_name': family_name,
                                     'tag': tag
                                 })

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
                                     'guarantee': guarantee,
                                     'car_level': car_level
                                 })

    def parse_index(self, response):
        brand_name = response.meta['brand_name']
        family_name = response.meta['family_name']
        clue_id = response.meta['clue_id']
        guarantee = response.meta['guarantee']
        car_level = response.meta['car_level']
        html = etree.HTML(str(response.body, encoding="utf-8"))

        # 第一页要取数据的解析
        info_dict = {}
        divs = html.xpath('//div[@class="item"]')
        for div in divs:
            key_name = div.xpath('./p[1]/text()')[0].strip()
            value_name = div.xpath('./p[2]/text()')[0].strip()
            #     print(key_name, value_name)
            info_dict[key_name] = value_name

        # 二手车价格
        try:
            price1 = html.xpath('//div[@class="c-series-market__car-info-item"][1]/text()')[0].strip() \
                .replace("当前车源：", "")
        except:
            price1 = \
                html.xpath('//div[@class="c-car-price__left-price"]/span[@class="c-car-price__left-value"]/text()')[0]
        else:
            price1 = None
        # 车辆标题描述
        try:
            shortdesc = html.xpath(
                '//div[@class="c-page-wrapper c-page-wrapper__success p-detail"]//div[@class="m-car-title"]/h4[@class="car-name"]/text()')
        except:
            shortdesc = None
        # 注册时间
        try:
            registeryear = html.xpath('//div[@class="m-car-record__body--top"]/div[@class="item"][1]/p[1]/text()')[0] \
                .strip()
        except:
            registeryear = None
        # 里程
        try:
            mileage = \
                html.xpath('//div[@class="m-car-record__body--top"]/div[@class="item"][2]/p[@class="text"]/text()')[0] \
                    .strip()
        except:
            mileage = None
        # 排放标准
        try:
            emission = \
                html.xpath('//div[@class="m-car-record__body--top"]/div[@class="item"][3]/p[@class="text"]/text()')[0] \
                    .strip()
        except:
            emission = None
        # 过户次数
        try:
            change_times = info_dict['过户次数']
        except:
            change_times = None
        # 排量
        try:
            output = info_dict['排量']
        except:
            output = None
        # 城市归属地
        try:
            city = info_dict['车牌归属地']
        except:
            city = None
        # 变速箱类型
        try:
            geartype = info_dict['变速箱']
        except:
            geartype = None
        # 年检到期时间
        try:
            yearchecktime = info_dict['年检到期']
        except:
            yearchecktime = None
        # 车辆用途
        try:
            usage = info_dict['使用性质']
        except:
            usage = None
        # 交强险
        try:
            insurance1_date = info_dict['交强险到期']
        except:
            insurance1_date = None
        # 颜色
        try:
            color = info_dict['车身颜色']
        except:
            color = None
        # 出厂日期
        try:
            produceyear = info_dict['出厂日期']
        except:
            produceyear = None
        # 车源号
        try:
            statusplus = info_dict['车源号']
        except:
            statusplus = None
        # 钥匙
        try:
            keynumbers = info_dict['钥匙数量']
        except:
            keynumbers = None
        # 图片地址
        try:
            img_url = html.xpath(
                '//div[@class="m-car-banner__swiper-item swiper-slide swiper-slide-active"]/img[@class="m-car-banner__img"]/@src')
        except:
            img_url = None
        url = 'https://m.guazi.com/car-record/v2?clueId={}'.format(clue_id)

        yield scrapy.Request(url=url, callback=self.parse_parameter, dont_filter=True,
                             meta={
                                 'brand_name': brand_name,
                                 'family_name': family_name,
                                 'clue_id': clue_id,
                                 'guarantee': guarantee,
                                 'registeryear': registeryear,
                                 'mileage': mileage,
                                 'emission': emission,
                                 'change_times': change_times,
                                 'output': output,
                                 'city': city,
                                 'geartype': geartype,
                                 'yearchecktime': yearchecktime,
                                 'usage': usage,
                                 'insurance1_date': insurance1_date,
                                 'color': color,
                                 'produceyear': produceyear,
                                 'statusplus': statusplus,
                                 'keynumbers': keynumbers,
                                 'price1': price1,
                                 'shortdesc': shortdesc,
                                 'img_url': img_url,
                                 'car_level': car_level,
                             })

    def parse_parameter(self, response):
        item = {}
        brand_name = response.meta['brand_name']
        family_name = response.meta['family_name']
        clue_id = response.meta['clue_id']
        guarantee = response.meta['guarantee']
        registeryear = response.meta['registeryear']
        mileage = response.meta['mileage']
        emission = response.meta['emission']
        change_times = response.meta['change_times']
        output = response.meta['output']
        city = response.meta['city']
        geartype = response.meta['geartype']
        yearchecktime = response.meta['yearchecktime']
        usage = response.meta['usage']
        insurance1_date = response.meta['insurance1_date']
        color = response.meta['color']
        produceyear = response.meta['produceyear']
        statusplus = response.meta['statusplus']
        # keynumbers = response.meta['keynumbers']
        price1 = response.meta['price1']
        shortdesc = response.meta['shortdesc']
        img_url = response.meta['img_url']

        html = etree.HTML(str(response.body, encoding="utf-8"))
        parameter_dict = {}
        configures = html.xpath('//li[@class="list-item__body__row"]')
        for configure in configures:
            key_name1 = configure.xpath('./span[@class="list-item__body__row__title"]/text()')[0].strip()
            try:
                value_name1 = configure.xpath('./div[@class="list-item__body__row__content"]/text()')[0].strip()
            except:
                try:
                    value_name1 = configure.xpath('./div[@class="list-item__body__row__content"]/span/@class')[0] \
                        .replace('list-item__body__row__content--', '')
                except:
                    value_name1 = ''.join(
                        configure.xpath('./div[@class="list-item__body__row__content"]//text()')) \
                        .replace('\n', '').replace(
                        ' ', '')
            parameter_dict[key_name1] = value_name1
        conf_dict = self.settings.get("CONF_DICT")
        desc_list = []
        desc_ = ['电动天窗', '倒车雷达', '前排座椅加热', 'GPS导航', '倒车影像系统', '多功能方向盘', '全景天窗']
        for i in desc_:
            try:
                if parameter_dict[i]:
                    desc_list.append(i)
            except:
                continue
        for i in conf_dict.keys():
            try:
                item[i] = parameter_dict[conf_dict[i]]
            except:
                item[i] = None

        item['carid'] = clue_id
        item['car_source'] = 'guazi'
        item['grab_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item['update_time'] = None
        item['post_time'] = None
        item["sold_date"] = None
        item["pagetime"] = "zero"
        item["parsetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["shortdesc"] = shortdesc
        item["pagetitle"] = shortdesc
        item["url"] = response.url
        item["status"] = "sale"
        item["brand"] = brand_name
        item["series"] = family_name
        item['desc'] = '/'.join(desc_list)
        item["registeryear"] = registeryear
        item["output"] = output
        item["geartype"] = geartype
        item["registerdate"] = registeryear
        item["price1"] = price1
        item["mileage"] = mileage
        item["usage"] = usage
        item["color"] = color
        item["city"] = city
        item["guarantee"] = guarantee
        item["change_times"] = change_times
        item["insurance1_date"] = insurance1_date
        item["yearchecktime"] = yearchecktime
        item["img_url"] = img_url
        item["carno"] = city
        item["produceyear"] = produceyear
        item["statusplus"] = statusplus
        item["emission"] = emission
        item['level'] = response.meta['car_level']

        jiance_url = 'https://m.guazi.com/check-report/v2?clueId={}'.format(clue_id)
        yield scrapy.Request(url=jiance_url, callback=self.parse_jiance, meta={'item': item}, dont_filter=True)

    def parse_jiance(self, response):
        item = response.meta['item']
        html = etree.HTML(str(response.body, encoding="utf-8"))
        # 检测综述
        try:
            totalcheck_desc = html.xpath('//div[@class="serious-problem check-report-container__item"]'
                                         '/div[@class="item-header"]/div[@class="item-header__desc"]/text()')[0]
        except:
            totalcheck_desc = None
        item['totalcheck_desc'] = totalcheck_desc
        yield item
