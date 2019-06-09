# -*- coding: utf-8 -*-
__author__="hq"

from  scrapy.cmdline import execute
import sys
import os

print(os.path.dirname(os.path.abspath(__file__)))#获取Article的路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy','crawl','jobbole'])
# execute(['scrapy','crawl','lagou'])