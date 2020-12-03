"""
@author Kowaine
@desc 通过Cloudflare提供的API实现DNS记录的查询、增加、更新和删除
@date 2020/08/10
"""

from ip import get_ip_info
from conf import *
import requests, json, argparse, sys
from requests import Session, HTTPError
from requests.adapters import HTTPAdapter, DEFAULT_POOLSIZE, DEFAULT_RETRIES, DEFAULT_POOLBLOCK


class DNSHTTPAdapter(HTTPAdapter):
    def __init__(self, domain, ip, pool_connections=DEFAULT_POOLSIZE, pool_maxsize=DEFAULT_POOLSIZE,
        max_retries=DEFAULT_RETRIES, pool_block=DEFAULT_POOLBLOCK):
        self.__domain = domain
        self.__ip = ip
        super(DNSHTTPAdapter, self).__init__(pool_connections=pool_connections, pool_maxsize=pool_maxsize,
            max_retries=max_retries, pool_block=pool_block)

    # def get_connection(self, url, proxies=None):
    #     redirected_url = url.replace(self.__domain, self.__ip)
    #     return super(DNSHTTPAdapter, self).get_connection(redirected_url, proxies=proxies)

    # def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs):
    #     pool_kwargs['assert_hostname'] = self.__domain
    #     pool_kwargs['server_hostname'] = self.__domain
    #     super(DNSHTTPAdapter, self).init_poolmanager(connections, maxsize, block=block, **pool_kwargs)

    def send(self, request, **kwargs):
        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        # 替换域名为ip
        request.url = request.url.replace(
            'https://' + self.__domain,
            'https://' + self.__ip,
        )
        connection_pool_kwargs['server_hostname'] = self.__domain  # SNI
        connection_pool_kwargs['assert_hostname'] = self.__domain

        # 添加Host头，防止服务器拒绝访问
        request.headers['Host'] = self.__domain

        return super(DNSHTTPAdapter, self).send(request, **kwargs)



def generate_conf():
    """
    统合配置为conf变量，支持覆盖
    @returns
        conf 根据配置文件或用户输入生成的配置变量 :dict
    """
    conf = {}
    if ALLWAYS_DEFAULT:
        # 直接使用默认值
        conf['user_email'] = USER_EMAIL
        conf['api_key'] = API_KEY
        conf['zone_id'] = ZONE_ID
    else:
        # 提示用户重写默认值
        print("[ 选项配置 ] (留空回车使用默认值)")
        conf['user_email'] = input("用户邮箱({}): ".format(USER_EMAIL)) or USER_EMAIL  
        conf['api_key'] = input("Global Key({}): ".format(API_KEY)) or API_KEY
        conf['zone_id'] = input("Zone Id({}): ".format(ZONE_ID)) or ZONE_ID
    conf['api'] = API
    return conf


def add_meta_conf(conf, require_id=True, require_priority=False, require_meta=True):
    """
    为配置变量增加或覆盖额外的选项
    @args
        conf 配置变量 :dict
        require_id: 是否配置DNS记录ID，默认为True :bool
        require_priority: 是否配置优先级，默认为False :bool
        require_meta: 是否配置通用选项, 默认为True :bool
    @returns
        conf 扩充后的配置变量 :dict
    """
    if require_meta:
        while True:
            conf['type'] = input("记录类型: ")
            if conf['type']:
                break
    if require_meta:
        while True:
            conf['name'] = input("主机记录: ")
            if conf['name']:
                break
    if require_meta:
        while True:
            conf['content'] = input("记录值(默认使用本机ip): ")
            if conf['content']:
                break
            else:
                conf['content'] = get_ip_info()
                break
    if require_id:
        while True:
            conf['id'] = input("记录id: ")
            if conf['id']:
                break
    if require_meta:
        while True:
            conf['proxied'] = True if input("是否开启代理服务(yes/no): ").lower() == "yes" else False
            if conf['proxied'] == True or conf['proxied'] == False:
                break
    if require_priority:
        priority = input("记录优先级(某些类型可用，默认为0): ")
        priority = int(priority) if priority.isdigit() else 0
        conf['priority'] = priority
    return conf




def list_dns(conf):
    """
    查询DNS记录
    @args
        conf 配置变量字典 :dict
            user_email :string
            api_key :string
            zone_id :string
    @outputs 服务器返回数据
    @returns 查询到的DNS记录 :dict
    """
    api = conf['api'].format(ZONE_ID=conf['zone_id'])

    # 查询
    headers = {
        "X-Auth-Email": conf['user_email'],
        "X-Auth-Key": conf['api_key'],
        "Content-Type": "application/json"
    }
    params = {"per_page": 100}
    res = requests.get(api, headers=headers, params=params, timeout=3)

    # 检查并输出返回数据
    res.encoding = "utf-8"
    if res.status_code == 200: # 检查是否正常响应
        data = json.loads(res.text)
        if data['success'] and len(data['result']): # 检查数据是否为空
            #print(data['result'])
            for record in data['result']:
                print(record)
                print("-----------------------------")
            return data['result']
        else:
            print("[ Failed! ]")
    else:
        print("[ Failed! ]", "ErrorCode:", res.status_code)


def update_dns(conf):
    """
    更新DNS记录
    @args
        conf 配置变量字典 :dict
            user_email :string
            api_key :string
            zone_id :string
            id 记录id :string
            type 记录类型 :string
            name 三级域名前缀 :string
            content 记录值 :string
            proxied 是否启用代理服务 :bool
    @outputs 更新状态
    """
    api = conf['api'].format(ZONE_ID=conf['zone_id']) + "/" + conf["id"]

    # 更新
    headers = {
        "X-Auth-Email": conf['user_email'],
        "X-Auth-Key": conf['api_key'],
        "Content-Type": "application/json"
    }
    params = {
        "type": conf['type'],
        "name": conf['name'],
        "content": conf['content'],
        "proxied": conf['proxied']
    }
    session = requests.Session()
    session.mount("https://", DNSHTTPAdapter(conf['domain'], conf['ip']))
    res = session.put(api, headers=headers, json=params, timeout=3)
    # print(res.headers)

    # 检查并输出返回数据
    res.encoding = "utf-8"
    if res.status_code == 200: # 检查是否正常响应
        data = json.loads(res.text)
        # print(data)
        if data['success'] and len(data['result']): # 检查数据是否为空
            print("[ Succeeded! ]")
            return data['result']
        else:
            print("[ Failed! ]")
            raise Exception("数据为空或访问服务器失败")
    else:
        print("[ Failed! ]", "ErrorCode:", res.status_code)
        raise Exception("ErrorCode: " + str(res.status_code))


def add_dns(conf):
    """
    增加DNS记录
    @args
        conf 配置变量字典 :dict
            user_email :string
            api_key :string
            zone_id :string
            type 记录类型 :string
            name 三级域名前缀 :string
            content 记录值 :string
            proxied 是否启用代理服务 :bool
            priority 优先级 :int
    @outputs 添加状态及添加的记录数据
    @returns 添加的记录数据 :dict

    """
    api = conf['api'].format(ZONE_ID=conf['zone_id'])
    # 添加
    headers = {
        "X-Auth-Email": conf['user_email'],
        "X-Auth-Key": conf['api_key'],
        "Content-Type": "application/json"
    }
    params = {
        "type": conf['type'],
        "name": conf['name'],
        "content": conf['content'],
        "proxied": conf['proxied'],
        "priority": conf['priority']
    }
    res = requests.post(api, headers=headers, json=params, timeout=3)

    # 检查并输出返回数据
    res.encoding = "utf-8"
    if res.status_code == 200: # 检查是否正常响应
        data = json.loads(res.text)
        # print(data)
        if data['success'] and len(data['result']): # 检查数据是否为空
            print(data['result'])
            print("[ Succeeded! ]")
            return data['result']
        else:
            print("[ Failed! ]")
    else:
        print("[ Failed! ]", "ErrorCode:", res.status_code)


def delete_dns(conf):
    """
    删除DNS记录
    @args
        conf 配置变量字典 :dict
            user_email :string
            api_key :string
            zone_id :string
            id 记录id :string
    @outputs 删除状态
    @returns 删除的记录数据(实际只包含id) :dict
    """
    api = conf['api'].format(ZONE_ID=conf['zone_id']) + "/" + conf['id']
    # 删除
    headers = {
        "X-Auth-Email": conf['user_email'],
        "X-Auth-Key": conf['api_key'],
        "Content-Type": "application/json"
    }
    res = requests.delete(api, headers=headers, timeout=3)

    # 检查并输出返回数据
    res.encoding = "utf-8"
    if res.status_code == 200: # 检查是否正常响应
        data = json.loads(res.text)
        # print(data)
        if data['success'] and len(data['result']): # 检查数据是否为空
            print("[ Succeeded! ]")
            return data['result']
        else:
            print("[ Failed! ]")
    else:
        print("[ Failed! ]", "ErrorCode:", res.status_code)


if __name__ == "__main__":
    try:
        # 参数处理
        parser = argparse.ArgumentParser(description="通过Cloudflare提供的API实现DNS记录的查询、增加、更新和删除")
        parser.add_argument("-l", "--list", action="store_true", help="查询DNS记录")
        parser.add_argument("-a", "--add", action="store_true", help="增加DNS记录")
        parser.add_argument("-u", "--update", action="store_true", help="更新DNS记录")
        parser.add_argument("-d", "--delete", action="store_true", help="删除DNS记录")
        args = parser.parse_args()

        # 统计参数数量
        args_list = list(vars(args).values())
        args_count = sum(args_list)

        # 处理
        if args_count != 1:
            print("标志数量过多或过少! 此脚本仅支持一个标志!")
            sys.exit(-1)
        else:
            # 配置
            conf = generate_conf()
            if(args.list):
                # 查询
                list_dns(conf)
            elif(args.add):
                # 进一步配置
                conf = add_meta_conf(conf, require_id=False, require_priority=True) 
                # 增加
                add_dns(conf)
            elif(args.update):
                # 进一步配置
                conf = add_meta_conf(conf)
                # 更新
                update_dns(conf)
            elif(args.delete):
                # 进一步配置
                conf = add_meta_conf(conf, require_meta=False)
                # 删除
                delete_dns(conf)
    except KeyboardInterrupt:
        sys.stderr.write("\n[ Stopped! ]\n")
        sys.exit(-1)