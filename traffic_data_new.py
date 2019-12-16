import csv
import pymysql
import datetime
import time

volume_table = 'volume_data'
rate_table = 'route_rate'

sql_v = "insert into `{}` () values(%s,%s,%s)".format(volume_table)
sql_r = 'INSERT INTO `{}`() VALUES (%s, %s, %s, %s, %s)'.format(rate_table)

def csv_to_tuple(type,n,time):
    path = 'D:/Program/Vissim_Rtime_Simulation/{}/{}.csv'.format(type,n)
    with open(path)as f:
        f_csv = csv.reader(f)
        list = []
        for row in f_csv:
            each_list = []
            each_list.append(time)
            for i in row:
                each_list.append(i)
            list.append(each_list)
    return list



now = datetime.datetime.now()
hour_now = now.hour
minu_now = now.minute
seco_now = now.second
micros_now = now.microsecond
first_time = now - datetime.timedelta(minutes=minu_now,seconds=seco_now,microseconds=micros_now)

n = 0

while n < 24:
    conn = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test', charset='utf8')
    cursor = conn.cursor()

    now_each = datetime.datetime.now()
    volume_list = csv_to_tuple('VolumeList', now_each.hour, first_time)
    rate_list = csv_to_tuple('RateList', now_each.hour, first_time)
    # print(volume_list)
    # print(rate_list)
    if n == 0:
        try:
            cursor.executemany(sql_v, volume_list)
            conn.commit()
            print(now_each, '完成第{}次流量模拟输入。'.format(n + 1))
        except:
            print("无法插入流量")

        try:
            cursor.executemany(sql_r, rate_list)
            conn.commit()
            print(now_each, '完成第{}次转向比模拟输入。'.format(n + 1))
        except:
            print("无法插入转向比例")
        time.sleep(3600 - minu_now*60 + seco_now)
        # time.sleep(60 - seco_now)
    elif n == 23:
        break
    else:
        try:
            cursor.executemany(sql_v, volume_list)
            conn.commit()
            print(now_each, '完成第{}次流量模拟输入。'.format(n + 1))
        except:
            print("无法插入流量")

        try:
            cursor.executemany(sql_r, rate_list)
            conn.commit()
            print(now_each, '完成第{}次转向比模拟输入。'.format(n + 1))
        except:
            print("无法插入转向比例")

        time.sleep(3600)
    first_time += datetime.timedelta(hours=1)
    conn.close()
    n += 1


