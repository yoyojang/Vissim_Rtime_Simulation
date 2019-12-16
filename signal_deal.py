# COM-Server
import win32com.client as com
import os
import xml.etree.ElementTree as ET
import datetime
from dateutil.parser import parse
import time

Vissim = com.Dispatch("Vissim.Vissim")
# Path_of_COM_Basic_Commands_network = os.getcwd() #'C:\\Users\\Public\\Documents\\PTV Vision\\PTV Vissim 11\\Examples Training\\COM\\Basic Commands\\'
Path_of_COM_Basic_Commands_network = os.path.abspath('F:\Development\DataInOut\zsvissim')

## Load a Vissim Network:
Filename                = os.path.join(Path_of_COM_Basic_Commands_network, 'zs03.inpx')
flag_read_additionally  = False # you can read network(elements) additionally, in this case set "flag_read_additionally" to true
Vissim.LoadNet(Filename, flag_read_additionally)

## Load a Layout:
Filename = os.path.join(Path_of_COM_Basic_Commands_network, 'zs03.layx')
Vissim.LoadLayout(Filename)
#仿真参数设置
Vissim.Simulation.SetAttValue('SimPeriod', 600)
Vissim.Simulation.SetAttValue('NumRuns', 1)
Vissim.Simulation.SetAttValue('SimSpeed', 1)

#计算信号配时起始时刻
#通过视频观看，人工读取数据，当图片中某个灯亮绿灯时，记录该时刻，及明确该绿灯启亮是第几个group
#采集图片中南北左转（即第二group）起始时刻为17:37:06
#信号配时：南北33 28 43 23 周期127


#计算周期开始时刻
def signal_start_time(pic_time,signal_period,signal_group):
    pc_time = datetime.datetime.strptime(pic_time,"%H:%M:%S")
    # pc_time = parse("17:37:06")
    time_1 = 0
    for n  in range(len(signal_group)-signal_period+1):
        time_1 = time_1 + signal_group[n+signal_period-1]
    # print(time_1)
    #加time_1秒
    start_time = pc_time + datetime.timedelta(seconds=time_1)
    return start_time

#计算相位差
def start_offset(time_now,start_time,cycle):
    interval =(time_now - start_time).seconds
    offset =cycle - (interval % cycle)   #取余数
    print(offset)
    return offset


#设置.sig文件
def sig_file_offset(path,name,progNo,offset):
    file_path = os.path.abspath(path)
    file = os.path.join(file_path,name)
    signal_file = ET.parse(file)
    tree = signal_file.getroot()
    program_list = tree.find('progs')
    program = program_list.findall('prog')
    signal = program[progNo - 1]
    offset_str = str(offset*1000)
    signal.set('offset', offset_str)
    signal_file.write(file)
    print('相位差设置成功')

## 已知参数
# 图片时间
pic_time = "17:30:12"
# 图片中信号灯对应的开始阶段号
signal_period = 1
#仿真信号.sig文件位置
path = "F:/Development/DataInOut/zsvissim"
name = 'zs022.sig'
#配时方案,后续开发根据时段获取配时方案
progNo = 4
cycle = 127
signal_group = [33,28,43,23]   #南北直、南北左、东西直、东西左,包含黄灯



start_time = signal_start_time(pic_time,signal_period,signal_group)

#仿真启动时刻
time_now = parse('17:32:57')
# print(time_now)

offset     = start_offset(time_now,start_time,cycle)
sig_file_offset(path,name,progNo,offset)

#开始仿真
Vissim.Simulation.RunContinuous()

