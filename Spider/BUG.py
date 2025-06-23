import http.client
import re
import requests
from bs4 import BeautifulSoup
import json
import time

country = "https://gangkou.gongjucha.com/guojia/Indonesia.html"
time.sleep(0.5)
# 记得加个延迟
conn = http.client.HTTPSConnection("gangkou.gongjucha.com")
payload = ''
headers = {}
conn.request("GET", country, payload, headers)
res = conn.getresponse()
data = res.read()
# print(data.decode("utf-8"))



# # 定义正则表达式模式  （第一版）
# port_pattern = re.compile(r"""
#         <tr>.*?  # 行开始
#         <td><a\s+href="(?P<url>[^"]+)"\s+title="(?P<chinese_name>[^"]+)(?P<english_name>[^"]+)">.*?</a></td>.*?
#         <td>(?P<port_code>[A-Z]+)</td>.*?
#         <td>.*?</td>.*?  # 跳过第三列
#         <td>.*?</td>.*?  # 跳过第四列
#         <td><a\s+href="[^"]+".*?>(?P<country>[^&nbsp;]+)&nbsp;(?P<country_english>[^<]+)</a></td>.*?
#         </tr>
#     """, re.DOTALL | re.VERBOSE)

# 改进的正则表达式模式  针对数字修改的版本
port_pattern = re.compile(r"""
    <tr>.*?  # 行开始
    <td><a\s+href="(?P<url>/gangkou/[^"]+)"\s+title="(?P<chinese_name>[\u4e00-\u9fa5]+[^\u4e00-\u9fa5]*)(?P<english_name>[^"]+)">.*?</a></td>.*?
    <td>(?P<port_code>[A-Z0-9]+)</td>.*?  # 允许港口代码包含数字
    <td>.*?</td>.*?  # 跳过第三列
    <td>.*?</td>.*?  # 跳过第四列
    <td><a\s+href="[^"]+".*?>(?P<country>[\u4e00-\u9fa5]+).*?&nbsp;(?P<country_english>[a-zA-Z\s()]+)</a></td>.*?
    </tr>
""", re.DOTALL | re.VERBOSE)


print(len(port_pattern.findall(data.decode('utf-8'))))
# 提取所有港口信息
ports = []
temp= port_pattern.finditer(data.decode("utf-8"))
for match in temp:
    ports.append({
        'chinese_name': match.group('chinese_name'),
        'english_name': match.group('english_name'),
        'port_code': match.group('port_code'),
        'country': match.group('country'),
        'country_english': match.group('country_english')
    })
print(ports)

for data in ports:
    pattern = re.compile(r'^([\u4e00-\u9fa5]+)(.*)$')
    match = pattern.match(data['chinese_name'])

    if match:
        chinese_part = match.group(1)  # 中文部分：纽瓦克
        english_part = match.group(2).strip()  # 英文部分：newark,n（去除首尾空格）
    else:
        # 若匹配失败，默认处理（可根据需求调整）
        chinese_part = data['chinese_name']
        english_part = ''

    # 2. 拼接英文部分到 english_name 前
    new_english_name = f"{english_part}{data['english_name']}"  # 拼接结果：newark,nj（原数据英文为 'j'）

    # 3. 更新字典数据
    data['chinese_name'] = chinese_part
    data['english_name'] = new_english_name
print(ports)