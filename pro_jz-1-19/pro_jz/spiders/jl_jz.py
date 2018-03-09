# -*- coding: utf-8 -*-
import scrapy
import time
import re
from copy import deepcopy


class JlJzSpider(scrapy.Spider):
    name = "jl_jz"
    allowed_domains = ["cx.jljsw.gov.cn"]

    # http://cx.jljsw.gov.cn/handle/NewHandler.ashx?method=SnCorpData&CorpName=&QualiType=&TradeID=&BoundID=&LevelID=&CityNum=&nPageIndex=1&nPageCount=261&nPageRowsCount=5205&nPageSize=20&_=1519444396004
    list_url = "http://cx.jljsw.gov.cn/handle/NewHandler.ashx?method=SnCorpData&CorpName=&QualiType=&TradeID=&BoundID=&LevelID=&CityNum=&nPageIndex={}&nPageCount=261&nPageRowsCount=5205&nPageSize=20&_={}"
    custom_settings = {
        "ITEM_PIPELINES": None,
        "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item={"page":1}
        nd = int(time.time()*1000)
        print(nd)
        list_url = self.list_url.format(item["page"],nd)
        yield scrapy.Request(
            list_url,
            dont_filter=True,
            meta={"item":item},
            callback=self.parse,
        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])
        # <td class=\"align_left company_name\" title=\"安图工程质量检测站\">
        # print(response.body.decode())
        json_html = response.body.decode()
        ret = re.findall(r'<td class=\\"align_left company_name\\" title=\\"(.*?)\\">', json_html)
        with open("/home/python/Desktop/company/jl_company.csv",'a') as f:
            for c in ret:
                print(c)
                f.write(c.strip()+'\n')

        item["page"] += 1
        if item["page"] <= 261:
            nd = int(time.time() * 1000)
            yield scrapy.FormRequest(
                self.list_url.format(item["page"],nd),
                meta={"item": deepcopy(item)},
                callback=self.parse,
            )



