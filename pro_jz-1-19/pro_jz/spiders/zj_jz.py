# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy


class ZjJzSpider(scrapy.Spider):
    name = "zj_jz"
    allowed_domains = ["115.29.2.37:8080"]
    list_url = "http://115.29.2.37:8080/enterprise_ajax.php"
    custom_settings = {
        "ITEM_PIPELINES": None,
        "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item = {"page":1}
        data = {
            "page": "",
            "CorpName": "",
            "APTITUDEKINDNAME": "",
            "CertID": "",
            "City": "",
            "EndDate": ""
        }
        yield scrapy.FormRequest(
            self.list_url,
            formdata=data,
            meta={"item": item},
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])
        # print(response.body.decode())
        tr_list = response.xpath('//div[@class="list_table"]/table//tr[@class="auto_h"]')
        for tr in tr_list:
            company_name = tr.xpath(".//td[2]//a/text()").extract_first('').strip()
            print(company_name)
            with  open("/home/python/Desktop/company/zj_company.csv",'a') as f:
                f.write(company_name+'\n')
        next_code = response.xpath("//div[@id='pagebar']/ul//li[3]/@alt").extract()[0]
        item["page"] += 1
        if item["page"] <= 973:
            yield scrapy.FormRequest(
                self.list_url,
                formdata={
                    "page": next_code,
                    "CorpName": "",
                    "APTITUDEKINDNAME": "",
                    "CertID": "",
                    "City": "",
                    "EndDate": ""
                },
                meta={"item":deepcopy(item)},
                callback=self.parse,
                dont_filter=True
            )

