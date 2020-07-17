import pandas as pd
import pymysql
import jieba
import numpy as np
import json
from pyecharts import Line
from pyecharts import Overlap
from pyecharts import Funnel
from pyecharts import Bar
from pyecharts import Pie,configure
from pyecharts import EffectScatter,configure
from pyecharts import WordCloud


class Mysql():
    def __init__(self,db='ujn_a',usr='root',pw='123456'):
        try:
            self.conn = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user=usr,
                passwd=pw,
                db=db,
                charset='utf8')
        except:
            print("database connect failed!")
        self.cursor = self.conn.cursor()

    def execute_sql(self,sql):
        self.cursor.execute(sql)
        col = self.cursor.description
        result = self.cursor.fetchall()
        #df = pd.DataFrame(list(result))
        return result, col

    def __del__(self):
        self.conn.close()

class Chart():
    def __init__(self,db=Mysql()):
        self.db=db

    def get_top_ave_salary(self, kw_num=10):
        '''
        柱状图，得到平均薪资前kw_num的技能
        :param kw_num: 展示的技能数目
        :return:
        '''
        sql = 'select keyword,avg(ave_pay) from job group by keyword order by avg(ave_pay) desc;'
        res = self.db.execute_sql(sql)[0]
        columns = []
        data = []
        for i in range(min(len(res), kw_num)):
            columns.append(res[i][0])
            data.append(res[i][1])
        # print(res)

        bar = Bar()

        # 添加柱状图的数据及配置项
        bar.add("平均薪资", columns, data, xaxis_rotate=45)
        # 生成本地文件（默认为.html文件）
        bar.render(path="D:/编程练习题/datasite/test/templates/charts/salary.html")

    def get_top_ave_salary_place(self,kw_num=10):
        '''
        饼状图,得到薪资前kw_num的城市排名
        :param kw_num: 展示的城市数目
        :return:
        '''
        sql = 'select place, avg(ave_pay) from job group by place order by avg(ave_pay) desc'
        res = self.db.execute_sql(sql)[0]
        columns = []
        data = []
        for i in range(min(len(res), kw_num)):
            columns.append(res[i][0])
            data.append(res[i][1])

        # 设置主标题与副标题，标题设置居中，设置宽度为900
        pie = Pie(background_color='white',width=1000, height=600)
        # 加入数据，设置坐标位置为【25，50】，上方的colums选项取消显示
        pie.add("平均薪资", columns, data, center=[50, 50], is_legend_show=False)
        # 加入数据，设置坐标位置为【75，50】，上方的colums选项取消显示，显示label标签
        # 保存图表
        pie.render(path="D:/编程练习题/datasite/test/templates/charts/place.html")

    def get_top_major(self, kw_num=10):
        '''
        南丁格尔玫瑰图，展示热门专业所占的比例
        :param kw_num: 展示的热门专业数目
        :return:
        '''
        sql = 'select keyword, sum(number) from job group by keyword order by sum(number) desc'
        res = self.db.execute_sql(sql)[0]
        columns = []
        data = []
        for i in range(min(len(res), kw_num)):
            columns.append(res[i][0])
            data.append(res[i][1])

        configure(output_image=True)
        pie = Pie(background_color='white',width=1000, height=600,page_title='rose')
        pie.add('热门专业', columns, data, center=[25, 50], radius=[30, 75], rosetype='radius')
        # pie.add('area', columns, data, center=[75, 50], radius=[30, 75], rosetype='area')

        # 圆环中的玫瑰图
        pie.add('热门方向', columns, data, radius=[65, 75], center=[75, 50])
        pie.add('热门方向', columns, data, radius=[0, 60], center=[75, 50], rosetype='area')
        print(__file__)

        print('****')
        filepath = 'D:/编程练习题/datasite/test/templates/charts/top_major.html'
        pie.render(path=filepath)

        # es = EffectScatter('散点图', background_color='white', title_text_size=25)
        # es.add('热门专业散点图', data, data, symbol='pin', effect_scale=5.5, xaxis_min=10)
        # es.render(path='top_major.html')

    def get_top_skill(self,funnel_num=9):
        jieba.load_userdict('D:/编程练习题/datasite/test/analysis/user_dict.txt')

        unuse_keywords = ['开发', '工程师', ')', '(', ' ', '（', '）', '高级', '编号', '.', ':', '/', '：', '-', '职位', '+', '、',
                          '，', '实习生', '..', '*', '_', '[', ']', '东莞', '3', '2', '二', '01', ',', '，', '2020', '一', '\\',
                          '8k', '呼和浩特', '内蒙古', '07', 'ZHGAly'
            , 'J11797', '04', '05', '03', 'J11797', 'ZHGAljw', 'J11959', 'J12619', '对', '003', '002', '苏州', '&', '02',
                          '.', '急聘', '应届生', '实习生', '月', '日'
            , '初级', '高级', '区域', '资深', '岗', '10', '实习', '五险一金', '讯飞', '大', '12K', '8K', '可', '双休', '出差', '平台', '福州',
                          '方向', '北京', '推广'
            , '中级', '助理', '千', '总监', '客服', '客户', '省区', '与', '驻场', '合伙人', '商务', '专家', '讲师', '#', 'J11804', '年薪', '上市公司',
                          '10W', '锁'
            , '员', '休闲', '娱乐', '医疗', '现场', '公安', '政府', '底薪', '负责人', '人事', '老师'
            , '五险', '一金', '重庆', '高新', '毕业生', '应届', '编程', '包', '合肥', '长期', '咨询', '师', '售后'
            , '小', '年', '程序员', 'RJ002', '号', '001', '个', '郑州', '武汉', '万', '招聘', '代表', '渠道', '4', '6', 'S', 'Y', '7',
                          '5', '不'
            , '急', '++', '西安']
        d = {}
        sql = 'select title,number from job'
        self.db.cursor.execute(sql)
        result = self.db.cursor.fetchall()
        for r in result:
            tmp = jieba.lcut(r[0])
            for skill in tmp:
                if skill in unuse_keywords:
                    continue
                if skill == '软件工程师':
                    skill = '软件开发'
                if skill not in d.keys():
                    d[skill] = 0
                d[skill] += int(r[1])
        wordcloud = WordCloud(width=1000, height=600)
        wordcloud.add("", d.keys(), d.values(), word_size_range=[20, 100])
        wordcloud.render(path="D:/编程练习题/datasite/test/templates/charts/wordcloud.html")

        d_order = sorted(d.items(), key=lambda x: x[1], reverse=True)
        d_order=dict(d_order[0:funnel_num])
        configure(output_image=True)
        funnel = Funnel(background_color='white', title_text_size=20, title_pos='center',width=1000, height=600)
        funnel.add('教育', d_order.keys(), d_order.values(), is_label_show=True, label_pos='inside', is_legend_show=False)
        funnel.render(path='D:/编程练习题/datasite/test/templates/charts/career_funnel.html')

    def get_welfare_wordcloud(self):
            '''
            福利的词云
            :return:
            '''
            jieba.load_userdict('D:/编程练习题/datasite/test/analysis/welfare_dict.txt')
            sql = 'select welfare from job'
            res = self.db.execute_sql(sql)[0]
            unuse_keywords = ['二', '2', '好', '可', ' ', ',', '[', ']', '#', '，', 'x', 'h', '=', 's', '!', '+', '.', ':',
                              '、',
                              'd', 'in', '~', '上'
                , '宿', '享', 'order', '(', ')', '广', '/', '17', '-', '原']
            d = {}
            for r in res:
                tmp = jieba.lcut(r[0])
                for s in tmp:
                    if s in unuse_keywords:
                        continue
                    if s not in d.keys():
                        d[s] = 0
                    d[s] += 1

            # d_order=sorted(d.items(),key=lambda x:x[1],reverse=True)
            # for s in d_order:
            #     print(s)
            wordcloud = WordCloud(width=1300, height=620)
            wordcloud.add("", d.keys(), d.values(), word_size_range=[20, 100])
            wordcloud.render(path="D:/编程练习题/datasite/test/templates/charts/welfare.html")

    def get_number_experience(self, kw_num=10):
            sql = 'select experience, sum(number) from job group by experience order by sum(number) desc'
            res = self.db.execute_sql(sql)[0]
            columns = []
            data = []
            for i in range(min(len(res), kw_num)):
                columns.append(res[i][0])
                data.append(res[i][1])

            es = EffectScatter(background_color='white', title_text_size=25, width=1000, height=600)
            es.add('工作经验与需求散点图', columns, data, symbol='triangle', effect_scale=5.5)
            es.render(path="D:/编程练习题/datasite/test/templates/charts/number.html")

    def get_all_data(db=Mysql(), experience='%%', place='%%', eduation='%%'):
        '''
        获取数据库中的内容，返回json对象
        :param db: 数据库对象
        :param experience: 工作经验
        :param place: 工作地
        :param eduation: 教育程度
        :return: json对象
        '''
        sql = "select * from job where " \
              "experience like '%%%%%s%%%%' and" \
              " place like '%%%%%s%%%%' and " \
              "education like '%%%%%s%%%%'" % (experience, place, eduation)
        result = db.execute_sql(sql)[0]
        jsonData = []
        for r in result:
            tmp = {}
            tmp['provider'] = r[0]
            tmp['keyword'] = r[1]
            tmp['title'] = r[2]
            tmp['place'] = r[3]
            tmp['salary'] = r[4]
            tmp['experience'] = r[5]
            tmp['education'] = r[6]
            tmp['description'] = r[7]
            tmp['number'] = r[8]
            tmp['welfare'] = r[9]
            tmp['pdate_time'] = str(r[10])
            tmp['url'] = r[11]
            tmp['work'] = r[14]
            tmp['companyname'] = r[15]
            tmp['id'] = r[16]
            jsonData.append(tmp)
        jsonData = json.dumps(jsonData, ensure_ascii=False)
        return jsonData
def main():
    mysql = Mysql(db='ujn_a', usr='root', pw='123456')
    chart = Chart(mysql)

    chart.get_top_skill(funnel_num=19)
    chart.get_top_major()
    chart.get_number_experience()
    chart.get_welfare_wordcloud()
    chart.get_top_ave_salary_place()
    chart.get_top_ave_salary()
if __name__ == '__main__':
        main()