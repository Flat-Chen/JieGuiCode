import scrapy


class QidianSpider(scrapy.Spider):
    name = 'qidian'
    allowed_domains = ['www.qidian.com']
    start_urls = ['https://www.qidian.com/rank/yuepiao/']

    def __init__(self):
        self.page = 1

    def parse(self, response):
        self.page = self.page + 1
        page_first_name = response.xpath('//*[@id="book-img-text"]/ul/li[1]/div[2]/h4/a/text()').extract_first()
        print(page_first_name)
        next_url = 'https://www.qidian.com/rank/yuepiao/page{}/'.format(self.page)
        if self.page < 6:
            yield scrapy.Request(url=next_url, callback=self.parse)
