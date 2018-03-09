# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import re


class LnJzSpider(scrapy.Spider):
    name = "ln_jz"
    allowed_domains = ["218.60.144.163"]
    list_url = 'http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx'
    custom_settings = {
        "ITEM_PIPELINES": None,
        "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item = {"page":1}
        yield scrapy.Request(
            self.list_url,
            dont_filter=True,
            callback=self.parse,
            meta={"item":item}
        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])
        tr_list = response.xpath("//div[@id='div_outCast']//tbody//tr")
        for tr in tr_list:
            c = tr.xpath(".//td[2]//text()").extract_first()
            company_name = c.strip()
            print(company_name)
            with open("/home/python/Desktop/company/ln_company.csv",'a') as f:
                f.write(company_name+'\n')
        __VIEWSTATE_list = response.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        __EVENTVALIDATION_list = response.xpath("//input[@id='__EVENTVALIDATION']/@value").extract()
        __VIEWSTATE = __VIEWSTATE_list[0] if __VIEWSTATE_list else ''
        __EVENTVALIDATION = __EVENTVALIDATION_list[0] if __EVENTVALIDATION_list else ''

        item["page"] += 1
        if item["page"] <= 527:
            yield scrapy.FormRequest(
                self.list_url,
                meta={"item": deepcopy(item)},
                callback=self.parse,
                formdata={
                    "__EVENTTARGET": "Linkbutton5",
                    "__EVENTARGUMENT": "",
                    "__VIEWSTATE": __VIEWSTATE,
                    "__EVENTVALIDATION": __EVENTVALIDATION,
                    "hidd_type": "1",
                    "txtCorpName": "",
                    "ddlZzlx": "",
                    "txtFOrgCode": "",
                    "txtCertNum": "",
                    "newpage": str(item["page"]),
                    "newpage1": ""
                }
            )
