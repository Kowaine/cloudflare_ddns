"""
@author Kowaine
@desc API key 和 用户配置
@date 2020/08/10
"""

# 用户邮箱配置
USER_EMAIL = ""

# Global API KEY
API_KEY = ""

# Zone ID
ZONE_ID = ""

# API
API = "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"

# 是否默认使用以上配置, 关闭则会每次提醒用户输入(关闭后依旧可以通过留空回车来使用默认值)
ALLWAYS_DEFAULT = True