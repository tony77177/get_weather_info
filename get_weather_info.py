#
#
#   作者：赵昱
#   时间：2019-05-28
#   主要作用：通过天气接口获取相应城市天气，再通过短信接口推送至相应的手机
#
#
#

import json
import requests
import datetime
import logging.handlers

receive_mobile = '15285149403'  # 接受短信手机号码
sms_template_num = 'T170317004526'  # 短信网关模板编号

# 设置日志配置环境
LOG_FILE = r'./weather.log'  #  本地缓解经
# LOG_FILE = r'/root/job_spider/job_spider/spider.log'    #线上环境

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5,
                                               encoding='utf-8')  # 实例化handler
fmt = '%(asctime)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('weather')  # 获取名为spider的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)

logger.info(u'天气接口开始获取信息：')

#   设置天气预报获取相关参数
host = 'http://freecityid.market.alicloudapi.com'

three_days_path = '/whapi/json/alicityweather/briefforecast3days'  # 未来3天精简天气预报
method = 'POST'
appcode = '89827366650247fab6bdd2acec7545a2'  # 天气预报APP COEE
querys = ''
headers = {}
three_days_bodys = {}
three_days_url = host + three_days_path  # 天气API URL

three_days_bodys['cityId'] = '2998'  # cityID:    2998观山湖 2982贵阳市 2991南明区
three_days_bodys['token'] = '677282c2f1b3d718152c4e25ed434bc4'  # 未来3天的精简预报

headers['Authorization'] = 'APPCODE ' + appcode

three_days_result = requests.post(three_days_url, headers=headers, data=three_days_bodys)

three_days_json_result = json.loads(three_days_result.text)

logger.info(u'三天天气情况获取JSON结果为：%s' % (three_days_json_result))

#  获取实时天气预报及天气温度差结束
today_high_temp = three_days_json_result['data']['forecast'][0]['tempDay']  # 当天最高气温
today_low_temp = three_days_json_result['data']['forecast'][0]['tempNight']  # 当天最低气温

# request.add_header('Authorization', 'APPCODE ' + appcode)

# print(bodys)
# print(url)
# print(headers)
# exit()

#    获取当前实时天气预报
curr_temp_path = '/whapi/json/alicityweather/briefcondition'  # 实时天气API地址
curr_temp_url = host + curr_temp_path
curr_temp_bodys = {}
curr_temp_bodys['cityId'] = '2998'
curr_temp_bodys['token'] = '46e13b7aab9bb77ee3358c3b672a2ae4'  # 实时天气的token

curr_temp_result = requests.post(curr_temp_url, headers=headers, data=curr_temp_bodys)

curr_temp_json_result = json.loads(curr_temp_result.text)

curr_temp = curr_temp_json_result['data']['condition']['temp']

# print(r.text)
logger.info(u'实时天气接口获取JSON信息：%s' % (curr_temp_json_result))

# print(today_high_temp)
# print(today_low_temp)
# print(curr_temp)

logger.info(u'------天气接口结束获取信息-------')

# exit()

logger.info(u'短信发送接口开始操作：')

#  开始执行短信发送步骤
sms_host = 'http://ali-sms.showapi.com'
sms_path = '/sendSms'
sms_url = sms_host + sms_path

sms_appcode = '89827366650247fab6bdd2acec7545a2'
sms_headers = {}
sms_headers['Authorization'] = 'APPCODE ' + sms_appcode

# 获取当前为周几
curr_day = ''
curr_day_info = datetime.datetime.now()
curr_day_tmp = curr_day_info.weekday()
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

sms_content = {}  # 短信网关发送的预置参数
sms_content['day'] = curr_day  # 今天是周几，填入输入一、二、三、四、五、六、天
sms_content['low'] = today_low_temp  # 当天最低气温度数
sms_content['high'] = today_high_temp  # 当前最高气温度数
sms_content['city'] = '观山湖'  # 当前所在城市，如贵阳市、南明区、观山湖区
sms_content['temp'] = curr_temp  # 当前实时气温

sms_mobile_num = receive_mobile  # 接收短信的号码
sms_tNum = sms_template_num  # 短信网关的模板编号

json_sms_content = json.dumps(sms_content)

sms_querys = 'content=' + (json_sms_content) + '&mobile=' + sms_mobile_num + '&tNum=' + sms_tNum

logger.info(u'短信接口组装地址为：%s' % (sms_querys))

sms_r = requests.get(sms_url + '?' + sms_querys, headers=sms_headers)

# print(sms_r)
# print(sms_r.text)
# print(json.loads(sms_r.text))

logger.info(u'短信接口请求返回JSON结果为：%s' % (json.loads(sms_r.text)))

logger.info(u'------短信发送接口结束操作-------')
