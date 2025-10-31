import re
import os
import json
import sys
sys.path.append('../Algorithm')
import pandas as pd
import networkx as nx
import unicodedata
from MyData.Read import Read


# Port_Name = Algorithm.Read.read_port_name_info()
# Remove_Port = Algorithm.Read.read_remove_port_info()


class ConstructNetwork:

    @classmethod
    def Read_Port_Data(cls):
        '''
        类方法 直接 cls. 出来用
        :return: Port_Data 标准表
        '''
        data_path = "../Data/2019/Port/Port_Info_Json.json"
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
    def change_hk_tw_am_to_china(cls):
        """
        把香港 台湾 澳门 的国家属性改成China
        :return:
        """
        years = range(2017, 2022)  # 一年一个单位
        seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
        for year in years:
            for season in seasons:
                file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
                if not os.path.exists(file_path):
                    print(f'⚠️ 文件不存在: {file_path}')
                    continue
                G = nx.read_graphml(file_path)
                for node, attr in G.nodes(data=True):
                    country = attr.get('Country')
                    if country in ['Hong Kong', 'Taiwan', 'Macau']:
                        attr['Country'] = 'China'
                        print(f"change the {node}")
                nx.write_graphml(G, file_path)
    @classmethod
    def Save_MultiDiGraph_To_Digraph(cls):
        years = range(2017, 2018)

        for year in years:
            file_path = f'../Data/{year}/US/US{year}.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            Multi_G = nx.read_graphml(file_path)

            # 假设 G 是 MultiDiGraph，边有 total_TEU 属性
            D = nx.DiGraph()  # 目标简单有向图
            D.add_nodes_from(Multi_G.nodes(data=True))  # 1. 先拷节点属性

            # 2. 把平行边的 TEU 累加
            for u, v, data in Multi_G.edges(data=True):
                teu = data.get('volumeTEU', 0)
                if D.has_edge(u, v):
                    D[u][v]['volumeTEU'] += teu
                else:
                    D.add_edge(u, v, volumeTEU=teu)

            # 使用 GraphML 保存图
            nx.write_graphml(D, f'../Data/{year}/US/US{year}_Digraph.graphml')

    @classmethod
    def Save_Network_USImport_Season_Winter(cls, year: int) -> None:

        last = [12]
        next = [1,2]


        port_data = cls.Read_Port_Data()
        HSCode = Read.read_USImpHSCode()

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

            US_data_path = 'D:/PortData/' + str(y) + '/USImport' + str(y) + '.csv'
            print(US_data_path)

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
            DataFrame['portOfLadingCountry'] = DataFrame['portOfLadingCountry'].astype(str)
            DataFrame['arrivalDate'] = DataFrame['arrivalDate'].astype(str)

            print("DataFrame加载完毕")

            print(f"原始DataFrame大小:{len(DataFrame)}")
            Origin_Len = len(DataFrame)
            # # 剔除重复数据
            # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
            DataFrame = DataFrame.drop_duplicates(subset=['billOfLadingNumber'], keep='first')
            print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

            # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
            null_counts = DataFrame.isnull().sum()
            print("每个字段的null值情况：")
            print(null_counts / len(DataFrame))

            # 1 使用均值填充 TEU
            DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
            # 2 删除 某某 列为空的行
            DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])
            DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引

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
                month = int(row['arrivalDate'][5:7])  # 这里就直接字符串切片了
                if (y == year and month not in last) or (y == year + 1 and month not in next):
                    continue

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
                portOfLading_country = row['portOfLadingCountry'].lower()

                for port in port_data:
                    port_name = port_data[port]["english_name"].lower()
                    port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                    port_country = port_data[port]["country_english"].lower()

                    if port_name in portOfLading and portOfLading_country == port_country:
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
        nx.write_graphml(G, '../Data/' + str(year) + '/US/Season/Winter/USImport' + str(year) + '_Winter' + '.graphml')

    @classmethod
    def Save_Network_USExport_Season_Winter(cls, year: int) -> None:

        last = [12]
        next = [1, 2]

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
    @classmethod
    def Save_Network_USImport_Season(cls, year:int, season:str) -> None:

        season_month_dict = {
            'Spring':[3,4,5],
            'Summer':[6,7,8],
            'Autumn':[9,10,11]
        }
        US_data_path = 'D:/PortData/' + str(year) + '/USImport' + str(year) + '.csv'
        port_data = cls.Read_Port_Data()
        HSCode = Read.read_USImpHSCode()

        # 过滤数据，只保留美国的港口
        us_data = {
            port_code: info
            for port_code, info in port_data.items()
            if "United States" in info.get("country_english", "")
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
        DataFrame['portOfLadingCountry'] = DataFrame['portOfLadingCountry'].astype(str)
        DataFrame['arrivalDate'] = DataFrame['arrivalDate'].astype(str)

        print("DataFrame加载完毕")

        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)
        # # 剔除重复数据
        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['billOfLadingNumber'], keep='first')
        print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        print(null_counts / len(DataFrame))

        # 1 使用均值填充 TEU
        DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
        # 2 删除 某某 列为空的行
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])
        DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引

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

            # 过滤季节
            month = int(row['arrivalDate'][5:7])        # 这里就直接字符串切片了
            if month not in season_month_dict[season]:
                continue

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
            portOfLading_country = row['portOfLadingCountry'].lower()
            # print("----------")
            # print(portOfLading_country)

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                port_country = port_data[port]["country_english"].lower()
                # print(port_country)

                if port_name in portOfLading and portOfLading_country == port_country:
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


            # 创建一个字典来存储边的属性
            edge_attrs = {
                'volumeTEU': row['volumeTEU'],
                'HSCode': HSCode[row['panjivaRecordId']],
                'month': month
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/' + str(year) + '/US' + '/Season' + '/' + season + '/USImport' + str(year) + '_' + season + '.graphml')

        print(USIndex / len(DataFrame))
        print(OriIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)

    @classmethod
    def Save_Network_USExport_Season(cls, year: int, season:str) -> None:

        season_month_dict = {
            'Spring': [3, 4, 5],
            'Summer': [6, 7, 8],
            'Autumn': [9, 10, 11]
        }
        US_data_path = 'D:/PortData/' + str(year) + '/USExport' + str(year) + '.csv'
        port_data = cls.Read_Port_Data()
        HSCode = Read.read_USExpHSCode()

        # 过滤数据，只保留美国的港口
        us_data = {
            port_code: info
            for port_code, info in port_data.items()
            if "United States" in info.get("country_english", "")
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

        G = nx.MultiDiGraph()

        for index, row in DataFrame.iterrows():
            timer += 1
            if timer / len(DataFrame) > 0.01:
                print('构建网络当前进度：{:.2%}'.format(index / len(DataFrame)))
                timer = 0

            # 过滤季节
            month = int(row['shpmtDate'][5:7])  # 这里就直接字符串切片了
            if month not in season_month_dict[season]:
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
                'month': month
            }
            # 给 edge 和 node 添加属性
            G.add_edge(Lading_Code, UnLading_Code, **edge_attrs)
            G.nodes[Lading_Code]['Country'] = port_data[Lading_Code]["country_english"]
            G.nodes[UnLading_Code]['Country'] = port_data[UnLading_Code]["country_english"]

        # 使用 GraphML 保存图
        nx.write_graphml(G, '../Data/' + str(year) + '/US' + '/Season' + '/' + season + '/USExport' + str(
            year) + '_' + season + '.graphml')

        print(USIndex / len(DataFrame))
        print(OriIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)

    @classmethod
    def Save_Network_USImport(cls, year:int) -> None:
        '''

        :param year: 直接填写年份   同时PortData中的数据也要按年份分类好
        '''
        US_data_path = 'D:/PortData/' + str(year) + '/USImport' + str(year) + '.csv'
        port_data = cls.Read_Port_Data()
        HSCode = Read.read_USImpHSCode()


        # 过滤数据，只保留美国的港口
        us_data = {
            port_code: info
            for port_code, info in port_data.items()
            if "United States" in info.get("country_english", "")
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
        DataFrame['portOfLadingCountry'] = DataFrame['portOfLadingCountry'].astype(str)

        print("DataFrame加载完毕")

        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)
        # # 剔除重复数据
        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['billOfLadingNumber'], keep='first')
        print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        print(null_counts / len(DataFrame))

        # 1 使用均值填充 TEU
        DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
        # 2 删除 某某 列为空的行
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])
        DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引

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
            portOfLading_country = row['portOfLadingCountry'].lower()
            # print("----------")
            # print(portOfLading_country)

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                port_country = port_data[port]["country_english"].lower()
                # print(port_country)

                if port_name in portOfLading and portOfLading_country == port_country:
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
        nx.write_graphml(G, '../Data/' + str(year) + '/US' + '/USImport' + str(year) + '.graphml')

        print(USIndex / len(DataFrame))
        print(OriIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)

    @classmethod
    def Save_Network_USExport(cls, year:int) -> None:
        '''

        :param year: 直接填写年份   同时PortData中的数据也要按年份分类好
        '''
        US_data_path = 'D:/PortData/' + str(year) + '/USExport' + str(year) + '.csv'
        port_data = cls.Read_Port_Data()
        HSCode = Read.read_USExpHSCode()

        # 过滤数据，只保留美国的港口
        us_data = {
            port_code: info
            for port_code, info in port_data.items()
            if "United States" in info.get("country_english", "")
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
        DataFrame['portOfUnladingCountry'] = DataFrame['portOfUnladingCountry'].astype(str)

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
        nx.write_graphml(G, '../Data/' + str(year) + '/US' + '/USExport' + str(year) + '.graphml')

        print(USIndex / len(DataFrame))
        print(OriIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)

    @classmethod
    def Save_Network_BRImport2019(cls):

        BR_data_path = 'D:/PortData/BRImport2019.csv'
        port_data = cls.Read_Port_Data()


        # nrows = 1000000
        DataFrame = pd.read_csv(BR_data_path, header=None)
        DataFrame.columns =  ['panjivaRecordId', 'billOfLadingNumber','shpmtDate', 'conCountry', 'shpCountry', 'shpmtOrigin','shpmtOriginCountry','shpmtDestination',
                            'shpmtDestinationCountry','portOfOriginCountry','portOfUnlading','portOfUnladingCountry','portOfLading', 'vesselName',
                           'hsCode','volumeTEU', 'grossWeightKg', 'valueOfGoodsUSD']
        # 剔除重复数据
        DataFrame = DataFrame.drop_duplicates()
        # 将 相关列转换为字符串类型
        DataFrame['portOfUnlading'] = DataFrame['portOfUnlading'].astype(str)
        DataFrame['portOfLading'] = DataFrame['portOfLading'].astype(str)
        DataFrame['panjivaRecordId'] = DataFrame['panjivaRecordId'].astype(str)
        DataFrame['portOfUnladingCountry'] = DataFrame['portOfUnladingCountry'].astype(str)
        DataFrame['portOfOriginCountry'] = DataFrame['portOfOriginCountry'].astype(str)


        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")

        Origin_Len = len(DataFrame)
        # # 剔除重复数据
        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['billOfLadingNumber'], keep='first')
        print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        print(null_counts / len(DataFrame))

        # 1 使用均值填充 TEU
        DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
        # 2 删除 某某 列为空的行
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])
        DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引

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
            portOfUnlading_country = row['portOfUnladingCountry'].lower()


            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)
            portOfLading_country = row['portOfOriginCountry'].lower()


            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                port_country = port_data[port]["country_english"].lower()

                if  (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False and port_country == portOfUnlading_country:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if  (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False and port_country == portOfLading_country:
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
        nx.write_graphml(G, '../Data/2019/BR2019/BRImport2019.graphml')

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
        DataFrame['portOfUnladingCountry'] = DataFrame['portOfUnladingCountry'].astype(str)
        DataFrame['portOfLadingCountry'] = DataFrame['portOfLadingCountry'].astype(str)


        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")

        Origin_Len = len(DataFrame)
        # # 剔除重复数据
        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['billOfLadingNumber'], keep='first')
        print(f"剔除重复数据后DataFrame大小:{len(DataFrame)}")

        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        print(null_counts / len(DataFrame))

        # 1 使用均值填充 TEU
        DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
        # 2 删除 某某 列为空的行
        DataFrame = DataFrame.dropna(subset=['portOfUnlading', 'portOfLading'])
        DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引
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
            portOfUnlading_country = row['portOfUnladingCountry'].lower()


            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)
            portOfLading_country = row['portOfLadingCountry'].lower()

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                port_country = port_data[port]["country_english"].lower()

                # 交叉匹配 无敌！！
                if (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False and port_country == portOfUnlading_country:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False and port_country == portOfLading_country:
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
        nx.write_graphml(G, '../Data/2019/BR2019/BRExport2019.graphml')

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
        DataFrame['portOfUnladingCountry'] = DataFrame['portOfUnladingCountry'].astype(str)
        DataFrame['portOfLadingCountry'] = DataFrame['portOfLadingCountry'].astype(str)


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
            portOfUnlading_country = row['portOfUnladingCountry'].lower()

            portOfLading = row['portOfLading'].lower()
            # 先去掉括号里的内容  例如：Manaus (BR) --> Manaus
            portOfLading = re.sub(r'\([^)]*\)', '', portOfLading).strip()
            # 处理特殊字符 例如：Paranaguá (BR)
            portOfLading = cls.To_English_Spelling(portOfLading)
            # 再去掉空格
            portOfLading = re.sub(r'[^a-zA-Z]', '', portOfLading)
            portOfLading_country = row['portOfLadingCountry'].lower()

            for port in port_data:
                port_name = port_data[port]["english_name"].lower()
                port_name = re.sub(r'[^a-zA-Z]', '', port_name)
                port_country = port_data[port]["country_english"].lower()

                if (portOfUnlading in port_name or port_name in portOfUnlading) and UnLading_Match is False and port_country == portOfUnlading_country:
                    UnLadingIndex += 1
                    UnLading_Match = True
                    UnLading_Code = port

                if (portOfLading in port_name or port_name in portOfLading) and Lading_Match is False and port_country == portOfLading_country:
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
        nx.write_graphml(G, '../Data/2019/CL2019/CLImport2019.graphml')

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
        DataFrame.columns = ['panjivaRecordId', 'exportDeclarationNumber','shpmtDate', 'conCountry','shpCountry', 'shpmtOrigin',
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
        DataFrame['shpmtDestinationCountry'] = DataFrame['shpmtDestinationCountry'].astype(str)
        DataFrame['portOfLadingCountry'] = DataFrame['portOfLadingCountry'].astype(str)

        # # 剔除重复数据
        # 删除 'exportDeclarationNumber' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['exportDeclarationNumber'], keep='first')


        # 检查 volumeTEU、weightKg、valueOfGoodsUSD 字段中的空值数量
        null_counts = DataFrame.isnull().sum()
        print("每个字段的null值情况：")
        print(null_counts / len(DataFrame))

        # 1 使用均值填充 TEU
        DataFrame.fillna({'volumeTEU': DataFrame['volumeTEU'].mean()}, inplace=True)
        DataFrame = DataFrame.reset_index(drop=True)  # drop=True 丢弃原索引

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
        nx.write_graphml(G, '../Data/2019/CO2019/COExport2019.graphml')

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
        DataFrame.columns = ['panjivaRecordId' ,'billOfEntryNumber' ,'departureDate' ,'conCity','conCountry','shpCity','shpCountry',
                             'portOfUnlading','portOfUnladingCountry','portOfUnladingUNLOCODE',
		                     'portOfLading', 'portOfLadingCountry', 'portOfLadingUNLOCODE',
                             'transportMethod', 'hsCode', 'volumeTEU']

        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)

        # 删除 'billOfEntryNumber' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['billOfEntryNumber'], keep='first')
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
        DataFrame['portOfLadingCountry'] = DataFrame['portOfLadingCountry'].astype(str)
        DataFrame['portOfUnladingCountry'] = DataFrame['portOfUnladingCountry'].astype(str)
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
        nx.write_graphml(G, '../Data/2019/IN2019/INImport2019.graphml')

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
        DataFrame.columns = ['panjivaRecordId', 'billOfLadingNumber' , 'departureDate', 'conCity', 'conCountry', 'shpCity', 'shpCountry',
                             'portOfUnlading', 'portOfUnladingCountry', 'portOfUnladingUNLOCODE',
                             'portOfLading', 'portOfLadingCountry', 'portOfLadingUNLOCODE',
                             'transportMethod', 'hsCode', 'volumeTEU']

        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)

        # 删除 'panjivaRecordId' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['billOfLadingNumber'], keep='first')
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
        nx.write_graphml(G, '../Data/2019/IN2019/INExport2019.graphml')

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
        DataFrame.columns = ['panjivaRecordId', 'billOfLadingNumber','shpmtDate','conCity','conCountry',
		                     'portOfUnlading','portOfUnladingCountry','portOfUnladingUNLOCODE',
		                     'portOfLading','portOfLadingCountry','portOfLadingUNLOCODE',
                             'transportMethod','hsCode','volumeTEU']

        print("DataFrame加载完毕")
        print(f"原始DataFrame大小:{len(DataFrame)}")
        Origin_Len = len(DataFrame)

        # 删除 'billOfLadingNumber' 列重复的行，只保留第一次出现的行
        DataFrame = DataFrame.drop_duplicates(subset=['billOfLadingNumber'], keep='first')
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
        DataFrame['portOfUnladingCountry'] = DataFrame['portOfUnladingCountry'].astype(str)
        DataFrame['portOfLadingCountry'] = DataFrame['portOfLadingCountry'].astype(str)
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
        nx.write_graphml(G, '../Data/2019/VE2019/VEImport2019.graphml')

        print(UnLadingIndex / len(DataFrame))
        print(LadingIndex / len(DataFrame))
        print("数据的最终利用率", G.number_of_edges() / Origin_Len)
        for item in error_port:
            print(item)