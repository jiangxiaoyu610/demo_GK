import scrapy
import os
from scrapy.http.request import Request
from tutorial.items import cninfoItem
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re

class cninfo_spider(scrapy.Spider):
    name = "cninfo"
    allowed_domains = ["cninfo.com.cn"]
    start_urls = ["http://www.cninfo.com.cn/cninfo-new/information/companylist"]

    '''
    def start_requests(self):
        yield  Request(self.url, callback=self.parse_url, dont_filter=True)
    '''
    def parse(self, response):
        linkdata = response.xpath('//ul[@class="company-list"]/li/a/@href').extract()[:100]

        for i in range(len(linkdata)):
            strlist = linkdata[i].split('?')
            tar_url = 'http://www.cninfo.com.cn/information/management/' + strlist[-1] + '.html'
            yield Request(tar_url, callback=self.parse_data, dont_filter=True)

    def parse_data(self, response):
        tddata = response.xpath('//div[@class="clear"]//tr/td/text()').extract()
        strlst = re.match(r'.*www.cninfo.com.cn/information/management/(.*)\.html', response.url)
        base_dir = os.getcwd()
        filename = base_dir + '/news.txt'

        for i in range(1, len(tddata)/5):
            item = cninfoItem()
            item['code'] = strlst.group(1)
            item['name'] = tddata[5*i].replace('\r\n','').strip()
            item['position'] = tddata[5*i+1].replace('\r\n','').strip()
            item['birthday'] = tddata[5*i+2].replace('\r\n','').strip()
            item['sex'] = tddata[5*i+3].replace('\r\n','').strip()
            item['edu'] = tddata[5*i+4].replace('\r\n','').strip()
            yield item

'''
            with open(filename, 'a') as f:
                f.write(item['code'] + '\n')
                f.write(item['name'] + '\n')
                f.write(item['position'] + '\n')
                f.write(item['birthday'] + '\n')
                f.write(item['sex'] + '\n')
                f.write(item['edu'] + '\n')
'''


