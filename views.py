from sqlalchemy import create_engine
import json
from django.http import HttpResponse
import six
from django.shortcuts import render
import numpy as np
import pandas as pd
import pickle

# Create your views here.

db_info = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'ujn_a'  # 这里我们事先指定了数据库，后续操作只需要表即可
}
# 使用绝对路径
xgb_model_min_loaded = pickle.load(open(r'C:\Users\1\Desktop\WorkAggregation-master\nlp_predict\model\min_xgb.pickle', "rb"))
xgb_model_max_loaded = pickle.load(open(r'C:\Users\1\Desktop\WorkAggregation-master\nlp_predict\model\max_xgb.pickle', "rb"))


sel_features = ['place', 'education', 'experience', 'C', 'CSS', 'HTML', 'Java', 'JavaScript',
                'Linux', 'MySQL', 'Oracle', 'Python', 'SQL', 'Web', '人工智能', '数学',
                '数据分析', '数据库', '数据结构', '机器学习', '测试', '算法', '逻辑思维']
skills = ['C','CSS','HTML','Java','JavaScript','Linux',
          ' MySQL','Oracle', 'Python','SQL', 'Web', '人工智能','数学','数据分析','数据库','数据结构','机器学习','测试',
          '算法', '逻辑思维']
#获取城市列表
citys = ['西安', '长沙', '重庆', '合肥', '东莞', '无锡', '大连', '宁波', '乌鲁木齐', '西宁', '郑州',
         '太原', '贵阳', '海口', '拉萨','南昌', '石家庄', '上海', '呼和浩特', '成都', '昆明', '兰州',
         '北京', '重庆', '哈尔滨','沈阳', '长春',  '杭州', '福州', '济南', '广州', '武汉',
         '南宁', '银川', '南京', '苏州']

# 获取学历列表
educations = ['大专', '本科', '硕士', '博士', '不限']
engine = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info,encoding='utf-8')
path = r'C:\Users\1\Desktop\datasite\datasite\test\static\data\single_skill_info.csv'
# Create your views here.

db_info = {
    'user':'root',
    'password':'123456',
    'host':'localhost',
    'database':'ujn_a'  # 这里我们事先指定了数据库，后续操作只需要表即可
}

engine = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info,encoding='utf-8')
DB_TABLE='job'

D_MULTI_SELECT ={
    '语言':'keyword',
    '技术':'title',

}

# sel_features = ['C', 'CSS', 'HTML', 'Java','JavaScript', 'Linux',' MySQL', 'Oracle', 'Python', 'SQL', 'Web',
#                     '人工智能', '数学', '数据分析', '数据库', '数据结构', '机器学习', '测试','算法', '逻辑思维']

D_LIST={
    '技能列表':'skill'
}
D_KEYWORD_PREDICT={
    'place': '北京',
    'education': '硕士',
    'experience': 2,
    'keywd': ['JAVA', 'C']
}

'''
预测主函数
'''
def predict(inputs_list):
    # 输入内容，list形式，包括place，education，experience，技能
    # inputlist是传入参数，形式为dict
    print('获取结果')
    print(type(inputs_list))
    data_average_min = 58115
    data_average_max = 90512

    place = citys.index(inputs_list['place'])
    education = educations.index(inputs_list['education'])
    experience = inputs_list['experience']
    inputs_list = inputs_list['keywd']
    def nyc_salary_with_skills(inputs_list):

        sample_list = [0] * (len(sel_features))
        input_X = pd.DataFrame([sample_list],
                               columns=list(sel_features))
        input_X['place'] = place
        input_X['education'] = education
        input_X['experience'] = experience
        for inputs in inputs_list:
            if inputs in list(input_X.columns):
                input_X[inputs] = 1

        salary = (int(xgb_model_min_loaded.predict(input_X)), int(xgb_model_max_loaded.predict(input_X)))
        return salary

    skill_money = {}
    skill_money_list = []
    for skill in sel_features[1:]:
        skill_money['skill'] = skill
        skill_money['salary'] = nyc_salary_with_skills([skill])
        skill_money_list.append(skill_money)
        skill_money = {}
    single_skill = pd.DataFrame(skill_money_list).sort_values('salary', ascending=False)

    def nyc_salary_with_skills_and(inputs_list):
        sample_list = [0] * (len(sel_features))
        input_x = pd.DataFrame([sample_list],
                               columns=list(sel_features))
        input_x['place'] = place
        input_x['education'] = education
        input_x['experience'] = experience
        for inputs in inputs_list:
            if inputs in list(input_x.columns):
                input_x[inputs] = 1
        salary_min = int(xgb_model_min_loaded.predict(input_x))
        salary_max = int(xgb_model_max_loaded.predict(input_x))
        # suggest skill with more salary
        suggest_list = []
        all_list = inputs_list
        for skill in single_skill['skill'][:10]:
            if skill not in inputs_list:
                suggest_list.append(skill)

            suggest_list_salary = {}
            suggest_list_salary_list = []
            for skill in suggest_list:
                all_list = []
                all_list = inputs_list + [skill]
                suggest_list_salary['skill'] = skill
                suggest_list_salary['salary'] = int(np.subtract(nyc_salary_with_skills(all_list),
                                                                nyc_salary_with_skills(inputs_list)).mean())
                suggest_list_salary_list.append(suggest_list_salary)
                suggest_list_salary = {}
        suggest_skills = pd.DataFrame(suggest_list_salary_list).sort_values('salary', ascending=True)
        suggest_skills = suggest_skills[suggest_skills['salary'] > 0]
        suggest_skills.columns = ['Skill', 'Salary_Increase']
        return {'Min_Salary': salary_min, 'Max_Salary': salary_max, 'Suggest_Skills': suggest_skills}

    salary_min = int(nyc_salary_with_skills_and(inputs_list)['Min_Salary'])
    salary_max = int(nyc_salary_with_skills_and(inputs_list)['Max_Salary'])
    Suggest_Skills = nyc_salary_with_skills_and(inputs_list)['Suggest_Skills']
    Suggest_Skills_Skills = Suggest_Skills['Skill'].to_json(orient='records')
    Suggest_Skills_SkillsSalary = list(Suggest_Skills['Salary_Increase'])
    min_Suggest_Skills_SkillsSalary = list(Suggest_Skills['Salary_Increase'])[0]
    max_Suggest_Skills_SkillsSalary = round(list(Suggest_Skills['Salary_Increase'])[-1],0)

    skill_info = pd.read_csv('C:/Users/1/Desktop/datasite/datasite/test/static/data/single_skill_info.csv', index_col=0).round(3)

    single_skill_info = skill_info[skill_info['name'].isin(inputs_list)]
    single_skill_info_names = list(single_skill_info['name'])
    single_skill_info_max = single_skill_info[['name','max']].to_dict('records')
    single_skill_info_avg = list(single_skill_info['avg'].values)
    single_skill_info_min = list(single_skill_info['min'].values)
    single_skill_info_max2 = list(single_skill_info['max'].values)
    single_skill_info_importance = list(single_skill_info['importance'].values)
    single_skill_info_avg_importance = np.array(single_skill_info[['avg','importance','name',]]).tolist()
    skill_info_avg_importance = np.array(skill_info[['avg','importance','name',]]).tolist()
    return salary_min, salary_max, Suggest_Skills_Skills, Suggest_Skills_SkillsSalary, min_Suggest_Skills_SkillsSalary, \
           max_Suggest_Skills_SkillsSalary, single_skill_info_names, single_skill_info_max, single_skill_info_avg, \
           single_skill_info_min, single_skill_info_max2, single_skill_info_importance, single_skill_info_avg_importance, \
           skill_info_avg_importance, Suggest_Skills, inputs_list, single_skill_info, data_average_min, data_average_max


def index(request):

    mselect_dict = {}
    for key, value in D_MULTI_SELECT.items():
        mselect_dict[key] = {}
        mselect_dict[key]['select'] = value
    sel_features_dict={}
    for key, value in D_LIST.items():
        sel_features_dict[key] = {}
        sel_features_dict[key]['options'] = skills
    sql = "SELECT DISTINCT place FROM job order by convert(job.place using gbk) collate gbk_chinese_ci asc"
    df = pd.read_sql_query(sql,engine)

    city_list = df.values.tolist()

    ci_li=[]
    for value in city_list:
        str2="".join(value)
        ci_li.append(str2)


    #predict
    salary_min, salary_max, Suggest_Skills_Skills, Suggest_Skills_SkillsSalary, min_Suggest_Skills_SkillsSalary, \
    max_Suggest_Skills_SkillsSalary, single_skill_info_names, single_skill_info_max, single_skill_info_avg, \
    single_skill_info_min, single_skill_info_max2, single_skill_info_importance, single_skill_info_avg_importance, \
    skill_info_avg_importance, Suggest_Skills, inputs_list, single_skill_info, data_average_min, data_average_max = predict(
        D_KEYWORD_PREDICT)
    context={
        'mselect_dict':mselect_dict,
        'ci_li':ci_li,
        'sel_features_dict':sel_features_dict,

        'Max_Salary': format(salary_max),
        'Min_Salary': format(salary_min),
         'Suggest_Skills':  format(Suggest_Skills),
        'Suggest_Skills_Skills': ["experience","Web","Java","MySQL","\u903b\u8f91\u601d\u7ef4","Linux","Python","\u4eba\u5de5\u667a\u80fd","\u7b97\u6cd5"],#format(Suggest_Skills_Skills),
        'Suggest_Skills_SkillsSalary': [168, 262, 1089, 1222, 1661, 3016, 3985, 4291, 5307],# format(Suggest_Skills_SkillsSalary),
        'max_Suggest_Skills_SkillsSalary': 5307,# format(max_Suggest_Skills_SkillsSalary),
        'min_Suggest_Skills_SkillsSalary ':  format(min_Suggest_Skills_SkillsSalary),
        'inputs_list': inputs_list,
        'single_skill_info': single_skill_info,
        'single_skill_info_max': format(single_skill_info_max),
        'single_skill_info_max2': format(single_skill_info_max2),
        'single_skill_info_avg': format(single_skill_info_avg),
        'single_skill_info_min': format(single_skill_info_min),
        'single_skill_info_importance': format(single_skill_info_importance),
        'single_skill_info_avg_importance': format(single_skill_info_avg_importance),
        'skill_info_avg_importance ': format(skill_info_avg_importance),
        'single_skill_info_names ': format(single_skill_info_names),
        'data_average_min ': format(data_average_min),
        'data_average_max ': format(data_average_max),
    }

    return render(request, 'display.html', context)


def search(request,column,kw):
    DB_TABLE='job'
    # sql = "SELECT DISTINCT %s FROM %s WHERE %s like '%%%s%%'" %(column,DB_TABLE,column,kw)
    sql = "SELECT DISTINCT %s FROM %s WHERE %s like '%%%%%s%%%%'" %(column,DB_TABLE,column,kw)
    try:
        df = pd.read_sql_query(sql,engine)
        l = df.values.flatten().tolist()
        results_list = []
        for element in l:
            option_dict = {
                'name':element,
                'value':element,
            }
            results_list.append(option_dict)
        res = {
            'success':True,
            'results':results_list,
            'code':200,
        }
    except Exception as e:
        res = {
            'success':False,
            'errMsg':e,
            "code":0,
        }
    print(res)
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json charset=utf-8")

def query(request):
    form_dict = dict(six.iterlists(request.GET))
    sql = sqlparse(form_dict)  # sql拼接
    print(sql)
    df = pd.read_sql_query(sql, engine)  # 将sql语句结果读取至Pandas Dataframe
    table = df.to_html(classes='ui grey selectable celled padded table',  # 指定表格css class为Semantic UI主题
                       table_id='ptable')
    context = {
        'ptable':table,
    }

    return HttpResponse(json.dumps(context, ensure_ascii=False),
                        content_type="application/json charset=utf-8")  # 返回结果必须是json格式

def sqlparse(context):
    print("**************************context*********************8")
    print(context)
    DB_TABLE='job'
    # sql = "Select * from %s Where education = '%s' And experience like '%%%%%s%%%%'" % \
    #       (DB_TABLE, context['EDUCATION_select'][0], context['EXPERIENCE_select'][0])  # 先处理单选部分
    sql = "Select keyword,title,place,salary,experience,education,welfare,companyname,description,pdate_time from %s Where place like '%%%%%s%%%%' And education like '%%%%%s%%%%' And experience like '%%%%%s%%%%'" % \
          (DB_TABLE, context['DIMENSION_select'][0],context['EDUCATION_select'][0], context['EXPERIENCE_select'][0])

    if (context['DIMENSION_select'][0]!=''):
        D_KEYWORD_PREDICT.update(place=context['DIMENSION_select'][0])
    if (context['EDUCATION_select'][0]!=''):
        D_KEYWORD_PREDICT.update(education=context['EDUCATION_select'][0])
    if (context['EXPERIENCE_select'][0]!=''):
        D_KEYWORD_PREDICT.update(experience=context['EXPERIENCE_select'][0])

    # 下面循环处理多选部分
    for k, v in context.items():
        if k not in ['csrfmiddlewaretoken', 'DIMENSION_select', 'EDUCATION_select', 'EXPERIENCE_select','list_select[]']:
            field_name = k[:-9]  # 字段名
            selected = v  # 选择项
            print(selected)
            sql = sql_extent(sql, field_name, selected)  #未来可以通过进一步拼接字符串动态扩展sql语句
    # 处理技能列表部分
    keywd = []
    for k,v in context.items():
        if k in ['list_select[]']:
            keywd = v


    D_KEYWORD_PREDICT.update(keywd=keywd)
    print(D_KEYWORD_PREDICT)
    return sql

def sql_extent(sql, field_name, selected, operator=" AND "):
    if selected is not None:
        statement = ''
        for data in selected:
            statement = statement + "'" + data + "', "
        statement = statement[:-2]
        if statement != '':
            sql = sql + operator + field_name + " in (" + statement + ")"
    return sql

def show(request):
    # analysis_main.Analyze.main()
    context={

    }
    return render(request,'show.html',context)

