import csv
import json
import powerlaw
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pyplot import scatter
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




animal_plant = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
grease = [15,16,17,18,19,20,21,22,23,24]
minerals = [25,26,27,28,29,30,31,32,33,34,35,36,37,38]
rubber_plastics = [39,40,41,42,43]
pulpwood = [44,45,46,47,48,49]
textile = [50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67]
metal = [71,72,73,74,75,76,77,78,79,80,81,82,83]
machinery = [84,85,86,87,88,89]
precision_instrument = [90,91,92,94,95,96]
special_other = [68,69,70,93,97,98,99]

# port_in_out_info = dict()
# for node in MultiDiG_2019.nodes():
#     degree = MultiDiG_2019.degree(node)
#     in_rate = MultiDiG_2019.in_degree(node) / degree
#     out_rate = MultiDiG_2019.out_degree(node) / degree
#
#     in_out_dict = dict()
#     in_out_dict["in_rate"] = in_rate
#     in_out_dict["out_rate"] = out_rate
#     port_in_out_info[node] = in_out_dict
# json_bytes = json.dumps(port_in_out_info).encode('utf-8')
#
# # 将编码后的字符串写入文件
# with open('../Data/FinalGraph/port_in_out_info.json', 'wb') as f:
#     f.write(json_bytes)

MultiDiG_2019 = nx.read_graphml('../Data/FinalGraph/MultiDiGraph2019.graphml')
# draw_in_out_rate_map()

def draw_in_out_rate_map() -> None:
    with open('../Data/FinalGraph/port_in_out_info.json', "r", encoding="utf-8") as file:
        port_in_out_info = json.load(file)

    Port_Data = ConstructNetwork.Read_Port_Data()

    # 得到 tuple 组成的 list  tuple中的元素依次为 longitude、latitude、节点中心性
    coord = [(float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]), port_in_out_info[node]['in_rate'],node)
             for node in port_in_out_info
             if "latitude" in Port_Data[node].keys() and "longitude" in Port_Data[node].keys() and Port_Data[node]["country_english"] == "China"]
    value = [data[2] for data in coord]
    # 使用内置的 coolwarm 颜色映射（从蓝色到红色）
    cmap = plt.cm.coolwarm
    # 创建归一化函数，将值映射到0-1范围
    norm = plt.Normalize(0, 1)


    world_map = Basemap(resolution='l')
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    x, y = world_map([data[0] for data in coord], [data[1] for data in coord])
    scatter = world_map.scatter(x, y, marker='o', c=value, norm=norm, cmap=cmap ,s=50, zorder=10 )
    # 添加颜色条
    cbar = plt.colorbar(scatter, shrink=0.5, aspect=10)
    # 一次性添加所有标签
    for i, (x_pos, y_pos) in enumerate(zip(x, y)):
        plt.annotate(
            f"{coord[i][3]}({coord[i][2]:.3f})",
            xy=(x_pos, y_pos),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
            zorder=11
        )

    plt.show()


port_hs_rate_info = dict()

for node in MultiDiG_2019:
    for neighbor, edge_dict in MultiDiG_2019[node].items():  # G[node] 等价于 G.adj[node]
        for key, data in edge_dict.items():
            print(f"    {node} → {neighbor} (键={key}), 属性: {data}")



    for predecessor, edge_dict in MultiDiG_2019.pred[node].items():
        for key, data in edge_dict.items():
            print(f"    {predecessor} → {node} (键={key}), 属性: {data}")

