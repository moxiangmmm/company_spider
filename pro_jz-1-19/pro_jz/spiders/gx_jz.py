# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import re

class GxJzSpider(scrapy.Spider):
    name = "gx_jz"
    allowed_domains = ["ztb.gxzjt.gov.cn:1121"]
    # http://ztb.gxzjt.gov.cn:1121/zjthy/HuiYuanInfoMis_JZ/BackEnd2/DanWeiInfo/DanWeiInfoChange_List2.aspx
    list_url = "http://ztb.gxzjt.gov.cn:1121/zjthy/HuiYuanInfoMis_JZ/BackEnd2/DanWeiInfo/DanWeiInfoChange_List2.aspx"
    custom_settings = {
        "ITEM_PIPELINES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item = {'page':1}
        yield scrapy.Request(
            self.list_url,
            meta={"item":item},
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])
        span_list = response.xpath("//span[@id='dd']")
        # print(response.body)
        for span in span_list:
            company_name = span.xpath(".//text()").extract_first().strip()
            print(company_name)
        html = response.body.decode()
        # with open('html_{}.html'.format(item["page"]), 'w') as f:
        #     f.write(html)
        if item["page"] == 1:
            try:
                __VIEWSTATE = response.xpath("//input[@id='__VIEWSTATE']/@value").extract()[0]
                __EVENTVALIDATION = response.xpath("//input[@id='__EVENTVALIDATION']/@value").extract()[0]

            except:
                __VIEWSTATE =''
                __EVENTVALIDATION=''

        else:
            try:
                __VIEWSTATE = re.findall(r'__VIEWSTATE\|(/w.*)\"',html)[0]
                __EVENTVALIDATION = re.findall(r'__EVENTVALIDATION\|(/w.*)\"', html)[0]
                __VIEWSTATE = __VIEWSTATE.split(",")[0]
                __EVENTVALIDATION = __EVENTVALIDATION.split(",")[0]

            except Exception as e:
                __VIEWSTATE=''
                __EVENTVALIDATION=''
        item["page"] += 1
        if item["page"] <= 696:
            yield scrapy.FormRequest(
                self.list_url,
                formdata={
                    "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1 | ctl00$ContentPlaceHolder1$Pager",
                    "ctl00$ContentPlaceHolder1$HidState": "0",
                    "ctl00$ContentPlaceHolder1$DDLXiaQu": "",
                    "ctl00$ContentPlaceHolder1$DDLDanWeiType":"",
                    "ctl00$ContentPlaceHolder1$txtDanWeiName":"",
                    "ctl00$ContentPlaceHolder1$Pager_input": str(item["page"]-1),
                    "__EVENTTARGET": "ctl00$ContentPlaceHolder1$Pager",
                    "__EVENTARGUMENT": str(item["page"]),
                    "__VIEWSTATE": __VIEWSTATE,
                    "__VIEWSTATEGENERATOR": "9FEC60E1",
                    "__EVENTVALIDATION": __EVENTVALIDATION,
                    "__ASYNCPOST": "true"
                },
                callback=self.parse,
                meta={"item":deepcopy(item)},
                dont_filter=True
            )





