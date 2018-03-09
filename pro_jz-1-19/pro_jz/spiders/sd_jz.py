# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json
import re

class SdJzSpider(scrapy.Spider):
    name = "sd_jz"
    allowed_domains = ["221.214.94.41:81"]
    list_url = "http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback=jQuery17106016717999327295_151961576078{}"
    custom_settings = {
        "ITEM_PIPELINES": None,
        "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item = {"page":1,"code":3}
        yield scrapy.FormRequest(
            self.list_url.format(item["code"]),
            formdata={
                "methodname": "GetCorpInfo",
                "CorpName": "",
                "CorpCode": "",
                "CertType": "",
                "LegalMan": "",
                "CurrPageIndex": str(item["page"]),
                "PageSize": "12"
            },
            meta={"item":item},
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode()
        # print(json_html)
        #jQuery17106016717999327295_1519615760786
        rule = r'_151961576078{}\((.*)\)'.format(item["code"])
        try:
            str_dic = re.findall(rule, json_html)[0]
            data_list = json.loads(str_dic)["data"]["CorpInfoList"]
            for data in data_list:
                company_name = data["CorpName"]
                print(company_name)
                with open("/home/python/Desktop/company/sd_company.csv",'a') as f:
                    f.write(company_name+'\n')
        except Exception as e:
            print("*"*10,str(e))

        item["page"] += 1
        item["code"] += 1
        if item["page"] <= 1748:
            yield scrapy.FormRequest(
                self.list_url.format(item["code"]),
                formdata={
                    "methodname": "GetCorpInfo",
                    "CorpName": "",
                    "CorpCode": "",
                    "CertType": "",
                    "LegalMan": "",
                    "CurrPageIndex": str(item["page"]),
                    "PageSize": "12"
                },
                meta={"item": item},
                callback=self.parse,
                dont_filter=True
            )
