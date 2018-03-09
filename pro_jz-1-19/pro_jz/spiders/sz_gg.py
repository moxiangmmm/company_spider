# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json

class SzGgSpider(scrapy.Spider):
    name = 'sz_gg'
    allowed_domains = ['szjsjy.com.cn','www.szjsjy.com.cn']
    custom_settings = {
    "ITEM_PIPELINES" :None,
    "DOWNLOADER_MIDDLEWARES": None,

    # "LOG_FILE": "./sz_gg_scrapy.log",
    # "LOG_LEVEL": "WARNING",
    }

    start_urls = ['http://szjsjy.com.cn/']
    zhaobiao_list = "https://www.szjsjy.com.cn:8001/jyw/queryGongGaoListJuNew.do"
    #                https://www.szjsjy.com.cn:8001/jyw/showGongGao.do?ggGuid=c9b85b6b-8631-4260-8150-c4d937b6f389
    zhaobiao_detail = "https://www.szjsjy.com.cn:8001/jyw/showGongGao.do?ggGuid={}"
    zhongbiao_list = "https://www.szjsjy.com.cn:8001/jyw/queryZBJieGuoListJuNew.do"



    def start_requests(self):
        item = {}
        item["page"] = 1
        yield scrapy.FormRequest(
            self.zhaobiao_list,
            formdata={
                "page": str(item["page"]),
                "rows": "15"
            },
            meta={"item": deepcopy(item)},
            callback=self.parse
        )


    def parse(self, response):
        # 取出关键字段
        item = deepcopy(response.meta["item"])
        json_str = response.body.decode()
        json_dic = json.loads(json_str)
        total = json_dic["total"]
        dic_list = json_dic["rows"]
        for dic in dic_list:
            item["pro_id"] = dic["ggGuid"]
            item["zbr"] = dic["zbRName"]
            # 请求详情页主页面
            print(dic)
            # yield scrapy.FormRequest(
            #     self.zhaobiao_detail.format(item["pro_id"]),
            #     formdata={"ggGuid":item["pro_id"]},
            #     meta={"item": deepcopy(item)},
            #     callback=self.main_parse
            # )

        page = item["page"] + 1

        if page <= total / 100 + 1:
            item["page"] = page
            yield scrapy.FormRequest(
                self.zhaobiao_list,
                formdata={
                    "page": str(item["page"]),
                    "rows": "15"
                },
                meta={"item": deepcopy(item)},
                callback=self.parse
            )
        else:
            yield item

    # 项目详情页
    def main_parse(self, response):
        item = deepcopy(response.meta["item"])
        json_str = response.body.decode()
        print("*"*20,json_str)
        json_dic = json.loads(json_str)
        item["pro_item"] = json_dic["html"]
        print("+" * 20, item)
        yield item

    # 中标项目详情
    def z_b_parse(self, response):
        item = deepcopy(response.meta["item"])
        json_str = response.body.decode()
        json_dic = json.loads(json_str)
        item["pro_item"] = json_dic["html"]
        print("+" * 20, item)
        yield item
