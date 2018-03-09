# -*- coding: utf-8 -*-
import scrapy
import time
from copy import deepcopy
import json
import re

class BjProSpider(scrapy.Spider):
    name = 'bj_pro'
    allowed_domains = ['xpt.bcactc.com']


    def start_requests(self):
        # url = "http://xpt.bcactc.com/G2/basic/gfm/info!performancePublicList.do?data&filter_params_=performanceId,rowNum,packageCode,projectName,enterpriseName,constructionUnit,contractValue,publishStartDate,publishEndDate&defined_operations_=&nocheck_operations_=&"
        url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceList.do?data&filter_params_=performanceId,rowNum,packageCode,projectName,enterpriseName,constructionUnit,contractValue,packageType&defined_operations_=&nocheck_operations_=&"
        #      http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceList.do?data&filter_params_=performanceId,rowNum,packageCode,projectName,enterpriseName,constructionUnit,contractValue,packageType&defined_operations_=&nocheck_operations_=&
        nd = str(int(time.time()) * 1000)
        item = {}
        item["page"] = 1
        yield scrapy.FormRequest(
            url,
            formdata={
                "gridSearch": "false",
                "nd": nd,
                "PAGESIZE": "15",
                "PAGE": str(item["page"]),
                "sortField": "",
                "sortDirection": "asc"
            },
            meta={"item": deepcopy(item)},
            callback=self.parse
        )

    # 列表页
    def parse(self, response):
        # 取出关键字段
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode()
        # 将json转换成字典
        dic_item = json.loads(json_html)
        total = dic_item["total"]  # 总页码
        for dic in dic_item["data"]:
            pro_id = dic["performanceId"] # 项目编号
            company = dic["enterpriseName"] # 承包公司
            item["company"] = company
            item["pro_id"] = pro_id

            if pro_id:
                nd = int(time.time()) * 1000
                detail_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceView.do?performanceId={}".format(pro_id, nd)
                #             http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceView.do?performanceId=8a8085c65ce3e02a015ce7f2c0da1d29
                # 请求详情页主页面
                yield scrapy.Request(
                    detail_url,
                    meta={"item": deepcopy(item)},
                    callback=self.detail_parse
                )

        page = item["page"] + 1
        url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceList.do?data&filter_params_=performanceId,rowNum,packageCode,projectName,enterpriseName,constructionUnit,contractValue,packageType&defined_operations_=&nocheck_operations_=&"
        if page <= total:
            item["page"] = page
            nd = str(int(time.time()) * 1000)
            yield scrapy.FormRequest(
                url,
                formdata={
                    "gridSearch": "false",
                    "nd": nd,
                    "PAGESIZE": "15",
                    "PAGE": str(item["page"]),
                    "sortField": "",
                    "sortDirection": "asc"
                },
                meta={"item": deepcopy(item)},
                callback=self.parse
            )
        else:
            yield item

    # 详情页
    def detail_parse(self, response):
        item = deepcopy(response.meta["item"])
        detail_item = []
        detail_list = response.xpath("//div[@style='width:85%;margin:10px auto;']/div[1]//text()").extract()
        if detail_list:
            for d in detail_list:
                p = re.compile('\s+')
                n_d = re.sub(p, '', d)
                if len(n_d)>0:
                    detail_item.append(n_d)

        # 资料下载
        detail_dow = response.xpath("//div[@style='width:85%;margin:10px auto;']/div[2]//tr")
        if detail_dow:
            for d in detail_dow:
                # http://xpt.bcactc.com/upload/20180112/15157485418733522.pdf
                dow_item = {}
                dow_item["title"] = d.xpath('.//a/text()').extract_first()
                href = d.xpath('.//a/@href').extract()
                dow_item["href"] = 'http://xpt.bcactc.com'+href[0] if href else ''
                detail_item.append(dow_item)
        item["pro_list"] = detail_item
        print(item)
        yield item


