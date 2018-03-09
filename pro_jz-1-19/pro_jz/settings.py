# -*- coding: utf-8 -*-

# Scrapy settings for pro_jz project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'pro_jz'

SPIDER_MODULES = ['pro_jz.spiders']
NEWSPIDER_MODULE = 'pro_jz.spiders'
# 启动全部spider
# COMMANDS_MODULE = 'cnblogs.commands'

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True

REDIS_URL = "redis://127.0.0.1:6379/6"

MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017

# log_file_path = "./scrapy.log"
#
# LOG_FILE = log_file_path
#
# LOG_LEVEL = "WARNING"

COOKIES_ENABLED = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DOWNLOAD_TIMEOUT = 100

DOWNLOAD_DELAY = 1

SPIDER_MIDDLEWARES = {
#    'pro_jz.middlewares.ProJzSpiderMiddleware': 543,

}

DOWNLOADER_MIDDLEWARES = {
   'pro_jz.middlewares.RrandomUA': 543,
   # 'pro_jz.middlewares.ProxyMiddleware': 544
}

ITEM_PIPELINES = {
   'pro_jz.pipelines.ProJzPipeline': 300,
}



USER_AGENTS = [
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"]


HTTPERROR_ALLOWED_CODES = [402]

# DEFAULT_REQUEST_HEADERS={
# "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
# "Accept-Encoding":"gzip, deflate",
# "Accept-Language":"zh-CN,zh;q=0.9",
# "Cache-Control":"max-age=0",
# "Connection":"keep-alive",
# "Host":"cx.jljsw.gov.cn",
# "Upgrade-Insecure-Requests":"1"
# }