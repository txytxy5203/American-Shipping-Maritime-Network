import time

import requests
import json

# LocationlQ
# https://docs.locationiq.com/docs/search-forward-geocoding
# port_name = "aqineh，Afghanistan"
# url = "https://us1.locationiq.com/v1/search?key=pk.abff6204e75809c0221e6da17a295174&q=" + port_name + "&format=json&"
# data=requests.get(url)
# print(data.json())

# Geokeo
# https://geokeo.com/documentation.php#response
# url = "https://geokeo.com/geocode/v1/search.php?q=osaka&api=7350bfc38af4d0d39eda0d3e69d44804"
# data=requests.get(url)
# print(data.json())

# yandex Map
# https://developer.tech.yandex.ru/services/3
# url = "https://geocode-maps.yandex.ru/v1/?apikey=69508d90-1809-40ce-879e-f6094475f18e&geocode=osaka&lang=en_US&format=json"
# data=requests.get(url)
# print(data.json())



# port_name = "aqineh，Afghanistan"
# url = "https://us1.locationiq.com/v1/search?key=pk.abff6204e75809c0221e6da17a295174&q=" + port_name + "&format=json&"
# data=requests.get(url)
data_path = "../Data/Port/Port_Info_Json.json"
# 一次性读取整个JSON文件
with open(data_path, "r", encoding="utf-8") as file:
    port_data = json.load(file)
for port in port_data:
    if not port_data[port]["isLocation"]:
        try:
            time.sleep(1)
            port_name = port_data[port]["english_name"] + "," +port_data[port]["country_english"]
            url = "https://us1.locationiq.com/v1/search?key=pk.abff6204e75809c0221e6da17a295174&q=" + port_name + "&format=json&"
            data = requests.get(url).json()
            port_data[port]["latitude"] = data[0]['lat']
            port_data[port]["longitude"] = data[0]['lon']
            print(port + "已经处理完成")
        except Exception as e:
            print(port + "出错")
# 一次性写入更新后的全部数据
with open(data_path, 'w', encoding='utf-8') as file:
    json.dump(port_data, file, ensure_ascii=False, indent=4)

# # port_name = port_data["AFAQE"]["english_name"] + "," +port_data["AFAQE"]["country_english"]
# # print(port_name)
# # print(type(port_name))
# url = "https://us1.locationiq.com/v1/search?key=pk.abff6204e75809c0221e6da17a295174&q=" + "aqineh，Afghanistan" + "&format=json&"
# data = requests.get(url).json()
# print(data[0]['lat'])
# print(data[0]['lon'])