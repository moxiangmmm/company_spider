# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy


class HbJzSpider(scrapy.Spider):
    name = "hb_jz"
    allowed_domains = ["59.175.169.110"]
    list_url = "http://59.175.169.110/web/QyManage/QyList.aspx"
    custom_settings = {
        "ITEM_PIPELINES": None,
        # "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item = {"page":1}
        yield scrapy.Request(
            self.list_url,
            meta={"item":item},
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])
        td_list = response.xpath('//td[@align="center"]//a')
        # print(td_list)
        for td in td_list[0:19]:
            company_name = td.xpath(".//text()").extract_first("").strip()
            print(company_name)
            with open("/home/python/Desktop/company/hb_company.csv", 'a') as f:
                f.write(company_name + '\n')
        try:
            __VIEWSTATE = response.xpath("//input[@id='__VIEWSTATE']/@value").extract()[0]

            __EVENTVALIDATION = response.xpath("//input[@id='__EVENTVALIDATION']/@value").extract()[0]
        except:
            __VIEWSTATE = ''
            __EVENTVALIDATION = ''

        item["page"] += 1
        if item["page"] <= 613:
            yield scrapy.FormRequest(
                self.list_url,
                formdata={
                    "__EVENTTARGET": "lbtnNext",
                    "__EVENTARGUMENT": "",
                    "__VIEWSTATE":__VIEWSTATE,
                    "__EVENTVALIDATION":__EVENTVALIDATION,
                    "txtQymc": "",
                    "txtWydm": "",
                    "txtPageIndex": str(item["page"]),
                    "hfQylx": ""
                },
                meta={"item": deepcopy(item)},
                callback=self.parse,
                # dont_filter=True
            )