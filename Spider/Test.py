import http.client
import re
import requests
from bs4 import BeautifulSoup
import json
import time

def GET_Country_Html():
    url = "https://gangkou.gongjucha.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    Country_html = []

    try:
        # 发送 GET 请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查 HTTP 错误状态
        response.encoding = response.apparent_encoding  # 自动识别编码

        # 解析 HTML
        soup = BeautifulSoup(response.text, "lxml")

        # 示例：提取港口列表（需根据实际网页结构调整）
        port_list = soup.find_all("div", class_="panel-body")  # 假设港口信息在 class 为 port-item 的 div 中
        ppp = port_list[2].find_all("a")
        for port in ppp:
            port = port.get("href")
            Country_html.append(port)
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
    except Exception as e:
        print(f"解析失败：{e}")
    return Country_html
    # for item in Country_html:
    #     print(item)
    # print(len(Country_html))

ports = []
Countrys = GET_Country_Html()

for country in Countrys:
    time.sleep(0.2)
    # 记得加个延迟
    conn = http.client.HTTPSConnection("gangkou.gongjucha.com")
    payload = ''
    headers = {}
    conn.request("GET", country, payload, headers)
    res = conn.getresponse()
    data = res.read()
    # print(data.decode("utf-8"))
    
    # # 定义正则表达式模式
    # port_pattern = re.compile(r"""
    #     <tr>.*?  # 行开始
    #     <td><a\s+href="[^"]+".*?title="(?P<chinese_name>[\u4e00-\u9fa5]+)(?P<english_name>[a-z]+)">.*?</a></td>.*?
    #     <td>(?P<port_code>[A-Z]+)</td>.*?
    #     <td>.*?</td>.*?  # 跳过第三列
    #     <td>.*?</td>.*?  # 跳过第四列
    #     <td><a\s+href="[^"]+".*?>(?P<country>[\u4e00-\u9fa5]+)&nbsp;(?P<country_english>[A-Za-z]+)</a></td>.*?
    #     </tr>
    # """, re.DOTALL | re.VERBOSE)
    
    # # 定义改进后的正则表达式模式
    # port_pattern = re.compile(r"""
    #     <tr>.*?  # 行开始
    #     <td><a\s+href="(?P<url>/gangkou/[^"]+)"\s+title="(?P<chinese_name>[\u4e00-\u9fa5]+)(?P<english_name>[^"]+)">.*?</a></td>.*?
    #     <td>(?P<port_code>[A-Z]{5})</td>.*?  # 明确港口代码为5个大写字母
    #     <td>.*?</td>.*?  # 跳过第三列
    #     <td>.*?</td>.*?  # 跳过第四列
    #     <td><a\s+href="[^"]+".*?>(?P<country>[\u4e00-\u9fa5]+)&nbsp;(?P<country_english>[a-zA-Z]+)</a></td>.*?
    #     </tr>
    # """, re.DOTALL | re.VERBOSE)
    
    # 定义正则表达式模式  （第一版）
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
    
    for match in port_pattern.finditer(data.decode("utf-8")):
        ports.append({
            'chinese_name': match.group('chinese_name'),
            'english_name': match.group('english_name'),
            'port_code': match.group('port_code'),
            'country': match.group('country'),
            'country_english': match.group('country_english')
        })
    
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

# 打印结果
for port in ports:
    print(port)
print(len(ports))

# 转换为以 port_code 为键的字典
ports_dict = {port['port_code']: port for port in ports}

# 保存为 JSON 文件（对象形式）
with open('../Data/Port/Port_Info_Json.json', 'w', encoding='utf-8') as f:
    json.dump(ports_dict, f, ensure_ascii=False, indent=4)

# 输出示例（仅演示）
print(json.dumps(ports_dict, ensure_ascii=False, indent=4))
