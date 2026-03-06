import heapq
import json
import pathlib
import random
import re
import glob
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
from multiprocessing import Pool
import sys
from MyData.Draw import Draw
from MyData.NullModel import NullModel
from MyData.DirectedWeighted import DirectedWeighted
from MyData.Undirected import Undirected
from MyData.Read import Read
from MyData.Main import Main
from MyData.Robustness import Robustness

sys.path.append('../Algorithm')


#region待处理
# Main.nodes_or_edges_attack("2017", "LWCC")
# Main.nodes_or_edges_attack("2020", "LWCC")
#
# fraction_axis = "Fraction"
# # metrics = "Average Shortest Path Length"
# metrics = "LWCC"
# data_2017 = pd.read_csv("Output/Robustness/Nodes/2017 LWCC nodes attack.csv")
# data_2020 = pd.read_csv("Output/Robustness/Nodes/2020 LWCC nodes attack.csv")
#
# data = {
#         fraction_axis: [],  # 移除节点的比例（如0.1, 0.2, 0.3...）
#         "2017 Strength": [],
#         "2020 Strength": [],
#         "2017 Betweenness": [],
#         "2020 Betweenness": []
# }
# # 遍历 fraction removed（假设 2017 和 2020 有相同的 fraction removed 列）
# for i in range(len(data_2017)):
#     frac = data_2017.loc[i, fraction_axis]
#
#     data[fraction_axis].append(frac)
#     data["2017 Strength"].append(data_2017.loc[i, "strength"])
#     data["2020 Strength"].append(data_2020.loc[i, "strength"])
#     data["2017 Betweenness"].append(data_2017.loc[i, "betweenness"])
#     data["2020 Betweenness"].append(data_2020.loc[i, "betweenness"])
# df = pd.DataFrame(data)
# Draw.draw_plot(
#     df,
#     'Robustness/Nodes/',
#     metrics,
#     f'2017 2020 {metrics} attack',
#     margin_rate=0.1,
#     is_label_step=False,
#     colors=1,
#     markers=1
# )
#endregion

# # 所有beta文件
# files = sorted(glob.glob("Output/Robustness/Cascade/Unload/2017_LWCC_beta_*.csv"))
#
# beta_list = []
# alpha_list = None
#
# # 假设先做 strength attack
# matrix_strength = []
#
# for file in files:
#
#     beta = float(file.split("_")[-1].replace(".csv",""))
#     beta_list.append(beta)
#
#     df = pd.read_csv(file)
#
#     if alpha_list is None:
#         alpha_list = df["Alpha"].values
#
#     matrix_strength.append(df["random"].values)
#
# matrix_strength = np.array(matrix_strength)
# # np.savetxt(
# #     "strength.csv",
# #     matrix_strength,
# #     delimiter=","
# # )
#
# plt.figure(figsize=(8,6))
#
# sns.heatmap(
#     matrix_strength,
#     xticklabels=np.round(alpha_list,2),
#     yticklabels=np.round(beta_list,2),
#     cmap="viridis"
# )
#
# plt.xlabel("Alpha (capacity upper bound)")
# plt.ylabel("Beta (capacity lower bound)")
# plt.title("Cascade Phase Diagram (Strength Attack)")
#
# plt.show()


alpha_list = np.round(np.linspace(1, 2, 51), 3)
print(alpha_list)

print(os.cpu_count())
# # 并行
# years = ["2017","2018","2019","2020"]
# if __name__ == "__main__":
#     with Pool(4) as p:
#         p.map(Main.cascade_attack_unload, years)