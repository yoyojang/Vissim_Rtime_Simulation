# 在整点刚过些时候开始运行


import pymysql
import time

conn_in = pymysql.connect(host="172.192.10.75", user="its", password='3er4#ER$', database='WCDATA', charset='utf8')
conn_out = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test', charset='utf8')
cursor_in = conn_in.cursor()
cursor_out = conn_out.cursor()

# now_time = time.time()

# interval_time = 60*60
#
# end_time = 0


interval = 60 * 60

nowtime = time.time()
time_2 = nowtime- nowtime % interval
time_1 = time_2 - interval
time_1_str = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time_1))
time_2_str = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time_2-1))

sql_in = "SELECT * FROM `TB_RADAR_QUEUEDATA` WHERE `Timestamp` BETWEEN '{0}'AND '{1}'".format(time_1_str,time_2_str)
sql_out = 'insert into route_rate() values(%s,%s,%s,%s,%s)'

try:
    cursor_in.execute(sql_in)
    result_in = cursor_in.fetchall()
except:
    print('error')

# while time.time() < (start_time + 60*60*12+1):
#     print(1)
#     time.sleep(60*5)

volume_lane = [0,0,0]
for i in range(len(result_in)):
    if result_in[i][4] == '1':
        volume_lane[0] += result_in[i][5]
    elif result_in[i][4] == '2':
        volume_lane[1] += result_in[i][5]
    else:
        volume_lane[2] += result_in[i][5]

value_out = [(),(),()]
for i in range(3):
    value_out[i] = (time_1_str,3,8,i+1,volume_lane[i])  #雷达数据为永丰大道东进口，三个车道由外向中间分别为1,2,3

try:
    cursor_out.executemany(sql_out, value_out)
    conn_out.commit()
except:
    conn_out.rollback()
    print('error')
