import pymysql
import pyecharts
import datetime

def data_visual_1():
    conn_eval = pymysql.connect(host="localhost", user="root", password='123456', database='vissim_evaluation',
                                charset='utf8')
    cursor_trvtm = conn_eval.cursor()
    # cursor_edge = conn_eval.cursor()
    # cursor_node = conn_eval.cursor()
    # cursor_datacollection = conn_eval.cursor()

    #由于数据库只存在26、27/28，夜间评价数据，故模拟之前时段运行
    predent_now_time = datetime.datetime.now()-datetime.timedelta(days=3)+datetime.timedelta(hours=5)
    time_1 = predent_now_time - datetime.timedelta(minutes=5)

    strtime1 = datetime.datetime.strftime(time_1, '%Y-%m-%d %H:%M:%S')
    strtime2 = datetime.datetime.strftime(predent_now_time, '%Y-%m-%d %H:%M:%S')

    # print(strtime2,strtime1)
    #1.当前时段，某个路段，行驶方向，直接显示分段行程时间。（列表）,分段

    ##方向组合
    road_ziyun_we = [1,2,3,4] #紫云大道自西向东依次
    road_ziyun_ew = [5,6,7,8] #紫云大道自东向西依次
    sql_1 = "select * from traveltime where cre_time < " + "'" + strtime2 + "' and cre_time > " + "'" + strtime1 + "'"
    # print(sql_1)
    try:
        # 执行SQL语句
        cursor_trvtm.execute(sql_1)
        # 获取所有记录列表
        results_trvtm = cursor_trvtm.fetchall()
        # return results
        # print(results_trvtm)
    except:
        print("Error: unable to fecth data")

    traveltime_west_to_east = 0
    traveltime_east_to_west = 0
    for i in range(len(results_trvtm)):
        id = results_trvtm[i][1]
        if id in road_ziyun_we:
            traveltime_west_to_east += results_trvtm[i][3]
        else:
            traveltime_east_to_west += results_trvtm[i][3]

    print("紫云大道当前行程时间:自西向东:{},自东向西:{}".format(traveltime_west_to_east,traveltime_east_to_west))

    conn_eval.close()
    ###问题，会存在没有车经过，行程时间则为空，需通过历史弥补——通过判断循环取上一次的值，来弥补
# data_visual_1()

#2.每小时，同一路段，各模块的行程时间占比图（x-时间24h，y-同一时间段行程时间占比，百分比堆积柱形图，1h）
def data_visual_2():
    conn_eval = pymysql.connect(host="localhost", user="root", password='123456', database='vissim_evaluation',
                                charset='utf8')
    cursor_trvtm = conn_eval.cursor()
    # cursor_edge = conn_eval.cursor()
    # cursor_node = conn_eval.cursor()
    # cursor_datacollection = conn_eval.cursor()

    #由于数据库只存在26、27/28，夜间评价数据，故模拟之前时段运行
    predent_now_time = datetime.datetime.now()-datetime.timedelta(days=3)+datetime.timedelta(hours=5)
    time_1 = predent_now_time - datetime.timedelta(minutes=5)

    strtime1 = datetime.datetime.strftime(time_1, '%Y-%m-%d %H:%M:%S')
    strtime2 = datetime.datetime.strftime(predent_now_time, '%Y-%m-%d %H:%M:%S')

    # print(strtime2,strtime1)
    #1.当前时段，某个路段，行驶方向，直接显示行程时间。（列表）

    ##方向组合
    road_ziyun_we = [1,2,3,4] #紫云大道自西向东依次
    road_ziyun_ew = [5,6,7,8] #紫云大道自东向西依次
    sql_1 = "select * from traveltime where cre_time < " + "'" + strtime2 + "' and cre_time > " + "'" + strtime1 + "'"
    # print(sql_1)
    try:
        # 执行SQL语句
        cursor_trvtm.execute(sql_1)
        # 获取所有记录列表
        results_trvtm = cursor_trvtm.fetchall()
        # return results
        # print(results_trvtm)
    except:
        print("Error: unable to fecth data")

    traveltime_west_to_east = 0
    traveltime_east_to_west = 0
    for i in range(len(results_trvtm)):
        id = results_trvtm[i][1]
        if id in road_ziyun_we:
            traveltime_west_to_east += results_trvtm[i][3]
        else:
            traveltime_east_to_west += results_trvtm[i][3]

#3.描述单个交叉口流率比，旭日图 ，内环为进口道，外环为进口道转向（与该评价无关），轮播4个



#4.LOS列表/交叉口id/交叉口名称/等级
def data_visual_4():
    conn_eval = pymysql.connect(host="localhost", user="root", password='123456', database='vissim_evaluation',
                                charset='utf8')
    cursor_node = conn_eval.cursor()

    #由于数据库只存在26、27/28，夜间评价数据，故模拟之前时段运行
    predent_now_time = datetime.datetime.now()-datetime.timedelta(days=3)+datetime.timedelta(hours=5)
    time_1 = predent_now_time - datetime.timedelta(minutes=5)

    strtime1 = datetime.datetime.strftime(time_1, '%Y-%m-%d %H:%M:%S')
    strtime2 = datetime.datetime.strftime(predent_now_time, '%Y-%m-%d %H:%M:%S')

    sql_4 = "select * from node_movement where cre_time < " + "'" + strtime2 + "' and cre_time > " + "'" + strtime1 + "'"
    print(sql_4)
    try:
        # 执行SQL语句
        cursor_node.execute(sql_4)
        # 获取所有记录列表
        results_node = cursor_node.fetchall()
        # return results
        # print(results_node)
    except:
        print("Error: unable to fecth data")

    ###node_id对应交叉口名称
    instruction_node_LOS = {'紫云大道双麒路':0,'紫云大道永丰大道':0,'紫云大道永智路':0,'紫云大道运粮河西路':0}
    for i in results_node:
        if i[1] == 1:
            instruction_node_LOS['紫云大道双麒路'] = i[5]
        elif i[1] == 2:
            instruction_node_LOS['紫云大道永丰大道'] = i[5]
        elif i[1] == 3:
            instruction_node_LOS['紫云大道永智路'] = i[5]
        else:
            instruction_node_LOS['紫云大道运粮河西路'] = i[5]
    for name, level in instruction_node_LOS.items():  # 用items方法 k接收key ,v接收value
        print(name, level)

# data_visual_4()

#5.24小时（x）4个交叉口延误（y），实时增加，趋势预测
def data_visual_5():
    conn_eval = pymysql.connect(host="localhost", user="root", password='123456', database='vissim_evaluation',
                                charset='utf8')
    cursor_node = conn_eval.cursor()

    #由于数据库只存在26、27/28，夜间评价数据，故模拟之前时段运行
    predent_now_time = datetime.datetime.now()-datetime.timedelta(days=3)+datetime.timedelta(hours=3)
    # time_1 = predent_now_time - datetime.timedelta(minutes=5)

    # strtime1 = datetime.datetime.strftime(time_1, '%Y-%m-%d %H:%M:%S')
    strtime2 = datetime.datetime.strftime(predent_now_time, '%Y-%m-%d %H:%M:%S')
    print(strtime2)
    # sql_5 = "select nodeID,vehdelay from node_movement where cre_time < '{}'".format(strtime2)


    # print(sql_5_1)
    node_list = [1,2,3,4]
    node_list_vehdelay = []
    for i in node_list:
        sql_5 = "select vehdelay from node_movement where cre_time < '{}' and nodeID = {}".format(strtime2, i)
        # print((sql_5))
        try:
            # 执行SQL语句
            cursor_node.execute(sql_5)
            # 获取所有记录列表
            results_node_speed = cursor_node.fetchall()
            # return results
            # print(results_node_speed)
        except:
            print("Error: unable to fecth data")
        node_list_vehdelay.append(results_node_speed)
    # print(node_list_vehdelay[3][1][0])
    node_list_delay = []
    for i in range(4):
        node_num = []
        for j in range(len(node_list_vehdelay[i])):
            node_num.append(node_list_vehdelay[i][j][0])
        node_list_delay.append(node_num)
    for i in node_list_delay:
        print(len(i))

    sql_5_1 = "select cre_time from node_movement where cre_time < '{}' group by cre_time order by cre_time".format(strtime2)
    # print(sql_5_1)
    try:
        # 执行SQL语句
        cursor_node.execute(sql_5_1)
        # 获取所有记录列表
        results_node_time = cursor_node.fetchall()
        # return results
        # print(results_node_time)
    except:
        print("Error: unable to fecth data")
    results_node_time_str =[]
    for i in results_node_time:
        results_node_time_str.append(datetime.datetime.strftime(i[0],'%Y-%m-%d %H:%M:%S'))
    print(results_node_time_str)
    import pyecharts.options as opts
    # from pyecharts.faker import Faker
    from pyecharts.charts import Line
    def line_base() -> Line:
        c = (
            Line()
                .add_xaxis(results_node_time_str)
                .add_yaxis("紫云大道双麒路", node_list_delay[0])
                .add_yaxis("紫云大道永丰大道", node_list_delay[1])
                .add_yaxis("紫云大道永智路", node_list_delay[2])
                .add_yaxis("紫云大道运粮河西路", node_list_delay[3])
                .set_global_opts(title_opts=opts.TitleOpts(title="各交叉口延误"))
        )
        return c
    aa = line_base()
    aa.render('node_delay.html')
# data_visual_5()


#6.排放物（“绿色”），【交叉口，油耗，总排放废气，环保是否达标】
def data_visual_6():
    conn_eval = pymysql.connect(host="localhost", user="root", password='123456', database='vissim_evaluation',
                                charset='utf8')
    cursor_node = conn_eval.cursor()

    #由于数据库只存在26、27/28，夜间评价数据，故模拟之前时段运行
    predent_now_time = datetime.datetime.now()-datetime.timedelta(days=3)+datetime.timedelta(hours=5)
    time_1 = predent_now_time - datetime.timedelta(minutes=5)

    strtime1 = datetime.datetime.strftime(time_1, '%Y-%m-%d %H:%M:%S')
    strtime2 = datetime.datetime.strftime(predent_now_time, '%Y-%m-%d %H:%M:%S')
    print(strtime1,strtime2)
    sql_4 = "select * from node_movement where cre_time < '{}' and cre_time > '{}' order by nodeID".format(strtime2,strtime1)
    # print(sql_4)
    try:
        # 执行SQL语句
        cursor_node.execute(sql_4)
        # 获取所有记录列表
        results_node = cursor_node.fetchall()
        # return results
        print(results_node)
    except:
        print("Error: unable to fecth data")

    nodes_id_list = [1,2,3,4]
    green_eva = ([0,0,0],[0,0,0],[0,0,0],[0,0,0])
    # print(len(results_node))
    for i in range(len(results_node)):
        emissions = 0
        for j in range(4):
            x = j+8
            emissions += results_node[i][x]
        green_eva[i][0] = results_node[i][1]
        green_eva[i][1] = emissions
        green_eva[i][2] = results_node[i][11]
        print(results_node[i][1],emissions,results_node[i][11])
        # green_eva[i]=[results_node[i][1],emissions,results_node[i][11]]
    instruction_list = ['紫云大道双麒路', '紫云大道永丰大道', '紫云大道永智路', '紫云大道运粮河西路']
    for i in range(4):
        if green_eva[i][1]>300 or green_eva[i][2]>150:  #设定环保标准
            aa = "否"
        else:
            aa = "是"
        print('{}:{},{},{}'.format(instruction_list[i],green_eva[i][1],green_eva[i][2],aa))
# data_visual_6()

#7.车速仪表盘，计算上行、下行平均速度
def data_visual_7():
    conn_eval = pymysql.connect(host="localhost", user="root", password='123456', database='vissim_evaluation',
                                charset='utf8')
    cursor_datacollection = conn_eval.cursor()

    #由于数据库只存在26、27/28，夜间评价数据，故模拟之前时段运行
    predent_now_time = datetime.datetime.now()-datetime.timedelta(days=3)+datetime.timedelta(hours=5)
    time_1 = predent_now_time - datetime.timedelta(minutes=5)

    strtime1 = datetime.datetime.strftime(time_1, '%Y-%m-%d %H:%M:%S')
    strtime2 = datetime.datetime.strftime(predent_now_time, '%Y-%m-%d %H:%M:%S')
    # print(strtime1,strtime2)
    sql_7 = "select datacollectionID,speedavgarith from datacollection where cre_time < '{}' and cre_time > '{}' order by datacollectionID".format(strtime2,strtime1)
    print(sql_7)
    try:
        # 执行SQL语句
        cursor_datacollection.execute(sql_7)
        # 获取所有记录列表
        results_datacollection = cursor_datacollection.fetchall()
        # return results
        # print(results_datacollection)
    except:
        print("Error: unable to fecth data")
    sum_up = 0
    sum_down = 0
    for i in range(4):
        sum_up += results_datacollection[i][1]
        avg_up = sum_up / (i+1)
        sum_down += results_datacollection[i+4][1]
        avg_down = sum_down / (i+1)

    print('自西向东平均速度：{},自东向西平均速度：{}'.format(avg_up,avg_down))

data_visual_7()

#8.车速时空分布图