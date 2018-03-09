# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
from pymongo import MongoClient
import hashlib

class ProJzPipeline(object):
    def open_spider(self, spider):
        self.r = redis.Redis(host='127.0.0.1', port=6379, db=0)
        self.item_key = "item_dumpkey"
        client = MongoClient(host=spider.settings["MONGO_HOST"], port=spider.settings["MONGO_PORT"])
        # self.collection1 = client["bj_jz"]["company"]
        # self.collection2 = client["bj_pro"]["company"]
        # self.collection3 = client["sz_jz"]["company"]
        # self.collection4 = client["sz_pro"]["company"]
        self.collection5 = client["hn_cf"]["company"]
        self.collection6 = client["cq_jz"]["company"]
        self.collection7 = client["sx_jz"]["company"]


    def process_item(self, item, spider):

        if spider.name == 'sx_jz':
            print("+" * 20)
            with open("/home/python/Desktop/company/sx_company.csv", 'a') as f:
                for c in item["company_list"]:
                    f.write(c + '\n')
                print("保存成功!")

        elif spider.name == 'hn_cf':
            item_exit = self.item_dupfilter(item, spider)
            if not item_exit:
                print("1" * 50)
                self.collection5.insert_one(dict(item))
                with open("./hn_cf.csv", 'a') as f:
                    company = item["company"]
                    f.write(company + '\n')

        elif spider.name == 'cq_jz':
            print("+"*20)
            with open("/home/python/Desktop/company/cq_company2.csv", 'a') as f:
                for c in item["company_list"]:
                    f.write(c+'\n')
                    print("保存成功!")





    # 数据去重
    def item_dupfilter(self, item, spider):
        # if spider.name == 'bj_jz':
        #     f = hashlib.sha1()
        #     f.update(item["company_id"].encode())
        #     fingerprint = f.hexdigest()
        #     added = self.r.sadd(self.item_key, fingerprint)
        #     return added == 0
        if spider.name == 'sx_jz':
            f = hashlib.sha1()
            f.update(item["href"].encode())
            fingerprint = f.hexdigest()
            added = self.r.sadd(self.item_key, fingerprint)
            return added == 0
        elif spider.name == 'cq_jz':
            f = hashlib.sha1()
            f.update(str(item["company_id"]).encode())
            fingerprint = f.hexdigest()
            added = self.r.sadd(self.item_key, fingerprint)
            return added == 0

# bjz_jz专用管道
# class Szjz_Pipeline(object):
#     def open_spider(self, spider):
#         self.r = redis.Redis(host='127.0.0.1', port=6379, db=2)
#         self.item_key = "sz_item_dumpkey"
#         client = MongoClient(host=spider.settings["MONGO_HOST"], port=spider.settings["MONGO_PORT"])
#         self.collection3 = client["sz_jz"]["company"]
#
#     def process_item(self, spider, item):
#         item_exit = self.item_dupfilter(item, spider)
#         if not item_exit:
#             print("0" * 50)
#             self.collection3.insert_one(dict(item))
#             with open("./sz_company.csv", 'a') as f:
#                 company = item["company"]
#                 f.write(company + '\n')
#
#     def item_dupfilter(self, item, spider):
#         f = hashlib.sha1()
#         f.update(str(item["company_id"]).encode())
#         fingerprint = f.hexdigest()
#         added = self.r.sadd(self.item_key, fingerprint)
#         return added == 0

class Szpro_Pipeline(object):
    def open_spider(self, spider):
        self.r = redis.Redis(host='127.0.0.1', port=6379, db=2)
        self.item_key = "sz_item_dumpkey"
        client = MongoClient(host=spider.settings["MONGO_HOST"], port=spider.settings["MONGO_PORT"])
        self.collection4 = client["sz_pro"]["company"]

    def process_item(self, spider, item):
        item_exit = self.item_dupfilter(item, spider)
        if not item_exit:
            self.collection4.insert_one(dict(item))
            print("1" * 50)
            with open("./sz_company.csv", 'a') as f:
                company = item["company"]
                f.write(company + '\n')

    def item_dupfilter(self, item, spider):
        f = hashlib.sha1()
        f.update(str(item["pro_id"]).encode())
        fingerprint = f.hexdigest()
        added = self.r.sadd(self.item_key, fingerprint)
        return added == 0