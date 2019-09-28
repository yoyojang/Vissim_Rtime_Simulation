import pymysql
import time

conn_in = pymysql.connect(host="172.192.10.75", user="its", password='3er4#ER$', database='WCDATA', charset='utf8')
conn_ = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test', charset='utf8')
cursor_in = conn_in.cursor()
cursor_out = conn_out.cursor()

now_time = time.time()

interval_time = 60*60

end_time = 0

sql_in = "SELECT * FROM `TB_RADAR_QUEUEDATA` WHERE `Timestamp` BETWEEN '{0}'AND '{1}'".format(time_1_str,time_2_str)
sql_out = 'insert into route_rate() values(%s,%s,%s,%s,%s)'

try:
    cursor_in.execute(sql_in)
    result = cursor_in.fetchall()
except:
    print('error')

while time.time() < (start_time + 60*60*12+1):
    print(1)
    time.sleep(60*5)

