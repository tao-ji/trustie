# -*- coding: utf-8 -*-  
import scrapy
import urlparse
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector

class TrustieSpider(scrapy.Spider):

  name = "Trustie"

  start_urls = ["https://www.trustie.net"]

  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

  def start_requests(self):
    return [Request("https://www.trustie.net/login", meta = {'cookiejar' : 2}, callback = self.post_login)]

  def post_login(self, response):      
    token = Selector(response).xpath('//input[@name="authenticity_token"]/@value').extract()[0]
    formadata = {
      'authenticity_token': token ,
      'username': '',
      'password': '',
      'autologin': '1'
    }
    return FormRequest.from_response(
      url='https://www.trustie.net/login/',
      meta={'cookiejar' : response.meta['cookiejar']},
      method="POST",
      headers=self.headers,
      response=response,
      formnumber=1,
      formdata=formadata,
      callback=self.after_login)

  def after_login(self, response):
    # check login succeed before going on
    if "user_manage_homeworks" not in response.body:
      self.logger.error("Login failed")
      return
    else:     
      hxs = HtmlXPathSelector(response)
      sites = hxs.select('//div/ul/div/li[3]/a/@href').extract()
      urls = []
      for site in sites:
        if site.find("boards") != -1 or site.find("news") != -1:
          yield Request(urlparse.urljoin('https://www.trustie.net', site), meta={'cookiejar': response.meta['cookiejar']}, headers=self.headers, callback=self.open_post)
  

  def open_post(self, response):
    token = Selector(response).xpath('//input[@name="authenticity_token"]/@value').extract()[0]
    print 'token:'+token
    journal_id = Selector(response).xpath('//input[@name="journal_id"]/@value').extract()[0]
    print 'journal_id:'+journal_id
    content = '赞'
    formadata = {
      'authenticity_token': token ,
      'jounal_id': journal_id,
      'content': content
    }
    return FormRequest.from_response(
      url= response.url + '/replies',
      meta = {'cookiejar' : response.meta['cookiejar']},
      method="POST",
      headers=self.headers,
      response=response,
      formnumber=1,
      formdata=formadata,
      callback=self.after_reply)

  def after_reply(sefl, reponse):
    print response.body
    if "" in response.body:
      self.logger.error("Reply failed")

