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
            print("将在{}s后开始下一次更新......".format(conf['interval']))
            time.sleep(conf['interval'])
        except KeyboardInterrupt:
            sys.stderr.write("\n[ Stopped! ]\n")
            sys.exit(-1)
        except Exception:
            sys.stderr.write("\n------ 遇到未知错误，将在1分钟后重试! ------\n")
            time.sleep(60)