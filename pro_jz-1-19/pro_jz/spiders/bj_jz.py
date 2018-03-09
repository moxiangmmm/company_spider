# -*- coding: utf-8 -*-
import scrapy
import time
import json
from bj_pro_d import Bj_pro_d
from copy import deepcopy

class BjJzSpider(scrapy.Spider):
    name = 'bj_jz'
    allowed_domains = ['xpt.bcactc.com']
    # start_urls = ['http://bcactc.com/']

    def start_requests(self):
        url = "http://xpt.bcactc.com/G2/basic/gfm/info!entOrganizationList.do?data&filter_params_=enterpriseId,rowNum,organizationCode,enterpriseName,enterpriseType,&defined_operations_=&nocheck_operations_=&"
        nd = str(int(time.time())*1000)
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
        meta = {"item":deepcopy(item)},
        callback= self.parse
        )
    # 列表页
    def parse(self, response):
        '''
        [{"enterpriseId":"8a8085c66078ccf901607bf9f4800ea9",详情页id
        "organizationCode":"07664028-2",组织机构代码
        "enterpriseName":"                   北京中通安邦装饰工程有限公司",公司名称
        "enterpriseType":"设计企业",公司类型
        "operations":[]}
        '''
        # 取出关键字段
        item = deepcopy(response.meta["item"])
        json_html = response.body.decode()
        # 将json转换成字典
        dic_item  = json.loads(json_html)
        total = dic_item["total"]# 总页码
        for dic in dic_item["data"]:
            company_id = dic["enterpriseId"] # 公司代码
            org_code = dic["organizationCode"].strip() # 组织机构代码
            company = dic["enterpriseName"].strip() # 公司名称
            type = dic["enterpriseType"].strip() # 公司类型
            item["company"] = company
            item["company_id"] = company_id
            item["org_code"] = org_code
            item["type"] = type
            nd = int(time.time())*1000
            main_url = "http://xpt.bcactc.com/G2/ajax/info!baseInfoView.do?enterpriseId={}&pattern=basic&_={}".format(company_id,nd)
            # 请求详情页主页面
            yield scrapy.Request(
                main_url,
                meta={"item":deepcopy(item)},
                callback=self.main_parse
            )

        page = item["page"]+1
        url = "http://xpt.bcactc.com/G2/basic/gfm/info!entOrganizationList.do?data&filter_params_=enterpriseId,rowNum,organizationCode,enterpriseName,enterpriseType,&defined_operations_=&nocheck_operations_=&"
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


    # 详情页主页面
    def main_parse(self, response):
        item = deepcopy(response.meta["item"])
        item["c_date"] = response.xpath("//table[@class='gs-table']//tr[1]//td[4]//text()").extract_first() #成立日期
        item["add"] = response.xpath("//table[@class='gs-table']//tr[2]//td[2]//text()").extract_first() #地址
        item["capital"] = response.xpath("//table[@class='gs-table']//tr[3]//td[2]//text()").extract_first() #注册资金
        item["licence_code"] = response.xpath("//table[@class='gs-table']//tr[3]//td[4]//text()").extract_first() #营业执照代码
        item["leader"] = response.xpath("//table[@class='gs-table']//tr[4]//td[2]//text()").extract_first() #法人
        item["scope"] = response.xpath("//table[@class='gs-table']//tr[6]//td[2]//text()").extract_first() # 经营范围
        item["s_date"] = response.xpath("//table[@class='gs-table']//tr[6]//td[4]//text()").extract_first() # 年检有效期
        # 请求资质页
        cf_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entQualificationList.do?data&enterpriseId={}&filter_params_=mainId,rowNum,certificateNo,typeLevel,qualificationType&defined_operations_=&nocheck_operations_=&".format(item["company_id"])
        nd = str(int(time.time())*1000)
        yield scrapy.FormRequest(
            cf_url,
            formdata={
                "gridSearch": "false",
                "nd": nd,
                "PAGESIZE": "10",
                "PAGE": "1",
                "sortField": "",
                "sortDirection": "asc"
            },
            meta={"item": deepcopy(item)},
            callback=self.cf_parse

        )

    # 资质页
    def cf_parse(self, response):
        item = deepcopy(response.meta["item"])
        pe_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPersonInfoList.do?data&enterpriseId={}&filter_params_=personId,rowNum,personName,sex,personType,qualificationNo,&defined_operations_=&nocheck_operations_=&".format(item["company_id"])
        # 证书编号 cf_id
        # 资质名称 cf_name
        # 资质划分 cf_type
        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["total"]
        cf_list = []
        # 如果没有资质信息,直接请求人员页
        if total == 0:
            item["cf_list"] = cf_list
            nd = str(int(time.time()) * 1000)
            yield scrapy.FormRequest(
                pe_url,
                formdata={
                        "gridSearch": "false",
                        "nd": nd,
                        "PAGESIZE": "10",
                        "PAGE": "1",
                        "sortField": "",
                        "sortDirection": "asc"
                    },
                callback=self.pe_parse,
                meta={"item":deepcopy(item)}
            )
        else:
            dic_item = json_dic["data"]

            for dic in dic_item:
                cf_item = {}
                cf_id = dic["certificateNo"]
                cf_type = dic["qualificationType"]
                cf_name = dic["typeLevel"]
                cf_item["cf_id"] = cf_id
                cf_item["cf_type"] = cf_type
                cf_item["cf_name"] = cf_name
                cf_list.append(cf_item)
            try:
                cf_page = item["cf_page"]
            except:
                cf_page = 1
            if cf_page == 1:
                item["cf_list"] = cf_list
            else:
                item["cf_list"] += cf_list
            cf_page += 1
            # 如果有下一页，发送请求
            if cf_page <= total:
                item["cf_page"] = cf_page
                cf_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entQualificationList.do?data&enterpriseId={}&filter_params_=mainId,rowNum,certificateNo,typeLevel,qualificationType&defined_operations_=&nocheck_operations_=&".format(item["company_id"])
                nd = str(int(time.time()) * 1000)
                yield scrapy.FormRequest(
                    cf_url,
                    formdata={
                        "gridSearch": "false",
                        "nd": nd,
                        "PAGESIZE": "10",
                        "PAGE": str(item["cf_page"]),
                        "sortField": "",
                        "sortDirection": "asc"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.cf_parse
                )
            else:
                nd = str(int(time.time()) * 1000)
                yield scrapy.FormRequest(
                    pe_url,
                    formdata={
                        "gridSearch": "false",
                        "nd": nd,
                        "PAGESIZE": "10",
                        "PAGE": "1",
                        "sortField": "",
                        "sortDirection": "asc"
                    },
                    callback=self.pe_parse,
                    meta={"item": deepcopy(item)}
                )

    # 人员页
    def pe_parse(self, response):
        item = deepcopy(response.meta["item"])
        pe_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPersonInfoList.do?data&enterpriseId={}&filter_params_=personId,rowNum,personName,sex,personType,qualificationNo,&defined_operations_=&nocheck_operations_=&".format(item["company_id"])
        pro_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceList.do?data&enterpriseId={}&filter_params_=performanceId,rowNum,projectName,constructionUnit,contractSigningTime,bidWinningMoney,&defined_operations_=&nocheck_operations_=&".format(item["company_id"])
        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["total"]
        pe_list = []
        # 如果没有人员信息，直接将数据传到管道
        if total == 0:
            item["pe_list"] = pe_list
            nd = str(int(time.time()) * 1000)
            yield scrapy.FormRequest(
                pro_url,
                formdata={
                    "gridSearch": "false",
                    "nd": nd,
                    "PAGESIZE": "10",
                    "PAGE": "1",
                    "sortField": "",
                    "sortDirection": "asc"
                },
                meta={"item": deepcopy(item)},
                callback=self.pro_parse
            )
        else:
            dic_item = json_dic["data"]

            for dic in dic_item:
                pe_item = {}
                p_id = dic["personId"]
                p_type = dic["personType"]
                p_name = dic["personName"]
                p_code = dic["qualificationNo"]
                p_sex = dic["sex"]
                pe_item["p_id"] = p_id
                pe_item["p_type"] = p_type
                pe_item["p_name"] = p_name
                pe_item["p_code"] = p_code
                pe_item["p_sex"] = p_sex
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
            if pe_page <= total:
                item["pe_page"] = pe_page
                nd = str(int(time.time()) * 1000)
                yield scrapy.FormRequest(
                    pe_url,
                    formdata={
                        "gridSearch": "false",
                        "nd": nd,
                        "PAGESIZE": "10",
                        "PAGE": str(item["pe_page"]),
                        "sortField": "",
                        "sortDirection": "asc"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.pe_parse
                )
            else:
                nd = str(int(time.time()) * 1000)
                yield scrapy.FormRequest(
                    pro_url,
                    formdata={
                        "gridSearch": "false",
                        "nd": nd,
                        "PAGESIZE": "10",
                        "PAGE": "1",
                        "sortField": "",
                        "sortDirection": "asc"
                    },
                    callback=self.pro_parse,
                    meta={"item":deepcopy(item)}
                )


    # 项目页
    def pro_parse(self, response):
        item = deepcopy(response.meta["item"])
        pro_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceList.do?data&enterpriseId={}&filter_params_=performanceId,rowNum,projectName,constructionUnit,contractSigningTime,bidWinningMoney,&defined_operations_=&nocheck_operations_=&".format(item["company_id"])
        json_html = response.body.decode()
        json_dic = json.loads(json_html)
        total = json_dic["total"]
        pro_list = []
        # 如果没有项目信息，直接将数据传到管道
        if total == 0:
            item["pro_list"] = pro_list
            print("+" * 20, item)
            yield item
        else:
            dic_item = json_dic["data"]

            for dic in dic_item:
                pro_item = {}
                pro_name = dic["projectName"] # 项目名称
                js_company = dic["constructionUnit"] # 建设单位
                zb_date = dic["contractSigningTime"] # 中标日期
                pro_id = dic["performanceId"] # 项目id
                pro_money = dic["bidWinningMoney"] # 合同金额
                pro_item["pro_name"] = pro_name
                pro_item["js_company"] = js_company
                pro_item["zb_date"] = zb_date
                pro_item["pro_id"] = pro_id
                pro_item["pro_money"] = pro_money

                # 请求项目详情页
                if pro_id:
                    detail = Bj_pro_d(pro_id)
                    d_list = detail.get_detail()
                    pro_item["d_list"] = d_list
                pro_list.append(pro_item)
                # [{[]}]
            try:
                pro_page = item["pro_page"]
            except:
                pro_page = 1
            if pro_page == 1:
                item["pro_list"] = pro_list
            else:
                item["pro_list"] += pro_list
            pro_page += 1
            if pro_page <= total:
                item["pro_page"] = pro_page
                nd = str(int(time.time()) * 1000)
                yield scrapy.FormRequest(
                    pro_url,
                    formdata={
                        "gridSearch": "false",
                        "nd": nd,
                        "PAGESIZE": "10",
                        "PAGE": str(item["pro_page"]),
                        "sortField": "",
                        "sortDirection": "asc"
                    },
                    meta={"item": deepcopy(item)},
                    callback=self.pro_parse
                )
            print('=' * 20, item)
            yield item











