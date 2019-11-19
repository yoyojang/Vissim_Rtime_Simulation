# 模拟数据，间隔往数据库存储交通数据
import pymysql
import datetime
import csv
import random
import time

## 1.交通流量模拟
def volume_make(path,time,data_table,cursor,conn):
    with open(path,encoding='utf-8-sig') as file:
        row = []
        reader = csv.reader(file)
        rows = [row for row in reader]  #转化为数组格式
    # print(rows)
    now_volume_list = rows[time.hour]

    sql = "insert into `{}` () values(%s,%s,%s)".format(data_table)
    total = []
    # INSERT INTO `volume_data` (`datetime`, `input_point`, `volume`) VALUES ('2019-10-09 20:03:47', '1', '2324')
    for i in range(len(now_volume_list)-1):
        each = []
        volume_random = int(int(now_volume_list[i+1]) * (1+random.uniform(-0.1,0.1)))
        each.append(time)
        each.append(i+1)
        each.append(volume_random)
        # print(each)
        total.append(each)
    # print(total)
    try:
        cursor.executemany(sql,total)
        conn.commit()
    except:
        print("无法插入流量")

## 2.交叉口转向比模拟
# INSERT INTO `route_rate` (`datetime`, `instruction`, `decision`, `movement`, `rate`) VALUES ('2019-10-10 17:00:38', '1', '2', '2', '3')
def rate_make(path,time,data_table,cursor,conn):
    sql = 'INSERT INTO `{}` () VALUES (%s, %s, %s, %s, %s)'.format(data_table)
    with open(path, encoding='utf-8-sig') as file:
        row = []
        reader = csv.reader(file)
        rows = [row for row in reader]
    total = []
    for i in range(len(rows[0])):
        each = []
        each.append(time)
        each.append(int(rows[0][i]))
        each.append(int(rows[1][i]))
        each.append(int(rows[2][i]))
        rate_random = float(float(rows[3][i]) * (1+random.uniform(-0.1,0.1)))
        each.append(rate_random)
        total.append(each)
    # print(total)
    try:
        cursor.executemany(sql,total)
        conn.commit()
    except:
        print("无法插入转向比")

def rate_make_real(path,time,data_table,cursor,conn,list):
    sql = 'INSERT INTO `{}`() VALUES (%s, %s, %s, %s, %s)'.format(data_table)
    # print(sql)
    with open(path, encoding='utf-8-sig') as file:
        row = []
        reader = csv.reader(file)
        rows = [row for row in reader]
    total = []
    for i in range(len(rows[0])):
        each = []
        each.append(time)
        instruction = int(rows[0][i])
        decision = int(rows[1][i])
        movement = int(rows[2][i])
        each.append(instruction)
        each.append(decision)
        each.append(movement)
        # print([instruction,decision] in list)
        if [instruction,decision] in list:
            real_volume,real = rate_real(time,movement)
            if real :
                each.append(real_volume)
            else:
                rate_random = float(float(rows[3][i]) * (1 + random.uniform(-0.1, 0.1)))
                each.append(rate_random)
            # print(each)
        else:
            rate_random = float(float(rows[3][i]) * (1+random.uniform(-0.1,0.1)))
            each.append(rate_random)
        total.append(each)
    # print(total)
    try:
        cursor.executemany(sql,total)
        conn.commit()
    except:
        print("无法插入转向比")

## 增加实际比例数据
# SELECT * FROM `TB_RADAR_QUEUEDATA` WHERE `Timestamp` BETWEEN '2019-10-10 18:00:00' AND '2019-10-10 19:00:00' AND `LaneNo` LIKE '%1%' LIMIT 0, 1000
def rate_real(time,lane):
    time_0 = time.strftime("%Y-%m-%d %H:%M:%S")
    time_1 = (time + datetime.timedelta(minutes= 59,seconds=59)).strftime("%Y-%m-%d %H:%M:%S")
    conn = pymysql.connect(host="172.192.10.75", user="its", password='3er4#ER$', database='WCDATA', charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT sum(Vehicle_Num) FROM `TB_RADAR_QUEUEDATA` WHERE `Timestamp` BETWEEN '{}' and '{}' and `LaneNo` = '{}' ".format(time_0,time_1,4-lane)
    # print(sql)
    try:
        cursor.execute(sql)
        rows = cursor.fetchone()
        # print(rows)
    except:
        print('error')
    if rows[0] is None:
        real = False
        volume = 0
    else:
        volume = float(rows[0]) / 100
        real = True
    return volume,real

    conn.close()
# rate_real('2019-09-20 13:23:36','2019-09-20 14:23:36')



conn = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test', charset='utf8')
cursor = conn.cursor()
volume_table = 'volume_data'
rate_table = 'route_rate'


now = datetime.datetime.now()
hour_now = now.hour
minu_now = now.minute
seco_now = now.second
micros_now = now.microsecond
first_time = now - datetime.timedelta(minutes=minu_now,seconds=seco_now,microseconds=micros_now)
# print(first_time)


volume_path = 'D:/Program/Vissim_Rtime_Simulation/00.csv'
rate_path = 'D:/Program/Vissim_Rtime_Simulation/02.csv'


real_volume_list = []
real_rate_list = [[3,8]]

n = 0
while n < 25:
    if n == 0:
        volume_make(volume_path, first_time, volume_table, cursor, conn)
        print(datetime.datetime.now(),'完成第{}次流量模拟输入。'.format(n+1))
        rate_make_real(rate_path, first_time, rate_table, cursor, conn, real_rate_list)
        print(datetime.datetime.now(), '完成第{}次转向比模拟输入。'.format(n + 1))
        time.sleep(3600 - minu_now*60 + seco_now)
        # time.sleep(60 - seco_now)
    else:
        first_time += datetime.timedelta(hours=1)
        volume_make(volume_path, first_time, volume_table, cursor, conn)
        print(datetime.datetime.now(), '完成第{}次流量模拟输入。'.format(n + 1))
        rate_make_real(rate_path, first_time, rate_table, cursor, conn, real_rate_list)
        print(datetime.datetime.now(), '完成第{}次转向比模拟输入。'.format(n + 1))
        time.sleep(3600)
    n += 1
#
# volume_make(volume_path,first_time,volume_table,cursor,conn)
# rate_make(rate_path,first_time,rate_table,cursor,conn)
# rate_make_real(rate_path,first_time,rate_table,cursor,conn,real_rate_list)       #历史与实际数据融合



conn.close()