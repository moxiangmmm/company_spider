# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import re

'''
<a href="http://jzsc.sxjs.gov.cn/Browse/JzyList.aspx" target="main" title="建筑业企业" onclick="tz(this)">建筑业</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/AqscList.aspx" target="main" title="建筑施工安全生产许可证" onclick="tz(this)">安全许可证</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/GcjlList.aspx" target="main" title="工程监理企业" onclick="tz(this)">工程监理</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/GckcList.aspx" target="main" title="工程勘察企业" onclick="tz(this)">工程勘察</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/Ent_DesignList.aspx" target="main" title="工程设计企业" onclick="tz(this)">工程设计</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/Ent_BiddingList.aspx" target="main" title="工程招标代理机构" onclick="tz(this)">招标代理</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/GczjList.aspx" target="main" title="工程造价咨询企业" onclick="tz(this)">工程造价</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/ZljcList.aspx" target="main" title="工程质量检测企业" onclick="tz(this)">质量检测</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/EntQua_Yllh.aspx" target="main" title="城市园林绿化企业" onclick="tz(this)">园林绿化</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/EntQua_Fckf.aspx" target="main" title="房地产开发企业" onclick="tz(this)">房地产开发</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/EntQua_Fcgj.aspx" target="main" title="房地产估价机构" onclick="tz(this)">房地产估价</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/EntQua_Wuye.aspx" target="main" title="物业服务企业" onclick="tz(this)">物业服务</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/EntQua_Cxgh.aspx" target="main" title="城乡规划编制单位" onclick="tz(this)">城乡规划</a>
<a href="http://jzsc.sxjs.gov.cn/Browse/Ent_DesignBuildList.aspx" target="main" title="工程设计与施工一体化企业">设计与施工</a>
'''
# {type:total_page}

class SxJzSpider(scrapy.Spider):
    name = 'sx_jz'
    allowed_domains = ['jzsc.sxjs.gov.cn','jzsc.sxjs.gov.cn/Browse']
    # allowed_domains = ['.*']
    type = "EntQua_Fckf" # 园林绿化企业
    start_urls = ['http://jzsc.sxjs.gov.cn/Browse/{}.aspx'.format(type)]
    main_url = "http://jzsc.sxjs.gov.cn/Browse/JzyList_1.aspx?ent_id=c782d826-0ed6-419c-97b4-ee1fb4ee7887&cert_id=f15b8985-f7da-43ff-814d-695b0575cf10"
    list_url = "http://jzsc.sxjs.gov.cn/Browse/{}.aspx?page={}"
    total_page = 307
    custom_settings = {
        # "ITEM_PIPELINES": None,
        "DOWNLOAD_DELAY": 1,
        "DOWNLOADER_MIDDLEWARES": None,
        # "LOG_FILE": './log/sx_jz_scrapy.log',
        # "LOG_LEVEL": "WARNING",
    }

    def parse(self, response):
        try:
            item = deepcopy(response.meta["item"])
        except:
            item = {"page": 1}
        print(item["page"])
        company_list = []
        company_item = {}
        tr_list = response.xpath("//form[@id='formList']//tr")
        for tr in tr_list:
            c = tr.xpath(".//td[1]//text()").extract_first()
            company = c.strip()
            if company and company!="企业名称":
                company_list.append(company)
        print(company_list)
        company_item["company_list"] = company_list
        yield company_item
        item["page"] += 1
        if item["page"] <= self.total_page:
            yield scrapy.Request(
                url=self.list_url.format(self.type, item["page"]),
                meta={"item":deepcopy(item)},
                callback=self.parse
            )


    # 详情页
    def main_parse(self, response):
        item = deepcopy(response.meta["item"])
        main_list = response.xpath("//div[@id='main8']//ul[1]//text()").extract() # 详细信息
        dt_list = response.xpath("//div[@id='main8']//ul[2]//text()").extract() # 动态考核
        xy_list = response.xpath("//div[@id='main8']//ul[3]//text()").extract() # 信用评价
        pe_list = response.xpath("//div[@id='main8']//ul[4]//text()").extract() # 执业注册人员
        prize_list = response.xpath("//div[@id='main8']//ul[5]//text()").extract() # 获奖信息
        penalize_list = response.xpath("//div[@id='main8']//ul[6]//text()").extract() # 不良记录
        pro_list = response.xpath("//div[@id='main8']//ul[7]//text()").extract() # 业绩信息
        text_item = {"main_list":main_list, "dt_list":dt_list, "xy_list":xy_list, "pe_list":pe_list,"prize_list":prize_list, "penalize_list":penalize_list}
        for key, value in text_item.items():
            lists = []
            for t in value:
                text = t.strip()
                if text:
                    lists.append(text)
            item[key] = lists

        # 项目页 如果有项目，提取项目详情url
        list_pro = []
        for t in pro_list:
            text = t.strip()
            if text:
                list_pro.append(text)
        if list_pro[-1] != '暂无相关内容！':
            print("="*20)
            pro_h_list = response.xpath("//div[@id='main8']//ul[7]//a/@href").extract() # 项目详情url
            list_pro.append(pro_h_list)
        item["pro_list"] = list_pro

        print(item)
        yield item
