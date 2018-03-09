# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json
import re
from sz import Sz

class SzJzSpider(scrapy.Spider):
    name = 'sz_jz'
    allowed_domains = ['portal.szjs.gov.cn']
    custom_settings = {
    "ITEM_PIPELINES" :{'pro_jz.pipelines.Szjz_Pipeline':300},
        "DOWNLOADER_MIDDLEWARES": None,
    }
    # start_urls = ['http://portal.szjs.gov.cn:8888/']
    list_url = 'http://portal.szjs.gov.cn:8888/publicShow/corpList.html'
    main_url = 'http://portal.szjs.gov.cn:8888/publicShow/corpDetail.html?param={}&corpType={}&orgCode={}'
    lead_url = "http://portal.szjs.gov.cn:8888/publicShow/queryPrincipal.html"
    cf_url = "http://portal.szjs.gov.cn:8888/publicShow/queryCertificateInfo.html"
    pe_url = "http://portal.szjs.gov.cn:8888/publicShow/queryTechnology.html"
    safety_url = "http://portal.szjs.gov.cn:8888/publicShow/querySafeProduction.html"
    safety_p_url = "http://portal.szjs.gov.cn:8888/publicShow/queryPersonSafe.html"
    pro_url = "http://portal.szjs.gov.cn:8888/publicShow/queryPerformance.html"
    prize_url = "http://portal.szjs.gov.cn:8888/publicShow/queryPrizes.html"
    penalize_url = "http://portal.szjs.gov.cn:8888/publicShow/queryPunish.html"
    type = "18"
    '''
    1 建筑业
    24 设计与施工一体化
    19 勘察设计企业
    9 专项设计企业
    21 施工图审查机构
    4 监理企业
    7 招标代理企业
    8 造价咨询企业
    18 预拌混凝土企业
    '''

    def start_requests(self):
        item = {}
        item["page"] = 1
        yield scrapy.FormRequest(
            self.list_url,
            formdata={
                "param": "",
                "corpType":self.type,
                "page": str(item["page"]),
                "corp_name":""
            },
            meta={"item": deepcopy(item)},
            callback=self.parse
        )

    def parse(self, response):

        # 取出关键字段
        item = deepcopy(response.meta["item"])
        tr_list = response.xpath("//tbody//tr")
        for tr in tr_list:
            item["company"] = tr.xpath(".//a/text()").extract_first()
            code_list = tr.xpath(".//a/@href").extract()
            # ["javascript:corpDetail('14372','231221732')"]
            # javascript:corpDetail('6099','132203360')
            codes = re.findall(r"corpDetail\((.*)\)", code_list[0]) if code_list else None
            c_id_str = re.findall(r"\'(\d+)\','", codes[0])[0]
            # c_code_str = re.findall(r",\'(\d+)\'", codes[0])[0]
            c_code_list = tr.xpath(".//td[3]/@title").extract()
            item["company_id"] = int(c_id_str)
            item["company_code"] = c_code_list[0] if c_code_list else None
            # 请求详情页主页面
            yield scrapy.Request(
                self.main_url.format(item["company_id"], self.type, item["company_code"]),
                meta={"item": deepcopy(item)},
                callback=self.main_parse
            )


        page = item["page"] + 1
        total_list = response.xpath('//div["text-align:center;padding-bottom:10px;"]//a[last()]/@href').extract()
        # javascript:topage('334')
        total = re.findall(r"topage\(\'(\d+)\'\)", total_list[0]) if total_list else None
        t_int = int(total[0])


        if page <= t_int:
            item["page"] = page
            yield scrapy.FormRequest(
                self.list_url,
                formdata={
                    "param": "",
                    "corpType": self.type,
                    "page": str(item["page"]),
                    "corp_name": ""
                },
                meta={"item": deepcopy(item)},
                callback=self.parse
            )
        else:
            yield item


    def main_parse(self, response):
        item = deepcopy(response.meta["item"])
        item["sz_jg"] = response.xpath('//tbody[@class="tbodydetail"]//tr[2]//td[2]/text()').extract_first() #在深机构
        item["lxr"] = response.xpath('//tbody[@class="tbodydetail"]//tr[4]//td[2]/text()').extract_first() #在联系人
        item["tel"] = response.xpath('//tbody[@class="tbodydetail"]//tr[5]//td[2]/text()').extract_first() #联系电话
        item["leader"] = response.xpath('//tbody[@class="tbodydetail"]//tr[6]//td[2]/text()').extract_first() #法人姓名
        item["cj"] = response.xpath('//tbody[@class="tbodydetail"]//tr[7]//td[2]/text()').extract_first() #传真
        item["mail"] = response.xpath('//tbody[@class="tbodydetail"]//tr[8]//td[2]/text()').extract_first() #邮箱
        item["add"] = response.xpath('//tbody[@class="tbodydetail"]//tr[9]//td[2]/text()').extract_first() #注册地址
        item["capital"] = response.xpath('//tbody[@class="tbodydetail"]//tr[10]//td[2]/text()').extract_first() #资金
        item["b_date"] = response.xpath('//tbody[@class="tbodydetail"]//tr[11]//td[2]/text()').extract_first() #成立时间
        yield scrapy.FormRequest(
            self.lead_url,
            formdata={
                "param": str(item["company_id"]),
                "corpType": self.type,
                "orgCode": item["company_code"],
                "page": "1"
            },
            meta={"item": deepcopy(item)},
            callback=self.lead_parse
        )

    # 领导页
    def lead_parse(self, response):
        item = deepcopy(response.meta["item"])

        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["totalRecord"] # 总人数
        total_page = json_dic["totalPage"] # 总页数
        lead_list = []
        # 如果没有人员信息，请求资质页
        if total == 0:
            item["lead_list"] = lead_list

            yield scrapy.FormRequest(
                self.cf_url,
                formdata={
                    "param": str(item["company_id"]),
                    "corpType": self.type,
                    "orgCode": item["company_code"],
                    "page": "1"
                },
                meta={"item": deepcopy(item)},
                callback=self.cf_parse
            )
        else:
            dic_item = json_dic["records"]

            for dic in dic_item:
                lead_item = {}
                lead_item["p_type"] = dic["emptype"] # 人员类型
                lead_item["p_name"] = dic["name"] # 姓名
                lead_item["p_duty"] = dic["duty"] # 职务
                lead_item["p_tel"] = dic["tel"] # 电话
                lead_list.append(lead_item)
            try:
                lead_page = item["lead_page"]
            except:
                lead_page = 1
            if lead_page == 1:
                item["lead_list"] = lead_list
            else:
                item["lead_list"] += lead_list
            lead_page += 1
            # 如果人员大于一页
            if lead_page <= total_page:
                item["lead_page"] = lead_page
                yield scrapy.FormRequest(
                    self.lead_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": str(item["lead_page"])
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.lead_parse
                )
            # 如果没有下页，请求下一个分类
            else:
                yield scrapy.FormRequest(
                    self.cf_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": "1"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.cf_parse
                )
    # 资质页
    def cf_parse(self, response):
        item = deepcopy(response.meta["item"])

        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["totalRecord"]  # 资质总数
        total_page = json_dic["totalPage"]  # 总页数
        cf_list = []
        # 如果没有人员信息，请求人员页
        if total == 0:
            print("*" * 20)
            item["cf_list"] = cf_list

            yield scrapy.FormRequest(
                self.pe_url,
                formdata={
                    "param": str(item["company_id"]),
                    "corpType": self.type,
                    "orgCode": item["company_code"],
                    "page": "1"
                },
                meta={"item": deepcopy(item)},
                callback=self.pe_parse
            )
        else:
            dic_item = json_dic["records"]

            for dic in dic_item:
                cf_list.append(dic)

            try:
                cf_page = item["cf_page"]
            except:
                cf_page = 1
            if cf_page == 1:
                item["cf_list"] = cf_list
            else:
                item["cf_list"] += cf_list
            cf_page += 1
            # 如果人员大于一页
            if cf_page <= total_page:
                item["cf_page"] = cf_page
                yield scrapy.FormRequest(
                    self.cf_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": str(item["cf_page"])
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.cf_parse
                )
            # 如果没有下页，请求下一个分类
            else:

                yield scrapy.FormRequest(
                    self.pe_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": "1"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.pe_parse
                )


    # 人员页
    def pe_parse(self, response):

        item = deepcopy(response.meta["item"])

        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["totalRecord"]  # 总数
        total_page = json_dic["totalPage"]  # 总页数
        pe_list = []
        # 如果没有人员信息，请求下一个分类
        if total == 0:
            item["pe_list"] = pe_list

            yield scrapy.FormRequest(
                self.safety_url,
                formdata={
                    "param": str(item["company_id"]),
                    "corpType": self.type,
                    "orgCode": item["company_code"],
                    "page": "1"
                },
                meta={"item": deepcopy(item)},
                callback=self.lics_parse
            )
        else:
            dic_item = json_dic["records"]

            for dic in dic_item:
                pe_item = {}
                pe_item["p_name"] = dic["name"]  # 人员类型
                pe_item["p_type"] = dic["typename"]  # 姓名
                pe_item["p_code"] = dic["alt_cert_id"]  # 职务
                pe_item["p_company"] = dic["corp_name"]  # 电话
                pe_list.append(pe_item)
            try:
                pe_page = item["pe_page"]
            except:
                pe_page = 1
            if pe_page == 1:
                item["pe_list"] = pe_list
            else:
                item["pe_list"] += pe_list
            pe_page += 1
            # 如果人员大于一页
            if pe_page <= total_page:
                item["pe_page"] = pe_page
                yield scrapy.FormRequest(
                    self.pe_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": str(item["pe_page"])
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.pe_parse
                )
            # 如果没有下页，请求下一个分类
            else:
                yield scrapy.FormRequest(
                    self.safety_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": "1"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.lics_parse
                )

    # 安全许可证
    def lics_parse(self, response):
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["totalRecord"]  # 总数
        total_page = json_dic["totalPage"]  # 总页数
        lics_list = []
        # 如果没有信息，请求下一分类
        if total == 0:
            print("*" * 20)
            item["lics_list"] = lics_list

            yield scrapy.FormRequest(
                self.pro_url,
                formdata={
                    "param": str(item["company_id"]),
                    "corpType": self.type,
                    "orgCode": item["company_code"],
                    "page": "1"
                },
                meta={"item": deepcopy(item)},
                callback=self.pro_parse
            )
        else:
            dic_item = json_dic["records"]

            for dic in dic_item:
                lics_item = {}
                lics_item["lics_id"] = dic["lics_id"]# 许可中编号
                lics_item["lics_range"] = dic["lics_range"]# 许可范围
                lics_item["b_date"] = dic["valid_start_date"]# 开始时间
                lics_item["s_date"] = dic["valid_end_date"]# 结束时间
                lics_item["issue_dept"] = dic["issue_dept"]# 发证机关
                lics_list.append(lics_item)
            try:
                lics_page = item["lics_page"]
            except:
                lics_page = 1
            if lics_page == 1:
                item["lics_list"] = lics_list
            else:
                item["lics_list"] += lics_list
            lics_page += 1
            # 如果大于一页
            if lics_page <= total_page:
                item["lics_page"] = lics_page
                yield scrapy.FormRequest(
                    self.safety_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": str(item["lics_page"])
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.lics_parse
                )
            # 如果没有下页，请求下一个分类
            else:
                # print('+' * 20, item)
                yield scrapy.FormRequest(
                self.pro_url,
                formdata={
                    "param": str(item["company_id"]),
                    "corpType": self.type,
                    "orgCode": item["company_code"],
                    "page": "1"
                },
                meta={"item": deepcopy(item)},
                callback=self.pro_parse
            )

    # 项目信息
    def pro_parse(self, response):
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["totalRecord"]  # 总数
        total_page = json_dic["totalPage"]  # 总页数
        pro_list = []
        # 如果没有人员信息，请求下一分类
        if total == 0:
            item["pro_list"] = pro_list

            yield scrapy.FormRequest(
                self.prize_url,
                formdata={
                    "param": str(item["company_id"]),
                    "corpType": self.type,
                    "orgCode": item["company_code"],
                    "page": "1"
                },
                meta={"item": deepcopy(item)},
                callback=self.prize_parse
            )
        else:
            dic_item = json_dic["records"]

            for dic in dic_item:
                pro_list.append(dic)

            try:
                pro_page = item["pro_page"]
            except:
                pro_page = 1
            if pro_page == 1:
                item["pro_list"] = pro_list
            else:
                item["pro_list"] += pro_list
            pro_page += 1
            # 如果大于一页
            if pro_page <= total_page:
                item["pro_page"] = pro_page
                yield scrapy.FormRequest(
                    self.pro_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": str(item["pro_page"])
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.pro_parse
                )
            # 如果没有下页，请求下一个分类
            else:
                yield scrapy.FormRequest(
                    self.prize_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": "1"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.prize_parse
                )
    # 获奖信息
    def prize_parse(self, response):
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["totalRecord"]  # 总数
        total_page = json_dic["totalPage"]  # 总页数
        prize_list = []
        # 如果没有人员信息，请求下一分类
        if total == 0:
            item["prize_list"] = prize_list

            yield scrapy.FormRequest(
                self.penalize_url,
                formdata={
                    "param": str(item["company_id"]),
                    "corpType": self.type,
                    "orgCode": item["company_code"],
                    "page": "1"
                },
                meta={"item": deepcopy(item)},
                callback=self.penalize_parse
            )
        else:
            dic_item = json_dic["records"]

            for dic in dic_item:
                prize_list.append(dic)

            try:
                prize_page = item["prize_page"]
            except:
                prize_page = 1
            if prize_page == 1:
                item["prize_list"] = prize_list
            else:
                item["prize_list"] += prize_list
            prize_page += 1
            # 如果人员大于一页
            if prize_page <= total_page:
                item["prize_page"] = prize_page
                yield scrapy.FormRequest(
                    self.prize_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": str(item["prize_page"])
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.prize_parse
                )
            # 如果没有下页，请求下一个分类
            else:
                yield scrapy.FormRequest(
                    self.penalize_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": "1"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.penalize_parse
                )

    # 行政处罚
    def penalize_parse(self, response):
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["totalRecord"]  # 总数
        total_page = json_dic["totalPage"]  # 总页数
        penalize_list = []
        # 如果没有人员信息，请求下一分类
        if total == 0:
            item["penalize_list"] = penalize_list

            yield scrapy.FormRequest(
                self.safety_p_url,
                formdata={
                    "param": str(item["company_id"]),
                    "corpType": self.type,
                    "orgCode": item["company_code"],
                    "page": "1"
                },
                meta={"item": deepcopy(item)},
                callback=self.safety_p_parse
            )
        else:
            dic_item = json_dic["records"]

            for dic in dic_item:
                penalize_list.append(dic)

            try:
                penalize_page = item["penalize_page"]
            except:
                penalize_page = 1
            if penalize_page == 1:
                item["penalize_list"] = penalize_list
            else:
                item["penalize_list"] += penalize_list
            penalize_page += 1
            # 如果大于一页
            if penalize_page <= total_page:
                item["penalize_page"] = penalize_page
                yield scrapy.FormRequest(
                    self.penalize_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": str(item["penalize_page"])
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.prize_parse
                )
            # 如果没有下页，请求下一个分类
            else:
                yield scrapy.FormRequest(
                    self.safety_p_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": "1"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.safety_p_parse
                )



    # 人员安全证书
    def safety_p_parse(self, response):
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["totalRecord"]  # 总数
        total_page = json_dic["totalPage"]  # 总页数
        safety_p_list = []
        # 如果没有人员信息，请求下一分类
        if total == 0:
            item["safety_p_list"] = safety_p_list
            # print("+" * 20, item)
            yield item

        else:
            dic_item = json_dic["records"]

            for dic in dic_item:
                safety_p_list.append(dic)

            try:
                safety_p_page = item["safety_p_page"]
            except:
                safety_p_page = 1
            if safety_p_page == 1:
                item["safety_p_list"] = safety_p_list
            else:
                item["safety_p_list"] += safety_p_list
            safety_p_page += 1
            # 如果人员大于一页
            if safety_p_page <= total_page:
                item["safety_p_page"] = safety_p_page
                yield scrapy.FormRequest(
                    self.safety_p_url,
                    formdata={
                        "param": str(item["company_id"]),
                        "corpType": self.type,
                        "orgCode": item["company_code"],
                        "page": str(item["safety_p_page"])
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.safety_p_parse
                )
            # 如果没有下页，请求下一个分类
            else:
                print("*"*20, item)
                yield item