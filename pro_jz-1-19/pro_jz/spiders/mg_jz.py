# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json


class MgJzSpider(scrapy.Spider):
    name = 'mg_jz'
    allowed_domains = ['http://110.16.70.26/','110.16.70.26']
    # http://110.16.70.26/nmjgpublisher/handle/ProjectsInfoHandler.ashx?type=CorpInfo
    list_url = "http://110.16.70.26/nmjgpublisher/handle/ProjectsInfoHandler.ashx?type=CorpInfo"
    custom_settings = {
        "ITEM_PIPELINES": None,
        # "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }


    def start_requests(self):
        item = {"page":1}
        yield scrapy.FormRequest(
            self.list_url,
            dont_filter=True,
            formdata={
            "lblPageCount": "31",
            "lblPageIndex": str(item["page"]),
            "lblRowsCount": "617",
            "lblPageSize": "20",
            "CorpName": "",
            "Zzlx": "",
            "CertNum": "",
            "City": ""
            },
            callback= self.parse,
            meta={"item":item},

        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode('gbk')
        json_dic = json.loads(json_html)["datainfo"]
        for info in json_dic:
            company_name = info["CorpName"]
            print(company_name)
            with open("/home/python/Desktop/company/mg_company.csv",'a') as f:
                f.write(company_name+'\n')
        item["page"]+=1
        if item["page"] <= 617:
            print("*"*10,str(item["page"]))
            yield scrapy.FormRequest(
                self.list_url,
                meta={"item":deepcopy(item)},
                callback=self.parse,
                formdata={
                "lblPageCount": "31",
                "lblPageIndex": str(item["page"]),
                "lblRowsCount": "617",
                "lblPageSize": "20",
                "CorpName": "",
                "Zzlx": "",
                "CertNum": "",
                "City": ""
                },
                dont_filter=True
            )






