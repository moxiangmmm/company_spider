# coding=utf-8
import requests
import json

class Sz(object):

    def __init__(self,company_id, cert_id):
        self.headers = {
            "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)"
        }
        self.detail_url = "http://portal.szjs.gov.cn:8888/publicShow/queryCertificateDetail.html"
        self.company_id = str(company_id)
        self.cert_id = str(cert_id)

        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"

        # 代理隧道验证信息
        proxyUser = "H65403216IJKN42D"
        proxyPass = "55697F9CCB86225E"

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        self.proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }

        # self.detail_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceView.do?performanceId=8a8085cb60e4c91c0160e9a598a72c90"
        # 详情页下载
        '''
        param:2000007645
        corpType:3
        cert_id:42097
        '''
    def get_detail(self):
        ret = requests.post(
            self.detail_url,
            proxies=self.proxies,
            headers = self.headers,
            data={
                "param": self.company_id,
                "corpType": "3",
                "cert_id": self.cert_id,
            })
        json_html = ret.content.decode()
        detail_item = []
        '''
        [{'appr_org': '浙江省住房和城乡建设厅',
        'name1': '建筑装修装饰工程专业承包',
        'appr_date': '2016-04-26', 'cert_type': '',
        'name2': '一级',
        'valid_period': '2021-03-21'}]
        '''
        detail_list = json.loads(json_html)
        for dic in detail_list:
            d_item = {}
            d_item["cf_name"] = dic["name1"]
            d_item["cf_level"] = dic["name2"]
            d_item["cf_org"] = dic["appr_org"]
            d_item["b_date"] = dic["appr_date"]
            d_item["s_date"] = dic["valid_period"]
            detail_item.append(d_item)

        # print(detail_item)
        # print(type(detail_item))


        return detail_item

if __name__ == '__main__':
    pass
    # b = Sz()
    # li = b.get_detail()
    # print(li)
