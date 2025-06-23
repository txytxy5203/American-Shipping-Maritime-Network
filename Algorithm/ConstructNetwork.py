import re
import json
import sys
sys.path.append('../Algorithm')
import pandas as pd
import numpy as np
import networkx as nx
import unicodedata
from Read import Read


# Port_Name = Algorithm.Read.read_port_name_info()
# Remove_Port = Algorithm.Read.read_remove_port_info()


class ConstructNetwork:


    @classmethod
    def Read_Port_Data(cls):
        '''
        类方法 直接 cls. 出来用
        :return: Port_Data 标准表
        '''
        data_path = "../Data/Port/Port_Info_Json.json"
        # 一次性读取整个JSON文件
        with open(data_path, "r", encoding="utf-8") as file:
            port_data = json.load(file)
        return port_data

    @classmethod
    def To_English_Spelling(cls, text: str) -> str:
        """将带有变音符号的字符串转换为英语化的拼写"""
        # 规范化为 NFKD 形式，分离变音符号
        normalized = unicodedata.normalize('NFKD', text)
        # 只保留 ASCII 字符（移除变音符号）
        return ''.join([c for c in normalized if ord(c) < 128])

    @classmethod
    def Save_Network_USImport2019(cls):

        US_data_path = 'D:/PortData/USImport2019.csv'
        port_data = cls.Read_Port_Data()
        HSCode = Read.read_USImpHSCode()


        # 过滤数据，只保留美国的港口
        us_data = {
            port_code: info
            for port_code, info in port_data.items()
            if "United States of America" in info.get("country_english", "")
        }
        us_data_dict = {value["english_name"]: key for key, value in us_data.items()}


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
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])

        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")
        print("DataFrame处理完毕")


        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        USIndex = 0
        OriIndex = 0

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 声明港口唯一代码
            UnLading_Code = str()
            Lading_Code = str()

            # 声明一个 是否匹配 的bool值
            match = False

            # 在美国的port里面去找即可  注意小写和按逗号分割
            portOfUnlading = row['portOfUnlading'].lower()
            for us_port in us_data_dict.keys():
                us_port_deal = us_port.lower().split(',', 1)[0]
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
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)

    @classmethod
    def Save_Network_USExport2019(cls):

        US_data_path = 'D:/PortData/USExport2019.csv'
        port_data = cls.Read_Port_Data()
        HSCode = Read.read_USExpHSCode()

        # 过滤数据，只保留美国的港口
        us_data = {
            port_code: info
            for port_code, info in port_data.items()
            if "United States of America" in info.get("country_english", "")
        }
        us_data_dict = {value["english_name"]: key for key, value in us_data.items()}

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

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

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
            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                if port_name in portOfUnlading:
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

            # 为每条边生成一个唯一的键
            edge_key = f"USExp2019_{row['panjivaRecordId']}"
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
        nx.write_graphml(G, '../Data/US2019/USExport2019.graphml')

        print(USIndex / len(DataFrame))
        print(OriIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)

    @classmethod
    def Save_Network_BRImport2019(cls):

        BR_data_path = 'D:/PortData/BRImport2019.csv'
        port_data = cls.Read_Port_Data()


        # nrows = 1000000
        DataFrame = pd.read_csv(BR_data_path, header=None)
        DataFrame.columns =  ['panjivaRecordId', 'shpmtDate', 'conCountry', 'shpCountry', 'shpmtOrigin','shpmtOriginCountry','shpmtDestination',
                            'shpmtDestinationCountry','portOfOriginCountry','portOfUnlading','portOfUnladingCountry','portOfLading', 'vesselName',
                           'hsCode','volumeTEU', 'grossWeightKg', 'valueOfGoodsUSD']
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
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])

        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")
        print("DataFrame处理完毕")


        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        LadingIndex = 0
        UnLadingIndex = 0

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 声明港口唯一代码
            Lading_Code = str()
            UnLading_Code = str()
            # 声明一个 是否 匹配 的bool值
            UnLading_Match = False
            Lading_Match = False


            portOfUnlading = row['portOfUnlading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfUnlading = re.sub(r'\([^)]*\)', '', portOfUnlading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfUnlading = cls.To_English_Spelling(portOfUnlading)
            # 再去掉空格
            portOfUnlading = re.sub(r'[^a-zA-Z]', '', portOfUnlading)


            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                if  (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if  (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False:
                    LadingIndex += 1
                    Lading_Match = True
                    Lading_Code = port

            # 如果没有找到匹配的港口 则 continue
            if not UnLading_Match:
                error_port.add(portOfUnlading)
                continue

            if not Lading_Match:
                error_port.add(portOfLading)
                continue

            # 这里判断 hsCode 是不是 None 即可
            if row['hsCode'] is None:
                continue

            # 为每条边生成一个唯一的键
            edge_key = f"BRImp2019_{row['panjivaRecordId']}"
            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': row['hsCode']
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, key=edge_key, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/BR2019/BRImport2019.graphml')

        print(UnLadingIndex / len(DataFrame))
        print(LadingIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)
        for item in error_port:
            print(item)

    @classmethod
    def Save_Network_BRExport2019(cls):

        BR_data_path = 'D:/PortData/BRExport2019.csv'
        port_data = cls.Read_Port_Data()

        # nrows = 1000000
        DataFrame = pd.read_csv(BR_data_path, header=None)
        DataFrame.columns = ['panjivaRecordId', 'billOfLadingNumber', 'shpmtDate', 'conCountry', 'shpCountry', 'shpmtOrigin',
                             'shpmtOriginCountry', 'shpmtDestination', 'shpmtDestinationCountry','portOfUnlading',
                             'portOfUnladingCountry','portOfLading','portOfLadingCountry','vesselName',
                             'hsCode','volumeTEU', 'grossWeightKg', 'valueOfGoodsUSD']

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
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])

        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")
        print("DataFrame处理完毕")

        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        LadingIndex = 0
        UnLadingIndex = 0

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 声明港口唯一代码
            Lading_Code = str()
            UnLading_Code = str()
            # 声明一个 是否 匹配 的bool值
            UnLading_Match = False
            Lading_Match = False

            portOfUnlading = row['portOfUnlading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfUnlading = re.sub(r'\([^)]*\)', '', portOfUnlading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfUnlading = cls.To_English_Spelling(portOfUnlading)
            # 再去掉空格
            portOfUnlading = re.sub(r'[^a-zA-Z]', '', portOfUnlading)


            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                # 交叉匹配 无敌！！
                if (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False:
                    LadingIndex += 1
                    Lading_Match = True
                    Lading_Code = port

            # 如果没有找到匹配的港口 则 continue
            if not UnLading_Match:
                error_port.add(portOfUnlading)
                continue

            if not Lading_Match:
                error_port.add(portOfLading)
                continue

            # 这里判断 hsCode 是不是 None 即可
            if row['hsCode'] is None:
                continue

            # 为每条边生成一个唯一的键
            edge_key = f"BRExp2019_{row['panjivaRecordId']}"
            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': row['hsCode']
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, key=edge_key, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/BR2019/BRExport2019.graphml')

        print(UnLadingIndex / len(DataFrame))
        print(LadingIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)
        for item in error_port:
            print(item)

    @classmethod
    def Save_Network_CLImport2019(cls):

        CL_data_path = 'D:/PortData/CLImport2019.csv'
        port_data = cls.Read_Port_Data()

        # nrows = 1000000
        DataFrame = pd.read_csv(CL_data_path, header=None)
        DataFrame.columns = ['panjivaRecordId', 'receiptDate', 'conCountry', 'shpmtOrigin' ,
                            'portOfUnlading', 'portOfUnladingCountry', 'portOfLading', 'portOfLadingCountry',
                            'countryOfSale', 'transportMethod',	'volumeTEU', 'grossWeightKg',
                            'valueOfGoodsFOBUSD', 'valueOfGoodsItemFOBUSD', 'hsCode']
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
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])

        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")
        print("DataFrame处理完毕")

        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        LadingIndex = 0
        UnLadingIndex = 0

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 声明港口唯一代码
            Lading_Code = str()
            UnLading_Code = str()
            # 声明一个 是否 匹配 的bool值
            UnLading_Match = False
            Lading_Match = False

            portOfUnlading = row['portOfUnlading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfUnlading = re.sub(r'\([^)]*\)', '', portOfUnlading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfUnlading = cls.To_English_Spelling(portOfUnlading)
            # 再去掉空格
            portOfUnlading = re.sub(r'[^a-zA-Z]', '', portOfUnlading)

            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                if (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False:
                    LadingIndex += 1
                    Lading_Match = True
                    Lading_Code = port

            # 如果没有找到匹配的港口 则 continue
            if not UnLading_Match:
                error_port.add(portOfUnlading)
                continue

            if not Lading_Match:
                error_port.add(portOfLading)
                continue

            # 这里判断 hsCode 是不是 None 即可
            if row['hsCode'] is None:
                continue

            # 为每条边生成一个唯一的键
            edge_key = f"CLImp2019_{row['panjivaRecordId']}"
            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': row['hsCode']
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, key=edge_key, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/CL2019/CLImport2019.graphml')

        print(UnLadingIndex / len(DataFrame))
        print(LadingIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)
        for item in error_port:
            print(item)

    @classmethod
    def Save_Network_COExport2019(cls):

        CO_data_path = 'D:/PortData/COExport2019.csv'
        port_data = cls.Read_Port_Data()

        # nrows = 1000000
        DataFrame = pd.read_csv(CO_data_path, header=None)
        DataFrame.columns = ['panjivaRecordId', 'shpmtDate', 'conCountry','shpCountry', 'shpmtOrigin',
		                     'shpmtDestination', 'shpmtDestinationCountry', 'portOfLading', 'portOfLadingCountry',
		                     'transportMethod', 'hsCode', 'volumeTEU', 'itemQuantity', 'itemUnit',
		                     'grossWeightKg', 'netWeightKg', 'valueOfGoodsFOBUSD', 'valueOfGoodsFOBCOP']

        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)

        # 剔除重复数据
        DataFrame = DataFrame.drop_duplicates()
        # 删除 某某 列为空的行  这个一定得放在前面  后面再转字符串
        DataFrame = DataFrame.dropna(subset=['shpmtDestination', 'portOfLading'])
        print(f"剔除重复数据、NULL值后DataFrame大小:{len(DataFrame)}")

        # 将 相关列转换为字符串类型
        DataFrame['shpmtDestination'] = DataFrame['shpmtDestination'].astype(str)
        DataFrame['portOfLading'] = DataFrame['portOfLading'].astype(str)
        DataFrame['panjivaRecordId'] = DataFrame['panjivaRecordId'].astype(str)

        # # 剔除重复数据
        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['panjivaRecordId'], keep='first')


        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        print(null_counts / len(DataFrame))

        # 1 使用均值填充 TEU
        DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)


        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")
        print("DataFrame处理完毕")

        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        LadingIndex = 0
        UnLadingIndex = 0

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 声明港口唯一代码
            Lading_Code = str()
            UnLading_Code = str()
            # 声明一个 是否 匹配 的bool值
            UnLading_Match = False
            Lading_Match = False


            # COExport的数据没有 portofUnlading 使用 shpmtDestination
            portOfUnlading = row['shpmtDestination'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfUnlading = re.sub(r'\([^)]*\)', '', portOfUnlading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfUnlading = cls.To_English_Spelling(portOfUnlading)
            # 再去掉空格
            portOfUnlading = re.sub(r'[^a-zA-Z]', '', portOfUnlading)

            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)

            # 增加国家验证
            UnLadingCountry = row['shpmtDestinationCountry']
            LadingCountry = row['portOfLadingCountry']


            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)

                port_country = port_data[port]["country_english"]
                # 交叉匹配 无敌！！  要增加国家验证  因为有一写港口名称很短 容易误判断
                if (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False and port_country == UnLadingCountry:
                    #
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False and port_country == LadingCountry:
                    #
                    LadingIndex += 1
                    Lading_Match = True
                    Lading_Code = port

            # 如果没有找到匹配的港口 则 continue
            if not UnLading_Match:
                error_port.add(portOfUnlading)
                continue

            if not Lading_Match:
                error_port.add(portOfLading)
                continue

            # 这里判断 hsCode 是不是 None 即可
            if row['hsCode'] is None:
                continue

            # 为每条边生成一个唯一的键
            edge_key = f"COExp2019_{row['panjivaRecordId']}"
            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': row['hsCode']
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, key=edge_key, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/CO2019/COExport2019.graphml')

        print(UnLadingIndex / len(DataFrame))
        print(LadingIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)
        for item in error_port:
            print(item)

    @classmethod
    def Save_Network_INImport2019(cls):

        IN_data_path = 'D:/PortData/INImport2019.csv'
        port_data = cls.Read_Port_Data()

        # nrows = 1000000
        DataFrame = pd.read_csv(IN_data_path, header=None)
        DataFrame.columns = ['panjivaRecordId' ,'departureDate' ,'conCity','conCountry','shpCity','shpCountry',
                             'portOfUnlading','portOfUnladingCountry','portOfUnladingUNLOCODE',
		                     'portOfLading', 'portOfLadingCountry', 'portOfLadingUNLOCODE',
                             'transportMethod', 'hsCode', 'volumeTEU']

        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)

        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['panjivaRecordId'], keep='first')
        print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        # print(null_counts / len(DataFrame))
        # 将小数比例转换为百分比，并格式化为带百分号的字符串
        percent_ratio = (null_counts / len(DataFrame) * 100).apply(lambda x: f"{x:.2f}%")
        print(percent_ratio)

        # # 1 使用均值填充 TEU   INImport2019的TEU全是null 不填充了
        # DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
        # 2 删除 某某 列为空的行
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])
        # 重置索引
        DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引
        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")

        # 将相关列转换为字符串类型
        DataFrame['portOfUnlading'] = DataFrame['portOfUnlading'].astype(str)
        DataFrame['portOfLading'] = DataFrame['portOfLading'].astype(str)
        DataFrame['panjivaRecordId'] = DataFrame['panjivaRecordId'].astype(str)
        print("DataFrame处理完毕")

        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        LadingIndex = 0
        UnLadingIndex = 0

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 声明港口唯一代码
            Lading_Code = str()
            UnLading_Code = str()
            # 声明一个 是否 匹配 的bool值
            UnLading_Match = False
            Lading_Match = False

            portOfUnlading = row['portOfUnlading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfUnlading = re.sub(r'\([^)]*\)', '', portOfUnlading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfUnlading = cls.To_English_Spelling(portOfUnlading)
            # 再去掉空格
            portOfUnlading = re.sub(r'[^a-zA-Z]', '', portOfUnlading)

            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)

            # 增加国家验证
            UnLadingCountry = row['portOfUnladingCountry'].lower()
            LadingCountry = row['portOfLadingCountry'].lower()

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)

                port_country = port_data[port]["country_english"].lower()
                if (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False and port_country == UnLadingCountry:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False and port_country == LadingCountry:
                    LadingIndex += 1
                    Lading_Match = True
                    Lading_Code = port

            # 如果没有找到匹配的港口 则 continue
            if not UnLading_Match:
                error_port.add(portOfUnlading)
                continue

            if not Lading_Match:
                error_port.add(portOfLading)
                continue

            # 这里判断 hsCode 是不是 None 即可
            if row['hsCode'] is None:
                continue

            # 为每条边生成一个唯一的键
            edge_key = f"INImp2019_{row['panjivaRecordId']}"
            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': row['hsCode']
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, key=edge_key, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/IN2019/INImport2019.graphml')

        print(UnLadingIndex / len(DataFrame))
        print(LadingIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)
        for item in error_port:
            print(item)

    @classmethod
    def Save_Network_INExport2019(cls):

        IN_data_path = 'D:/PortData/INExport2019.csv'
        port_data = cls.Read_Port_Data()

        # nrows = 1000000
        DataFrame = pd.read_csv(IN_data_path, header=None)
        DataFrame.columns = ['panjivaRecordId', 'departureDate', 'conCity', 'conCountry', 'shpCity', 'shpCountry',
                             'portOfUnlading', 'portOfUnladingCountry', 'portOfUnladingUNLOCODE',
                             'portOfLading', 'portOfLadingCountry', 'portOfLadingUNLOCODE',
                             'transportMethod', 'hsCode', 'volumeTEU']

        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)

        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['panjivaRecordId'], keep='first')
        print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        # print(null_counts / len(DataFrame))
        # 将小数比例转换为百分比，并格式化为带百分号的字符串
        percent_ratio = (null_counts / len(DataFrame) * 100).apply(lambda x: f"{x:.2f}%")
        print(percent_ratio)

        # 1 使用均值填充 TEU   INImport2019的TEU全是null 不填充了
        # DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
        # 2 删除 某某 列为空的行
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])
        # 重置索引
        DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引
        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")

        # 将相关列转换为字符串类型
        DataFrame['portOfUnlading'] = DataFrame['portOfUnlading'].astype(str)
        DataFrame['portOfLading'] = DataFrame['portOfLading'].astype(str)
        DataFrame['panjivaRecordId'] = DataFrame['panjivaRecordId'].astype(str)
        print("DataFrame处理完毕")

        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        LadingIndex = 0
        UnLadingIndex = 0

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 声明港口唯一代码
            Lading_Code = str()
            UnLading_Code = str()
            # 声明一个 是否 匹配 的bool值
            UnLading_Match = False
            Lading_Match = False

            portOfUnlading = row['portOfUnlading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfUnlading = re.sub(r'\([^)]*\)', '', portOfUnlading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfUnlading = cls.To_English_Spelling(portOfUnlading)
            # 再去掉空格
            portOfUnlading = re.sub(r'[^a-zA-Z]', '', portOfUnlading)

            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)

            # 增加国家验证
            UnLadingCountry = row['portOfUnladingCountry'].lower()
            LadingCountry = row['portOfLadingCountry'].lower()

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                port_country = port_data[port]["country_english"].lower()

                if (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False and port_country == UnLadingCountry:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False and port_country == LadingCountry:
                    LadingIndex += 1
                    Lading_Match = True
                    Lading_Code = port

            # 如果没有找到匹配的港口 则 continue
            if not UnLading_Match:
                error_port.add(portOfUnlading)
                continue

            if not Lading_Match:
                error_port.add(portOfLading)
                continue

            # 这里判断 hsCode 是不是 None 即可
            if row['hsCode'] is None:
                continue

            # 为每条边生成一个唯一的键
            edge_key = f"INExp2019_{row['panjivaRecordId']}"
            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': row['hsCode']
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, key=edge_key, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/IN2019/INExport2019.graphml')

        print(UnLadingIndex / len(DataFrame))
        print(LadingIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)
        for item in error_port:
            print(item)

    @classmethod
    def Save_Network_VEImport2019(cls):

        VE_data_path = 'D:/PortData/VEImport2019.csv'
        port_data = cls.Read_Port_Data()

        # nrows = 1000000
        DataFrame = pd.read_csv(VE_data_path, header=None)
        DataFrame.columns = ['panjivaRecordId' ,'shpmtDate','conCity','conCountry',
		                     'portOfUnlading','portOfUnladingCountry','portOfUnladingUNLOCODE',
		                     'portOfLading','portOfLadingCountry','portOfLadingUNLOCODE',
                             'transportMethod','hsCode','volumeTEU']

        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)

        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['panjivaRecordId'], keep='first')
        print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        # print(null_counts / len(DataFrame))
        # 将小数比例转换为百分比，并格式化为带百分号的字符串
        percent_ratio = (null_counts / len(DataFrame) * 100).apply(lambda x: f"{x:.2f}%")
        print(percent_ratio)

        # # 1 使用均值填充 TEU   INImport2019的TEU全是null 不填充了
        # DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
        # 2 删除 某某 列为空的行
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])
        # 重置索引
        DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引
        print(f"剔除不能使用的数据后DataFrame大小:{len(DataFrame)}({len(DataFrame) / Origin_Len * 100:.2f}%)")

        # 将相关列转换为字符串类型
        DataFrame['portOfUnlading'] = DataFrame['portOfUnlading'].astype(str)
        DataFrame['portOfLading'] = DataFrame['portOfLading'].astype(str)
        DataFrame['panjivaRecordId'] = DataFrame['panjivaRecordId'].astype(str)
        print("DataFrame处理完毕")

        error_port = set()
        timer = 0
        # 计数用 记录有多少数据能够在 标准表中找到
        LadingIndex = 0
        UnLadingIndex = 0

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 声明港口唯一代码
            Lading_Code = str()
            UnLading_Code = str()
            # 声明一个 是否 匹配 的bool值
            UnLading_Match = False
            Lading_Match = False

            portOfUnlading = row['portOfUnlading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfUnlading = re.sub(r'\([^)]*\)', '', portOfUnlading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfUnlading = cls.To_English_Spelling(portOfUnlading)
            # 再去掉空格
            portOfUnlading = re.sub(r'[^a-zA-Z]', '', portOfUnlading)

            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)

            # 增加国家验证
            UnLadingCountry = row['portOfUnladingCountry'].lower()
            LadingCountry = row['portOfLadingCountry'].lower()

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)

                port_country = port_data[port]["country_english"].lower()
                if (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False and port_country == UnLadingCountry:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False and port_country == LadingCountry:
                    LadingIndex += 1
                    Lading_Match = True
                    Lading_Code = port

            # 如果没有找到匹配的港口 则 continue
            if not UnLading_Match:
                error_port.add(portOfUnlading)
                continue

            if not Lading_Match:
                error_port.add(portOfLading)
                continue

            # 这里判断 hsCode 是不是 None 即可
            if row['hsCode'] is None:
                continue

            # 为每条边生成一个唯一的键
            edge_key = f"VEImp2019_{row['panjivaRecordId']}"
            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': row['hsCode']
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, key=edge_key, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/VE2019/VEImport2019.graphml')

        print(UnLadingIndex / len(DataFrame))
        print(LadingIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)
        for item in error_port:
            print(item)
# def Check_Error_Port(error_port):
#     # for item in error_port:
#     #     print(f"{item};{item}")
#     # 方法一 利用difflib库检查有没有相似的port
#     for item in error_port:
#         matches = difflib.get_close_matches(item, Port_Name.keys(), n=1, cutoff=0.5)
#         if matches:
#             for matched_port in matches:
#                 # 直接一步到位
#                 # pass
#                 print(f"{item};{Port_Name[matched_port]}")
#         else:
#             print(item)
#
#     # # 方法二  去掉后面的（国家）
#     # for item in error_port:
#     #     item_Cut =item[:-5]
#     #     for port in Port_Name.keys():
#     #         if item_Cut in port:
#     #             print(f"{item};{Port_Name[port]}")
#
#     # # 方法三
#     # for item in error_port:
#     #     # 将 PortName 提取到第一个逗号前
#     #     Port_Name_Cut = []
#     #     for key in Port_Name.keys():
#     #         # 查找第一个逗号的位置
#     #         comma_index = key.find(',')
#     #         if comma_index != -1:
#     #             # 如果找到逗号，提取到第一个逗号之前的部分
#     #             Port_Name_Cut.append(key[:comma_index].strip())
#     #         else:
#     #             # 如果没有逗号，使用整个键
#     #             Port_Name_Cut.append(key.strip())
#     #
#     #     matches = difflib.get_close_matches(item, Port_Name_Cut, n=2, cutoff=0.5)
#     #     if matches:
#     #         for matched_port in matches:
#     #             # 直接一步到位
#     #             # pass
#     #             print(f"{item};{Port_Name[matched_port]}")
#     #     else:
#     #         print(item)
#
#     # # 方法四
#     # # 先预处理 Port_Name，生成截断后的键到原始值的映射
#     # truncated_to_full = {}
#     # for key in Port_Name.keys():
#     #     comma_index = key.find(',')
#     #     truncated_key = key[:comma_index].strip() if comma_index != -1 else key.strip()
#     #     # 处理可能的键冲突（多个原始键截断后相同）
#     #     if truncated_key not in truncated_to_full:
#     #         truncated_to_full[truncated_key] = Port_Name[key]
#     #
#     # # 提取所有截断后的键用于匹配
#     # Port_Name_Cut = list(truncated_to_full.keys())
#     #
#     # # 执行匹配
#     # for item in error_port:
#     #     item_Cut = item[:-5]
#     #     matches = difflib.get_close_matches(item_Cut, Port_Name_Cut, n=2, cutoff=0.5)
#     #     if matches:
#     #         for matched_port in matches:
#     #             # 使用预处理的映射获取原始值，避免 KeyError
#     #             print(f"{item};{truncated_to_full[matched_port]}")
#     #     else:
#     #         print(item)