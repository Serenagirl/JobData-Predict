import pymysql
import re
def ways(func):


    def wrapper(*args, **kw):
        return func(*args, **kw)

    return wrapper

def main():
    global db,cursor
    user = "root"
    password = "123456"
    db = pymysql.connect(host="localhost", user=user, password=password, charset="utf8")
    cursor = db.cursor()
    cursor.execute('USE `ujn_a`;')



@ways
def job_del_null():
    # cursor.execute("update job set salary = '' where salary is null")
    # db.commit()
    cursor.execute("delete from job where salary=''")
    db.commit()
    #cursor.execute("update job set experience ='0年经验' where experience=''")
    #db.commit()
    cursor.execute("update job set education = '' where education is null")
    db.commit()
    #    !!!!!注意 特殊的值有 None null
    cursor.execute("update job set experience = '不限' where experience = 'None'")
    db.commit()
    cursor.execute("update job set experience = '1' where experience = '-1'")
    db.commit()
    cursor.execute("update job set experience = '不限' where experience = 'null'")
    db.commit()
    cursor.execute("update job set education = '不限' where education = ''")
    db.commit()
    cursor.execute("update job set welfare = '' where welfare is null")
    db.commit()
    cursor.execute("update job set education = '不限' where education like '%经验%'")
    db.commit()




@ways
def job1():
    cursor.execute("select experience,number from job")
    data = cursor.fetchall()
    id = 1
    for i in data:
        # 处理人数
        if i[1].isalpha():
            res = 0
            sql = "update job set number = " + str(res) + " where id = '%s'" % str(id)
            cursor.execute(sql)
            # db.commit()
        elif i[1].find('-') != -1:
            pattern = re.compile(r'\d+')
            res = re.findall(pattern, i[1])
            res = int((int(res[0]) + int(res[1])) / 2)
            sql = "update job set number = " + str(res) + " where id = '%s'" % str(id)
            cursor.execute(sql)
            # db.commit()
        else:
            pattern = re.compile(r'\d+')
            res = re.findall(pattern, i[1])
            sql = "update job set number = " + str(res[0]) + " where id = '%s'" % str(id)
            cursor.execute(sql)
            # db.commit()
        # 提经验值
        if i[0].isalpha():
            sql = "update job set experience = '0' where id = '%s'" % str(id)
            cursor.execute(sql)
            # db.commit()
        elif i[0].find('-') != -1:
            pattern = re.compile(r'\d+')
            res = re.findall(pattern, i[0])
            res = int((int(res[0]) + int(res[1])) / 2)
            sql = "update job set experience = " + str(res) + " where id = '%s'" % str(id)
            cursor.execute(sql)
            # db.commit()
        else:
            pattern = re.compile(r'\d+')
            res = re.findall(pattern, i[0])
            if len(res)==0:
                sql = "update job set experience = '0'"  + " where id = '%s'" % str(id)
            else:
                sql = "update job set experience = " + str(res[0]) + " where id = '%s'" % str(id)

            cursor.execute(sql)
            # db.commit()
        if int(id) % 100000 == 0:
            db.commit()
        print(id)
        id += 1
    db.commit()

    cursor.execute("SELECT number FROM job ")
    results = cursor.fetchall()
    sum = 0
    count = 0
    for row in results:
        if int(row[0]) != 0:
            sum += int(row[0])
            count += 1
    b = int(sum / count)
    print(b)
    id = 1
    for row in results:
        if int(row[0]) != 0:
            id += 1
            continue
        else:
            sql = "update job set number = " + str(b) + " where id = '%s'" % str(id)
            cursor.execute(sql)
        if int(id) % 100000 == 0:
            db.commit()
        print(id)
        id += 1
    db.commit()


@ways
def job2():
    cursor.execute('select salary from job ')
    data = cursor.fetchall()
    id = 1
    for i in data:
        pay = i[0]
        if pay.find('千') != -1 or pay.find('万') != -1 or pay.find('元') != -1:  # 如果为空值不处理，当字符串中存在千、万的时候就进行如下处理
            if pay.find('年') != -1:
                x = 12
            elif pay.find('天') != -1:
                x = 1 / 30
            else:
                x = 1
            if pay.find('千') != -1:
                if pay.find('-') != -1:
                    pay_min = pay.split('-')[0]
                    pay_max = pay.split('-')[1].split('千')[0]
                    min = float(pay_min) * 1000 / x
                    max = float(pay_max) * 1000 / x
                    ave = (min + max) / 2
                else:
                    min = max = ave = float(pay.split('千')[0]) * 1000 / x
            elif pay.find('万') != -1:
                if pay.find('-') != -1:

                    pay_min = pay.split('-')[0]
                    pay_max = pay.split('-')[1].split('万')[0]
                    min = float(pay_min) * 10000 / x
                    max = float(pay_max) * 10000 / x
                    ave = (min + max) / 2
                else:
                    min = max = ave = float(pay.split('万')[0]) * 10000 / x
            else:
                if pay.find('-') != -1:
                    pay_min = pay.split('-')[0]
                    pay_max = pay.split('-')[1].split('元')[0]
                    min = float(pay_min) / x
                    max = float(pay_max) / x
                    ave = (min + max) / 2
                else:
                    min = max = ave = float(pay.split('元')[0]) / x

            # sql语句是将min max ave放入数据库
            sql = "UPDATE job" \
                  " SET MIN_PAY=" + str(min) + ",MAX_PAY=" + str(max) + ",AVE_PAY=" + str(
                ave) + " WHERE id=" + str(id)
            cursor.execute(sql)

        if int(id) % 100000 == 0:
            db.commit()
        print(id)
        id += 1
    db.commit()