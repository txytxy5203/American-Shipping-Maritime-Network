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





# 假设有一个MultiDiGraph对象G
G = nx.MultiDiGraph()
G.add_edge(1, 2, hs=1)
G.add_edge(1, 2, hs=2)
G.add_edge(2, 1, hs=1)
G.add_edge(1, 3, hs=2)


# for node in G.nodes():
#     out_degree = G.out_degree(node)
#     in_degree = G.in_degree(node)
for node in G:
    print(f"\n节点 {node} 的邻接关系:")

    # 出边（从node出发）
    print("  出边:")
    for neighbor, edge_dict in G[node].items():  # G[node] 等价于 G.adj[node]
        for key, data in edge_dict.items():
            print(f"    {node} → {neighbor} (键={key}), 属性: {data}")

    # 入边（指向node）
    print("  入边:")
    for predecessor, edge_dict in G.pred[node].items():
        for key, data in edge_dict.items():
            print(f"    {predecessor} → {node} (键={key}), 属性: {data}")


# # 转换为无向图（忽略多重边和方向）
# G_1 = nx.Graph(G_multi)  # 或使用G_multi.to_undirected(as_view=False)
# G_2 = nx.Graph()
# G_2.add_edge(1, 2)
# G_2.add_edge(1, 3)
#
# g = nx.Graph()
# g.add_edge(0, 1)
# # g.add_edge(0, 2)
# g.add_edge(1, 2)
# g.add_edge(3, 2)
# # g.add_edge(1, 3)
# # g.add_edge(0, 3)

# G_combined = nx.compose(G_1, G_2)
# G_combined = nx.compose(G_combined, G_3)
# # 使用 GraphML 保存图
# # nx.write_graphml(G_combined, '../Data/FinalGraph/test.graphml')
#
# # # 验证结果
# print(G_combined.edges())

print("tan","xue")