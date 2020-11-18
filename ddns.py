"""
@author Kowaine
@desc 基于dns.py脚本编写DDNS更新脚本
@date 2020/08/11
"""

import ip
from conf import *
from ddns_conf import *
from dns import update_dns
import time, sys

if __name__ == "__main__":
    # 配置项整合
    conf = {}
    conf['user_email'] = USER_EMAIL
    conf['api_key'] = API_KEY
    conf['zone_id'] = ZONE_ID
    conf['api'] = API
    conf['ddns_list'] = DDNS_LIST
    conf['interval'] = INTERVAL

    print("【DDNS服务启动】")

    # 循环更新
    while True:
        try:
            print("------ 开始更新 ------")
            conf['content'] = ip.get_ip_info()
            for ddns in conf['ddns_list']:
                # 封装单个DDNS配置
                conf['id'] = ddns['ID']
                conf['type'] = ddns['TYPE']
                conf['name'] = ddns['NAME']
                conf['proxied'] = ddns['PROXIED']
                # 单个更新
                print("------------")
                print("[ Start {} ]".format(conf['name']))
                update_dns(conf)
                print("[ End {} ]".format(conf['name']))
                print("------------")
            print("------ 结束更新 ------")
            with open("record.log", "a") as f:
                temp_time = time.localtime(time.time())
                f.write("{}/{:0>2d}/{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(temp_time.tm_year, temp_time.tm_mon, temp_time.tm_mday, 
            temp_time.tm_hour, temp_time.tm_min, temp_time.tm_sec), conf, "\n")
            print("将在{}s后开始下一次更新......".format(conf['interval']))
            time.sleep(conf['interval'])
        except KeyboardInterrupt as e:
            sys.stderr.write("\n[ Stopped! ]\n")
            with open("error.log", "a") as f:
                temp_time = time.localtime(time.time())
                f.write("{}/{:0>2d}/{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(temp_time.tm_year, temp_time.tm_mon, temp_time.tm_mday, 
            temp_time.tm_hour, temp_time.tm_min, temp_time.tm_sec), " ")
                f.write(e, "\n")
            sys.exit(-1)
        except requests.exceptions.RequestException as e:
            sys.stderr.write("\n------ 连接超时，将在1分钟后重试! ------\n")
            with open("error.log", "a") as f:
                temp_time = time.localtime(time.time())
                f.write("{}/{:0>2d}/{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(temp_time.tm_year, temp_time.tm_mon, temp_time.tm_mday, 
            temp_time.tm_hour, temp_time.tm_min, temp_time.tm_sec), " ")
                f.write(e, "\n")
            time.sleep(60)
        except Exception as e:
            sys.stderr.write("\n------ 遇到未知错误，将在1分钟后重试! ------\n")
            with open("error.log", "a") as f:
                temp_time = time.localtime(time.time())
                f.write("{}/{:0>2d}/{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(temp_time.tm_year, temp_time.tm_mon, temp_time.tm_mday, 
            temp_time.tm_hour, temp_time.tm_min, temp_time.tm_sec), " ")
                f.write(e, "\n")
            time.sleep(60)