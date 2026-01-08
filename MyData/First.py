import heapq
import json
import pathlib
import random
import re
from typing import Set
from matplotlib.lines import Line2D
import os
import networkx as nx
import seaborn as sns
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.special import comb
from networkx.algorithms.assortativity import degree_assortativity_coefficient
from tqdm import tqdm

from Algorithm.ConstructNetwork import ConstructNetwork
from sklearn.preprocessing import minmax_scale
from matplotlib import patheffects
from scipy import stats  # 用于线性回归拟合
from heapq import nlargest
from collections import deque
from collections import defaultdict
from matplotlib.path import Path
import matplotlib.patches as patches
import sys
from MyData.Draw import Draw
from MyData.NullModel import NullModel
from MyData.DirectedWeighted import DirectedWeighted
from MyData.Undirected import Undirected
from MyData.Read import Read
from MyData.Main import Main
from MyData.Robustness import Robustness
sys.path.append('../Algorithm')

# g = nx.DiGraph()
# edges = [
#     (0, 1, {"volumeTEU": 1}),
#     (1, 2, {"volumeTEU": 1}),
#     (0, 3, {"volumeTEU": 1}),
#     (4, 1, {"volumeTEU": 1}),
#     (4, 5, {"volumeTEU": 1})
# ]
#
# # 加边（weight = 流量）
#
# g.add_edges_from(edges)
#
# for node in g.nodes():
#     g.nodes[node]['total_TEU'] = 0
#     TEU_in = 0
#     TEU_out = 0
#     for _, _, attr in g.in_edges(node, data=True):
#         TEU_in += attr.get("volumeTEU", 0)
#     for _, _, attr in g.out_edges(node, data=True):
#         TEU_out += attr.get("volumeTEU", 0)
#     g.nodes[node]['total_TEU'] = TEU_in + TEU_out
#
# # for node,attr in g.nodes(data=True):
# #     print(node, attr["total_TEU"])
# # for u,v,attr in g.edges(data=True):
# #     print(u,v,attr["volumeTEU"])
#
#
# Robustness.simulate_underload_cascade(g, [1.2],[0.8],
#                                       Robustness.node_attack_betweenness, Robustness.LWCC)

time = "2017"
alpha_list = np.linspace(0, 0.5, 20)
DiG, _ = Main.get_certain_networks_by_years(time)

configure = {
    "random": Robustness.node_attack_random,
    "degree": Robustness.node_attack_degree,
    "strength": Robustness.node_attack_strength,
    "betweenness": Robustness.node_attack_betweenness
}

data = {
    "Fraction": [frac for frac in alpha_list]
}
for attack, func in configure.items():
    print(f"{attack}级联开始：")
    result = Robustness.simulate_cascade(DiG, alpha_list, func, Robustness.Number_Of_Connected_Components)
    data[attack] = list(result.values())

df = pd.DataFrame(data)
Draw.draw_plot(
    df,
    f'Robustness/Cascade/',
    "Number Of Connected Components",
    f"{time} Number Of Connected Components",
    colors=1,
    markers=1
)