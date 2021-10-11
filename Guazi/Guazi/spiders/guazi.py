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
        '''
        第一页要取数据的解析 
        
        '''
        url = 'https://m.guazi.com/car-record/v2?clueId={}'.format(clue_id)
        yield scrapy.Request(url=url, callback=self.parse_parameter, dont_filter=True,
                             meta={
                                 'brand_name': brand_name,
                                 'family_name': family_name,
                                 'clue_id': clue_id,
                                 'guarantee': guarantee
                             })

    def parse_parameter(self, response):
        item = {}
        brand_name = response.meta['brand_name']
        family_name = response.meta['family_name']
        clue_id = response.meta['clue_id']
        guarantee = response.meta['guarantee']
        html = etree.HTML(str(response.body, encoding="utf-8"))
        parameter_dict = {}
        configures = html.xpath('//li[@class="list-item__body__row"]')
        for configure in configures:
            key_name1 = configure.xpath('./span[@class="list-item__body__row__title"]/text()')[0].strip()
            try:
                value_name1 = configure.xpath('./div[@class="list-item__body__row__content"]/text()')[0].strip()
            except:
                try:
                    value_name1 = configure.xpath('./div[@class="list-item__body__row__content"]/span/@class')[
                        0].replace('list-item__body__row__content--', '')
                except:
                    value_name1 = ''.join(
                        configure.xpath('./div[@class="list-item__body__row__content"]//text()')).replace('\n',
                                                                                                          '').replace(
                        ' ', '')
            parameter_dict[key_name1] = value_name1

        item['carid'] = clue_id
        item['car_source'] = 'guazi'
        update_time = None
