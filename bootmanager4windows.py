"""
@author Kowaine
@desc windows环境下添加、删除、与查询启动项的功能模块组
@date 2020/12/14
"""


import winreg


""" 基本配置项 """
# 注册表键（一般来说不需要修改）
BOOT_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"


class QueryError(Exception):
    def __init__(self, boot_name):
        self.boot_name = boot_name
    
    def __str__(self):
        return "找不到该名称的启动项 {boot_name}".format(boot_name=self.boot_name)


def query(boot_name):
    """
    查询对应名称的启动项
    @args
        boot_name 启动项名称 :string
    @returns
        成功: 返回启动项路径
        失败: 抛出QueryError
    """
    try:
        # 打开启动项有关键
        try:
            key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, BOOT_KEY)
        except FileNotFoundError:
            raise QueryError(BOOT_KEY)
        
        # 查询
        try:
            value = winreg.QueryValueEx(key, r"CloudflareDDNS")[0]
        except FileNotFoundError:
            raise QueryError(boot_name)
    except Exception as e:
        raise e
    finally:
        winreg.CloseKey(key)
    
    return value


def delete(boot_name):
    """
    删除对应名称的启动项
    @args
        boot_name 启动项名称 :string
    @returns
        成功: True :boolean
        失败: 抛出QueryError
    """
    try:
        # 打开启动项有关键
        try:
            key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, BOOT_KEY, 0, winreg.KEY_SET_VALUE)
        except FileNotFoundError:
            raise QueryError(BOOT_KEY)
        
        # 查询
        try:
            winreg.DeleteValue(key, r"CloudflareDDNS")
        except FileNotFoundError:
            raise QueryError(boot_name)
    except Exception as e:
        raise e
    finally:
        winreg.CloseKey(key)

    return True


def add(boot_name, path):
    """
    添加对应名称的启动项
    @args
        boot_name 启动项名称 :string
        path 启动项路径 :string
    @returns
        成功: True :boolean
        失败: 抛出QueryError
    """
    try:
        # 打开启动项有关键
        try:
            key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, BOOT_KEY, 0, winreg.KEY_SET_VALUE)
        except FileNotFoundError:
            raise QueryError(BOOT_KEY)
        
        # 查询
        try:
            winreg.SetValueEx(key, r"CloudflareDDNS", 0, winreg.REG_SZ, path)
        except FileNotFoundError:
            raise QueryError(boot_name)
    except Exception as e:
        raise e
    finally:
        winreg.CloseKey(key)

    return True