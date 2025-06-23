import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx
import sys
sys.path.append('..')
import Algorithm.Basic_Topology
import difflib
from mpl_toolkits.basemap import Basemap

data_path = 'E:/GLSN/Source Data-Fig. 1d.csv'

df = pd.read_csv(data_path, header=None)

G = nx.Graph()
for index, row in df.iterrows():
    start, end = row[0], row[1]
    G.add_edge(start,end)
# 零模型
G_zero = Algorithm.Basic_Topology.zero_model(G)

Algorithm.Basic_Topology.draw_degree_cluster(G)
# 这两个度分布的画图函数 的 拟合部分都有问题   改！！！
# Algorithm.Basic_Topology.draw_degree_frequency_distribution(G)
# Algorithm.Basic_Topology.draw_degree_frequency_cumulative_distribution(G)
# Algorithm.Basic_Topology.draw_betweenness_centrality_cumulative_distribution(G,G1)
# Algorithm.Basic_Topology.draw_closeness_centrality_cumulative_distribution(G,G1)
# Algorithm.Basic_Topology.draw_degree_frequency_distribution(G1)

# # 一个由 set 组成的 list
# Communities = nx.community.louvain_communities(G,seed=123)
# print("Communities:", nx.community.modularity(G, Communities))
# # Q = nx.community.modularity(G, Communities)
# # # for i in Communities:
# # #     print(len(i),i)
# # # print("Q:",Q)
#
#
#
# Latitude = {}
# Longitude = {}
#
# # 逐行读取txt文档 记录经纬度 有一些点有问题就不读取了
# with open('../Data/PortCoordinateInfo.txt', 'r', encoding='utf-8') as file:
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
#         sign = latitude[-1]     # 记录latitude最后一个字符是 N还是S
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
#         pass
#
# Latitude_list = []
# Longitude_list = []
#
# Port = []
#
# # 模糊匹配
# for port in G.nodes():
#     matches = difflib.get_close_matches(port, Latitude.keys(), n=1, cutoff=0.5)
#     if matches:
#         matched_port = matches[0]
#         Port.append(port)
#         Latitude_list.append(Latitude[matched_port])
#         Longitude_list.append(Longitude[matched_port])
#
# # print(Port)
# print(len(Port))
# # print(Latitude_list)
# # print(Longitude_list)
#
# Port_Colors = {}    # 存放每个港口的颜色
# Colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'black', 'gray']
# # 为每个港口 根据社团划分 添加颜色
# for i,com in enumerate(Communities):
#     for port in com:
#         # 这里加一行判断 因为原始数据中有 1386个港口 但是处理后只有 1210个港口有经纬度坐标可以使用
#         # if port in Latitude.keys():
#         Port_Colors[port] = Colors[i]
# # print("Port_Colors",Port_Colors)
# print(len(Port_Colors))
#
#
# # 按照画图时港口的顺序 生成一个 Draw_Color list
# Draw_Color = []
# for port in Port:
#     Draw_Color.append(Port_Colors[port])
#
#
# world_map = Basemap()
# # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
# world_map.drawmapboundary(fill_color='#D0CFD4')
# world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
# world_map.drawcoastlines()
#
#
# x,y = world_map(Longitude_list,Latitude_list)
# world_map.scatter(x, y, marker='o', color=Draw_Color, s=15, zorder=10)
# # plt.savefig('../Figure/GLSN_Community.svg', dpi=300, format='svg')
# plt.show()