# -*- coding: utf-8 -*-
import configparser
import csv
import json
import os
import random
import threading
import time
from multiprocessing import Process, Queue
from threading import Thread
import re
import bs4
import requests
from lxml import etree
import signal
from tool import log, timer


class SpiderMeta(type):

    spiders = []

    def __new__(cls, name, bases, attrs):
        cls.spiders.append(type.__new__(cls, name, bases, attrs))
        return type.__new__(cls, name, bases, attrs)


class BaseSpider(object):

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/64.0.3282.119 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
    }

    request_sleep = 0.7
    _time_recode = 0
    number = 0

    def request(self, method='get', url=None, encoding=None, **kwargs):

        if not kwargs.get('headers'):
            kwargs['headers'] = self.headers

        if not kwargs.get('timeout'):
            kwargs['timeout'] = 5

        rand_multi = random.uniform(0.8, 1.2)
        interval = time.time() - self._time_recode
        if interval < self.request_sleep:
            time.sleep((self.request_sleep - interval) * rand_multi)

        resp = getattr(requests, method)(url, **kwargs)
        self._time_recode = time.time()

        self.number = self.number + 1

        if encoding:
            resp.encoding = encoding
        return resp.text


class Job51Spider(BaseSpider, metaclass=SpiderMeta):
    """
    爬取前程无忧网站数据
    从conf.ini读取citycode
    获取provider，keyword，title，city，salary，experience，education， number，welfare，update，url
    """
    request_sleep = 0

    def run(self):
        # conf = configparser.ConfigParser()
        # # 修改为绝对路径
        # conf.read(r'C:\Users\1\Desktop\WorkAggregation-master\WorkAggregation-master\spider\conf.ini')
        # citycode = conf['citycode'][self.city]
        page = 1
        # 获得总页数

        url = "https://search.51job.com/list/000000,000000,0000,01%252C37,9,99,{},2," \
        "{}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99" \
        "&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&" \
        "specialarea=00&from=&welfare=" .format(self.job, page)
        a = self.request(url=url, method='get', encoding='GBK')
        html = etree.HTML(a)
        # 获取包含总页数的一段字符串txt
        maxpage = "".join(html.xpath("//div[@class='dw_page']//div[@class='p_in']/span[1]/text()"))
        a = html.xpath('//*[@id="resultList"]/div[2]/div[4]/text()')
        # print('职位')
        # print(a)
        if a==[]:
            print('error')
            result = []
            self.queue.put(result)
            self.numbers.put(result)
            return
        n = int(a[0].replace('条职位','').replace('共',''))
        self.numbers.put(n)
        if  n == 0:
            print('error')
            result = []
            self.queue.put(result)
            self.numbers.put(result)
            return
        else:
            # print('总条数传入：')
            # print(self.numbers)
            # 从字符串txt提取总页数
            try:
                end_page = int(maxpage.split('页', 1)[0][1:])
                maxpage = end_page
                # print('最大页数：')
                # print(maxpage)
                # 解析页数
            except:
                time.sleep(3)
            while True:
                url = "https://search.51job.com/list/000000,000000,0000,01%252C37,9,99,{},2," \
                      "{}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99" \
                      "&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&" \
                      "specialarea=00&from=&welfare=".format(self.job, page)

                self.get_urls(url)
                log.printlog('多线程+' + str(page) + '页完成--' + self.job)
                page = page + 1
                print('page：')
                print(page)
                if page == maxpage + 1:
                    print('break')
                    break
            return'over'



    def get_urls(self, url):
        try:
            a = self.request(url=url, method='get', encoding='GBK')
            html = etree.HTML(a)
            urls = html.xpath('//*[@id="resultList"]/div[@class="el"]/p/span/a')
            if threading.activeCount() > 10:
                log.printlog(str(threading.activeCount()) + '线程存在，请注意检查程序外部阻塞原因')
                time.sleep(3)
            if self.threads:
                for i in urls:
                    t = threading.Thread(target=self.get_job_detail, args=(i.get('href'),))
                    t.start()
                    time.sleep(0.03)
            else:
                for i in urls:
                    self.get_job_detail(i.get('href'))
        except:
            time.sleep(2)
            self.get_urls(url)

    def get_job_detail(self, url):
        if 'jobs' not in url:
            return
        try:
            while True:
                try:
                    a = self.request(url=url, method='get', encoding='GBK')

                    html = etree.HTML(a)
                    break
                except:
                    time.sleep(3)
            try:
                pay = html.xpath('/ html / body / div[3] / div[2] / div[2] / div / div[1] / strong/text()')[0].strip()
            except:
                pay = ''
            list1 = html.xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/p[2]/@title')[0].split("|")

            list1 = [i.strip() for i in list1]
            if '招' in list1[2]:
                education = list1[1]
                experience = None
                number = list1[2]

                update_time = list1[3]

            else:
                education = list1[2]
                experience = list1[1]
                number = list1[3]

                update_time = list1[4]
                update_time = update_time.replace('发布', '')
                update_time = '2020-'+update_time

            result = {
                'keyword': self.job,
                'provider': '前程无忧网',
                'place': list[0],
                'title': html.xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/h1/text()')[0].strip(),
                'salary': pay,
                'experience': experience,
                'education': education,
                'description': html.xpath(' / html / body / div[3] / div[2] / div[3] / div[1] / div')[0].xpath(
                    'string(.)').strip().replace('"', '').strip().replace('\t', '').replace('\r', '').replace('\n', ''),
                'number': number,
                 'companyname': html.xpath('/html/body/div[3]/div[2]/div[4]/div[1]/div[1]/a[1]/p[1]/text()')[0].strip(),
                'update_time': update_time,
                'welfare': html.xpath('/html/body/div[3]/div[2]/div[2]/div[1]/div[1]/div')[0].xpath(
                    'string(.)').strip().replace('"', '').strip().replace('\t', '').replace('\r', '').replace('\n', ''),
                'url': url
            }
            self.queue.put(result)
            # print(result)
            return
        except:
            time.sleep(2)
            return

class LiePinSpider(BaseSpider, metaclass=SpiderMeta):
    """猎聘网"""

    def run(self):
        city_code = self._parse_city()
        if not city_code:
            self.logger.error('%s 不支持目标城市' % __class__.__name__)
            return
        url = 'https://www.liepin.com/zhaopin/'
        params = {
            'dqs': city_code,
            'key': self.job,
            'headckid': '7d66a97979abf7ec',
            'curPage': 0
            }

        control = True
        while control:
            resp = self.request('get', url, params=params)
            html = etree.HTML(resp.text)
            elements = html.xpath('//div[@class="job-info"]/h3/a')
            for each in elements:
                if '/job/' in each.get('href'):
                    if self.job.lower() in each.text.lower():
                        yield self._parse_detail(each.get('href').split('?')[0])
                    else:
                        control = False
            params['curPage'] += 1

    def _parse_city(self):
        index_url = 'https://www.liepin.com/citylist/'
        resp = self.request('get', index_url)
        city_index = re.findall(r'href="(/\w+/)"\stitle="%s' % self.city, resp.text)
        if city_index:
            search_url = 'https://www.liepin.com' + city_index[0]
            search_resp = self.request('get', search_url)
            city_code = re.findall(r'name="dqs"\svalue="(\d+)"', search_resp.text)[0]
            return city_code

    def _parse_detail(self, detail_url):
        resp = self.request('get', detail_url)
        html = etree.HTML(resp.text)
        title = html.xpath('//div[@class="title-info"]/h1/text()')
        if not title:
            self.logger.warning('%s 解析出错' % detail_url)
            return self._parse_detail(detail_url)
        result = {
            'title': title[0],
            'company': html.xpath('//div[@class="title-info"]/h3/a/text()')[0],
            'salary': html.xpath('//p[@class="job-item-title"]/text()')[0].strip(),
            'experience': html.xpath('//div[@class="job-qualifications"]/span[2]/text()')[0],
            'education': html.xpath('//div[@class="job-qualifications"]/span[1]/text()')[0],
            'url': detail_url,
            'description': html.xpath('string(//div[contains(@class,"job-description")]/div)')
        }
        self.queue.put(result)
        return result

# 自定义爬虫类可在这里添加


class SpiderProcess(Process):

    def __init__(self, numbers, data_queue, job, type, threads):
        Process.__init__(self)
        self.numbers = numbers
        self.data_queue = data_queue
        self.job = job
        self.type = type
        self.threads = threads

    def iter_spider(self, spider):
        setattr(spider, 'job', self.job)
        setattr(spider, 'threads', self.threads)
        setattr(spider, 'numbers', self.numbers)
        setattr(spider, 'queue', self.data_queue)
        error = 0
        result = spider.run()
        # print('error')
        # print(error)
        if result == 'over':
            error = error + 1
            print('爬虫可能已结束')
        if error == 5:
            log.printlog('%s-%s-%s- 爬虫已结束' % (spider.__class__.__name__, self.job))
            return

    def run(self):
        spiders = []

        if '51' in self.type:
            spiders.append(SpiderMeta.spiders[0]())
        if 'liepin' in self.type:
            spiders.append(SpiderMeta.spiders[1]())
        spider_count = len(spiders)
        threads = []
        for i in range(spider_count):
            t = Thread(target=self.iter_spider, args=(spiders[i],))
            t.setDaemon(True)
            t.start()
            threads.append(t)
        while True:
            if len([True for i in threads if i.is_alive() == False]) == spider_count:
                break
            time.sleep(2)

        # return


class WriterProcess(Process):
    """写数据进程"""

    def __init__(self, numbers, data_queue, type=None):
        Process.__init__(self)
        self.data_queue = data_queue
        self.numbers = numbers
        self.type = type

    def run(self):
        with open('data/test.csv', 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            num = self.numbers.get()
            # self.numbers = 103
            # print('总条数传出：')
            # print(num)
            id = 0
            # if num > 100:
            #     num = 100
            while True:
                if (id == num):
                    # print('实际:')
                    # print(id)
                    f.close()
                    return
                result = self.data_queue.get(timeout=10)
                # print(id)
                try:
                    if result:
                        row = [
                            result.get('provider'), result.get('keyword'), result.get('title'), result.get('place'),
                            result.get('salary'), result.get('experience'), result.get('education'),
                            result.get('description'), result.get('number'), result.get('companyname'),
                            result.get('update_time'), result.get('welfare'), result.get('url')
                        ]
                        writer.writerow(row)
                except:
                    # print('continue')
                    continue
                id = id + 1



def main():
    queue = Queue()
    numbers = Queue()
    dict_parameter = {'type': ['51'], 'time': False, 'hour': '8', 'minute': '20', 'date': '3', 'threads': True}

    #
    jobs = ['sql','区块链']
            # 'C++','自然语言处理', 'PHP','.NET', 'Hadoop', 'Python', 'Perl', 'Nodejs', 'Go', 'Javascript',
            #   'Java',  '软件开发', '图像处理', '人工智能', '深度学习', '机器学习', '数据',
            # '算法', '测试', '网络安全', '运维', 'UI',  '网络', '全栈', '硬件', 'Ruby']

    # citys = [ '西安', '长沙', '重庆', '合肥', '东莞', '无锡', '大连', '宁波', '乌鲁木齐', '西宁', '郑州',
    #           '太原', '贵阳', '海口', '拉萨','南昌', '石家庄', '上海',
    #           '北京', '重庆', '哈尔滨','沈阳', '长春',  '杭州', '福州','济南', '广州', '武汉', '成都', '昆明', '兰州',
    #          '南宁', '银川', '南京']

    with open('test.csv', 'a+', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['provider', 'keyword', 'title', 'place', 'salary', 'experience', 'education',
             'description', 'number', 'update_time', 'companyname', 'welfare', 'url'])
    if dict_parameter.get('threads'):
        threads = True
    else:
        threads = None
    no = 1
    # for city in citys:
    length = len(jobs)
    for job in jobs:
        if dict_parameter.get('time'):
            timer.main(beginhour=eval(dict_parameter.get('hour')[0]),
                       beginminute=eval(dict_parameter.get('minute')[0]),
                       begindate=eval(dict_parameter.get('date')[0]),)
        p1 = SpiderProcess(numbers, queue, job, type=dict_parameter.get('type'), threads=threads)
        p2 = WriterProcess(numbers, queue)
        p1.start()
        p2.start()
        # print('git1')
        p2.join()
        log.printlog(string=job + '爬取完成')
        p1.terminate()
        if no >= length :
            log.easypush('数据爬取完成')
            os.system('csvtotable ./data/test.csv ./templates/data.html')
            p2.terminate()
            return
        p1.join()
        no = no + 1


if __name__ == '__main__':
    main()
