# -*- coding:utf-8 -*-
from  datetime import datetime
from elasticsearch_dsl import DocType,Date,Nested,Boolean,\
    analyzer,Completion,Text,Keyword,Integer,tokenizer
from elasticsearch_dsl.connections import connections

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer


connections.create_connection(hosts=["localhost"])

#使用Completion字段必须重写这个类,防止报错
class CustomAnalyzer(_CustomAnalyzer):                                      # 自定义CustomAnalyzer类，来重写CustomAnalyzer类

    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

#映射数据类型
class  ArticType(DocType):
    suggest=Completion(analyzer=ik_analyzer)#搜索建议自动补全的功能

    title = Text(analyzer="ik_max_word")
    create_date = Date()
    link_url =  Keyword()#不分析
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path =Keyword()
    # 点赞数
    praise_num = Integer()
    # 评论数
    comment_num = Integer()
    # 收藏数
    fav_num = Integer()
    # 标签
    tags = Text(analyzer="ik_max_word")
    # 内容
    content =Text(analyzer="ik_max_word")
    class Meta:
         index="jobbole"
         doc_type='article'
if __name__ == '__main__':
    ArticType.init()