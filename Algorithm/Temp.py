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
from collections import deque


# #regioncombine Export and Import to Total
# years = range(2017, 2022)
# seasons = ['Spring','Summer','Autumn','Winter']
# for year in years:
#     for season in seasons:
#         G_Im = nx.read_graphml(f'../Data/{year}/US/Season/{season}/USImport{year}_{season}.graphml')
#         G_Ex = nx.read_graphml(f'../Data/{year}/US/Season/{season}/USExport{year}_{season}.graphml')
#
#         # 合并两个图
#         G_combined = nx.compose(G_Im, G_Ex)
#
#         print("N:", G_combined.number_of_nodes())
#         print("M:", G_combined.number_of_edges())
#
#         # 使用 GraphML 保存图
#         nx.write_graphml(G_combined, f'../Data/{year}/US/Season/{season}/US{year}_{season}.graphml')
# #endregion

#region允许多边的图——>Digraph
# years = range(2017, 2022)
# seasons = ['Spring','Summer','Autumn','Winter']
#
# for year in years:
#     for season in seasons:
#         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}.graphml'
#         if not os.path.exists(file_path):
#             print(f'⚠️ 文件不存在: {file_path}')
#             continue
#         Multi_G = nx.read_graphml(file_path)
#
#         # 假设 G 是 MultiDiGraph，边有 volumeTEU 属性
#         D = nx.DiGraph()  # 目标简单有向图
#         D.add_nodes_from(Multi_G.nodes(data=True))  # 1. 先拷节点属性
#
#         # 2. 把平行边的 TEU 累加
#         for u, v, data in Multi_G.edges(data=True):
#             teu = data.get('volumeTEU', 0)
#             if D.has_edge(u, v):
#                 D[u][v]['volumeTEU'] += teu
#             else:
#                 D.add_edge(u, v, volumeTEU=teu)
#
#         # 使用 GraphML 保存图
#         nx.write_graphml(D, f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml')
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






def weighted_k_core(G, k, weight='volumeTEU', degree_type='total'):
    """
    计算加权有向图的k-核（支持加权度、加权入度、加权出度）

    参数:
        G: 有向图 (nx.DiGraph)
        k: k-核的阶数
        weight: 边的权重属性名称（默认'weight'）
        degree_type: 加权度类型
            'total'：加权度（总权重和）
            'in'：加权入度（入边权重和）
            'out'：加权出度（出边权重和）

    返回:
        子图 (nx.DiGraph)：满足条件的k-核
    """
    # 复制原图避免修改输入
    H = G.copy()
    n = H.number_of_nodes()
    if n == 0:
        return H

    # 1. 初始化节点的加权度
    def get_weighted_degree(node):
        if degree_type == 'total':
            deg = sum(data.get(weight, 1.0) for _,_, data in H.edges(node, data=True))
            return deg
        elif degree_type == 'in':
            return sum(data.get(weight, 1.0) for _, _, data in H.in_edges(node, data=True))
        elif degree_type == 'out':
            return sum(data.get(weight, 1.0) for _, _, data in H.out_edges(node, data=True))
        else:
            raise ValueError("degree_type必须是'total'、'in'或'out'")

    # 计算初始加权度
    weighted_degrees = {node: get_weighted_degree(node) for node in H.nodes()}

    # 2. 迭代剥离加权度 < k 的节点
    # 使用队列存储待处理节点（加权度 < k）
    queue = deque([node for node, deg in weighted_degrees.items() if deg < k])

    while queue:
        u = queue.popleft()
        if u not in H.nodes():  # 已被移除
            continue

        # 记录与u相连的节点（用于后续更新加权度）
        neighbors = list(H.neighbors(u))  # 获取u的所有邻居

        # 移除节点u
        H.remove_node(u)

        # 3. 更新邻居的加权度，并检查是否需要加入队列
        for v in neighbors:
            if v not in H.nodes():
                continue
            # 重新计算v的加权度
            new_deg = get_weighted_degree(v)
            old_deg = weighted_degrees[v]
            weighted_degrees[v] = new_deg
            # 若v的加权度从≥k变为<k，加入队列
            if old_deg >= k and new_deg < k:
                queue.append(v)
    return H


# -------------------------- 示例用法 --------------------------
if __name__ == "__main__":
    # 创建带权重的有向图
    # G = nx.DiGraph()
    # edges = [
    #     (1, 2, {'weight': 1}),
    #     (1, 3, {'weight': 1}),
    #     (2, 4, {'weight': 1}),
    #     (3, 4, {'weight': 1}),
    #     (4, 2, {'weight': 1}),
    #     (5, 3, {'weight': 1}),
    #     (2, 3, {'weight': 1}),
    #     (1, 4, {'weight': 1}),
    #     (2, 6, {'weight': 1})
    # ]
    # G.add_edges_from(edges)
    G = nx.les_miserables_graph()



    k = 1
    core_number_dict = {}
    max_weight = max(dict(nx.degree(G, weight='weight')).values())

    while k < max_weight + 2:

        k_core_total = weighted_k_core(G, k=k, degree_type='total')
        for node in k_core_total:
            core_number_dict[node] = k

        k += 1

    print(core_number_dict)
    print(nx.core_number(G))


    # k_core_in = weighted_k_core(G, k=2, degree_type='in')
    # print(k_core_in.nodes())
    # print(k_core_in.edges(), "\n")
    #
    #
    # k_core_out = weighted_k_core(G, k=2, degree_type='out')
    # print(k_core_out.nodes())
    # print(k_core_out.edges())