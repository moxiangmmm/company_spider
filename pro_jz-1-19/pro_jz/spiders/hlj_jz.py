# -*- coding: utf-8 -*-
import scrapy
import random
from copy import deepcopy
import json

class HljJzSpider(scrapy.Spider):
    name = "hlj_jz"
    allowed_domains = ["ztb.hljjs.gov.cn"]
    # start_urls = ['http://www/']
    # http://ztb.hljjs.gov.cn/showbid_tzs.aspx?FID=FE7ED7AA-4B9D-42F9-803C-C5F1D8BD2137
    list_url = 'http://ztb.hljjs.gov.cn/ajaxtools.ashx'
    custom_settings = {
        "ITEM_PIPELINES": None,
        # "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item = {"page":1219}
        rand = random.randint(999999999999999,9999999999999999)/10000000000000000
        print(rand)
        yield scrapy.FormRequest(
            self.list_url,
            formdata={
                "dopost": "product_list",
                "pagesize": "5",
                "CategoryID": "7",
                "sort": "",
                "keyword": "",
                "pageno": str(item["page"]),
                "rnd": str(rand)
            },
            callback=self.parse,
            meta={"item":item}

        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])
        html_json = response.body.decode()
        try:
            list_page = json.loads(html_json)['listpage']
            list_data = list_page["listdata"]
            for pro in list_data:
                SUrl = pro["SUrl"]
                d_url = 'http://ztb.hljjs.gov.cn/' + SUrl if SUrl else ''
                # print(d_url)
                yield scrapy.Request(
                    d_url,
                    callback=self.parse_detail,
                )
        except Exception as e:
            print(str(e))
        item["page"] += 1
        if item["page"] <= 1226:
            print("*"*10,str(item["page"]))
            rand = random.randint(999999999999999, 9999999999999999) / 10000000000000000
            yield scrapy.FormRequest(
                self.list_url,
                formdata={
                    "dopost": "product_list",
                    "pagesize": "5",
                    "CategoryID": "7",
                    "sort": "",
                    "keyword": "",
                    "pageno": str(item["page"]),
                    "rnd": str(rand)
                },
                callback=self.parse,
                meta={"item": deepcopy(item)}
            )



    def parse_detail(self, response):
        # print(response.body.decode())
        try:
            company_name = response.xpath("//span[@id='lblFWinTenderee']//text()").extract()[0].strip()
        except Exception as e:
            company_name = '获取失败'
        with open("/home/python/Desktop/company/hlj_company.csv", 'a') as f:
            f.write(company_name + '\n')
        print(company_name)


