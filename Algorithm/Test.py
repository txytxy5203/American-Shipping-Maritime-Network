import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx
import sys
import difflib
import csv
import re

sys.path.append('..')
import Algorithm.Basic_Topology
import Algorithm.Draw
import Algorithm.Read
import Algorithm.Map
import Algorithm.ConstructNetwork
from mpl_toolkits.basemap import Basemap


def Read_and_save_port_region():
    data_path = 'E:/panjivaUSImport.csv'

    df = pd.read_csv(data_path, usecols=['portOfUnladingRegion', 'portOfLading'])
    df.columns = ['portOfLading', 'portOfLadingRegion']
    # print(df.head())

    # 删除包含null值的行
    df.dropna(inplace=True)
    # 删除完全重复的行
    df = df.drop_duplicates()
    # 保存成csv文件
    df.to_csv('../Data/port_Region.csv', index=False, sep=';', encoding='utf-8')
def draw_world_region_map(g):
    world_map = Basemap()
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    for node in g.nodes():
        try:
            # if port_Region[node] == 'South America':
            for neighbor in g.neighbors(node):
                if node in Longitude and neighbor in Longitude and node in Latitude and neighbor in Latitude:
                    x1, y1 = world_map(Longitude[node], Latitude[node])
                    x2, y2 = world_map(Longitude[neighbor], Latitude[neighbor])
                    # world_map.drawgreatcircle(x1, y1, x2, y2, linewidth=0.5, color='blue')
                    world_map.plot([x1, x2], [y1, y2], linewidth=0.1, color='b')
        except KeyError as k:
            pass
    plt.show()

# # 读取port经纬度坐标
# Latitude = {}
# Longitude = {}
# # 逐行读取txt文档 记录经纬度 有一些Ports有问题就不读取了
# with open('../Data/Port/PortCoordinateInfo.txt', 'r', encoding='utf-8') as file:
#     lines = file.readlines()
# for line in lines:
#     try:
#         # 去掉行尾的换行符号
#         line = line.strip()
#         # 切分
#         parts = line.split(":")
#
#         # 切分后第一段是港口 第二段是经纬度信息
#         Port = parts[0].strip()
#         coordinates = parts[1].strip()
#
#         # 因为有一些是泛指 没有经纬度坐标
#         if len(coordinates.split(",")) != 2:
#             raise ValueError("没有具体经纬度坐标")
#
#         latitude = coordinates.split(",")[0].strip()
#         longitude = coordinates.split(",")[1].strip()
#
#         Port = Port[2:]
#
#         sign = latitude[-1]  # 记录latitude最后一个字符是 N还是S
#
#         latitude = latitude[:-2]
#         longitude = longitude[:-2]
#
#         # 如果是 N 则为 ＋  是 S 则为 -
#         latitude = float(latitude) if sign == 'N' else -float(latitude)
#         longitude = float(longitude)
#
#         Latitude[Port] = latitude
#         Longitude[Port] = longitude
#         # print(f"Port: {Port}")
#         # print(f"Latitude: {latitude}")
#         # print(f"Longitude: {longitude}")
#     except ValueError as e:
#         print(Port)

# Algorithm.ConstructNetwork.Save_Network_BRExport2019()
# G_BR = nx.read_graphml('../Data/BR2019/BRImport2019.graphml')
# # G_US = nx.read_graphml('../Data/US/USImport2019.graphml')
# # G_US.add_edges_from(G_BR)
# G_Graph = nx.Graph(G_BR)
# Algorithm.Basic_Topology.basic_topology_metrics(G_Graph)

