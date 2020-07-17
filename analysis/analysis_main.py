import configparser
import os
import pymysql
import sys
from test.analysis import process_data,analyze_data


class Analyze():
    process_fn_list = []
    analyze_fn_list = []
    chart_fn_list = []

    conf = configparser.ConfigParser()

    # 以下配置请修改
    user = "root"
    password = "123456"

    # 连接数据库
    db = pymysql.connect(host="localhost", user=user, password=password, charset="utf8")

    cursor = db.cursor()  # 使用cursor()方法获取操作游标

    # cursor.execute("CREATE DATABASE `ujn_a` CHARACTER SET 'utf8';")
    cursor.execute('USE `ujn_a`;')  # 使用execute方法执行SQL语句

    path = os.getcwd().replace('\\', '/')

    @classmethod
    def main(cls):
        # script_path = os.path.realpath(__file__)
        # print(__file__)
        # script_dir = os.path.dirname(script_path)
        # sys.path.append(script_dir)

        # input_data.main()

        process_data.main()

        analyze_data.main()

    # test_analyze_data.main()

a=Analyze()
if __name__ == '__main__':
    a.main()