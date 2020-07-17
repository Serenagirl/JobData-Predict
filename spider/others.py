class ZhiPinSpider(BaseSpider, metaclass=SpiderMeta):
    """BOSS直聘"""

    # 很容易封IP，所以间隔长一些
    request_sleep = 15

    def run(self):
        # 获取城市的编号构成链接
        print('zai')
        city_code = self._parse_city()
        if not city_code:
            self.logger.error('%s 不支持目标城市' % __class__.__name__)
            return
        search_url = 'https://www.zhipin.com/c' + city_code
        page = 1
        while True:
            print('zai')
            params = {'query': self.job, 'page': page, 'ka': 'page-%s' % page}
            resp = self.request('get', search_url, params=params)
            html = etree.HTML(resp.text)
            detail_urls = html.xpath('//div[@class="info-primary"]/h3/a/@href')
            if not detail_urls:
                if page == 1:
                    self.logger.error('%s 可能已被BAN' % __class__.__name__)
                break
            for each in detail_urls:
                yield self._parse_detail('https://www.zhipin.com' + each)
            page += 1

    def _parse_city(self):
        """从首页索引获取对应的城市编号"""
        index_url = 'https://www.zhipin.com/common/data/city.json'
        resp = self.request('get', index_url)
        city_code = re.findall(r'"code":(\d+),"name":"%s"' % self.city, resp.text)
        if city_code:
            return city_code[0]

    def _parse_detail(self, detail_url):
        resp = self.request('get', detail_url)
        html = etree.HTML(resp.text)
        title = html.xpath('//div[@class="info-primary"]/div[@class="name"]/h1/text()')
        if not title:
            if re.search(r'您暂时无法继续访问～', resp.text):
                self.logger.error('%s 可能已被BAN' % __class__.__name__)
                return
            self.logger.warning('%s 解析出错' % detail_url)
            return self._parse_detail(detail_url)
        result = {
            'title': title[0],
            'companyname': html.xpath('//div[@class="info-company"]/h3/a/text()')[0],
            'salary': html.xpath('//div[@class="info-primary"]/div[@class="name"]/span/text()')[0],
            'experience': html.xpath('//div[@class="info-primary"]/p/text()')[1].replace('经验：', ''),
            'education': html.xpath('//div[@class="info-primary"]/p/text()')[2].replace('学历：', ''),
            'url': detail_url,
            'description': html.xpath('string(//div[@class="job-sec"][1]/div)'),
            'keyword': self.job,
            'place': self.city,
             'welfare': 'none'
        }
        print(result)
        self.queue.put(result)
        return result

class BaiduSpider(BaseSpider, metaclass=SpiderMeta):
    """
    从百度百聘网站爬取招聘信息
    获取provider，keyword，title，city，salary，experience，education， number，welfare，update，url
    """
    request_sleep = 1

    def run(self):
        i = 0
        while True:
            url = 'http://zhaopin.baidu.com/api/qzasync?query={}&city={}&pcmod=1&pn={}&rn=50&sort_type=1'.format(
                self.job, self.city, i * 50)
            if i * 50 >= 760:
                return 'over'
            i = i + 1
            self.get_job_detail(url)

    def get_job_detail(self, url):
        html = self.request(url=url, method='get')
        try: dict1 = json.loads(html)
        except:
            time.sleep(3)
            return
        dict2 = dict1['data']['disp_data']

        for i in dict2:
            if 'jobfirstclass' not in i.keys():
                i['jobfirstclass'] = ''
            welfare = i['ori_welfare']
            result = {
                'provider': i['provider'],
                'keyword': self.job,
                'place': self.city,
                'title': i['title'],
                'salary': i['ori_salary'],
                'experience': i['ori_experience'],
                'education': i['ori_education'],
                'welfare': ''.join(welfare),
                'number': i['number'],
                'update_time': i['lastmod'],
                'url':  dict1['data']['urls'][0],
                'companyname': i['company']
            }
            print(result)
            self.queue.put(result)