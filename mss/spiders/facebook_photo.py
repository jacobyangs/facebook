# -*- coding: UTF-8 -*-
from scrapy.spider import CrawlSpider,Rule,Spider
from scrapy.linkextractor import LinkExtractor
from facebook_login import FacebookLogin
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy import Item, Field
import re

class FacebookPhotoItems(Item):
    name = Field()
    photo_links = Field()
class CrawlPhoto(FacebookLogin):
    name = 'fbphtot'
    timelint_photo = None
    def after_login(self, response):
        yield Request('https://m.facebook.com/RobertScoble/photos',callback=self.parse_item)
    def parse_item(self,response):
        # print response.body
        urls = response.xpath('//span').extract()
        for i in urls:
            if i.find(u'时间线照片')!=-1:
                self.timeline_photo = Selector(text=i).xpath('//span/a/@href').extract()[0]
        if self.timeline_photo is not None:
            yield Request('https://m.facebook.com/%s'%self.timeline_photo,callback=self.parse_photos)
    def parse_photos(self,response):
        urls = response.xpath("//a[@class=\'bw bx\']/@href").extract()
        # urls = response.xpath("//a[@class=\'_39pi _4i6j\']/@href").extract()
        for i in urls:
            yield Request('https://m.facebook.com/%s'%i,callback=self.process_photo_url)
        if len(urls) == 12:
            next_page = response.xpath('//div[@id=\'m_more_item\']/a/@href').extract()[0]
            yield Request('https://m.facebook.com/%s'%next_page,callback=self.parse_photos)
    def process_photo_url(self,response):
        # photo_url = response.xpath('//i[@class=\'img img\']').extract()
        item = FacebookPhotoItems()
        item['name'] = 'RobertScoble'
        photo_url = response.xpath('//div[@style=\'text-align:center;\']/img/@src').extract()[0]
        item['photo_links'] = photo_url
        yield item
    def wirtefile(self,str):
        with open('temp2.html','w') as file:
            file.write(str)
