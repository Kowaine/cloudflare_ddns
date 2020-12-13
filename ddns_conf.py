"""
@author Kowaine
@desc 配置DDNS
@date 2020/08/10
"""

# 此为需要进行动态更新的DNS记录列表
# 字段说明
# ID: 记录ID（可以通过 'python dns.py -l' 查询）
# TYPE: 记录类型
# NAME: 三级域名前缀
# PROXIED: 是否使用代理服务(不使用则仅作为DNS，使用则附加CDN等功能)
DDNS_LIST = [
    {
        "ID": "",
        "TYPE": "",
        "NAME": "",
        "PROXIED": False
    },
    {
        "ID": "",
        "TYPE": "",
        "NAME": "",
        "PROXIED": False
    },
]

# 更新时间间隔(s), 不建议低于1800s
INTERVAL = 1800

# 超时时间
TIMEOUT = 3