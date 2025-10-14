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


#regioncombine Export and Import to Total
years = range(2017, 2022)
seasons = ['Spring','Summer','Autumn','Winter']
for year in years:
    for season in seasons:
        G_Im = nx.read_graphml(f'../Data/{year}/US/Season/{season}/USImport{year}_{season}.graphml')
        G_Ex = nx.read_graphml(f'../Data/{year}/US/Season/{season}/USExport{year}_{season}.graphml')

        # 合并两个图
        G_combined = nx.compose(G_Im, G_Ex)

        print("N:", G_combined.number_of_nodes())
        print("M:", G_combined.number_of_edges())

        # 使用 GraphML 保存图
        nx.write_graphml(G_combined, f'../Data/{year}/US/Season/{season}/US{year}_{season}.graphml')
#endregion

#region允许多边的图——>Digraph
years = range(2017, 2022)
seasons = ['Spring','Summer','Autumn','Winter']

for year in years:
    for season in seasons:
        file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}.graphml'
        if not os.path.exists(file_path):
            print(f'⚠️ 文件不存在: {file_path}')
            continue
        Multi_G = nx.read_graphml(file_path)

        # 假设 G 是 MultiDiGraph，边有 volumeTEU 属性
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
        nx.write_graphml(D, f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml')
#endregion

#region给节点加上 in_TEU out_TEU total_TEU
# years = range(2017, 2022)
# seasons = ['Spring','Summer','Autumn','Winter']
# for year in years:
#     for season in seasons:
#         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
#         if not os.path.exists(file_path):
#             print(f'⚠️ 文件不存在: {file_path}')
#             continue
#         G = nx.read_graphml(file_path)
#
#         for node in G.nodes:
#             G.nodes[node]['in_TEU'] = G.nodes[node]['out_TEU'] = G.nodes[node]['total_TEU'] = 0
#             TEU_in = 0
#             TEU_out = 0
#             for _, _, attr in G.in_edges(node, data=True):
#                 TEU_in += attr.get("volumeTEU", 0)
#             for _, _, attr in G.out_edges(node, data=True):
#                 TEU_out += attr.get("volumeTEU", 0)
#             G.nodes[node]['in_TEU'] = TEU_in
#             G.nodes[node]['out_TEU'] = TEU_out
#             G.nodes[node]['total_TEU'] = TEU_in + TEU_out
#         nx.write_graphml(G, f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml')
#endregion

#region给node加上洲属性
# path = '../Data/Port/country_continent.json'
# with open(path, 'r', encoding='utf-8') as f:
#     port_continent = json.load(f)
# years = range(2017, 2022)
# seasons = ['Spring','Summer','Autumn','Winter']
# for year in years:
#     for season in seasons:
#         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
#         if not os.path.exists(file_path):
#             print(f'⚠️ 文件不存在: {file_path}')
#             continue
#         G = nx.read_graphml(file_path)
#         for node, attr in G.nodes(data=True):
#             if node[:2] in port_continent.keys():
#                 attr['continent'] = port_continent[node[:2]]["continent_code"]
#             else:
#                 print(node)
#         nx.write_graphml(G, f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml')
#endregion

#region画图程序模板
# # 1. 读取数据
# df = pd.read_csv('Figure/all_in_one_Digraph.csv')
# # 4. 创建画布和坐标轴
# fig, ax = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
# # 5. 绘制折线图
# # 绘制edges折线
# ax.plot(df['time'], df['M'],
#         label='Edges',
#         color='blue',
#         marker='o',  # 数据点标记
#         linestyle='-',  # 线条样式
#         linewidth=2,    # 线条宽度
#         markersize=6)   # 标记大小
# # 绘制nodes折线
# ax.plot(df['time'], df['N'],
#         label='Nodes',
#         color='red',
#         marker='s',  # 方形标记
#         linestyle='--', # 虚线
#         linewidth=2,
#         markersize=6)
# # 6. 设置坐标轴标签和标题
# ax.set_xlabel('Time', fontsize=12)
# ax.set_ylabel('Numbers', fontsize=12)
# ax.set_title('Changes in the number of edges and nodes in the network over time', fontsize=14, pad=20)
# # 7. 设置坐标轴刻度
# ax.tick_params(axis='x', rotation=45)  # x轴标签旋转45度，避免重叠
# ax.tick_params(axis='both', which='major', labelsize=10)
# # 9. 添加图例
# ax.legend(fontsize=10, loc='best')  # loc='best' 自动选择最佳位置
# # 10. 调整布局，避免标签被截断
# plt.tight_layout()
# # 11. 保存图片（可选）
# plt.savefig('Figure/Season/edges_nodes_time_series.png', dpi=300, bbox_inches='tight')
# # 12. 显示图表
# plt.show()
#endregion