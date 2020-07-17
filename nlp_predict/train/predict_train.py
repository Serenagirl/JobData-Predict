import matplotlib.pyplot as plt
import xgboost as xgb
import math
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd
#读取csv
read_csv = pd.read_csv("predict_data.csv", index_col=False)
# print(read_csv)
df1 = read_csv
df1['Web'] = df1['Web'].fillna('null')  # 将df中A列所有空值赋值为'null'
# print(df1)
df1 = df1[~df1['Web'].isin(['null'])]
# print(df1)

# 删除某行空值所在列
df2 = df1.copy()
df2[0:1] = df2[0:1].fillna('null')
# print(df2)
cols = [x for i, x in enumerate(df2.columns) if df2.iat[0, i] == 'null']
# print(cols)
df2 = df2.drop(cols, axis=0)
# df2 = df2[0:1000]
df_update_all_num = df2.drop(labels='Unnamed: 0', axis=1)
df_update_all_num = df_update_all_num.reset_index(drop=True)
# print(df_update_all_num)


def max_n_estimators(mm, start_n_estimators, max_n_estimators, step):
    RMSE_list = []
    n_estimators_list = []
    X = df_update_all_num[feature_names].values
    y = df_update_all_num[mm].values
    # print(X)
    # print(y)
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)
    # print(X_train.size)
    # print(y_train.size)
    for n_estimators in np.arange(start_n_estimators, max_n_estimators, step):
        xgb_model = xgb.XGBRegressor( objective="reg:squarederror", random_state=123, n_estimators = n_estimators)
        xgb_model.fit(X_train, y_train)
        y_pred = xgb_model.predict(X)
        mse = mean_squared_error(y, y_pred)
        n_estimators_list.append(n_estimators)
        RMSE_list.append(np.sqrt(mse))
        df = pd.DataFrame({'n_estimators_list': n_estimators_list,
        'RMSE_list': RMSE_list},
        columns = ['n_estimators_list', 'RMSE_list'])
    return df


feature_names = list(df_update_all_num.drop(columns=['min_salary', 'max_salary']).columns)
# df_nestimators_min = max_n_estimators('min_salary', 1000, 20000, 200)
# df_nestimators_max = max_n_estimators('max_salary', 1000, 20000, 200)
# print(df_nestimators_min)
# print(df_nestimators_max)
# import plotly.graph_objects as go
#
# line1 = go.Scatter(x=df_nestimators_min['n_estimators_list'][1:], y=df_nestimators_min['RMSE_list'][1:],
#                     # mode='markers',
#                     name='min_salary')  # name定义每条线的名称
# line2 = go.Scatter(x=df_nestimators_max['n_estimators_list'][1:], y=df_nestimators_max['RMSE_list'][1:],
#                     # mode='markers',
#                     name='max_salary')
# fig = go.Figure([line1, line2])
# # fig.update_layout(
# #     title = 'n_estimators', #定义生成的plot 的标题
# #     xaxis_title = 'DATE',		#定义x坐标名称
# #     yaxis_title = 'Weather'		#定义y坐标名称
# # )
# import plotly.offline as of  	# 这个为离线模式的导入方法
# of.plot(fig)
X = df_update_all_num[feature_names]
y = df_update_all_num['max_salary']
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test= train_test_split(X, y, test_size=0.2, random_state=123)
xgb_model_max = xgb.XGBRegressor(objective="reg:squarederror", random_state=123,n_estimators = 2000)
xgb_model_max.fit(X_train, y_train)
y_pred_max = xgb_model_max.predict(X)
mse=mean_squared_error(y, y_pred_max)
print('RMSE:',np.sqrt(mse))
print(xgb_model_max.score(X, y))
import pickle
pickle.dump(xgb_model_max, open('max_xgb.pickle', 'wb'))
X = df_update_all_num[feature_names]
y = df_update_all_num['min_salary']
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test= train_test_split(X, y, test_size=0.2, random_state=123)
xgb_model_min = xgb.XGBRegressor(objective="reg:squarederror", random_state=123, n_estimators = 2000)
xgb_model_min.fit(X_train, y_train)
y_pred_min = xgb_model_min.predict(X)
mse=mean_squared_error(y, y_pred_min)
print('RMSE:',np.sqrt(mse))
print(xgb_model_min.score(X, y))
pickle.dump(xgb_model_min, open('min_xgb.pickle', 'wb'))


