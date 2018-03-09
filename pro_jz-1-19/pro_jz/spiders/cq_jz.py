# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
# 重庆网站先爬新标企业，后面几个分类规则不相同再分析
# 本地施工企业列表页 http://183.64.1.92/CQCollect/Qy_Query/Sgqy/Sgqy_List.aspx
# 外地企业 http://183.64.1.92/CQCollect/Qy_Query/Ryxxbs/Rybabs_List.aspx

class CqJzSpider(scrapy.Spider):
    name = 'cq_jz'
    allowed_domains = ['183.64.1.92']
    start_urls = ["http://183.64.1.92/CQCollect/Qy_Query/Ryxxbs/Rybabs_List.aspx"]
    value = "7C4CC765"
    list_url = "http://183.64.1.92/CQCollect/Qy_Query/Ryxxbs/Rybabs_List.aspx"
    total_page = 133
    # xb_list = "http://183.64.1.92/CQCollect/Qy_Query/YhzSgqy/YhzSgqy_List.aspx"
    # main_url = "http://183.64.1.92/CQCollect/Qy_Query/YhzSgqy/YhzSgqy_Info.aspx?co={}"
    # total = 10021347

    # http://183.64.1.92/CQCollect/Qy_Query/Ryxxbs/Rybaqy_Info.aspx?co=10102800
    # http://183.64.1.92/CQCollect/Qy_Query/Ryxxbs/Rybaqy_Info.aspx?co=10108600

    custom_settings = {
        # "ITEM_PIPELINES": None,
        # "LOG_FILE": "./cq_jz_scrapy.log",
        # "LOG_LEVEL": "WARNING",
        # "REDIS_URL": "redis://127.0.0.1:6379/3",

        "DOWNLOAD_DELAY": 1,
        "DOWNLOADER_MIDDLEWARES": None
    }


    def parse(self, response):
        try:
            item = deepcopy(response.meta["item"])
        except:
            item = {"page": 1}
        print(item["page"])
        c_item = {}
        company_list = []
        view = response.xpath("//input[@name='__VIEWSTATE']/@value").extract()
        v = view[0] if len(view)>0 else ''
        # print(v)
        tr_list = response.xpath("//table[@id='DataGrid1']//tr")
        for tr in tr_list:
            c = tr.xpath(".//td[2]//text()").extract_first()
            company = c.strip()
            if company and company!="企业名称":
                company_list.append(company)
        print(company_list)
        c_item["company_list"] = company_list
        yield c_item
        data = {
            "__EVENTTARGET": "Pager1:LB_Next",
            "__  EVENTARGUMENT":"",
            "__VIEWSTATE":v,
            "__VIEWSTATEGENERATOR": self.value,
            "FName":"",
            "FList":"0",
            "FType":"0",
            "FLevel":"0",
            "FIsBase":"(unable to decode value)",
            "Pager1":"NewPage:"
            }
        item["page"] += 1
        if item["page"] <= self.total_page:
            yield scrapy.FormRequest(
                url=self.list_url,
                formdata=data,
                meta={"item":item},
                callback=self.parse
            )




