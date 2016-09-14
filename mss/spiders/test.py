# -*- coding: UTF-8 -*-
import re,HTMLParser
def getMatch(patten, str):
    match = re.search(patten, str)
    while(match):
            print match.group()
def handle_starttag(self, tag, attrs):
    if tag == 'a':
      for name,value in attrs:
        if name == 'href':
          print value
if __name__ == '__main__':
    str = '<span class="cp"><a href="/RobertScoble/albums/458123019654/">时间线照片</a></span>'
    print str.find('458123019654')

