import csv
import powerlaw
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from Algorithm.ConstructNetwork import ConstructNetwork
# from Algorithm.Basic_Topology import *
# from Algorithm.Map import *

def generate_graph():
    # # # 读取 GraphML 文件
    BR_Im = nx.read_graphml('../Data/BR2019/BRImport2019.graphml')
    BR_Ex = nx.read_graphml('../Data/BR2019/BRExport2019.graphml')
    # BR_Im_Graph = nx.Graph(BR_Im)
    # BR_Ex_Graph = nx.Graph(BR_Ex)
    G_BR = nx.compose(BR_Im, BR_Ex)
    print("BR is ready")

    CL_Im = nx.read_graphml('../Data/CL2019/CLImport2019.graphml')
    # G_CL = nx.Graph(CL_Im)
    print("CL is ready")


    CO_Ex = nx.read_graphml('../Data/CO2019/COExport2019.graphml')
    # G_CO = nx.Graph(CO_Ex)
    print("CO is ready")

    IN_Im = nx.read_graphml('../Data/IN2019/INImport2019.graphml')
    IN_Ex = nx.read_graphml('../Data/IN2019/INExport2019.graphml')
    # IN_Im_Graph = nx.Graph(IN_Im)
    # IN_Ex_Graph = nx.Graph(IN_Ex)
    G_IN = nx.compose(IN_Im, IN_Ex)
    print("IN is ready")

    US_Im = nx.read_graphml('../Data/US2019/USImport2019.graphml')
    US_Ex = nx.read_graphml('../Data/US2019/USExport2019.graphml')
    # US_Im_Graph = nx.Graph(US_Im)
    # US_Ex_Graph = nx.Graph(US_Ex)
    G_US = nx.compose(US_Im, US_Ex)
    print("US is ready")

    VE_Im = nx.read_graphml('../Data/VE2019/VEImport2019.graphml')
    # G_VE = nx.Graph(VE_Im)
    print("VE is ready")

    # 合并两个图
    G_combined = nx.compose(G_BR, CL_Im)
    G_combined = nx.compose(G_combined, CO_Ex)
    G_combined = nx.compose(G_combined, G_IN)
    G_combined = nx.compose(G_combined, G_US)
    G_combined = nx.compose(G_combined, VE_Im)

    print("N:",G_combined.number_of_nodes())
    print("M:",G_combined.number_of_edges())

    # 使用 GraphML 保存图
    nx.write_graphml(G_combined, '../Data/FinalGraph/MultiDiGraph2019.graphml')


# print(G_2019.number_of_edges())

# G_null = G_2019.copy()

# # 进行n_swaps次边交换
# nx.double_edge_swap(G_null, nswap=100000, max_tries=1000000)
# # 确保没有自环
# G_null.remove_edges_from(nx.selfloop_edges(G_null))
# print(G_null.number_of_edges())


# community = nx.community.louvain_communities(G_2019)
# for com in community:
#     print(len(com))

# Port_Data = ConstructNetwork.Read_Port_Data()
# # error = []
# #
# # for data in Port_Data.values():
# #     try:
# #         print(data["latitude"])
# #     except:
# #         error.append(data["english_name"])
# # print(error)
#
# world_map = Basemap()
# # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
# world_map.drawmapboundary(fill_color='#D0CFD4')
# world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
# world_map.drawcoastlines()
# # 读经纬度时一定记得转成 float
# coord_all_port = [(float(port["longitude"]),float(port["latitude"])) for port in Port_Data.values() if "latitude" in port and "longitude" in port]
# x, y = world_map([data[0] for data in coord_all_port], [data[1] for data in coord_all_port])
# world_map.scatter(x, y, marker='o', color='g', s=10, zorder=10)
#
#
# coord = [(float(Port_Data[node]["longitude"]),float(Port_Data[node]["latitude"]))
#          for node in G_2019.nodes() if "latitude" in Port_Data[node].keys() and "longitude" in Port_Data[node].keys()]
# print(coord)
# print(len(coord))
#
#
# a, b = world_map([data[0] for data in coord], [data[1] for data in coord])
# world_map.scatter(a, b, marker='o', color='b', s=10, zorder=10)
# plt.show()
# MultiDiG_2019 = nx.read_graphml('../Data/FinalGraph/MultiDiGraph2019.graphml')

def draw_degree_bc_cc(g, value:str) -> None:
    '''
    查看三种中心性指标之间的关系
    :param g: 传入要计算的 Graph
    :param value: 有 Degree——BC，Degree——CC，BC--CC三种模式
    :return:
    '''
    bc = nx.betweenness_centrality(g)
    degree = nx.degree_centrality(g)
    cc = nx.closeness_centrality(g)
    degree_bc_cc = [(degree[node], bc[node], cc[node], node) for node in g.nodes()]

    if value == "DB":
        plt.scatter([data[0] for data in degree_bc_cc], [data[1] for data in degree_bc_cc], marker='s', c='red')
        plt.xlabel("degree")
        plt.ylabel("BC")
        plt.title("degree--BC")
        plt.savefig('../Figure/节点度值与BC的关系.svg')
        plt.show()
    elif value == "DC":
        plt.scatter([data[0] for data in degree_bc_cc], [data[2] for data in degree_bc_cc], marker='s', c='red')
        plt.xlabel("degree")
        plt.ylabel("CC")
        plt.title("degree--CC")
        plt.savefig('../Figure/节点度值与CC的关系.svg')
        plt.show()
    elif value == "BC":
        plt.scatter([data[1] for data in degree_bc_cc], [data[2] for data in degree_bc_cc], marker='s', c='red')
        plt.xlabel("BC")
        plt.ylabel("CC")
        plt.title("BC--CC")
        plt.savefig('../Figure/节点BC与CC的关系.svg')
        plt.show()




# # 读取GraphML文件并只保留边的HScode属性
MultiDiGraph_2019 = nx.read_graphml('../Data/FinalGraph/MultiDiGraph2019.graphml')

# MultiDiGraph_2019 = nx.read_graphml('../Data/FinalGraph/Graph2019.graphml')


degree_frequency_numbers = nx.degree_histogram(MultiDiGraph_2019)  # 度的频数

N = MultiDiGraph_2019.number_of_nodes()
# [0, 675, 789, 676, 428, 258, 205, 153, 140, 99, 92, 65, 45, 57, 38, 48, 25, 44, 20, 18, 28, 16, 12, ...]
# print(len(nx.degree_histogram(G)))  # 82
x_degree = list(range(len(degree_frequency_numbers)))  # 所有的度数 作为下面画图的x坐标


# 删去 度为0的元素
for i in sorted(x_degree, reverse=True):  # 注意这里要反向遍历 不然索引会出问题
    if degree_frequency_numbers[i] == 0:
        del degree_frequency_numbers[i]
        del x_degree[i]

degree_frequency = [x / N for x in degree_frequency_numbers]  # 度的频率

# 使用 numpy.polyfit 进行线性拟合
coefficients = np.polyfit(np.log10(x_degree), np.log10(degree_frequency), 1)
slope, intercept = coefficients



# 绘制原始数据点
plt.scatter(x_degree, degree_frequency, color='blue', label='Ports')
print("x_degree长度",len(x_degree))
# 绘制拟合得到的幂律分布曲线
# pdf = fit.power_law.pdf(x_degree)
y_fit = np.power(x_degree, slope) * np.power(10, intercept)
plt.plot(x_degree, y_fit, color='red', linestyle='--', label=f'Fit $k^{{{slope:.3f}}}$')

# 设置对数坐标轴
plt.xscale("log")
plt.yscale("log")

# 设置坐标轴范围
plt.xlim([min(x_degree) * 0.6, max(x_degree) * 1.7])  # 设置x轴范围为数据的最小值到最大值的1.1倍
plt.ylim([min(degree_frequency) * 0.6, max(degree_frequency) * 1.7])  # 设置y轴范围为数据的最小值到最大值的1.1倍

# 添加图例和标题
plt.legend()
plt.title("Degree Distribution")
plt.xlabel("Degree")
plt.ylabel("Degree Frequency")
plt.show()
