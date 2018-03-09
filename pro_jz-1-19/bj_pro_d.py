# coding=utf-8
import requests
from lxml import etree
import re

class Bj_pro_d(object):

    def __init__(self,pro_id):
        self.headers = {
            "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)"
        }
        self.detail_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceView.do?performanceId={}".format(pro_id)
        # self.detail_url = "http://xpt.bcactc.com/G2/basic/gfm/info!entPerformanceView.do?performanceId=8a8085cb60e4c91c0160e9a598a72c90"
        # 详情页下载
    def get_detail(self):
        ret = requests.get(self.detail_url,headers = self.headers)
        html = etree.HTML(ret.content.decode())
        detail_item = []
        detail_list = html.xpath("//div[@style='width:85%;margin:10px auto;']/div[1]//text()")# 工程编号
        for d in detail_list:
            p = re.compile('\s+')
            n_d = re.sub(p,'',d)
            if len(n_d)>0:
                detail_item.append(n_d)

        # 资料下载
        detail_dow = html.xpath("//div[@style='width:85%;margin:10px auto;']/div[2]//tr")
        for d in detail_dow:
            # http://xpt.bcactc.com/upload/20180112/15157485418733522.pdf
            dow_item = {}
            title = d.xpath('.//a/text()')
            dow_item["title"]=title[0] if len(title)>0 else ''
            href = d.xpath('.//a/@href')
            dow_item["href"] = 'http://xpt.bcactc.com'+href[0] if len(href) > 0 else ''
            detail_item.append(dow_item)

        return detail_item

if __name__ == '__main__':
    id = '8a8085cb60e4c91c0160e9a598a72c90'
    b = Bj_pro_d(id)
    li = b.get_detail()
    print(li)
