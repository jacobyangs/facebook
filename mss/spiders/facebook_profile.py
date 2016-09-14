# -*- coding: UTF-8 -*-
import re
from urlparse import urljoin

from scrapy import Item, Field
from scrapy.http import Request
from scrapy.selector import Selector

from facebook_login import FacebookLogin


class FacebookItems(Item):
    url = Field()
    name = Field()
    work = Field()
    education = Field()
    family = Field()
    skills = Field()
    address = Field()
    contact_info = Field()
    basic_info = Field()
    bio = Field()
    quote = Field()
    nicknames = Field()
    relationship = Field()
    image_urls = Field()

class FacebookProfile(FacebookLogin):
    download_delay = 2
    name = "fb"
    links = None
    start_ids = [
        "plok74122", "bear.black.12","tabaco.wang","chaolin.chang.q","ashien.liu","liang.kevin.92","bingheng.tsai.9","psppupu",
                  'cscgbakery',"hc.shiao.l","asusisbad","benjamin","franklin",
        'RobertScoble']
                  # "https://m.facebook.com/tabaco.wang?v=info",'https://m.facebook.com/RobertScoble?v=info']

    def after_login(self, response):
        for url in self.start_ids:
            url = "https://m.facebook.com/%s?v=info" %url
            yield Request(url, callback=self.parse_profile)

    def parse_profile(self, response):
        item = FacebookItems()
        item['url'] = response.url
        item["name"] = "".join(response.css('#root strong *::text').extract())

        item["work"] = self.parse_info_has_image(response, response.css('#work'))
        item["education"] = self.parse_info_has_image(response, response.css('#education'))
        item["family"] = self.parse_info_has_image(response, response.css('#family'))

        item["address"] = self.parse_info_has_table(response.css('#living'))
        item["contact_info"] = self.parse_info_has_table(response.css('#contact-info'))
        item["basic_info"] = self.parse_info_has_table(response.css('#basic-info'))
        item["nicknames"] = self.parse_info_has_table(response.css('#nicknames'))

        item["skills"] = self.parse_info_text_only(response.css('#skills'))
        item["bio"] = self.parse_info_text_only(response.css('#bio'))
        item["quote"] = self.parse_info_text_only(response.css('#quote'))
        item["relationship"] = self.parse_info_text_only(response.css('#relationship'))
        # item['image_urls'] = ['http://img5.cache.netease.com/photo/0001/2016-09-13/C0QTSIEB3R710001.jpg']
        # https://m.facebook.com/RobertScoble/photos
        request1 = Request('https://www.facebook.com/%s/photos'%item['url'].split('?')[0].split('/')[-1],callback=self.parse_image_url,dont_filter=True)
        request1.meta['item'] = item
        return request1

        # yield item
    def parse_image_url(self,response):
        item = response.meta['item']
        urls = response.xpath('//span').extract()
        for i in urls:
            if i.find(u'时间线照片') != -1:
                self.timeline_photo = Selector(text=i).xpath('//span/a/@href').extract()[0]
        if self.timeline_photo is not None:
            request2 =  Request('https://m.facebook.com/%s' % self.timeline_photo, callback=self.parse_photos)
        request2.meta['item'] = item
        return request2
    def parse_photos(self,response):
        item = response.meta['item']
        urls = response.xpath("//a[@class=\'bw bx\']/@href").extract()
        for i in urls:
            yield Request('https://m.facebook.com/%s'%i,callback=self.process_photo_url)
        if len(urls) == 12:
            next_page = response.xpath('//div[@id=\'m_more_item\']/a/@href').extract()[0]
            yield Request('https://m.facebook.com/%s'%next_page,callback=self.parse_photos)

    def process_photo_url(self, response):
        photo_url = response.xpath('//div[@style=\'text-align:center;\']/img/@src').extract()[0]

    def parse_info_has_image(self, response, css_path):
        info_list = []
        for div in css_path.xpath('div/div[2]/div'):
            url = urljoin(response.url, "".join(div.css('div > a::attr(href)').extract()))
            title = "".join(div.css('div').xpath('span | h3').xpath('a/text()').extract())
            info = "\n".join(div.css('div').xpath('span | h3').xpath('text()').extract())
            if url and title and info:
                info_list.append({"url": url, "title": title, "info": info})
        return info_list

    def parse_info_has_table(self, css_path):
        info_dict = {}
        for div in css_path.xpath('div/div[2]/div'):
            key = "".join(div.css('td:first-child div').xpath('span | span/span[1]').xpath('text()').extract())
            value = "".join(div.css('td:last-child').xpath('div//text()').extract()).strip()
            if key and value:
                if key in info_dict:
                    info_dict[key] += ", %s" % value
                else:
                    info_dict[key] = value
        return info_dict

    def parse_info_text_only(self, css_path):
        text = css_path.xpath('div/div[2]//text()').extract()
        text = [t.strip() for t in text]
        text = [t for t in text if re.search('\w+', t) and t != "Edit"]
        return "\n".join(text)
