import random,base64
from mss.settings import PROXIES
class ProxyMiddleware(object):
  def process_request(self, request, spider):
    proxy = random.choice(PROXIES)
    request.meta['proxy'] = "http://%s" % proxy['ip_port']


class PrintUrlMiddleware(object):
    def process_response(self, request, response, spider):
        print request.url + '-----------request'
        return response
