# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import datetime
from Search_Engine.models.es_article_types import ArticType
from w3lib.html import remove_tags
from elasticsearch_dsl.connections import connections

# es=connections.create_connection(ArticType._doc_type.using)

# def get_suggest(index,info_tuple):
#     #根据字符串生成搜索数据
#     used_word=set()#加入在title中有"python" 而在tags中也有"python"但是他们权重不一样,但是权重比较高的分析到了python,tags中的就忽略,
#     suggest=[]
#     for text,weight  in info_tuple:
#         if text:
#             #调用es的analyer接口分析字符串
#             words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
#             anylyed_words=set([r["token"]  for r  in words["tokens"] if  len(r["token"])>1])
#             new_words=anylyed_words-used_word
#         else:
#             new_words=set()
#         if new_words:
#             suggest.append({"input":list(new_words),"weigth":weight})
#     return suggest
def gen_suggest(index, info_tuple):
    # 根据字符串生成搜索建议数组
    """
    此函数主要用于,连接elasticsearch(搜索引擎)，使用ik_max_word分词器，将传入的字符串进行分词，返回分词后的结果
    此函数需要两个参数：
    第一个参数：要调用elasticsearch(搜索引擎)分词的索引index，一般是（索引操作类._doc_type.index）
    第二个参数：是一个元组，元祖的元素也是元组，元素元祖里有两个值一个是要分词的字符串，第二个是分词的权重，多个分词传多个元祖如下
    书写格式：
    gen_suggest(lagouType._doc_type.index, (('字符串', 10),('字符串', 8)))
    """# 连接elasticsearch(搜索引擎)，使用操作搜索引擎的类下面的_doc_type.using连接
    es = connections.create_connection(ArticType._doc_type.using)
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串，
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})
    return suggests

def item_create_date(value):
    try:
        create_data = datetime.datetime.strptime(value, "%Y/%m/%/%d").date()
    except Exception as e:
        create_data = datetime.datetime.now().date()
    return create_data


def get_praise_num(value):
    if len(value[0].strip()) == 0 or value is None:
        value = 0
    else:
        value = value
    return value


def get_num(value):
    strip_1 = value.strip()
    split_2 = strip_1.split(" ")
    split_3 = split_2[0]
    if not split_3.isdigit():
        return "0"
    print(split_3)
    return split_3


def remove_comment(value):
    if '评论' in value:
        return ''
    else:
        return value

class SearchEngineItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field(
        output_processor=TakeFirst()
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(item_create_date),
        output_processor=TakeFirst()
    )
    link_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    url_object_id = scrapy.Field(
        output_processor=TakeFirst()
    )
    # front_image_url = scrapy.Field(
    #
    # )
    # front_image_path = scrapy.Field(
    #     output_processor=TakeFirst()
    # )
    # 点赞数
    praise_num = scrapy.Field(
        input_processor=MapCompose(get_praise_num),
        output_processor=TakeFirst()
    )
    # 评论数
    comment_num = scrapy.Field(
        input_processor=MapCompose(get_num),
        output_processor=TakeFirst()
    )
    # 收藏数
    fav_num = scrapy.Field(
        input_processor=MapCompose(get_num),
        output_processor=TakeFirst()
    )
    # 标签
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment),
        output_processor=Join(',')
    )
    content = scrapy.Field(
        input_processor=Join(','),
        output_processor=TakeFirst()
    )  # 内容
    def save_artic_to_es(self):
        article = ArticType()
        article.title = self['title']
        article.create_date = self['create_date']
        article.content = remove_tags(self['content'])
        # article.front_image_url = self['front_image_url']
        # if "front_image_path" in self:
        #     article.front_image_path = self['front_image_path']
        # article.front_image_path = self['front_image_path']
        try:
            article.praise_num= self['praise_num']
        except:
            article.praise_num=0
        article.fav_num = self['fav_num']
        article.comment_num = self['comment_num']
        article.link_url = self['link_url']
        article.tags = self['tags']
        article.meta.id = self['url_object_id']
        # 搜索建议
        article.suggest=gen_suggest(ArticType._doc_type.index,((article.title,10),(article.tags,7)))

        article.save()
        return