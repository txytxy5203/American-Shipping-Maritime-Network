import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import sys
sys.path.append('../Algorithm')
import re
import json
import powerlaw
from ConstructNetwork import *


def Save_Network_USExport_Season(cls, year: int, season: str) -> None:

    last = [12]
    next = [1,2]

    port_data = cls.Read_Port_Data()
    HSCode = Read.read_USExpHSCode()

    # 过滤数据，只保留美国的港口
    us_data = {
        port_code: info
        for port_code, info in port_data.items()
        if "United States" in info.get("country_english", "")
    }
    us_data_dict = {value["english_name"]: key for key, value in us_data.items()}

    G = nx.MultiDiGraph()
    for y in [year, year + 1]:
        # 因为Winter横跨两年
        US_data_path = 'D:/PortData/' + str(y) + '/USExport' + str(y) + '.csv'

        # nrows = 1000000
        DataFrame = pd.read_csv(US_data_path, header=None)
        DataFrame.columns = ['panjivaRecordId', 'billOfLadingNumber', 'shpmtDate', 'shpCountry', 'shpmtDestination',
                             'portOfUnlading', 'portOfLading', 'portOfLadingCountry', 'portOfUnladingCountry',
                             'vessel', 'volumeTEU', 'weightKg', 'valueOfGoodsUSD']
        # 剔除重复数据
        DataFrame = DataFrame.drop_duplicates()
        # 将 相关列转换为字符串类型
        DataFrame['portOfUnlading'] = DataFrame['portOfUnlading'].astype(str)
        DataFrame['portOfLading'] = DataFrame['portOfLading'].astype(str)
        DataFrame['panjivaRecordId'] = DataFrame['panjivaRecordId'].astype(str)
        DataFrame['portOfUnladingCountry'] = DataFrame['portOfUnladingCountry'].astype(str)
        DataFrame['shpmtDate'] = DataFrame['shpmtDate'].astype(str)

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
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])

        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")
        print("DataFrame处理完毕")

        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        USIndex = 0
        OriIndex = 0

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 过滤季节
            month = int(row['shpmtDate'][5:7])  # 这里就直接字符串切片了
            if (y == year and month not in last) or (y == year + 1 and month not in next):
                continue

            # 声明港口唯一代码
            UnLading_Code = str()
            Lading_Code = str()

            # 声明一个 是否匹配 的bool值
            match = False

            portOfLading = row['portOfLading'].lower()
            for us_port in us_data_dict.keys():
                us_port_deal = us_port.lower().split(',', 1)[0]
                if us_port_deal in portOfLading:
                    USIndex += 1
                    match = True
                    # 将港口代码赋值给Lading_Code即可
                    Lading_Code = us_data_dict[us_port]
                    break
            # 如果没有找到匹配的港口 则 continue
            if not match:
                error_port.add(portOfLading)
                continue

            # 声明一个 是否匹配 的bool值
            match = False

            portOfUnlading = row['portOfUnlading'].lower()
            portOfUnlading = re.sub(r'[^a-zA-Z]', '', portOfUnlading)
            portOfUnlading_country = row['portOfUnladingCountry'].lower()

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                port_country = port_data[port]["country_english"].lower()
                if port_name in portOfUnlading and portOfUnlading_country == port_country:
                    OriIndex += 1
                    match = True
                    UnLading_Code = port
                    break
            if not match:
                error_port.add(portOfUnlading)
                continue

            # 注意这里的字符串是 str 类型
            if row['panjivaRecordId'] not in HSCode.keys():
                continue
            if HSCode[row['panjivaRecordId']] is None:
                continue

            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': HSCode[row['panjivaRecordId']],
                'year': y,
                'month': month
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

    # 使用 GraphML 保存图
    nx.write_graphml(G, '../Data/' + str(year) + '/US/Season/Winter/USExport' + str(year) + '_Winter' + '.graphml')

    print(USIndex / len(DataFrame))
    print(OriIndex / len(DataFrame))
    print("数据的最终利用率", G.number_of_edges() / Origin_Len)