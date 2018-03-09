# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy


class Ah2JzSpider(scrapy.Spider):
    name = "ah2_jz"
    allowed_domains = ["www"]
    list_url = "http://www.ahgcjs.com.cn:3318/pub/query/outComp/outCompList/ALL/131120164101727004"
    custom_settings = {
        "ITEM_PIPELINES": None,
        "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item = {"page":1}
        yield scrapy.FormRequest(
            self.list_url,
            formdata={
            "$total": "7827",
            "$pgsz": "15",
            "$pg": str(item["page"]),
            "$reload": "0"
            },
            meta={"item": deepcopy(item)},
            callback=self.parse,
            dont_filter=True
        )


    def parse(self, response):
        item = deepcopy(response.meta["item"])
        a_list = response.xpath("//a[@class='actbar-btn']")
        print(a_list)
        for a in a_list:
            company_name = a.xpath(".//text()").extract_first('').strip()
            print(company_name)
            with open("/home/python/Desktop/company/ah_company.csv", 'a') as f:
                f.write(company_name + '\n')
        item["page"] += 1
        if item["page"] <= 522:
            yield scrapy.FormRequest(
                self.list_url,
                meta={"item": deepcopy(item)},
                callback=self.parse,
                formdata={
                    "$total": "7827",
                    "$pgsz": "15",
                    "$pg": str(item["page"]),
                    "$reload": "0"
                },
                dont_filter=True
            )

