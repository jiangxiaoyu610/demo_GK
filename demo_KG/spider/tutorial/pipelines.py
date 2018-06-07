# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class TutorialPipeline(object):
    def process_item(self, item, spider):
        base_dir = os.getcwd()
        filename = base_dir + '/news.txt'

        with open(filename, 'a') as f:
            f.write(item['code'] + '\n')
            f.write(item['name'] + '\n')
            f.write(item['position'] + '\n')
            f.write(item['birthday'] + '\n')
            f.write(item['sex'] + '\n')
            f.write(item['edu'] + '\n')

        return item
