# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy


class JxJzSpider(scrapy.Spider):
    name = "jx_jz"
    allowed_domains = ["wwww"]
    # start_urls = ['http://wwww/']
    list_url = "http://59.52.254.106:8093/qualificationCertificateListForPublic?pageIndex={}&enterpriseLevel=&enterpriseName=&legalRepresentative=&certificateNum=&registrationNum="
    custom_settings = {
        "ITEM_PIPELINES": None,
        "DOWNLOADER_MIDDLEWARES": None,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        item = {"page":1}
        yield scrapy.Request(
            self.list_url.format(item["page"]),
            meta={"item":item},
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        item = deepcopy(response.meta["item"])

        tr_list = response.xpath("//tr[@class='tr_change']")
        # print(tr_list)
        for tr in tr_list:
            company_name = tr.xpath('.//td[2]//text()').extract_first("").strip()
            print(company_name)
            with open("/home/python/Desktop/company/jx_company.csv",'a') as f:
                f.write(company_name+'\n')

        item["page"] += 1
        if item["page"] <= 1063:
            yield scrapy.FormRequest(
                self.list_url.format(item["page"]),
                meta={"item": deepcopy(item)},
                callback=self.parse,
                dont_filter=True

            )
