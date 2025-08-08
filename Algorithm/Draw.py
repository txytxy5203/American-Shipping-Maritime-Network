from matplotlib import pyplot as plt
import pandas as pd


def draw_The_proportion_of_the_number_of_transactions_on_each_continent():
    '''
    写得比较乱 后续在用的时候注意一下
    :return:
    '''
    # 读取port位置区域
    port_Region = {}
    with open('../Data/2019/Port/port_Region.csv', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        # 去掉行尾的换行符号
        line = line.strip()
        # 切分
        parts = line.split(";")

        # 切分后第一段是港口 第二段是区域信息
        Port = parts[0].strip()
        Region = parts[1].strip()
        port_Region[Port] = Region
    del port_Region['portOfLading']


    # G = nx.read_weighted_edgelist("graph_weighted.edgelist",nodetype=str, delimiter=':')

    data_path = 'E:/panjivaUSImport2019.csv'
    # 原文件列名有点问题 不对应
    # df = pd.read_csv(data_path, usecols=['shpmtDestinationRegion', 'portOfUnladingRegion'])
    # df = pd.read_csv(data_path, usecols=['orderId','shpmtDestinationRegion', 'portOfUnladingRegion'])     #
    df = pd.read_csv(data_path)     # 2019年的数据用这个
    df.columns = ['portOfUnlading', 'portOfLading']


    # 删除包含null值的行
    df.dropna(inplace=True)
    # # 删除完全相同的行 注意这里 别用错了
    # df = df.drop_duplicates()

    region_trade_counts = {}

    for row in df.itertuples():
        try:
            if port_Region[row.portOfLading] not in region_trade_counts:
                region_trade_counts[port_Region[row.portOfLading]] = 1
            else:
                region_trade_counts[port_Region[row.portOfLading]] += 1
        except KeyError as k:
            # print(k)
            pass

    print(sum(region_trade_counts.values()))
    # print(region_trade_counts)

    # 计算占比
    region_trade_portion = {key : value / sum(region_trade_counts.values())
                            for key, value in region_trade_counts.items()}
    # print(region_trade_portion)


    # Central America,Caribbean ,North America合并
    # Southern Europe,Western Europe, Northern Europe ,Eastern Europe合并
    # Southern Africa,Northern Africa,Middle Africa,Western Africa,Eastern Africa
    # Australasia,Polynesia,Melanesia,Micronesia

    region_trade_portion['Central North America'] = (region_trade_portion['Central America'] + region_trade_portion['Caribbean']
                                       + region_trade_portion['North America'])
    region_trade_portion['Europe'] = (region_trade_portion['Southern Europe'] + region_trade_portion['Western Europe']
                                       + region_trade_portion['Northern Europe'] + region_trade_portion['Eastern Europe'])
    region_trade_portion['Africa'] = (region_trade_portion['Southern Africa'] + region_trade_portion['Northern Africa']
                                       + region_trade_portion['Middle Africa'] + region_trade_portion['Western Africa']
                                      + region_trade_portion['Eastern Africa'])
    region_trade_portion['Oceania'] = (region_trade_portion['Australasia'] + region_trade_portion['Polynesia']
                                       + region_trade_portion['Melanesia'] + region_trade_portion['Micronesia'])
    del region_trade_portion['Central America']
    del region_trade_portion['Caribbean']
    del region_trade_portion['North America']
    del region_trade_portion['Southern Europe']
    del region_trade_portion['Western Europe']
    del region_trade_portion['Northern Europe']
    del region_trade_portion['Eastern Europe']
    del region_trade_portion['Southern Africa']
    del region_trade_portion['Northern Africa']
    del region_trade_portion['Middle Africa']
    del region_trade_portion['Western Africa']
    del region_trade_portion['Eastern Africa']
    del region_trade_portion['Australasia']
    del region_trade_portion['Polynesia']
    del region_trade_portion['Melanesia']
    del region_trade_portion['Micronesia']


    region_trade_portion = dict(sorted(region_trade_portion.items(), key=lambda item: item[1], reverse=True))
    print(region_trade_portion)


    # 提取标签和值
    labels = list(region_trade_portion.keys())
    values = list(region_trade_portion.values())
    # 计算平均值
    average_value = sum(values) / len(values)


    # 创建柱状图
    plt.figure(figsize=(12, 10))
    plt.bar(labels, values, color='skyblue', label='Proportion')
    # 添加平均值线
    plt.axhline(y=average_value, color='red', linestyle='--', linewidth=2, label=f'Average ({average_value:.2f})')
    plt.title('The proportion of the number of transactions on each continent ')
    plt.xlabel('Continent')
    plt.ylabel('Proportion')
    plt.xticks(rotation=30, ha='center')
    # 调整布局以确保标签完全显示
    plt.tight_layout()
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 显示图表
    plt.show()