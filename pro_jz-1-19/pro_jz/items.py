# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProJzItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company = scrapy.Field() # 公司名称
    company_id = scrapy.Field() # 公司代号
    org_code = scrapy.Field() # 组织机构代码
    type = scrapy.Field() # 公司类型
    c_date = scrapy.Field() # 成立日期
    add = scrapy.Field() # 注册地址
    capital = scrapy.Field() # 注册资金
    licence_code = scrapy.Field() # 营业执照代码
    leader = scrapy.Field() # 法人
    s_date = scrapy.Field() # 年检有效期
    scope = scrapy.Field() # 经营范围
    cf_list = scrapy.Field() # 资质列表
    cf_page = scrapy.Field() # 资质页码
    pe_list = scrapy.Field() # 人员列表
    pe_page = scrapy.Field() # 人员页码
    pro_list = scrapy.Field() # 项目列表
    pro_page = scrapy.Field() # 项目页









