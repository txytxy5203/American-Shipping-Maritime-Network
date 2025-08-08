import json
import requests
from bs4 import BeautifulSoup
import re
import time

def GET_Port_Coordinate(port_code):
    '''
    传入港口代码 得到经纬度
    :param port_code: 港口代码
    :return:
    '''
    url = "https://gangkou.gongjucha.com/gangkou/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    # try:
    # 发送 GET 请求
    response = requests.get(url + port_code + ".html", headers=headers, timeout=10)
    response.raise_for_status()  # 检查 HTTP 错误状态
    response.encoding = response.apparent_encoding  # 自动识别编码

    # 解析 HTML
    soup = BeautifulSoup(response.text, "lxml")

    # 示例：提取港口列表（需根据实际网页结构调整）
    possible_Info = soup.find_all("li", class_="list-group-item")

    target_Info = possible_Info[6]

    Coord = extract_coordinates(str(target_Info))

    return Coord

    # except requests.exceptions.RequestException as e:
    #     print(f"请求失败：{e}")
    # except Exception as e:
    #     print(f"解析失败：{e}")
def extract_coordinates(text):
    # 定义匹配经纬度的正则表达式模式
    # 匹配 "经度：数字" 或 "纬度：数字" 格式，允许负数
    pattern = r'(经度|纬度)：([-+]?[\d.]+)'

    # 用于存储提取的经纬度
    coordinates = {}

    # 查找所有匹配项
    matches = re.finditer(pattern, text)

    for match in matches:
        key = match.group(1)
        value = float(match.group(2))

        # 将"经度"和"纬度"映射为标准键名
        if key == "经度":
            coordinates["longitude"] = value
        elif key == "纬度":
            coordinates["latitude"] = value
    # 检查是否提取到经纬度
    if not coordinates:
        raise ValueError("未在文本中找到有效的经纬度信息")
    return coordinates

    # 打开文件并加载 JSON 数据


isLocation1 = {"isLocation": True}  # 修正键名拼写
isLocation2 = {"isLocation": False}

data_path = "../Data/2019/Port/Port_Info_Json.json"

# 一次性读取整个JSON文件
with open(data_path, "r", encoding="utf-8") as file:
    port_data = json.load(file)

# 遍历所有港口代码
for port_code in list(port_data.keys()):  # 使用列表副本避免修改迭代器
    time.sleep(0.4)
    try:
        coordinates = GET_Port_Coordinate(port_code)
        # 更新经纬度信息和标记
        port_data[port_code].update(coordinates)
        port_data[port_code].update(isLocation1)
        print(f"成功更新港口 {port_code} 的经纬度信息")

    except Exception as e:
        # 记录错误信息并标记为未找到经纬度
        print(f"获取港口 {port_code} 经纬度失败: {str(e)}")
        if port_code in port_data:  # 确保键存在
            port_data[port_code].update(isLocation2)

# 一次性写入更新后的全部数据
with open(data_path, 'w', encoding='utf-8') as file:
    json.dump(port_data, file, ensure_ascii=False, indent=4)

print("所有港口信息更新完成")

