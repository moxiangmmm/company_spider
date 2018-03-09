# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy


class HnSpider(scrapy.Spider):
    name = "hn"
    # http://pt.hnjst.gov.cn:8008/WebSite_Publish/Default.aspx?action=IntegrityMge/ucCreditCompanyInfoList&Type=建筑业企业资质
    allowed_domains = ["pt.hnjst.gov.cn:8008"]
    list_url = "http://pt.hnjst.gov.cn:8008/WebSite_Publish/Default.aspx?action=IntegrityMge/ucCreditCompanyInfoList&Type=建筑业企业资质"
    custom_settings = {
        "ITEM_PIPELINES": None,
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
        item = response.meta["item"]
        a_list = response.xpath("//table[@class='ListStyle']//a")
        for a in a_list:
            company_name = a.xpath(".//text()").extract_first("").strip()
            print(company_name)
            with open("/home/python/Desktop/company/hainan_company.csv",'a') as f:
                f.write(company_name+'\n')

        item["page"] += 1
        try:
            __VIEWSTATE = response.xpath("//input[@id='__VIEWSTATE']/@value").extract()[0]
        except:
            __VIEWSTATE = ''
        if item["page"] <= 143:
            print('*'*10,item["page"])
            yield scrapy.FormRequest(
                self.list_url,
                formdata={
                "__EVENTTARGET": "ID_IntegrityMge_ucCreditCompanyInfoList$ucPager1$btnGo0",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": __VIEWSTATE,
                "__VIEWSTATEGENERATOR": "F006C583",
                "ID_IntegrityMge_ucCreditCompanyInfoList$txtProjectName": "",
                "ID_IntegrityMge_ucCreditCompanyInfoList$ddlProvince": "全部",
                "ID_IntegrityMge_ucCreditCompanyInfoList$txtValidCode": "",
                "ID_IntegrityMge_ucCreditCompanyInfoList$ucPager1$txtCurrPage": str(item["page"])
                },
                callback=self.parse,
                meta={"item":deepcopy(item)},
                dont_filter=True
            )


