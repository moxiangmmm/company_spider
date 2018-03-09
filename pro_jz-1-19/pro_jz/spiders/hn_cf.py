# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import re
# 先爬河南公司的资质
# 企业信息部分分类可以访问
# 一页20家公司，按理说爬完应该有4000家，为什么只有两千家

class HnCfSpider(scrapy.Spider):
    name = 'hn_cf'
    allowed_domains = ['hnjs.net.cn','http://www.hnjs.net.cn/']
    # start_urls = ['http://hnjs.net.cn/']
    custom_settings = {
        # "ITEM_PIPELINES":None,
        "LOG_FILE": './hn_cf_scrapy.log',
        "LOG_LEVEL": "WARNING",
        "DOWNLOAD_DELAY":2,
        "DOWNLOADER_MIDDLEWARES":None
    }
    list_url = "http://www.hnjs.net.cn/qualification{}.shtml?page={}"
    main_url = "http://www.hnjs.net.cn/qualificationDetail.aspx?qymc={}"
    type_list = [{"房地产开发企业资质": "105"}, {"建设工程勘察设计企业资质": "118"}, {"建设工程造价咨询企业资质": "13"}, {"城市园林绿化企业资质": "40"}]


    # 燃气公司页面规则不一样
    # "建筑业企业资质""监理企业资质", "质量检测机构资质", "安全生产许可证资质", "招标代理机构资格资质","施工图审查机构资质", "劳务企业资质",页面规则不一样
    def start_requests(self):
        for type in self.type_list:
            print("+"*20,type)
            for key, value in type.items():
                item = {}
                item["type"] = key
                item["page"] = 1
                item["t_page"] = value
                yield scrapy.Request(
                    self.list_url.format(key, item["page"]),
                    meta={"item": deepcopy(item)},
                    callback=self.parse
                )

    #
    def parse(self, response):
        # 取出关键字段
        item = deepcopy(response.meta["item"])
        tr_list = response.xpath("//table//tr")
        for tr in tr_list:
            item["company"] = tr.xpath(".//td[1]/a/text()").extract_first() # 公司名称
            item["cf_code"] = tr.xpath(".//td[2]/text()").extract_first() # 证书编号
            # print(item)
            # 请求详情页主页面
            yield scrapy.Request(
                self.main_url.format(item["company"]),
                meta={"item": deepcopy(item)},
                callback=self.main_parse
            )

        page = item["page"] + 1

        # 先尝试在item中取出总页码，如果没有再从网页中获取这样能减少出错的几率
        t_page = int(item["t_page"])

        if page <= t_page:
            item["page"] = page
            yield scrapy.Request(
                self.list_url.format(item["type"], item["page"]),
                meta={"item": deepcopy(item)},
                callback=self.parse
            )
        else:
            yield item

    # 详情页
    def main_parse(self, response):
        item = deepcopy(response.meta["item"])
        text_list = response.xpath("//table//text()").extract()
        d_list = []
        for text in text_list:
            t = text.strip()
            if t:
                d_list.append(t)
        item["d_list"] = d_list
        print(item)
        yield item



        # 证书类别
        # 证书标号
        # 注册地址
        # 资质等级
        # 法定代表人
        # 公司类型
        # 批准从事经营时间
        # 营业执照注册号
        # 实收资本
        # 开始时间
        # 结束时间
        # 发证机构
