# -*- coding: UTF-8 -*-
import re
from urlparse import urljoin

from scrapy import Item, Field
from scrapy.http import Request
from scrapy.selector import Selector

from facebook_login import FacebookLogin


class FacebookItems(Item):
    id = Field()
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
        "plok74122", "bear.black.12","tabaco.wang","chaolin.chang.q","ahsien.liu","kaiwen.cheng.100","liang.kevin.92","bingheng.tsai.9","psppupu",
                  'cscgbakery',"hc.shiao.l","asusisbad","benjamin","franklin",
        # 'RobertScoble'
    ]
                  # "https://m.facebook.com/tabaco.wang?v=info",'https://m.facebook.com/RobertScoble?v=info']

    def after_login(self, response):
        for id in self.start_ids:
            url = "https://m.facebook.com/%s?v=info" %id
            yield Request(url, callback=self.parse_profile,meta={"id":id})

    def parse_profile(self, response):
        item = FacebookItems()

        item['id'] = response.meta['id']
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

        yield item


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
