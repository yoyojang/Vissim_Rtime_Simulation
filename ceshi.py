import pymysql
import csv
import datetime

conn = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test', charset='utf8')
cursor = conn.cursor()
sql = "insert into historic_volume() values(%s,%s,%s)"

file = open('00.csv',encoding='utf-8-sig')
his_volume = csv.reader(file)


total = []
for row in his_volume:

    for i in range(10):
        each = []
        a = datetime.datetime.strptime(row[0],'%H:%M:%S')
        each.append(a)
        each.append(i+1)
        each.append(row[i+1])
        print(each)
        total.append(each)
try:
    cursor.executemany(sql, total)
    conn.commit()
except:
    print("Error: unable to fecth data")

conn.close()

