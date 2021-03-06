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
import multiprocessing, os
import ext4error
import subprocess


ip_dns_time = 2 * TIMEOUT
time_lock = multiprocessing.Lock()
record_lock = multiprocessing.Lock()
error_lock = multiprocessing.Lock()

# 记录上次ip，减少更新次数，防止被ban
old_ip = "0.0.0.0"


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

def flush_dns():
    """
    清除dns缓存
    """
    return subprocess.Popen("ipconfig /flushdns", shell=True, stdout=subprocess.PIPE)


def do_ddns():
    """
    ddns
    """
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
        socket.setdefaulttimeout(TIMEOUT)

        # 编译正则
        domain_reg = re.compile("(?<=//)[^/]{1,}?(?=/)")

        print("【DDNS服务启动】\n")

        """ 循环更新 """
        while True:
            try:
                print("------ 开始更新 {time} ------".format(time=get_formatted_time(time.time())))
                
                print("开始获取本机IP与解析DNS...")
                s_time = time.time()

                # 获取本机ip
                conf['content'] = ip.get_ip_info()
                print("当前IP:", conf['content'])
                global old_ip
                if conf['content'] == old_ip:
                    print("IP4地址未发生变化，跳过本次更新！")
                    print("------ 结束更新 {time} ------".format(time=get_formatted_time(time.time())))
                    print("将在{}s后开始下一次更新......\n".format(conf['interval']/3))
                    time.sleep(conf['interval']/3)
                    continue
                else:
                    pass

                
                # 重新解析dns，以求避开dns污染
                original_domain = domain_reg.search(API).group()
                # print(original_domain)
                real_ip = domain_name_res(original_domain)
                # print(real_ip)
                conf['domain'] = original_domain
                conf['ip'] = real_ip
                e_time = time.time()
                time_lock.acquire()
                ip_dns_time = e_time - s_time    
                print("结束 用时约{time:.2f}s".format(time=ip_dns_time))
                time_lock.release()

                for ddns in conf['ddns_list']:
                    # 封装单个DDNS配置
                    conf['id'] = ddns['ID']
                    conf['type'] = ddns['TYPE']
                    conf['name'] = ddns['NAME']
                    conf['proxied'] = ddns['PROXIED']
                    # ipv6
                    if conf['type'] == "AAAA":
                        ipv6_p = subprocess.Popen("ipconfig", shell=True, stdout=subprocess.PIPE)
                        # ipv6_line = ipv6_p.stdout.readlines()[23]
                        output = ipv6_p.stdout.read()
                        # ipv6_line = re.search(b"(?<=IPv6 \xb5\xd8\xd6\xb7 [\s\.]{1,}: )", output)
                        conf['content'] = re.search(b"(?<=IPv6 \xb5\xd8\xd6\xb7 . . . . . . . . . . . . : )[0-9a-z:]{15,}(?=\r\n)", output).group(0).decode()
                        # print(conf['content'])
                        # input()

                    # 单个更新
                    print("------------")
                    print("[ Start {} ]".format(conf['name']))
                    update_dns(conf)
                    print("[ End {} ]".format(conf['name']))
                    print("------------")
                print("------ 结束更新 {time} ------".format(time=get_formatted_time(time.time())))
                print("将在{}s后开始下一次更新......\n".format(conf['interval']))
                old_ip = conf['content']
                
                # 输出日志
                record_lock.acquire()
                with open("record.log", "a") as f:
                    f.write(get_formatted_time(time.time()) + " ")
                    f.write(str(conf) + "\n")
                record_lock.release()
                time.sleep(conf['interval'])

            # 错误处理
            # 键盘中断
            except KeyboardInterrupt as e:
                raise KeyboardInterrupt
            # 超时
            except requests.exceptions.RequestException as e:
                sys.stderr.write("\n------ 连接超时，将在{timeout}秒后重试! ------\n\n".format(timeout=TIMEOUT))
                error_lock.acquire()
                with open("error.log", "a") as f:
                    f.write(get_formatted_time(time.time()) + " ")
                    f.write(str(e) + "\n")
                error_lock.release()
                flush_dns()
                time.sleep(TIMEOUT)
            # 未知错误
            except Exception as e:
                sys.stderr.write("\n------ 遇到未知错误，将在{timeout}秒后重试! ------\n".format(timeout=TIMEOUT*10))
                error_lock.acquire()
                with open("error.log", "a") as f:
                    f.write(get_formatted_time(time.time()) + " ")
                    f.write(str(e) + "\n")
                error_lock.release()
                ext4error.process(e)
                flush_dns()
                time.sleep(TIMEOUT*10)
    
    # 键盘中断
    except KeyboardInterrupt as e:
        sys.stderr.write("\n------ 已主动停止! ------\n")
        # error_lock.acquire()
        # with open("error.log", "a") as f:
        #     f.write(get_formatted_time(time.time()) + " ")
        #     f.write("主动键盘中断" + "\n")
        # error_lock.release()
        sys.exit(-1)


if __name__ == "__main__":
    # 管理ddns，监测DDNS线程是否假死，若假死则重启该进程
    ddns_process = multiprocessing.Process(target=do_ddns)
    ddns_process.start()
    try:
        time_lock.acquire()
        check_interval = len(DDNS_LIST) * (TIMEOUT + 1) + 2 * ip_dns_time
        time_lock.release()
        time.sleep(check_interval)
        while(True):
            record_info = os.stat("record.log")
            error_info = os.stat("error.log")
            ntime = time.time()

            # 若假死
            if ntime - record_info.st_mtime > INTERVAL and ntime - error_info.st_mtime > INTERVAL:
                # 获取锁以防释放前进程被杀死导致的死锁
                error_lock.acquire()

                record_lock.acquire()
                time_lock.acquire()

                # 杀死进程
                ddns_process.terminate()
                ddns_process.join()

                # 释放不必要的锁
                time_lock.release()
                record_lock.release()
                
                # 记录错误日志
                sys.stderr.write("\n------ DDNS进程假死，即将自动重启进程! ------\n")
                with open("error.log", "a") as f:
                    f.write(get_formatted_time(time.time()) + " ")
                    f.write("进程假死重启" + "\n")
                error_lock.release()
                # 重启进程
                ddns_process = multiprocessing.Process(target=do_ddns)
                ddns_process.start()

            time.sleep(check_interval)
    
    # 键盘中断
    except KeyboardInterrupt as e:
        ddns_process.terminate()
        ddns_process.join()
        sys.exit(-1)
    except Exception:
        ddns_process.terminate()
        ddns_process.join()
        sys.exit(-1)
    