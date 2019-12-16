import pymysql
import datetime
import win32com.client as com
import os
import time

# Set a signal controller program:
def set_progNo(SC_number,new_signal_programm_number):
    SignalController = Vissim.Net.SignalControllers.ItemByKey(SC_number)
    SignalController.SetAttValue('ProgNo', new_signal_programm_number)

def toList(NestedTuple):
    # function to convert a nested tuple to a nested list
    return list(map(toList, NestedTuple)) if isinstance(NestedTuple, (list, tuple)) else NestedTuple

# timemeasurement = #获取车辆出行时间模块列表
# nodes = #获取节点列表
# datacollections =  #获取数据采集组
instruction_id = [1,2,3,4]
#对应时间段的信号配时序号
instruction_1_signal_progno = [3,1,1,1,2,2,3,3]
instruction_2_signal_progno = [3,1,1,2,3,4,4,5]
instruction_3_signal_progno = [3,1,2,2,3,3,4,4]
instruction_4_signal_progno = [3,1,1,2,3,4,4,5]
#编辑对应配时文件
signal_Prog_file = [[1,'zs033.sig'],[2,'zs022.sig'],[3,'zs034.sig'],[4,'zs035.sig']]
Vissim = com.gencache.EnsureDispatch("Vissim.Vissim")
# Vissim = com.Dispatch("Vissim.Vissim")
Path_of_COM_Basic_Commands_network = os.path.abspath('D:/Program/Vissim_Rtime_Simulation/zsvissim')
Filename  = os.path.join(Path_of_COM_Basic_Commands_network, 'Road ziyun.inpx')
flag_read_additionally  = False
Vissim.LoadNet(Filename, flag_read_additionally)

#清理上次仿真结果
Attribute = "Name"
NameOfLinks = Vissim.Net.Links.GetMultiAttValues(Attribute)
NameOfLinks = toList(NameOfLinks) # convert to list

#设置仿真速度
Vissim.Simulation.SetAttValue('UseMaxSimSpeed', False)
Vissim.Simulation.SetAttValue('SimSpeed', 1)

total_end_time = 60*60*12
interval = 60*5

# Vissim.Simulation.SetAttValue('SimPeriod', total_end_time)
# Vissim.Simulation.RunSingleStep()

#连接本地交通数据输入库
conn = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test', charset='utf8')
cursor_vlm = conn.cursor()
cursor_rtr = conn.cursor()

#连接本地交通评价输出库 172.192.10.101 trsp
# conn_eval = pymysql.connect(host="localhost", user="root", password='123456', database='vissim_evaluation',charset='utf8')
conn_eval = pymysql.connect(host="172.192.10.101", user="root", password='123456', database='trsp',charset='utf8')
cursor_trvtm = conn_eval.cursor()
cursor_edge = conn_eval.cursor()
cursor_node = conn_eval.cursor()
cursor_datacollection = conn_eval.cursor()

#获取配时时段
instruction_signal_group = []
# conn_traffic_database = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test', charset='utf8')
# cursor = conn_traffic_database.cursor()
for i in instruction_id:
    sql = 'SELECT * FROM `instruction_signal_program` where `instructionID` = {}'.format(i)
    try:
        cursor_vlm.execute(sql)
        rows = cursor_vlm.fetchall()
        instruction_signal_group.append(rows)
    except:
        print("error:can't get signal program")

sql_time =  'SELECT `start_time` FROM `instruction_signal_program` group by start_time order by start_time'
try:
    cursor_vlm.execute(sql_time)
    period_list = cursor_vlm.fetchall()
except:
    print("error:can't get signal program start time")

conn.close()

period = [x[0].seconds for x in period_list]
period.insert(0,0)
period.insert(len(period)+1,86400)

# def period_each_time(period,now_time):
#     n = len(period) -1
#     i = 0
#     while i < n:
#         if period[i]<= now_time and period[i+1] > now_time:
#             run_first_time = period[i+1] - now_time
#             break
#         i += 1
#     return i, run_first_time

#设置周期区间
period_double = []
for i in range(len(period)-1):
    each = []
    each.append(period[i])
    each.append(period[i + 1])
    period_double.append(each)

#每个时间段间隔
each_time_list = []
for each_double in period_double:
    period_interval = each_double[1]-each_double[0]
    each_time_list.append(period_interval)


now = datetime.datetime.now()
hour_now = now.hour
minu_now = now.minute
seco_now = now.second
micros_now = now.microsecond

now_time = hour_now*3600 + minu_now*60 + seco_now

for i in range(len(period_double)):
    if now_time >= period_double[i][0] and now_time < period_double[i][1]:
        first_run_time = period_double[i][1]-now_time
        number = i

print("首次启动运行至下一阶段时间为：",first_run_time)

#整理开始时的阶段号 并循环。
initial_list = []
for i in range(len(period_double)):
    initial_list.append(i)

run_list = initial_list[number:] + initial_list[:number]


#评价SQL语句
sql_trvtm = "insert into traveltime() values(%s,%s,%s,%s,%s)"
sql_node = "insert into node_movement() values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
sql_edge = "insert into edge_movement() values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
sql_datacollection = "insert into datacollection() values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

total_start_time = datetime.datetime.now()
print("应用启动时间:",total_start_time)


cumu_num = 0
while cumu_num < len(period_double) and datetime.datetime.now().hour < 23:
    print('\n')

    if cumu_num == 0:
        end_time = first_run_time
    else:
        end_time = each_time_list[run_list[cumu_num]]

    Vissim.Simulation.SetAttValue('SimPeriod', end_time)
    print('本次仿真总时间：',end_time)
    progNo = []
    progNo.append(instruction_1_signal_progno[run_list[cumu_num]])
    progNo.append(instruction_2_signal_progno[run_list[cumu_num]])
    progNo.append(instruction_3_signal_progno[run_list[cumu_num]])
    progNo.append(instruction_4_signal_progno[run_list[cumu_num]])

    #下发配时序号
    for i in signal_Prog_file:
        # print(i[0])
        progNo_one = progNo[i[0]-1]
        set_progNo(i[0],progNo_one)
        # print(progNo_one)


    start_time = time.time()

    #间隔时间自增，循环判断
    n = 0
    break_time = 0
    while break_time < end_time:
        n += 1
        break_time += interval
        # 连接本地交通数据输入库
        conn = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test',
                               charset='utf8')
        cursor_vlm = conn.cursor()
        cursor_rtr = conn.cursor()
        # print(break_time)
        print("第{}阶段，第{}间隔，开始时间：{}".format(run_list[cumu_num],n,datetime.datetime.now()))

        #设置仿真间隔时间
        Vissim.Simulation.SetAttValue('SimBreakAt', break_time)

        #设置流量输入查询的时间段
        time2 = datetime.datetime.now()
        time1 = time2 - datetime.timedelta(hours=1)
        strtime1 = datetime.datetime.strftime(time1,'%Y-%m-%d %H:%M:%S')
        strtime2 = datetime.datetime.strftime(time2,'%Y-%m-%d %H:%M:%S')

        print("查询时段{}~{}".format(strtime1,strtime2))
        sql_vlm = "select * from volume_data where datetime between '{}' and '{}'".format(strtime1,strtime2)
        sql_rtr = "select * from route_rate where datetime between '{}' and '{}'".format(strtime1,strtime2)
        #启动查询，错误报错退出
        try:
           # 执行SQL语句
           cursor_vlm.execute(sql_vlm)
           # 获取所有记录列表
           results_vlm = cursor_vlm.fetchall()
           # return results
           # print(results_rtr[1])
        except:
           print("Error: unable to fecth data")
           break

        #启动查询，错误报错退出
        try:
           # 执行SQL语句
           cursor_rtr.execute(sql_rtr)
           # 获取所有记录列表
           results_rtr = cursor_rtr.fetchall()
           # return results
           # print(results_rtr[1])
        except:
           print("Error: unable to fecth data")
           break

        #遍历并设置各流量输入点
        volume_list = []
        for i in range(len(results_vlm)):
            VI_number = results_vlm[i][1]
            new_volume = results_vlm[i][2]
            volume_list.append(new_volume)
            # print(new_volume)
            Vissim.Net.VehicleInputs.ItemByKey(VI_number).SetAttValue('Volume(1)', new_volume)
        print('输入流量组为：',volume_list)


        #遍历并设置每个转向比
        rate_list = []
        for i in range(len(results_rtr)):
            instruction = results_rtr[i][1]
            decision = results_rtr[i][2]
            movement = results_rtr[i][3]
            rate = results_rtr[i][4]
            rate_list.append(rate)
            # print(instruction,decision,movement,rate)
            SVRD_number = results_rtr[i][2]  # SVRD = Static Vehicle Routing Decision
            SVR_number = results_rtr[i][3]  # SVR = Static Vehicle Route (of a specific Static Vehicle Routing Decision)
            new_relativ_flow = results_rtr[i][4]
            # print(new_relativ_flow)
            Vissim.Net.VehicleRoutingDecisionsStatic.ItemByKey(SVRD_number).VehRoutSta.ItemByKey(SVR_number).SetAttValue(
                'RelFlow(1)', new_relativ_flow)
        print('转向比为：',rate_list)

        conn.close()

        now = str(datetime.datetime.now())

        #启动仿真
        Vissim.Simulation.RunContinuous()

        every_endtime = time.time()
        # print(every_endtime - start_time + break_time)

        # 评价数据列表
        TravTm = "TravTm(1,{},All)".format(n)
        Vehs = "Vehs(1,{},All)".format(n)
        DistTrav = "DistTrav(1,{},All)".format(n)
        att1 = ['No', TravTm, Vehs, DistTrav]

        Qlen = "QLen(1,{})".format(n)
        QlenM = "QLenMax(1,{})".format(n)
        Vehs = "Vehs(1,{},All)".format(n)
        LOSVal = "LOSVal(1,{},All)".format(n)
        VehDelay = "VehDelay(1,{},All)".format(n)
        Stops = "Stops(1,{},All)".format(n)
        EmissionsCO = "EmissionsCO(1,{})".format(n)
        EmissionsNOx = "EmissionsNOx(1,{})".format(n)
        EmissionsVOC = "EmissionsVOC(1,{})".format(n)
        FuelConsumption = "FuelConsumption(1,{})".format(n)
        att2 = ['Node', 'Edges', Qlen, QlenM, Vehs, LOSVal, VehDelay, Stops, EmissionsCO, EmissionsNOx, EmissionsVOC,
                FuelConsumption]

        Acceleration = "Acceleration(1,{},All)".format(n)
        Dist = "Dist(1,{},All)".format(n)
        Length = "Length(1,{},All)".format(n)
        Vehs = "Vehs(1,{},All)".format(n)
        QueueDelay = "QueueDelay(1,{},All)".format(n)
        SpeedAvgArith = "SpeedAvgArith(1,{},All)".format(n)
        SpeedAvgHarm = "SpeedAvgHarm(1,{},All)".format(n)
        OccupRate = "OccupRate(1,{},All)".format(n)
        att3 = ['No', Acceleration, Dist, Length, Vehs, QueueDelay, SpeedAvgArith, SpeedAvgHarm, OccupRate]


        xi = [now]

        #车辆行程时间
        Veh_TT_measurement = Vissim.Net.VehicleTravelTimeMeasurements
        TravelTimeValue = Veh_TT_measurement.GetMultipleAttributes(att1)

        TravelTimeGroup = []
        for each in TravelTimeValue:
            xo = []
            xo = xi + list(each)
            TravelTimeGroup.append(xo)


        try:
            cursor_trvtm.executemany(sql_trvtm, TravelTimeGroup)
            conn_eval.commit()
        except:
            print("Error: unable to fecth data")

        # MOVEMENT
        NodeGroup = Vissim.Net.Nodes
        NodeEdgeTotalList = []
        for each in NodeGroup:
            NodeEdgeTotal = each.Movements.GetMultipleAttributes(att2)
            NodeEdgeTotalList += NodeEdgeTotal

        EdgesValueGroup = []
        NodesValueGroup = []
        EdgesValueGroup_each = [now]
        NodesValueGroup_each = [now]
        for each in NodeEdgeTotalList:
            EdgesValueGroup_each = [now]
            NodesValueGroup_each = [now]
            if each[1] == '':
                NodesValueGroup_each += each[0]
                NodesValueGroup_each += each[2:]
                NodesValueGroup.append(NodesValueGroup_each)
            else:
                EdgesValueGroup_each += each[1:]
                EdgesValueGroup.append(EdgesValueGroup_each)

        try:
            cursor_node.executemany(sql_node, NodesValueGroup)
            conn_eval.commit()
        except:
            print("Error: unable to fecth data")

        try:
            cursor_edge.executemany(sql_edge, EdgesValueGroup)
            conn_eval.commit()
        except:
            print("Error: unable to fecth data")


        # 路段数据采集datacollection
        Datacollection = Vissim.Net.DataCollectionMeasurements
        DatacollectionValue = Datacollection.GetMultipleAttributes(att3)
        DatacollectionGroup = []
        for each in DatacollectionValue:
            xo = []
            xo = xi + list(each)
            DatacollectionGroup.append(xo)

        try:
            cursor_trvtm.executemany(sql_datacollection, DatacollectionGroup)
            conn_eval.commit()
        except:
            print("Error: unable to fecth data")

        print(datetime.datetime.now())

    cumu_num += 1
    endtime= time.time()
    # print(start_time-endtime)
    print("第{}阶段，第{}间隔，结束时间：{}".format(run_list[cumu_num],n,datetime.datetime.now()))
# 关闭数据库连接
conn_eval.close()
print("应用结束时间：",datetime.datetime.now())