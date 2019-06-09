# -*- coding: utf-8 -*-
import scrapy
from Search_Engine.items import SearchEngineItem
from  Search_Engine.utils.common import get_md5
from  scrapy.loader import ItemLoader
import logging
import time

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/page/255/']
    # #收集伯乐在线的url页面数以及
    # handle_httpstatus_list=[404]
    # def __init__(self):
    #     self.fail_urls=[]

    def parse(self, response):
       #向fail_urls里添加
       # if  response.status==404:
       #     self.fail_urls.append(response.url)
       #     self.crawler.stats.inc_value('failed_url')
       for   url  in response.xpath('//div[@class="grid-8"]/div[@class="post floated-thumb"]'):
              # front_image_url=url.xpath('.//div[@class="post-thumb"]/a/img/@src').extract()[0]
              url=url.xpath('.//div[@class="post-meta"]/p/a[@class="archive-title"]/@href').extract()[0]
              print(url)
              yield scrapy.Request(url,meta={'link_url':url},callback=self.parse_detail)
        #打印当前爬取的页数
       current_page = response.xpath('//div[@class="navigation margin-20"]/span[@class="page-numbers current"]/text()').extract()[0]
       print("当前正在爬取的是第%s:页" % current_page)
       #翻页
       next_url=response.xpath('//div[@class="navigation margin-20"]/a[@class="next page-numbers"]/@href').extract()[0]
       time.sleep(3)
       if next_url:
         yield scrapy.Request(next_url,callback=self.parse)


    def  parse_detail(self,response):
        # 通过item_loader加载item
        logging.warning("1"*100)
        logging.warning("异常")
        item_loader = ItemLoader(item=SearchEngineItem(), response=response)
        item_loader.add_value('link_url', response.meta['link_url'])
        # item_loader.add_value('front_image_url', [response.meta["front_image_url"]])
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_xpath('create_date', '//div[@class="entry-meta"]/p/text()')
        item_loader.add_xpath('tags', '//div[@class="entry-meta"]/p/a/text()')
        # 问题  这个xpath仅能匹配有收藏数的,若收藏数为0则xpath报错
        item_loader.add_xpath('praise_num', '//div[@class="post-adds"]/span/h10/text()')
        item_loader.add_xpath('fav_num', '//div[@class="post-adds"]/span[2]/text()')
        item_loader.add_xpath('comment_num', '//div[@class="post-adds"]/a/span/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]//p/text()')

        article_item = item_loader.load_item()

        yield article_item
