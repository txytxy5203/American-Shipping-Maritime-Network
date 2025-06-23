import json

import networkx as nx
import pandas as pd
import difflib
import re
import sys
sys.path.append('..')
import Algorithm.Read


HSCode = Algorithm.Read.read_USImpHSCode()
data_path = "../Data/Port/Port_Info_Json.json"
# 一次性读取整个JSON文件
with open(data_path, "r", encoding="utf-8") as file:
    port_data = json.load(file)
# 过滤数据，只保留美国的港口
us_data = {
    port_code: info
    for port_code, info in port_data.items()
    if "United States of America" in info.get("country_english", "")
}
us_data_dict = {value["english_name"]: key for key, value in us_data.items()}


US_data_path = 'D:/PortData/USImport2019.csv'
# nrows = 1000000
DataFrame = pd.read_csv(US_data_path, header=None)
DataFrame.columns = ['panjivaRecordId', 'billOfLadingNumber', 'arrivalDate', 'conCountry', 'shpCountry',
                     'portOfUnlading', 'portOfLading',
                     'portOfLadingCountry', 'portOfLadingRegion', 'transportMethod', 'vessel', 'volumeTEU',
                     'weightKg',
                     'valueOfGoodsUSD']
# 剔除重复数据
DataFrame = DataFrame.drop_duplicates()
# 将 相关列转换为字符串类型
DataFrame['portOfUnlading'] = DataFrame['portOfUnlading'].astype(str)
DataFrame['portOfLading'] = DataFrame['portOfLading'].astype(str)
DataFrame['panjivaRecordId'] = DataFrame['panjivaRecordId'].astype(str)

print("DataFrame加载完毕")

print(f"原始DataFrame大小:{len(DataFrame)}")
Origin_Len = len(DataFrame)
# # 剔除重复数据
# 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
DataFrame = DataFrame.drop_duplicates(subset=['panjivaRecordId'], keep='first')
print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

# 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
null_counts = DataFrame.isnull().sum()
print("每个字段的null值情况：")
print(null_counts / len(DataFrame))

# 1 使用均值填充 TEU
DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
# 2 删除 某某 列为空的行
DataFrame = DataFrame.dropna(subset=['portOfUnlading','portOfLading'])

print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")
print("DataFrame处理完毕")



error_port = set()
timer = 0
# 计数用 记录有多少数据能够在 标准表中找到
USIndex = 0
OriIndex = 0
match = False
G= nx.MultiDiGraph()
for index, row in DataFrame.iterrows():
    timer += 1
    if timer / len(DataFrame) > 0.01:
        print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
        timer = 0

    # 声明港口唯一代码
    UnLading_Code= str()
    Lading_Code= str()

    # 声明一个 是否匹配 的bool值
    match = False

    # 在美国的port里面去找即可  注意小写和按逗号分割
    portOfUnlading = row['portOfUnlading'].lower()
    for us_port in us_data_dict.keys():
        us_port_deal = us_port.lower().split(',',1)[0]
        if us_port_deal in portOfUnlading:
            USIndex += 1
            match = True
            # 将港口代码赋值给UnLading_Code即可
            UnLading_Code = us_data_dict[us_port]
            break
    # 如果没有找到匹配的港口 则 continue
    if not match:
        error_port.add(portOfUnlading)
        continue



    # 声明一个 是否匹配 的bool值
    match = False

    portOfLading = row['portOfLading'].lower()
    portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)
    for port in port_data:
        port_name = port_data[port]["english_name"].lower()
        port_name = re.sub(r'[^a-zA-Z]', '', port_name)
        if port_name in portOfLading:
            OriIndex += 1
            match = True
            Lading_Code = port
            break
    if not match:
        error_port.add(portOfLading)
        continue

    # 注意这里的字符串是 str 类型
    if row['panjivaRecordId'] not in HSCode.keys():
        continue
    if HSCode[row['panjivaRecordId']] is None:
        continue

    # 为每条边生成一个唯一的键
    edge_key = f"USImp2019_{row['panjivaRecordId']}"
    # 创建一个字典来存储边的属性
    edge_attrs = {
        'volumeTEU': row['volumeTEU'],
        'HSCode': HSCode[row['panjivaRecordId']]
    }
    # 给 edge 和 node 添加属性
    G.add_edge(Lading_Code, UnLading_Code, key=edge_key, **edge_attrs)
    G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
    G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]


# 使用 GraphML 保存图
nx.write_graphml(G, '../Data/US2019/USImport2019.graphml')

print(USIndex / len(DataFrame))
print(OriIndex / len(DataFrame))
print("数据的最终利用率",G.number_of_edges() / Origin_Len)
# for error in error_port:
#     print(error)