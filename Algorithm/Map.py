from fontTools.misc.bezierTools import epsilon
from matplotlib.colors import LogNorm
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import networkx as nx
import  matplotlib.cm as cm
import pandas as pd
from ConstructNetwork import *



def draw_world_ports_communities_map(g, communities):
    '''
    世界港口社团检测结果图  不同社团用不同颜色标注
    :param g:
    :param communities:
    :return:
    '''
    Colors = ['#670096', '#d78306', '#f205c1', '#3ba91e', '#0068d7', '#e64a03', '#020202', '#CCCCCC']
    Port_Data = ConstructNetwork.Read_Port_Data()



    Port_Colors = {}

    for i, com in enumerate(communities):
        print(len(com))
        for port in com:
            Port_Colors[port] = Colors[i]

    coord = [(float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]), Port_Colors[node])
             for node in g.nodes() if "latitude" in Port_Data[node].keys() and "longitude" in Port_Data[node].keys()]

    world_map = Basemap()
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    x, y = world_map([data[0] for data in coord], [data[1] for data in coord])
    world_map.scatter(x, y, marker='o', color=[data[2] for data in coord], s=10, zorder=10)
    plt.show()
def draw_world_ports_degree_heat_map(g, centrality):
    '''
    港口重要性  可视化图
    :param g:
    :param centrality:
    :return:
    '''

    Port_Data = ConstructNetwork.Read_Port_Data()

    # 得到 tuple 组成的 list  tuple中的元素依次为 longitude、latitude、节点中心性
    coord = [(float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]), centrality[node])
             for node in g.nodes() if "latitude" in Port_Data[node].keys() and "longitude" in Port_Data[node].keys()]
    value = [data[2] for data in coord]

    # 计算散点大小 - 使用度值的线性映射，并添加最小尺寸
    min_size = 10
    max_size = 100
    min_value = min(value)
    max_value = max(value)

    # 线性映射函数：将度值映射到散点大小
    sizes = [min_size + (d - min_value) * (max_size - min_size) / (max_value - min_value) for d in value]
    # 计算与度值相关的透明度（0.3-1.0）
    alphas = [0.1 + (d - min_value) * (1.0 - 0.3) / (max_value - min_value) for d in value]

    world_map = Basemap()
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    x, y = world_map([data[0] for data in coord], [data[1] for data in coord])
    world_map.scatter(x, y, marker='o', color='b', s=sizes, zorder=10, alpha=alphas)
    plt.show()
def draw_world_ports_in_out_degree_heat_map(g, value:str) ->None:
    '''
    画出度和入度的热力图 就是进出口 次数
    :param g:
    :param value: 选择 出度还是入度
    :return:
    '''
    Port_Data = ConstructNetwork.Read_Port_Data()
    g = nx.read_graphml('../Data/FinalGraph/MultiDiGraph2019.graphml')


    if value == "in":
        # 得到 tuple 组成的 list  tuple中的元素依次为 longitude、latitude、节点中心性
        coord = [(float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]), g.in_degree(node), node)
                 for node in g.nodes() if
                 "latitude" in Port_Data[node].keys() and "longitude" in Port_Data[node].keys()]
    elif value == "out":
        # 得到 tuple 组成的 list  tuple中的元素依次为 longitude、latitude、节点中心性
        coord = [(float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]), g.out_degree(node), node)
                 for node in g.nodes() if
                 "latitude" in Port_Data[node].keys() and "longitude" in Port_Data[node].keys()]

    print(len(coord))
    value = [data[2] for data in coord]

    # 计算散点大小 - 使用度值的线性映射，并添加最小尺寸
    min_size = 10
    max_size = 100
    min_value = min(value)
    max_value = max(value)

    # 线性映射函数：将度值映射到散点大小
    sizes = [min_size + (d - min_value) * (max_size - min_size) / (max_value - min_value) for d in value]
    # 计算与度值相关的透明度（0.3-1.0）
    alphas = [0.1 + (d - min_value) * (1.0 - 0.3) / (max_value - min_value) for d in value]

    world_map = Basemap()
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    x, y = world_map([data[0] for data in coord], [data[1] for data in coord])
    world_map.scatter(x, y, marker='o', color='b', s=sizes, zorder=10, alpha=alphas)
    plt.title("in" if value == "in" else "out" + "_Degree")
    plt.show()

    for item in coord:
        print(item)

def draw_world_ports_map(g):
    Latitude = {}
    Longitude = {}

    # 逐行读取txt文档 记录经纬度 有一些Ports有问题就不读取了
    with open('../Data/Port/PortCoordinateInfo.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        try:
            # 去掉行尾的换行符号
            line = line.strip()
            # 切分
            parts = line.split(":")

            # 切分后第一段是港口 第二段是经纬度信息
            Port = parts[0].strip()
            coordinates = parts[1].strip()

            # 因为有一些是泛指 没有经纬度坐标
            if len(coordinates.split(",")) != 2:
                raise ValueError("没有具体经纬度坐标")

            latitude = coordinates.split(",")[0].strip()
            longitude = coordinates.split(",")[1].strip()

            Port = Port[2:]

            sign = latitude[-1]  # 记录latitude最后一个字符是 N还是S

            latitude = latitude[:-2]
            longitude = longitude[:-2]

            # 如果是 N 则为 ＋  是 S 则为 -
            latitude = float(latitude) if sign == 'N' else -float(latitude)
            longitude = float(longitude)

            Latitude[Port] = latitude
            Longitude[Port] = longitude
            # print(f"Port: {Port}")
            # print(f"Latitude: {latitude}")
            # print(f"Longitude: {longitude}")
        except ValueError as e:
            pass  # 异常后什么都不执行

    world_map = Basemap()
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    # 在经纬度字典查找 G.nodes()
    Latitude_nodes = [Latitude.get(port, None) for port in g.nodes()]
    Longitude_nodes = [Longitude.get(port, None) for port in g.nodes()]

    x, y = world_map(Longitude_nodes, Latitude_nodes)
    scatter = world_map.scatter(x, y, marker='o', s=3, zorder=10, color='darkblue')
    plt.show()
def draw_Panama_map(g):

    Latitude = {}
    Longitude = {}

    # 逐行读取txt文档 记录经纬度 有一些Ports有问题就不读取了
    with open('../Data/Port/PortCoordinateInfo.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        try:
            # 去掉行尾的换行符号
            line = line.strip()
            # 切分
            parts = line.split(":")

            # 切分后第一段是港口 第二段是经纬度信息
            Port = parts[0].strip()
            coordinates = parts[1].strip()

            # 因为有一些是泛指 没有经纬度坐标
            if len(coordinates.split(",")) != 2:
                raise ValueError("没有具体经纬度坐标")

            latitude = coordinates.split(",")[0].strip()
            longitude = coordinates.split(",")[1].strip()

            Port = Port[2:]

            sign = latitude[-1]  # 记录latitude最后一个字符是 N还是S

            latitude = latitude[:-2]
            longitude = longitude[:-2]

            # 如果是 N 则为 ＋  是 S 则为 -
            latitude = float(latitude) if sign == 'N' else -float(latitude)
            longitude = float(longitude)

            Latitude[Port] = latitude
            Longitude[Port] = longitude
            # print(f"Port: {Port}")
            # print(f"Latitude: {latitude}")
            # print(f"Longitude: {longitude}")
        except ValueError as e:
            pass  # 异常后什么都不执行
    # Panama_port = []
    # 这里先暂时这样直接给出  后续还是要仔细地洗一边数据
    Panama_port = ['Cristobal, Panama', 'Manzanillo, Panama', 'Balboa, Panama', 'Armuelles, Panama',
                   'Panama Canal Caribbean, Panama', 'Panama Canal  Pacific, Panama',
                   'Chiriqui Grande Terminal, Panama', 'Bahia De Las Minas, Panama', 'Aguadulce, Panama',
                   'Coco Solo, Panama']
    Panama_color = []
    Neighbor_port = []
    Neighbor_color = []

    world_map = Basemap(llcrnrlon=-170, llcrnrlat=0,
                        urcrnrlon=-55, urcrnrlat=55)

    for node in Panama_port:
        Panama_color.append('darkblue')
        for neighbor in g.neighbors(node):
            if neighbor != 'nan':
                world_map.drawgreatcircle(Longitude[node], Latitude[node], Longitude[neighbor], Latitude[neighbor],
                                          linewidth=0.5, color='blue')
                Neighbor_port.append(neighbor)
                Neighbor_color.append('red')

    # # world_map = Basemap()
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    # 画 Panama_port
    Latitude_nodes = [Latitude.get(port, None) for port in Panama_port]
    Longitude_nodes = [Longitude.get(port, None) for port in Panama_port]
    x, y = world_map(Longitude_nodes, Latitude_nodes)
    world_map.scatter(x, y, marker='o', s=5, zorder=10, color=Panama_color)

    # 画 Panama_neighbor_port
    Latitude_nodes = [Latitude.get(port, None) for port in Neighbor_port]
    Longitude_nodes = [Longitude.get(port, None) for port in Neighbor_port]
    x, y = world_map(Longitude_nodes, Latitude_nodes)
    world_map.scatter(x, y, marker='o', s=5, zorder=10, color=Neighbor_color)

    plt.show()
    # plt.savefig("../Figure/Panama.svg", dpi=300, format='svg')
def draw_except_US_port_strength_map():
    '''
    画出与美国港口交易的其他港口的强度值 map
    如果要画其他的图 记得改动一些参数
    :return:
    '''
    data_path = 'E:/panjivaUSImport2019.csv'
    # 原文件列名有点问题 不对应
    # df = pd.read_csv(data_path, usecols=['shpmtDestinationRegion', 'portOfUnladingRegion'])
    # df = pd.read_csv(data_path, usecols=['orderId','shpmtDestinationRegion', 'portOfUnladingRegion'])
    df = pd.read_csv(data_path)  # 2019年的数据用这个
    df.columns = ['portOfUnlading', 'portOfLading']

    # 删除包含null值的行
    df.dropna(inplace=True)

    Latitude = {}
    Longitude = {}

    # 逐行读取txt文档 记录经纬度 有一些Ports有问题就不读取了
    with open('../Data/Port/PortCoordinateInfo.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        try:
            # 去掉行尾的换行符号
            line = line.strip()
            # 切分
            parts = line.split(":")

            # 切分后第一段是港口 第二段是经纬度信息
            Port = parts[0].strip()
            coordinates = parts[1].strip()

            # 因为有一些是泛指 没有经纬度坐标
            if len(coordinates.split(",")) != 2:
                raise ValueError("没有具体经纬度坐标")

            latitude = coordinates.split(",")[0].strip()
            longitude = coordinates.split(",")[1].strip()

            Port = Port[2:]

            sign = latitude[-1]  # 记录latitude最后一个字符是 N还是S

            latitude = latitude[:-2]
            longitude = longitude[:-2]

            # 如果是 N 则为 ＋  是 S 则为 -
            latitude = float(latitude) if sign == 'N' else -float(latitude)
            longitude = float(longitude)

            Latitude[Port] = latitude
            Longitude[Port] = longitude
            # print(f"Port: {Port}")
            # print(f"Latitude: {latitude}")
            # print(f"Longitude: {longitude}")
        except ValueError as e:
            pass  # 异常后什么都不执行

    port_trade_counts = {}

    for row in df.itertuples():
        try:
            if row.portOfLading not in port_trade_counts:
                port_trade_counts[row.portOfLading] = 1
            else:
                port_trade_counts[row.portOfLading] += 1
        except KeyError as k:
            print(k)

    # 按值降序排序字典
    port_trade_counts_sorted = dict(sorted(port_trade_counts.items(), key=lambda item: item[1], reverse=True))
    print(port_trade_counts_sorted)
    base_size = 0.0001
    node_sizes = [base_size * strength for strength in port_trade_counts.values()]

    world_map = Basemap()
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    Latitude_nodes = [Latitude.get(port, None) for port in port_trade_counts]
    Longitude_nodes = [Longitude.get(port, None) for port in port_trade_counts]
    x, y = world_map(Longitude_nodes, Latitude_nodes)
    world_map.scatter(x, y, marker='o', s=node_sizes, zorder=10, color='#191993')

    plt.show()

# def draw_world_ports_communities_map(g, communities):
#     '''
#
#     :param g: 传入一个图
#     :param communities: 图的社团检测结果
#     :return:
#     '''
#     Latitude = {}
#     Longitude = {}
#
#     # 逐行读取txt文档 记录经纬度 有一些点有问题就不读取了
#     with open('../Data/Port/PortCoordinateInfo.txt', 'r', encoding='utf-8') as file:
#         lines = file.readlines()
#     for line in lines:
#         try:
#             # 去掉行尾的换行符号
#             line = line.strip()
#             # 切分
#             parts = line.split(":")
#
#             # 切分后第一段是港口 第二段是经纬度信息
#             Port = parts[0].strip()
#             coordinates = parts[1].strip()
#
#             # 因为有一些是泛指 没有经纬度坐标
#             if len(coordinates.split(",")) != 2:
#                 raise ValueError("没有具体经纬度坐标")
#
#             latitude = coordinates.split(",")[0].strip()
#             longitude = coordinates.split(",")[1].strip()
#
#             Port = Port[2:]
#
#             sign = latitude[-1]  # 记录latitude最后一个字符是 N还是S
#
#             latitude = latitude[:-2]
#             longitude = longitude[:-2]
#
#             # 如果是 N 则为 ＋  是 S 则为 -
#             latitude = float(latitude) if sign == 'N' else -float(latitude)
#             longitude = float(longitude)
#
#             Latitude[Port] = latitude
#             Longitude[Port] = longitude
#             # print(f"Port: {Port}")
#             # print(f"Latitude: {latitude}")
#             # print(f"Longitude: {longitude}")
#         except ValueError as e:
#             pass  # 异常后什么都不执行
#
#     Port_Colors = {}  # 存放每个港口的颜色
#     # Colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'black']
#     Colors = ['#670096', '#d78306', '#f205c1', '#3ba91e', '#0068d7', '#e64a03', '#020202', '#CCCCCC']
#     # Colors = ['white', 'white', 'white', 'white', 'white', 'white', 'white', '#CCCCCC']
#
#
#     for i, com in enumerate(communities):
#         print(len(com))
#         for port in com:
#
#             # 这里加一行判断 因为原始数据中有 1386个港口 但是处理后只有 1210个港口有经纬度坐标可以使用
#             # if port in Latitude.keys():
#             Port_Colors[port] = Colors[i]
#
#     # 按照画图时港口的顺序 生成一个 Draw_Color list
#     Draw_Color = []
#     for port in g.nodes():
#         Draw_Color.append(Port_Colors[port])
#
#     world_map = Basemap()
#     # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
#     world_map.drawmapboundary(fill_color='#D0CFD4')
#     world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
#     world_map.drawcoastlines()
#
#     # 在经纬度字典查找 G.nodes()
#     Latitude_nodes = [Latitude.get(port, None) for port in g.nodes()]
#     Longitude_nodes = [Longitude.get(port, None) for port in g.nodes()]
#
#     x, y = world_map(Longitude_nodes, Latitude_nodes)
#     world_map.scatter(x, y, marker='o', color=Draw_Color, s=10, zorder=10)
#     plt.show()
# def draw_world_ports_degree_heat_map(g, centrality):
#     '''
#     画中心性指标热力图  使用该函数时 可能需要调整base_size的大小
#     :param g: 传入一个图
#     :param centrality: 节点中心性指标dict  例如： 度中心性，BC，CC等； key为港口名称，value为中心性指标的值
#     :return:
#     '''
#     # 对数归一化 可能会有 0  所以用一个非常小的正数代替
#     centrality = {key:value if value != 0 else epsilon for key,value in centrality.items()}
#
#     # 对数归一化
#     norm = LogNorm(vmin=min(centrality.values()), vmax=max(centrality.values()))
#
#
#     # 创建颜色映射  已弃用
#     # cmap = plt.colormaps['viridis']
#     # norm = plt.Normalize(min(degree_dict.values()), max(degree_dict.values()))  # 归一化度值
#     # node_colors = [cmap(norm(degree)) for degree in degree_dict.values()]
#
#     # 节点大小映射
#     base_size = 0.1
#     node_sizes = [base_size * degree for degree in centrality.values()]
#
#     Latitude = {}
#     Longitude = {}
#
#     # 逐行读取txt文档 记录经纬度 有一些Ports有问题就不读取了
#     with open('../Data/Port/PortCoordinateInfo.txt', 'r', encoding='utf-8') as file:
#         lines = file.readlines()
#     for line in lines:
#         try:
#             # 去掉行尾的换行符号
#             line = line.strip()
#             # 切分
#             parts = line.split(":")
#
#             # 切分后第一段是港口 第二段是经纬度信息
#             Port = parts[0].strip()
#             coordinates = parts[1].strip()
#
#             # 因为有一些是泛指 没有经纬度坐标
#             if len(coordinates.split(",")) != 2:
#                 raise ValueError("没有具体经纬度坐标")
#
#             latitude = coordinates.split(",")[0].strip()
#             longitude = coordinates.split(",")[1].strip()
#
#             Port = Port[2:]
#
#             sign = latitude[-1]  # 记录latitude最后一个字符是 N还是S
#
#             latitude = latitude[:-2]
#             longitude = longitude[:-2]
#
#             # 如果是 N 则为 ＋  是 S 则为 -
#             latitude = float(latitude) if sign == 'N' else -float(latitude)
#             longitude = float(longitude)
#
#             Latitude[Port] = latitude
#             Longitude[Port] = longitude
#             # print(f"Port: {Port}")
#             # print(f"Latitude: {latitude}")
#             # print(f"Longitude: {longitude}")
#         except ValueError as e:
#             pass  # 异常后什么都不执行
#
#     world_map = Basemap()
#     # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
#     world_map.drawmapboundary(fill_color='#D0CFD4')
#     world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
#     world_map.drawcoastlines()
#
#     # 在经纬度字典查找 G.nodes()
#     Latitude_nodes = [Latitude.get(port, None) for port in g.nodes()]
#     Longitude_nodes = [Longitude.get(port, None) for port in g.nodes()]
#
#     x, y = world_map(Longitude_nodes, Latitude_nodes)
#     scatter = world_map.scatter(x, y, marker='o', s=node_sizes, zorder=10, cmap='Reds',
#                                 c=[norm(degree) for degree in centrality.values()])
#
#     print([norm(degree) for degree in centrality.values()])
#
#     # 添加颜色条   shrink是为了缩小颜色条保持与世界地图一致
#     colorbar = plt.colorbar(scatter, orientation='vertical', pad=0.05, shrink=0.7)
#     colorbar.set_label('Node Degree (log-scaled)')
#     plt.show()