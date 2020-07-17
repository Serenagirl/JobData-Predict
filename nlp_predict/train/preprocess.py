import pymysql
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
from nltk import collections
from wordcloud import WordCloud, STOPWORDS
# import plotly.express as px
# 以下配置请修改
user = "root"
password = "123456"

# 连接数据库
db = pymysql.connect(host="localhost", user=user, password=password, charset="utf8")

cursor = db.cursor()  # 使用cursor()方法获取操作游标

# cursor.execute("CREATE DATABASE `ujn_a` CHARACTER SET 'utf8';")
cursor.execute('USE `ujn_a`;')  # 使用execute方法执行SQL语句

cursor.execute("select id,  place, education, experience,MIN_PAY,MAX_PAY, description from job")
data = cursor.fetchall()

# id = 1
# # # 读取硬技能字典
# with open('./dict/chinese_keywords.txt', "r") as f:
#     chinese_skills = f.read()
# chinese_skills = chinese_skills.split('\n')
# demand = []
# for i in data:
#     # print(type(i[0]))
#     # description = i[0].replace('微信分享', '')
#     description = i[0].split('职能类别')
#     duty = description[0]
#     # print(duty)
#     templist = []
#     for key in chinese_skills:
#         if key in duty:
#             templist.append(key)
#     rule = re.compile(r'[a-zA-z]+')
#     demand = demand+rule.findall(duty)+templist
#
#
# print('开始')
# word_counts = collections.Counter(demand) # 对分词做词频统计
# word_counts_top40 = word_counts.most_common(40) # 获取前10最高频的词
# print(word_counts_top40)
# word_counts_top40 = [('数据库', 39224), ('测试', 30040), ('C', 24693),('Java', 22152), ('算法', 16498), ('SQL', 13032),
#                      ('Python', 12018), ('Linux', 10896), ('Oracle', 8411), ('Web', 8271), ('CSS', 8123),
#                      ('HTML', 8076),('逻辑思维', 7274), ('数学', 7252), ('机器学习', 7020),
#                      ('数据结构', 6906), ('数据分析', 6338), ('人工智能', 6012), ('JavaScript', 5794), ('MySQL', 5712),
#                      ('深度学习', 5616), ('Spring', 5592), ('统计', 5390),
#                      ('IT', 4965), ('建模', 4812), ('UI', 4772), ('linux', 4566), ('web', 4478), ('报告', 4307),
#                      ('NET', 4284), ('英语', 4240), ('PHP', 4093), ('数据挖掘', 3750),
#                      ('Android', 3293),('Hadoop', 3277), ('Server', 3168)]
# 词频统计
# #  做柱状图
# x = []
# y = []
# i = 0
# for word in word_counts_top40:
#     if i==20:
#         break
#     i += 1
#     x.append(word[0])
#     y.append(word[1])
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.bar(x, y)
# plt.show()
# print(type(data))
# print(data)
#获取技能列表
with open('./dict/keywords.txt', "r") as f:
    skills = f.read()
skills = skills.split('\n')
#获取城市列表
citys = ['西安', '长沙', '重庆', '合肥', '东莞', '无锡', '大连', '宁波', '乌鲁木齐', '西宁', '郑州',
         '太原', '贵阳', '海口', '拉萨','南昌', '石家庄', '上海', '呼和浩特', '成都', '昆明', '兰州',
         '北京', '重庆', '哈尔滨','沈阳', '长春',  '杭州', '福州', '济南', '广州', '武汉',
         '南宁', '银川', '南京', '苏州']
# 获取学历列表
educations = ['大专', '本科', '硕士', '在校生/应届生', '博士', '不限']
res = pd.DataFrame(columns=('place', 'education', 'experience', 'min_salary','max_salary', 'skills'))

for i in data:
    # 获取城市编码
    place = i[1]
    place_num = citys.index(place)
    # 获取学历编码
    education = i[2]
    if education not in educations:
        education_num = 5
    else:
        education_num = educations.index(education)
    experience_num = i[3]
    # 获取技能编码
    description = i[6].split('职能类别')
    duty = description[0]
    # print(duty)
    templist = []
    for key in skills:
        if key in duty:
            templist.append(key)
    description_num = templist
    # cell_list = (id, place_num, education_num, experience_num, description_num)
    res = res.append([{'place': place_num, 'education': education_num, 'experience':experience_num,'min_salary': i[4],
                       'max_salary': i[5], 'skills': description_num}], ignore_index=True)


# 构建技能列表
print(res.columns)
df_noskill = res.drop(['skills'], axis=1)
df_skill = pd.get_dummies(res['skills'].apply(pd.Series).stack()).sum(level=0)
df_update_all_num = pd.concat([df_noskill, df_skill], axis=1)
# df_update_all_num = df_update_all_num.reset_index(drop=True).dropna(0)
print('在')
print(df_update_all_num)
df_update_all_num.to_csv("predict_data.csv")














