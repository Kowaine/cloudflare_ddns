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
import requests
import socket
import DNS, re

def get_formatted_time(any_time):
    """
    获取格式化的时间字符串
    @args
        any_time 任意合法时间戳
    @returns 格式化后的时间字符串 :string
    """
    formatter = "{}/{:0>2d}/{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}"
    temp_time = time.localtime(any_time)
    formatted_time = formatter.format(temp_time.tm_year, temp_time.tm_mon, temp_time.tm_mday, temp_time.tm_hour, temp_time.tm_min, temp_time.tm_sec)
    return formatted_time


def domain_name_res(domain):
    """
    主动域名解析（为了防止dns污染）
    @args
        domain 域名 :string
    @returns 解析得到的ip :string
    """
    req = DNS.Request(name=domain, server="223.5.5.5")
    result = req.req().answers
    # print(result)
    return result[0]['data']



if __name__ == "__main__":
    try:
        # 配置项整合
        conf = {}
        conf['user_email'] = USER_EMAIL
        conf['api_key'] = API_KEY
        conf['zone_id'] = ZONE_ID
        conf['api'] = API
        conf['ddns_list'] = DDNS_LIST
        conf['interval'] = INTERVAL

        # 设置全局超时
        socket.setdefaulttimeout(3)

        # 编译正则
        domain_reg = re.compile("(?<=//)[^/]{1,}?(?=/)")

        print("【DDNS服务启动】")

        # 循环更新
        while True:
            try:
                print("------ 开始更新 {time} ------".format(time=get_formatted_time(time.time())))
                conf['content'] = ip.get_ip_info()

                # 重新解析dns，以求避开dns污染
                original_domain = domain_reg.search(API).group()
                # print(original_domain)
                real_ip = domain_name_res(original_domain)
                print(real_ip)
                # print(domain_name_res(original_domain))
                # old_api = conf['api']
                # conf['api'] = conf['api'].replace(original_domain, real_ip)
                # print(conf['api'])
                # conf['referer'] = old_api
                conf['domain'] = original_domain
                conf['ip'] = real_ip

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
                print("------ 结束更新 {time} ------".format(time=get_formatted_time(time.time())))
                print("将在{}s后开始下一次更新......".format(conf['interval']))
                
                # 输出日志
                with open("record.log", "a") as f:
                    f.write(get_formatted_time(time.time()) + " ")
                    f.write(str(conf) + "\n")
                time.sleep(conf['interval'])

            # 错误处理
            # 键盘中断
            except KeyboardInterrupt as e:
                raise KeyboardInterrupt
            # 超时
            except requests.exceptions.RequestException as e:
                sys.stderr.write("\n------ 连接超时，将在1分钟后重试! ------\n")
                with open("error.log", "a") as f:
                    f.write(get_formatted_time(time.time()) + " ")
                    f.write(str(e) + "\n")
                time.sleep(60)
            #未知错误
            except Exception as e:
                sys.stderr.write("\n------ 遇到未知错误，将在1分钟后重试! ------\n")
                with open("error.log", "a") as f:
                    f.write(get_formatted_time(time.time()) + " ")
                    f.write(str(e) + "\n")
                time.sleep(60)
    
    # 键盘中断
    except KeyboardInterrupt as e:
        sys.stderr.write("\n------ 已主动停止! ------\n")
        with open("error.log", "a") as f:
            f.write(get_formatted_time(time.time()) + " ")
            f.write("主动键盘中断" + "\n")
        sys.exit(-1)