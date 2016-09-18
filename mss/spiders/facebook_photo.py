# -*- coding: UTF-8 -*-
from scrapy.spider import CrawlSpider,Rule,Spider
from scrapy.linkextractor import LinkExtractor
from facebook_login import FacebookLogin
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy import Item, Field
import re,hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class FacebookPhotoItems(Item):
    url = Field()
    id = Field()
    photo_links = Field()
    md5 = Field()
class CrawlPhoto(FacebookLogin):
    name = 'fbphoto'
    timelint_photo = None
    id = None
    links = []
    start_ids = [
        "plok74122", "bear.black.12", "tabaco.wang", "chaolin.chang.q",
        # "ashien.liu",
        "liang.kevin.92","qia.chen",
        "bingheng.tsai.9", "psppupu",
        'cscgbakery', "hc.shiao.l", "asusisbad", "benjamin", "franklin",
        # 'RobertScoble'
    ]

    def after_login(self, response):
        for url in self.start_ids:
            yield Request('https://m.facebook.com/%s/photos'%url,callback=self.parse_item,meta={"id":url})
        # yield Request('https://m.facebook.com/%s/photos'%self.id,callback=self.parse_item)
    def parse_item(self,response):
        # print response.body
        urls = response.xpath('//span').extract()
        next_page = None
        try:
            next_page = response.xpath('//div[@class=\'co\']/a/@href').extract()[0].strip()
        except:
            pass
        # urls = response.xpath('//div[@data-sigil=\'marea\']').extract()
        for i in urls:
            # if i.find(u'时间线照片')!=-1:
            try:
                self.timeline_photo = Selector(text=i).xpath('//span/a/@href').extract()[0]
                if self.timeline_photo is not None:
                    yield Request('https://m.facebook.com/%s'%self.timeline_photo,callback=self.parse_photos,meta=response.meta)
            except:
                continue
        if next_page:
            print '-----------------------next image page -----------------------------------------'
            yield Request('https://m.facebook.com/%s'%next_page,callback=self.parse_item,meta=response.meta)
    def parse_photos(self,response):
        urls = response.xpath("//a[@class=\'bw bx\']/@href").extract()
        # urls = response.xpath("//a[@class=\'_39pi _4i6j\']/@href").extract()
        for i in urls:
            yield Request('https://m.facebook.com/%s'%i,callback=self.process_photo_url,meta=response.meta)
        if len(urls) == 12:
            next_page = response.xpath('//div[@id=\'m_more_item\']/a/@href').extract()[0]
            yield Request('https://m.facebook.com/%s'%next_page,callback=self.parse_photos,meta=response.meta)
    def process_photo_url(self,response):
        # photo_url = response.xpath('//i[@class=\'img img\']').extract()
        item = FacebookPhotoItems()
        item['url'] = response.url
        item['id'] = response.meta['id']
        photo_url = response.xpath('//div[@style=\'text-align:center;\']/img/@src').extract()[0]
        item['photo_links'] = photo_url
        item['md5'] = self.getstr_md5(item['photo_links'])+".jpg"
        yield item

    def wirtefile(self,str):
        with open('temp2.html','w') as file:
            file.write(str)
            file.write('\n')

    def getstr_md5(self, input):
        if input is None:
            input = ''
        md = hashlib.md5()
        md.update(input)
        return md.hexdigest()
