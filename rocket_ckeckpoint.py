import datetime
import re
import time
import sys
import requests
from bs4 import BeautifulSoup
from collections import Counter

def findIndex(list,x):
    index=[]
    for i, item in enumerate(list):
        if item == x:
            index.append(i+1)

    return index





# ------------------------------获取平台的app上传的数据----------------------------------------------
def getPointsData(userid,dt,keyword):
    # 结构: [dict1, dict2, ...], dict结构{'埋点字段1-name': 'name', '埋点字段2-id': 'id', '埋点字段3-time': 'time'}
    PointsData_All = []
    respondText = requests.get(
        'https://bigdata-schedule.codemao.cn/tools/checklogs?logtype=2&topicstr=kids&keystr=%s'%keyword).text

    soup = BeautifulSoup(respondText, 'html.parser')
    # with open('datas.html', 'r') as f:
    # respondText = f.read()
    # soup = BeautifulSoup(respondText,'html.parser')

    for idx, tr in enumerate(soup.find_all('tr')):
        if idx != 0:
            tds = tr.find_all('td')
            PointsData_All.append({
                '上报时间0': tds[0].contents[0],
                '记录id': tds[1].contents[0],
                '事件id': tds[2].contents[0],
                '上报时间': tds[3].contents[0],
                '用户id': tds[4].contents[0], #容易判空先注释掉
                '用户标识': tds[5].contents[0],
                '业务数据map': tds[6].contents[0],
                '平台数据map': tds[7].contents[0],
                '设备类型': tds[8].contents[0],
                '产品代码': tds[9].contents[0],
                '日期': tds[10].contents[0]
            })


    # 选出你自己要测试的手机的数据,用‘用户ID’区分多个人同时测试时数据乱的问题
    # 新增上报时间判断
    PointsData = []
    z = 0
    for i in PointsData_All:
        if PointsData_All[z]['事件id'] == userid:


            if int(PointsData_All[z]['上报时间'])>int(time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S")))\
                    or int(PointsData_All[z]['上报时间'])+6000>int(time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S"))):
                PointsData.append({
                    '上报时间0': PointsData_All[z]['上报时间0'],
                    '记录id': PointsData_All[z]['记录id'],
                    '事件id': PointsData_All[z]['事件id'],
                    '上报时间': PointsData_All[z]['上报时间'],
                    '用户id': PointsData_All[z]['用户id'],
                    '用户标识': PointsData_All[z]['用户标识'],
                    '业务数据map': PointsData_All[z]['业务数据map'],
                    '平台数据map': PointsData_All[z]['平台数据map'],
                    '设备类型': PointsData_All[z]['设备类型'],
                    '产品代码': PointsData_All[z]['产品代码'],
                    '日期': PointsData_All[z]['日期']
                })

            else:
                print("平台数据"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(PointsData_All[z]['上报时间'])))+"已过滤!-----原因:上报时间小于操作:"+dt+"以后的数据，属于无效数据")
        z = z + 1
    # print('guolv')
    # print(PointsData)

    return PointsData
# --------------------------时间戳正确性判断--------------------------------
def deal_timeStamp(timeStamp):  # timeStamp为字符串类型点数字，返回这种格式的时间2021-01-03 20:40:00
    # 数字时间戳转字符串时间
    # print(timeStamp)
    dateArray = datetime.datetime.fromtimestamp(float(timeStamp))
    timeStamp_str = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    # print(timeStamp_str)   # 2021-01-03 20:40:00
    return timeStamp_str


# limittime的单位为分钟,判断逻辑：把usercontrol_start和usercontrol_end分别减去上报时间，差值在limittime分钟内正常


def is_time_correct(logtime, usercontrol_start, usercontrol_end, timelimit):
    now = int(time.time())
    timeArray = time.localtime(now)
    now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

    # 字符串时间转数字
    startTime2 = datetime.datetime.strptime(logtime, "%Y-%m-%d %H:%M:%S")
    endTime2 = datetime.datetime.strptime(
        usercontrol_start, "%Y-%m-%d %H:%M:%S")
    endTime3 = datetime.datetime.strptime(usercontrol_end, "%Y-%m-%d %H:%M:%S")
    # print('数据上报时间：'+str(startTime2))
    # print(str(startTime2).split(" "))
    # print(now_time_str.split(' '))
    # 这里的数据上报时间是指数据平台第3列上报时间戳
    print('😊  数据上报时间正确    ☑️' if str(startTime2).split(" ")[
                                      0] == now_time_str.split(' ')[0] else "数据上报时间不正确    ❌ ")

    # seconds = (endTime2 - startTime2).seconds
    # 来获取时间差中的秒数。注意，seconds获得的秒只是时间差中的小时、分钟和秒部分的和，并没有包含时间差的天数（既是两个时间点不是同一天，失效）
    total_seconds_usercontrolstart = (endTime2 - startTime2).total_seconds()
    total_seconds_usercontrolend = (endTime3 - startTime2).total_seconds()
    # 来获取准确的时间差，并将时间差转换为秒
    mins = total_seconds_usercontrolstart / 60

    if mins > timelimit:
        print('😖  usercontrol_start的时间戳不正确    ❌')
    else:
        print('😊  usercontrol_start的时间戳正确    ☑️')

    mins2 = total_seconds_usercontrolend / 60
    if mins2 > timelimit:
        print('😊  usercontrol_end的时间戳不正确    ❌')
    else:
        print('😊  usercontrol_end的时间戳正确    ☑️')


# 处理解析usercontrol[]的数据


def getUsercontrolDatas(num, userid,keyword,requirePointNameList00):
    PointsData = getPointsData(userid,dt,keyword)
    PointsDataList = str.split(PointsData[num]['业务数据map'], ',')
    datamap = {}  # print(datamap)#每一条埋点字符串转化为map结构
    for data in PointsDataList:
        dictKey = str.split(data, '=')[0]
        dictValue = str.split(data, '=')[1]
        datamap[dictKey] = dictValue
    try:
        flag = 0
        newListUsercontrol = (datamap['usercontrol'].replace('%2c', ','))
        newUCstr = newListUsercontrol.split('}')[0].lstrip('[{')
        # m的数据："usercontrol_start": 1610111101883 ,"usercontrol_result": 1 " ,usercontrol_end": 1610111101967
        m = newUCstr.split(',')
    except:
        flag = 1
        print('⚠️  埋点返回值中没有usercontrol字段    ❌')


        returnPointLists = datamap.keys()
        surplusPoints00 = set(requirePointNameList00).difference(
            set(returnPointLists))
        print('😖  ' + str(len(surplusPoints00)) + "个缺失埋点：" +
              (str(surplusPoints00)) + '   ❌')  # 缺失点埋点
        return 1, 1, 1
    if flag != 1:
        try:
            for i in range(3):
                if 'star' in m[i]:
                    start_time_str = m[i]
                if 'end' in m[i]:
                    end_time_str = m[i]
                if 'result' in m[i]:
                    result_str = m[i]
            user_start_time = start_time_str.split(':')[1]
            usercontrol_result = result_str.split(':')[1]
            user_end_time = end_time_str.split(':')[1]

            return user_start_time, user_end_time, usercontrol_result
        except:
            print(
                "⚠️  usercontrol[]内容不完整，检查其返回值是否包含3个元素usercontrol_start、usercontrol_end、usercontrol_result  ❌")
            requirePointNameList00 = ['link_name', 'step_type', 'link_id', 'tryCount', 'step_id', 'package_id',
                                      'latencyInteract', 'objective',
                                      'is_complete', 'duration', 'step_name', 'term_id', 'course_id', 'page',
                                      'game_restart', 'usercontrol', 'hint_time']  # 埋点需求文档上要求的字段

            print('⚠️  usercontrol的返回值是：' + newListUsercontrol + '    ❌')
            if datamap['objective'] == 'false':
                # print(datamap['objective'])
                print('⚠️  该题目是创想乐园，请不要进场就点通关按钮，执行下游戏步骤后再进行检测！     ❌')
            returnPointLists = datamap.keys()
            surplusPoints00 = set(requirePointNameList00).difference(
                set(returnPointLists))
            print('😖  ' + str(len(surplusPoints00)) + "个缺失埋点：" + (str(surplusPoints00)) +
                  "  ❌" if len(surplusPoints00) > 0 else "😊  返回字段无缺失     ☑️ ")  # 缺失点埋点

            return 1, 1, 1  # 控制跳出该异常数据继续执行下面的数据


# ------------------------先独立简单判断下返回的埋点数是否正常---------------------------
def is_pointCount_correct(requireCount, realCount):
    if requireCount - realCount == 0:
        print("😊  埋点的数量正确    ☑️")
        return True
    if realCount - requireCount > 0:
        print("😖  多了" + str(realCount - requireCount) + "个埋点    ❌")
        return False
    if realCount - requireCount < 0:
        print("😖  少了" + str(requireCount - realCount) + "个埋点    ❌")
        return False


# -------------------------埋点自动判断正确总入口函数------------------------------------------


# requirePointNameList,limittime,requireCount,correctPointValueDict
def runCheckingPoint(eventid, dt,requirePointCount, notrequirePointNameList,keyword,requirePointNameList):
    PointsData = getPointsData(eventid, dt,keyword)
    print("\n\n当前验证筛选埋点的信息数据为eventId:"+eventid)
    if len(PointsData) == 0:
        print("⚠️ 平台暂时无数据，请先打开app玩游戏上传数据！")
    print('当前useid下型号下发现了一共'+str(len(PointsData))+'条数据\n')
    k = 0
    for i in PointsData:
        print("🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓第" + str(k + 1) +
              "条游戏数据🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓")

        # --------------------判断触发埋点的时间戳正确性-------------------------------
        log_time = PointsData[k]['上报时间']
        new_log_time = deal_timeStamp(log_time)
        time1, time2, usercontrol_result = getUsercontrolDatas(k, eventid,keyword,requirePointNameList)
        # if time1 == 1:
        # k = k + 1
        # continue
        starttime = float(time1) / 1000
        endtime = float(time2) / 1000
        flag2 = 0
        try:
            user_start_time = deal_timeStamp(starttime)
        except:
            print('😖  usercontrol_start的时间戳不正确    ❌')
            flag2 = 3
        try:
            user_end_time = deal_timeStamp(endtime)
        except:
            # print(user_end_time)
            print('😖  usercontrol_end的时间戳不正确    ❌')
        try:
            # 上报时间和usercontrl_start的时间对比，可以存在误差30分钟之内，修改为自己想要的范围即可
            # print(user_start_time)
            # print(flag2)
            if flag2 != 3:
                is_time_correct(new_log_time, user_start_time,
                                user_end_time, 30)
        except:
            pass
        # ------------------- 判断埋点个数正常----------------------------------
        real_pointCount = len(str.split(PointsData[k]['业务数据map'], ','))
        # 最外层简单控制下返回的埋点数是否正常
        is_pointCount_correct(requirePointCount, real_pointCount - 1)


        PointsDataList = str.split(PointsData[k]['业务数据map'], ',')
        datamap = {}  # print(datamap)#每一条埋点字符串转化为map结构
        for data in PointsDataList:
            dictKey = str.split(data, '=')[0]
            dictValue = str.split(data, '=')[1]
            datamap[dictKey] = dictValue
        pointKeyList = list(datamap.keys())
        pointKeyList.remove('1')  # 实际埋点返回列表中多出埋点 ‘1’，先去除。
        # 先判断返回的埋点是否含有重复埋点，比如id出现2次的情况
        if len(pointKeyList) != len(set(pointKeyList)):
            # print('have duplicates!!!')
            # 打印出返回的埋点重复的元素和重复次数
            Pkey = dict(Counter(pointKeyList))
            print('😖  返回的埋点字段存在重复元素及其对应重复的次数是：' +
                  str({key: value for key, value in Pkey.items() if value > 1}) + '  ❌')  # 展现重复元素和重复次数

        else:
            print('😊  返回的埋点字段无重复字段    ☑️')
            normalPoints = set(pointKeyList) & set(
                requirePointNameList)  # 正常的埋点字段
            print('😊  ' + str(len(normalPoints)) + "个需要校验的正确的埋点：" + str(normalPoints))

            surplusPoints = set(requirePointNameList).difference(
                set(pointKeyList))
            print('🙄  ' + str(len(surplusPoints)) + "个缺失的埋点：" + (str(surplusPoints) +
                                                                  "  ❌" if len(
                surplusPoints) > 0 else "-        ☑️"))  # 缺失的埋点

            omitPoints = set(pointKeyList).difference(
                set(requirePointNameList+notrequirePointNameList))
            print('🙄  ' + str(len(omitPoints)) + "个多余的埋点：" + (str(omitPoints) +
                                                               "  ❌" if len(
                omitPoints) > 0 else "-        ☑️️"))  # 缺失点埋点

            # ----------------------------------判断埋点的返回值正常-----------------------------------------

            try:
                print('---------正在检测埋点返回值--------')
                for keyname in requirePointNameList:
                    #通用数据修改 flag
                    if keyname in notrequirePointNameList:
                        # 意义不大的字段简单判断返回值不为空即可
                        if datamap[keyname] != '':
                            pass
                        else:
                            print('😖  ' + keyname + '的返回值为空值    ❌')
                    # else:
                    #     if keyname == "usercontrol":
                    #         # print(keyname+"  =  "+datamap[keyname].replace('%2c',','))
                    #         data = eval(datamap[keyname].replace('%2c', ','))
                    #         data_result = []
                    #         for i, value in enumerate(data):
                    #             data_result.append(
                    #                 value.get("usercontrol_result"))
                    #         # for i,item in enumerate(data_result):
                    #         #     print("点击无反馈的操作分别是第")
                    #         #     if item==0:
                    #         #         print(str(i+1))
                    #         #     elif item==1:
                    #         #         print("usercontrol_result = 1 的次数"+str(i+1))
                    #         #     elif item==2:
                    #         #         print("usercontrol_result = 2 的次数"+str(i+1))
                    #         #     else:
                    #         #         print("无法匹配到结果对应值")
                    #
                    #         print("usercontrol_result = 0 的次数：" +
                    #               str(data_result.count(0))+"------操作无反馈的的次数分别在第"+str(findIndex(data_result, 0))+"次")
                    #
                    #         print("usercontrol_result = 1 的次数：" +
                    #               str(data_result.count(1))+"------操作正确的次数分别在第"+str(findIndex(data_result, 1))+"次")
                    #
                    #         print("usercontrol_result = 2 的次数：" +
                    #               str(data_result.count(2))+"------操作错误的次数分别在第"+str(findIndex(data_result, 2))+"次")
                    #
                    #     elif keyname == 'latencyInteract':
                    #         if datamap[keyname] == '0':
                    #             print("😖  latencyInteract的返回值为0异常    ❌")
                    #     elif keyname == 'duration':
                    #         if datamap[keyname] == '0':
                    #             print("😖  duration的返回值为0异常    ❌")
                    #     elif keyname == 'is_complete':
                    #         if datamap[keyname] == 'false':
                    #             print(
                    #                 "😖  is_complete的返回值为false异常(已经通关，应返回true)    ❌")
                    #     elif keyname=='game_restart':
                    #         print(keyname + "  =  " + datamap[keyname])
                    #         #转换一下game_restart里面的时间戳转换为时间
                    #         datamap[keyname]=datamap[keyname].replace('%2c', ',')
                    #         timelist=re.findall('\d+',datamap[keyname])
                    #         for i in range(len(timelist)):
                    #             timestamp=timelist[i]
                    #             # 转换成localtime
                    #             dt=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp) / 1000))
                    #             # 转换成新的时间格式(2016-05-05 20:28:54)
                    #             print('第 %s 次点击重玩的时间为：%s'% (i+1,dt))
                    #
                    #         print('---------------------------------')
                    #     else:
                    #         print(keyname + "  =  " + datamap[keyname])
            except:
                print('❗️ 检测埋点返回值中断········')
                print("出现异常:" + "埋点返回值中缺失" + keyname + "这个字段，请联系对应开发同事处理。")

        k = k + 1


if __name__ == '__main__':
    #需要过滤的关键字  这里直接写userid就行
    #keyword='rc_play_time'
    userid='12824778'
    # --------------------判断埋点的字段名字正常-----------------------------
    requirePointNameList = ['time','section_time', 'play_time']  # 埋点需求文档上要求的字段
    notrequirePointNameList=['step_id', 'study_today', 'element','link_name', 'term_id','is_complete','buy'
                             'package_id','step_most_id','step_progress','step_name','link_id','link_wasdone','section_id',
                             'lesson_type','step_type','course_id','story_name','is_last']
    #时间标识
    eventid='rc_play_time'
    #dt="2021-03-16 14:01:07"   #手动输入一个时间段，如果埋点上报的时间小于你这个时间，就会被过滤掉
    dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #如果上报时间+5不大于运行此程序时间的时候，数据就会被过滤掉
    #print(dt)

    runCheckingPoint(eventid, dt, 22,
                      notrequirePointNameList,userid,requirePointNameList)  # 时间id、当前时间、需求中埋点数、不需要关注的埋点字段的key、用户id、需要关注埋点字段的key
