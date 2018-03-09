# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json


class SzProSpider(scrapy.Spider):
    name = 'sz_pro'
    custom_settings = {
        # "ITEM_PIPELINES": {'pro_jz.pipelines.Szjz_Pipeline': 300},
    # "LOG_FILE" : "./sz_pro_scrapy.log",
    # "LOG_LEVEL" : "WARNING",
    # "ITEM_PIPELINES": None,
    "DOWNLOADER_MIDDLEWARES": None,
    "DOWNLOAD_DELAY" :3
    }

    allowed_domains = ['projreg.szjs.gov.cn']
    start_urls = ['http://peojreg.szjs.gov.cn/']
    list_url = "http://projreg.szjs.gov.cn/web/webService/getProjectList1.json"
    main_url = "http://projreg.szjs.gov.cn/web/webService/getProjectInfo.json"
    eng_main = "http://projreg.szjs.gov.cn/web/webService/getEngInfo.json"
    eng_list = "http://projreg.szjs.gov.cn/web/webService/getEngList1.json"

    def start_requests(self):
        item = {}
        item["page"] = 1
        yield scrapy.FormRequest(
            self.eng_list,
            formdata={
                "limit": "10",
                "offset": "0",
                "pageNumber": str(item["page"]),
                "engname": ""
            },
            meta={"item": deepcopy(item)},
            callback=self.parse
        )

    # 列表页
    def parse(self, response):
        # 取出关键字段
        item = deepcopy(response.meta["item"])
        json_str = response.body.decode()
        json_dic = json.loads(json_str)
        total = json_dic["total"]
        dic_list = json_dic["rows"]
        for dic in dic_list:
            item["pro_id"] = dic["id"]
            item["company"] = dic["constructionunit"]
            # 请求详情页主页面
            yield scrapy.FormRequest(
                self.eng_main,
                formdata={"id": item["pro_id"]},
                meta={"item": deepcopy(item)},
                callback=self.main_parse
            )

        page = item["page"] + 1

        if page <= total/100 + 1:
            item["page"] = page
            yield scrapy.FormRequest(
                self.list_url,
                formdata={
                    "limit": "10",
                    "offset": "0",
                    "pageNumber": str(item["page"]),
                    "engname": ""
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
        json_dic = json.loads(json_str)
        item["pro_item"] = json_dic
        print("+"*20, item)
        # yield item





