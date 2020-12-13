"""
@author Kowaine
@desc windows环境下将脚本添加到开机启动,或从开机启动删除
@date 2020/12/14
"""


import platform, sys
import argparse
import bootmanager4windows as bm


""" 配置项 """
# 脚本位置
SCRIPT_PATH = r"E:\Github\cloudflare_ddns\ddns.py"
# 启动项名称
BOOT_NAME = "CloudflareDDNS"


if __name__ == "__main__":
    try:
        # 判断是否是windows系统
        if not platform.system() is "Windows":
            sys.stderr.write("\n请在Windows环境下使用!\n")
            sys.exit(-1)
        else:
            # 参数处理
            parser = argparse.ArgumentParser(description="将DDNS脚本添加到启动项(管理员可用)、从启动项删除(管理员可用)、或是查询是否已存在于启动项")
            parser.add_argument("-a", "--add", action="store_true", help="将DDNS脚本添加到启动项")
            parser.add_argument("-d", "--delete", action="store_true", help="将DDNS脚本从启动项删除")
            parser.add_argument("-q", "--query", action="store_true", help="查询DDNS脚本是否已存在于启动项")
            args = parser.parse_args()

            # 统计参数数量
            args_list = list(vars(args).values())
            args_count = sum(args_list)
            # print(args_list)

            # 处理
            if args_count != 1:
                print("标志数量过多或过少! 此脚本仅支持一个标志!")
                sys.exit(-1)
            else:
                if(args.add):
                    # 添加
                    bm.add(BOOT_NAME, SCRIPT_PATH)
                    sys.stdout.write("添加成功！\n")
                elif(args.delete):
                    bm.delete(BOOT_NAME)
                    sys.stdout.write("删除成功！\n")
                elif(args.query):
                    try:
                        bm.query(BOOT_NAME)
                        sys.stdout.write("查询结果：启动项已存在！\n")
                    except bm.QueryError as e:
                        if e.boot_name == BOOT_NAME:
                            sys.stdout.write("查询结果：启动项尚未添加！\n")
                        else:
                            raise e
    except bm.QueryError as e:
        boot_name = e.boot_name
        sys.stderr.write("未查询到指定键值！请检查本脚本配置！\n")
    except KeyboardInterrupt:
        sys.stderr.write("[ Stopped! ]\n")