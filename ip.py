"""
@Author: Kowaine
@Description: 获取本机公网ip的函数及相关函数
@Date: 2020-08-11 05:10:49
@LastEditTime: 2021-02-20 14:53:34
"""

import requests
import socket
import json

def by_requests_wrapper(func):
    """
    使用requests的包装器
    @args 
        func 包装前的get_ip_info函数 :function()
    @returns
        wrapped 包装后的get_ip_info, 使用requests :function()
    """
    def wrapped():
        # 已废弃
        # info = requests.get("http://ipv4.icanhazip.com", timeout=3)
        # info = info.text[:-1]
        info = requests.get("http://ip-api.com/json/?lang=zh-CN", timeout=5)
        info = json.loads(info.text)
        info = info['query']
        return info

    return wrapped


def by_socket_wrapper(func):
    """
    使用socket的包装器
    @args 
        func 包装前的get_ip_info函数 :function()
    @returns
        wrapped 包装后的get_ip_info, 使用socket :function()
    """
    def wrapped():
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(('223.5.5.5',80))
            ip=s.getsockname()
        finally:
            s.close()
        # ip = socket.gethostbyname_ex(socket.gethostname())

        return ip

    return wrapped



@by_requests_wrapper
def get_ip_info():
    """
    用于解耦的占位函数，防止将来可能存在的方法更新影响其余的代码调用

    """
    pass
