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



G = nx.MultiDiGraph()
G.add_nodes_from([
    (1, {'country': 'US'}),
    (2, {'country': 'CN'}),
    (3, {'country': 'DE'}),
    (4, {'country': 'NL'})
])
G.add_edges_from([
    (1, 2, {'total_TEU': 100}),
    (2, 1, {'total_TEU': 200}),   # 反向
    (2, 1, {'total_TEU': 300}),   # 第二条平行边
    (1, 3, {'total_TEU': 150}),
    (3, 4, {'total_TEU': 80}),
    (4, 3, {'total_TEU': 90})
])
# for u, v, w in G.edges(data='weight'):   # data='weight' 直接拿到权重值
#     print(u, v, w)

# 假设 G 是 MultiDiGraph，边有 total_TEU 属性
D = nx.DiGraph()          # 目标简单有向图
D.add_nodes_from(G.nodes(data=True))   # 1. 先拷节点属性

# 2. 把平行边的 TEU 累加
for u, v, data in G.edges(data=True):
    teu = data.get('total_TEU', 0)
    if D.has_edge(u, v):
        D[u][v]['total_TEU'] += teu
    else:
        D.add_edge(u, v, total_TEU=teu)

for u, v, w in D.edges(data=True):
    teu = w.get('total_TEU', 0)
    u_country = D.nodes[u].get('country', 'Unknown')
    v_country = D.nodes[v].get('country', 'Unknown')
    print(u, u_country, v, v_country,teu)