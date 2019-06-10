#
#
#   出差等特殊时间，天气推送逻辑处理
#   作者：赵昱
#   时间：2019-06-08
#
#

import time
import json
import requests
import datetime
import logging.handlers

# 设置日志配置环境
LOG_FILE = r'/root/get_weather_info/weather.log'  #  日志存储路径
#LOG_FILE = r'./weather.log'  #  日志存储路径

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5,
                                               encoding='utf-8')  # 实例化handler
fmt = '%(asctime)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('weather')  # 获取名为weather的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)

#  公共参数配置
receive_mobile = '15285149403'  # 接受短信手机号码
sms_template_num = ''  # 短信网关模板编号
city_id = ''  # 推送城市ID
city_name = ''  # 推送的城市名字
special_flag = ''  # 发送判断依据，值为1时：出发天气提醒；值为2时：返程提醒
curr_day_info = datetime.datetime.now()
today_info = curr_day_info.strftime("%Y%m%d")  # 当前时间，格式示例为：20190608

logger.info(u'------特殊提醒开始处理信息-------')

#is_special_day_path = './special_day.json'
is_special_day_path = '/root/get_weather_info/special_day.json' #线上环境日志
special_file = open(is_special_day_path, 'r+')
special_result = special_file.read()
special_json_result = json.loads(special_result)

#
#   特殊逻辑开始处理：
#       1）出发前一天晚上进行出发提醒，判断依据：当前时间 + 86400秒 = 开始时间，采用特殊地点进行推送
#       2）回城前一天晚上进行回程提醒，判断依据：当前时间 + 86400秒 = 结束时间，采用南明区进行推送
#
#   文件每行介绍说明（采用JSON格式）
#       第一行、二行：开始时间和结束时间，判断依据：当前时间>=开始时间 and 当前时间<结束时间
#       第三行：为城市ID:cityID
#       第四行：为城市名字
#       第五行：判断是否与女票同行标志，值为0时：不同行；值为1时：同行
#               此处用于同行及女票单独出行时推送不同的短信模板
#
if (time.mktime(time.strptime(today_info, '%Y%m%d')) + 86400 == time.mktime(
        time.strptime(special_json_result['begin_time'], '%Y%m%d'))):
    city_id = special_json_result['city_id']
    city_name = special_json_result['city_name']
    special_flag = 1  # 出发提醒判断依据
    if (special_json_result['is_together'] == 0):   #判断是否与女票同行出发依据，0为不同行，1为同行
        sms_template_num = 'T170317004583'  # 女票单独出发提醒的短信网关模板
    else:
        sms_template_num = 'T170317004588'  # 同行出发提醒的短信网关模板
elif (time.mktime(time.strptime(today_info, '%Y%m%d')) + 86400 == time.mktime(
        time.strptime(special_json_result['end_time'], '%Y%m%d'))):
    city_id = 2991
    city_name = '南明区'
    special_flag = 2  # 返程提醒判断依据
    if (special_json_result['is_together'] == 0):  # 判断是否与女票同行出发依据，0为不同行，1为同行
        sms_template_num = 'T170317004585'  # 女票单独回程提醒的短信网关模板
    else:
        sms_template_num = 'T170317004589'  # 同行回程提醒的短信网关模板
else:
    logger.info(u'无需要提醒信息')
    logger.info(u'------特殊提醒结束处理信息-------')
    special_file.close()
    exit()

logger.info(u'需要特殊提醒，city_id：%s，city_name：%s，sms_template_num：%s' % (city_id, city_name, sms_template_num))
special_file.close()

#   设置天气预报获取相关参数
logger.info(u'------天气接口开始获取信息-------')
host = 'http://aliv18.data.moji.com'  # 更改为墨迹天气专业版API接口
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
logger.info(u'------天气接口结束获取信息-------')

# 短信发送操作模块
logger.info(u'------短信发送接口开始操作-------')
#  开始执行短信发送步骤
sms_host = 'http://ali-sms.showapi.com'
sms_path = '/sendSms'
sms_url = sms_host + sms_path

sms_appcode = '89827366650247fab6bdd2acec7545a2'
sms_headers = {}
sms_headers['Authorization'] = 'APPCODE ' + sms_appcode

#    短信模板参数：S1：城市名字，S2：当天最低气温，S3:当天最高气温，S4:天气情况
sms_content = {}  # 短信网关发送的预置参数
sms_content['s1'] = city_name  # 今天是周几，填入输入一、二、三、四、五、六、天
sms_content['s2'] = today_low_temp  # 当天最低气温度数
sms_content['s3'] = today_high_temp  # 当前最高气温度数
sms_content['s4'] = today_condition  # 当前天气实时情况

sms_mobile_num = receive_mobile  # 接收短信的号码
sms_tNum = sms_template_num  # 短信网关的模板编号

json_sms_content = json.dumps(sms_content)

sms_querys = 'content=' + (json_sms_content) + '&mobile=' + sms_mobile_num + '&tNum=' + sms_tNum

logger.info(u'短信接口组装地址为：%s' % (sms_querys))

sms_r = requests.get(sms_url + '?' + sms_querys, headers=sms_headers)

logger.info(u'短信接口请求返回JSON结果为：%s' % (json.loads(sms_r.text)))

logger.info(u'------短信发送接口结束操作-------')
logger.info(u'------特殊提醒结束处理信息-------')
