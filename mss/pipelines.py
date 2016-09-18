# -*- coding: utf-8 -*-


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json,codecs,os
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.http import Request
from scrapy.exceptions import DropItem

class MssPipeline(object):
    def process_item(self, item, spider):
        return item

class JSONPipeline(object):
    def __init__(self):
        self.file = codecs.open('demo_out.html', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=True) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self):
        self.file.close()


class MyImagesPipeline(ImagesPipeline):
    def file_path(self,request, response=None, info=None):
        image_guid = request.url.split('/')[-1]
        return 'full/%s' % (image_guid)

    def get_media_requests(self, item, info):
        # for image_url in item['photo_links']:
        #     yield Request(image_url)
        yield Request(item['photo_links'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item
class MyImagesPipeline1(ImagesPipeline):

    def get_media_requests(self, item, info):
        yield Request(item['photo_links'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        print image_paths
        print '======================path================='
        item['image_paths'] = item['id']+'/'+image_paths[0]
        return item
class MyOwenImageDownload(object):
    def process_item(self, item,spider):
        if len(item) >6:
            pass
        else:
            file = "image/"+item['id']
            if os.path.exists(file):
                pass
            else:
                os.makedirs(file)
            cmd = 'wget \'%s\' -O %s -P %s --timeout=10 -q'%(item['photo_links'],file+"/"+item['md5'],file)
            os.system(cmd)
        return item