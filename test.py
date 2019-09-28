import pymysql
import datetime
import win32com.client as com
import os
import time

# timemeasurement = #获取车辆出行时间模块列表
# nodes = #获取节点列表
# datacollections =  #获取数据采集组
# Vissim = com.gencache.EnsureDispatch("Vissim.Vissim")
Vissim = com.Dispatch("Vissim.Vissim")
Path_of_COM_Basic_Commands_network = os.path.abspath('F:/Development/Vissim_Rtime_Simulation/zsvissim')
Filename  = os.path.join(Path_of_COM_Basic_Commands_network, 'Road ziyun.inpx')
flag_read_additionally  = False
Vissim.LoadNet(Filename, flag_read_additionally)

def toList(NestedTuple):
    # function to convert a nested tuple to a nested list
    return list(map(toList, NestedTuple)) if isinstance(NestedTuple, (list, tuple)) else NestedTuple
Attribute = "Name"
NameOfLinks = Vissim.Net.Links.GetMultiAttValues(Attribute)
NameOfLinks = toList(NameOfLinks) # convert to list

end_time = 60*60*12
interval = 60*5
break_time = 0
n = 0
Vissim.Simulation.SetAttValue('SimPeriod', end_time)
# Vissim.Simulation.RunSingleStep()

conn = pymysql.connect(host="localhost", user="root", password='123456', database='traffic_test', charset='utf8')
cursor_vlm = conn.cursor()
cursor_rtr = conn.cursor()

conn_eval = pymysql.connect(host="localhost", user="root", password='123456', database='vissim_evaluation',
                            charset='utf8')
cursor_trvtm = conn_eval.cursor()
cursor_edge = conn_eval.cursor()
cursor_node = conn_eval.cursor()
cursor_datacollection = conn_eval.cursor()

start_time = time.time()
while break_time < end_time:
    n += 1
    break_time += interval
    # print(break_time)
    Vissim.Simulation.SetAttValue('SimBreakAt', break_time)




    time2 = datetime.datetime.now()
    time1 = time2 - datetime.timedelta(hours=1)
    strtime1 = datetime.datetime.strftime(time1,'%Y-%m-%d %H:%M:%S')
    strtime2 = datetime.datetime.strftime(time2,'%Y-%m-%d %H:%M:%S')

    sql_vlm = "select * from volume_data where datetime < "+"'"+strtime2+"' and datetime > "+"'"+strtime1+"'"
    sql_rtr = "select * from route_rate where datetime < "+"'"+strtime2+"' and datetime > "+"'"+strtime1+"'"
    try:
       # 执行SQL语句
       cursor_vlm.execute(sql_vlm)
       cursor_rtr.execute(sql_rtr)
       # 获取所有记录列表
       results_vlm = cursor_vlm.fetchall()
       results_rtr = cursor_rtr.fetchall()
       # return results
       # print(results_rtr[1])
    except:
       print("Error: unable to fecth data")
       break



    for i in range(len(results_vlm)):
        VI_number = results_vlm[i][1]
        new_volume = results_vlm[i][2]
        # print(new_volume)
        Vissim.Net.VehicleInputs.ItemByKey(VI_number).SetAttValue('Volume(1)', new_volume)

    for i in range(len(results_rtr)):
        instruction = results_rtr[i][1]
        decision = results_rtr[i][2]
        movement = results_rtr[i][3]
        rate = results_rtr[i][4]
        # print(instruction,decision,movement,rate)
        SVRD_number = results_rtr[i][2]  # SVRD = Static Vehicle Routing Decision
        SVR_number = results_rtr[i][3]  # SVR = Static Vehicle Route (of a specific Static Vehicle Routing Decision)
        new_relativ_flow = results_rtr[i][4]
        # print(new_relativ_flow)
        Vissim.Net.VehicleRoutingDecisionsStatic.ItemByKey(SVRD_number).VehRoutSta.ItemByKey(SVR_number).SetAttValue(
            'RelFlow(1)', new_relativ_flow)

    now = str(datetime.datetime.now())

    Vissim.Simulation.RunContinuous()

    every_endtime = time.time()
    print(every_endtime - start_time + break_time)

    #车辆行程时间
    sql_trvtm = "insert into traveltime() values(%s,%s,%s,%s,%s)"
    tmmsmts = [1, 2, 3, 4, 5, 6, 7, 8]
    TravTm = "TravTm(1,{},All)".format(n)
    Vehs = "Vehs(1,{},All)".format(n)
    DistTrav = "DistTrav(1,{},All)".format(n)
    for i in tmmsmts:
        # print(i)
        Veh_TT_measurement = Vissim.Net.VehicleTravelTimeMeasurements.ItemByKey(i)
        TT = Veh_TT_measurement.AttValue(TravTm)
        TV = Veh_TT_measurement.AttValue(Vehs)
        TD = Veh_TT_measurement.AttValue(DistTrav)
        values_trvtm = (now,i,TT,TV,TD)
        try:
            cursor_trvtm.execute(sql_trvtm, values_trvtm)
            conn_eval.commit()
        except:
            print("Error: unable to fecth data")



    # 节点数据
    Nodes_list = [1, 2, 3, 4]
    edges_list = []
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
    for i in Nodes_list:
        Node_Movement = Vissim.Net.Nodes.ItemByKey(i).Movements
        Edges = Node_Movement.GetMultiAttValues('Edges')
        for i in range(len(Edges)):
            add_item = Edges[i][1]
            if len(add_item) > 0:
                edges_list.append(add_item)

    sql_edge = "insert into edge_movement() values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    for i in edges_list:
        edge_movement = Vissim.Net.Edges.ItemByKey(i).Movement
        EQ = edge_movement.AttValue(Qlen)
        EQM = edge_movement.AttValue(QlenM)
        EV = edge_movement.AttValue(Vehs)
        EL = edge_movement.AttValue(LOSVal)
        EVD = edge_movement.AttValue(VehDelay)
        ES = edge_movement.AttValue(Stops)
        EEC = edge_movement.AttValue(EmissionsCO)
        EEN = edge_movement.AttValue(EmissionsNOx)
        EEV = edge_movement.AttValue(EmissionsVOC)
        EFC = edge_movement.AttValue(FuelConsumption)
        values_edge = (now,i,EQ,EQM,EV,EL,EVD,ES,EEC,EEN,EEV,EEC)
        try:
            cursor_edge.execute(sql_edge, values_edge)
            conn_eval.commit()
        except:
            print("Error: unable to fecth data")

    # 某节点综合指数
    sql_node = "insert into node_movement() values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    for i in Nodes_list:
        node = Vissim.Net.Nodes.ItemByKey(i).TotRes
        EQ = node.AttValue(Qlen)
        EQM = node.AttValue(QlenM)
        EV = node.AttValue(Vehs)
        EL = node.AttValue(LOSVal)
        EVD = node.AttValue(VehDelay)
        ES = node.AttValue(Stops)
        EEC = node.AttValue(EmissionsCO)
        EEN = node.AttValue(EmissionsNOx)
        EEV = node.AttValue(EmissionsVOC)
        EFC = node.AttValue(FuelConsumption)
        values_node = (now, i, EQ, EQM, EV, EL, EVD, ES, EEC, EEN, EEV, EEC)
        try:
            cursor_node.execute(sql_node, values_node)
            conn_eval.commit()
        except:
            print("Error: unable to fecth data")

    # 路段数据采集datacollection
    sql_datacollection = "insert into datacollection() values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    datacollections_list = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]
    Acceleration = "Acceleration(1,{},All)".format(n)
    Dist = "Dist(1,{},All)".format(n)
    Length = "Length(1,{},All)".format(n)
    Vehs = "Vehs(1,{},All)".format(n)
    QueueDelay = "QueueDelay(1,{},All)".format(n)
    SpeedAvgArith = "SpeedAvgArith(1,{},All)".format(n)
    SpeedAvgHarm = "SpeedAvgHarm(1,{},All)".format(n)
    OccupRate = "OccupRate(1,{},All)".format(n)

    for i in datacollections_list:
        datacollection = Vissim.Net.DataCollectionMeasurements.ItemByKey(i)
        DA = datacollection.AttValue(Acceleration)
        DD = datacollection.AttValue(Dist)
        DL = datacollection.AttValue(Length)
        DV = datacollection.AttValue(Length)
        DQ = datacollection.AttValue(QueueDelay)
        DSA = datacollection.AttValue(SpeedAvgArith)
        DSH = datacollection.AttValue(SpeedAvgHarm)
        DO = datacollection.AttValue(OccupRate)
        values_datacollection = (now,i,DA,DD,DL,DV,DQ,DSA,DSH,DO)
        try:
            cursor_datacollection.execute(sql_datacollection, values_datacollection)
            conn_eval.commit()
        except:
            print("Error: unable to fecth data")
endtime= time.time()
print(start_time-endtime)
# 关闭数据库连接
conn.close()
conn_eval.close()