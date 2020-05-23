#
#
#   作者：赵昱
#   时间：2019-05-28
#   主要作用：通过天气接口获取相应城市天气，再通过短信接口推送至相应的手机
#
#   2020.05.23  更新SMS短信提供商
#
#

import json
import time
import requests
import datetime
import logging.handlers

receive_mobile = '+86'  # 接受短信手机号码

sms_template_num = '20200521165327'  # 短信网关模板编号

# common_path = '/root/get_weather_info/'  # 线上公共目录
common_path = '/Users/tony/PycharmProjects/get_weather_info/get_weather_info/'  # 测试环境

# is_special_day_path = './special_day.json'
is_special_day_path = common_path + 'special_day.json'  # 线上环境日志

# 设置日志配置环境
LOG_FILE = common_path + 'weather.log'  #  日志存储路径
# LOG_FILE = r'./weather.log'  #  日志存储路径

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5,
                                               encoding='utf-8')  # 实例化handler
fmt = '%(asctime)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('weather')  # 获取名为weather的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)

# 获取当前为周几，用于判断：工作日时间推送观山湖区天气预报，休息日推送南明区天气预报 南明区ID：2991  观山湖区ID：2998
curr_day = ''  # 短信推送周几的变量
city_id = ''  # 推送城市ID
city_name = ''  # 推送的城市名字
curr_day_info = datetime.datetime.now()
curr_day_tmp = curr_day_info.weekday()  # 获取当前周几数字

if curr_day_tmp == 0:
    curr_day = '一'
elif curr_day_tmp == 1:
    curr_day = '二'
elif curr_day_tmp == 2:
    curr_day = '三'
elif curr_day_tmp == 3:
    curr_day = '四'
elif curr_day_tmp == 4:
    curr_day = '五'
elif curr_day_tmp == 5:
    curr_day = '六'
elif curr_day_tmp == 6:
    curr_day = '天'


# 通过自建接口，判断当前时间是否为工作日
# 判断说明：只需要判断结果是否为0即可
# 接口使用方式如下：
#   请求地址：http://api.freedomdream.cn/
#   请求参数：d 字符串形式 举例：?d=20190505
#   返回参数：工作日对应结果为 0, 休息日对应结果为 1, 节假日对应的结果为 2；
#   请求示例：http://api.freedomdream.cn/?d=20190505
#   返回示例：{"result":0}
#  开始执行短信发送步骤

def check_holiday(curr_day_info, curr_day_tmp):
    year_info = curr_day_info.strftime("%Y")
    key_info = curr_day_info.strftime("%m%d")
    holiday_file_url = common_path + year_info + '_data.json'
    f = open(holiday_file_url)
    res = json.loads(f.read())
    result = 0
    if (key_info in res):
        result = res[key_info]
    elif (curr_day_tmp == 5 or curr_day_tmp == 6):
        result = 1
    return result


#
# holiday_host = 'http://api.freedomdream.cn/?d='
#
holiday_para = curr_day_info.strftime("%Y%m%d")
#
# holiday_url = holiday_host + holiday_para

# 更改日期判断为本地判断，取消API接口获取
holiday_result = check_holiday(curr_day_info, curr_day_tmp)

# print(holiday_result)
# exit()


logger.info(u'------节假日判断接口开始操作-------')

# logger.info(u'节假日判断接口组装地址为：%s' % (holiday_url))

# holiday_r = requests.get(holiday_url)

# holiday_json_result = json.loads(holiday_r.text)

logger.info(u'节假日判断接口请求返回JSON结果为：%s' % (holiday_result))

logger.info(u'------节假日判断接口结束操作-------')

# print(holiday_json_result['result'])

if (holiday_result != 0):  # 如果不等于0则是周末，则推送南明区天气，否则推送观山湖区
    city_id = 2991
    city_name = '南明区'
else:
    city_id = 2998
    city_name = '观山湖'

# 以下为特殊逻辑，当不在"南明区"及"观山湖"两个区域时，采用特定逻辑指定 城市ID 城市名字，进行数据推送
#   文件每行介绍说明（采用JSON格式）
#   第一行、二行：开始时间和结束时间，判断依据：当前时间>=开始时间 and 当前时间<结束时间
#   第三行：为城市ID:cityID
#   第四行：为城市名字
#   第五行：判断是否与女票同行标志，值为0时：不同行；值为1时：同行
#
logger.info(u'------特殊逻辑开始处理信息-------')

special_file = open(is_special_day_path, 'r+')
special_result = special_file.read()
special_json_result = json.loads(special_result)

# print(special_result)
if (holiday_para >= special_json_result['begin_time'] and holiday_para < special_json_result['end_time']):
    city_id = special_json_result['city_id']
    city_name = special_json_result['city_name']
    logger.info(u'采用特殊逻辑处理，读取结果为：%s' % (special_json_result))
else:
    logger.info(u'无特殊逻辑，正常处理')

special_file.close()

logger.info(u'------特殊逻辑结束处理信息-------')

logger.info(u'------天气接口开始获取信息-------')

#   设置天气预报获取相关参数
# host = 'http://freecityid.market.alicloudapi.com'   #墨迹天气免费版API接口
host = 'http://aliv18.data.moji.com'  # 更改为墨迹天气专业版API接口
# three_days_path = '/whapi/json/alicityweather/briefforecast3days'  # 免费版未来3天精简天气预报
three_days_path = '/whapi/json/alicityweather/forecast15days'  # 更改为专业版15天天气

appcode = '89827366650247fab6bdd2acec7545a2'  # 天气预报APP COEE
headers = {}
three_days_bodys = {}
three_days_url = host + three_days_path  # 天气API URL

three_days_bodys['cityId'] = city_id  # cityID:    2998观山湖 2982贵阳市 2991南明区
three_days_bodys['token'] = 'f9f212e1996e79e0e602b08ea297ffb0'  # 更改为专业版15天的天气预报

headers['Authorization'] = 'APPCODE ' + appcode

three_days_result = requests.post(three_days_url, headers=headers, data=three_days_bodys)

three_days_json_result = json.loads(three_days_result.text)

today_high_temp = three_days_json_result['data']['forecast'][1]['tempDay']  # 当天最高气温
today_low_temp = three_days_json_result['data']['forecast'][1]['tempNight']  # 当天最低气温
today_condition = three_days_json_result['data']['forecast'][1]['conditionDay']  # 当天天气实况

logger.info(u'15天天气情况获取JSON结果为：%s' % (three_days_json_result))

#   此处增加sleep函数，防止请求过快API服务器拒绝
#   休眠单位：秒
#   休眠时间：1秒
time.sleep(1)

#    获取当前实时天气预报
curr_temp_path = '/whapi/json/alicityweather/condition'  # 实时天气API地址
curr_temp_url = host + curr_temp_path
curr_temp_bodys = {}
curr_temp_bodys['cityId'] = city_id
curr_temp_bodys['token'] = '50b53ff8dd7d9fa320d3d3ca32cf8ed1'  # 实时天气的token

# 执行POST操作
curr_temp_result = requests.post(curr_temp_url, headers=headers, data=curr_temp_bodys)

curr_temp_json_result = json.loads(curr_temp_result.text)

curr_temp = curr_temp_json_result['data']['condition']['temp']

# print(r.text)
logger.info(u'实时天气接口获取JSON信息：%s' % (curr_temp_json_result))
logger.info(u'------天气接口结束获取信息-------')

# 短信发送操作模块
# 2020.5.21 更换SMS提供商
logger.info(u'------短信发送接口开始操作-------')
#  开始执行短信发送步骤
sms_host = 'http://edisim.market.alicloudapi.com'
sms_path = '/comms/sms/sendmsg'
sms_url = sms_host + sms_path

sms_appcode = '89827366650247fab6bdd2acec7545a2'
sms_headers = {}
sms_headers['Authorization'] = 'APPCODE ' + sms_appcode
sms_headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

sms_content = {}  # 短信网关发送的预置参数
# 以下为老短信网关模板所需参数，现废弃更改为使用新短信网关模板
# sms_content['day'] = curr_day  # 今天是周几，填入输入一、二、三、四、五、六、天
# sms_content['low'] = today_low_temp  # 当天最低气温度数
# sms_content['high'] = today_high_temp  # 当前最高气温度数
# sms_content['city'] = city_name  # 当前所在城市，如贵阳市、南明区、观山湖区
# sms_content['temp'] = curr_temp  # 当前实时气温

#   更换新短信模板 宝贝：今天是周[s1]，气温[s2]至[s3]度，[s4]，现在[s5]实时温度为[s6]度，美好的一天赵先生与你共享!
# sms_content['s1'] = curr_day  # 今天是周几，填入输入一、二、三、四、五、六、天
# sms_content['s2'] = today_low_temp  # 当天最低气温度数
# sms_content['s3'] = today_high_temp  # 当前最高气温度数
# sms_content['s4'] = today_condition  # 当前天气实时情况
# sms_content['s5'] = city_name  # 当前所在城市，如贵阳市、南明区、观山湖区
# sms_content['s6'] = curr_temp  # 当前实时气温

# 2020.5.21 更换新的SMS提供商
sms_content["mobile"] = receive_mobile  # 接收短信的号码
sms_content['templateID'] = sms_template_num  # 短信网关的模板编号
sms_content['templateParamSet'] = "['" + curr_day + "','" + today_low_temp + "','" + today_high_temp + "','" + today_condition + "','" + city_name + "','" + curr_temp + "']"

logger.info(u'短信接口参数为：%s' % (sms_content))

sms_r = requests.post(sms_url, data=sms_content, headers=sms_headers)

logger.info(u'短信接口请求返回JSON结果为：%s' % (json.loads(sms_r.content)))

logger.info(u'------短信发送接口结束操作-------')
