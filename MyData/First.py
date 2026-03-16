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
#region 找相变的alpha和beta值
# 所有beta文件
# files = sorted(glob.glob("Output/Robustness/Cascade/Unload/step 1e-2/2020_LWCC_beta_*.csv"))
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
#     matrix_strength.append(df["strength"].values)
#
# matrix_strength = np.array(matrix_strength)
# # 确保 alpha_list 和 beta_list 是一维的 numpy 数组，方便索引
# alpha_array = np.array(alpha_list)
# beta_array = np.array(beta_list)
#
# # ==========================================
# # 1. 寻找临界 Alpha (alpha_c) - 基于固定的 Beta
# # ==========================================
# # 沿 alpha 轴（水平方向，axis=1）计算一阶差分
# # 差分值最大的地方，就是网络存活率发生“跳水”的相变点
# diff_alpha = np.diff(matrix_strength, axis=1)
# critical_alpha_indices = np.argmax(diff_alpha, axis=1)
#
# # 获取对应的 alpha_c 临界值
# alpha_c_curve = alpha_array[critical_alpha_indices]
#
# # ==========================================
# # 2. 寻找临界 Beta (beta_c) - 基于固定的 Alpha
# # ==========================================
# # 沿 beta 轴（垂直方向，axis=0）计算一阶差分
# diff_beta = np.diff(matrix_strength, axis=0)
# critical_beta_indices = np.argmax(diff_beta, axis=0)
#
# # 获取对应的 beta_c 临界值
# beta_c_curve = beta_array[critical_beta_indices]
#
# # ==========================================
# # 3. 打印部分结果用于检验
# # ==========================================
# print("--- 临界 Alpha 检验 ---")
# # 打印前 5 个 beta 对应的临界 alpha
# for i in range(5):
#     print(f"当 Beta = {beta_array[i]:.2f} 时，临界 Alpha_c = {alpha_c_curve[i]:.2f}")
#
# print("\n--- 临界 Beta 检验 ---")
# # 选取几个特定的 alpha 查看临界 beta
# sample_alpha_indices = [len(alpha_array)//2, -1] # 取中间和最后一个 alpha
# for idx in sample_alpha_indices:
#     print(f"当 Alpha = {alpha_array[idx]:.2f} 时，临界 Beta_c = {beta_c_curve[idx]:.2f}")
#
#
#
#
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
#endregion





# TODO  alpha平均上升多少 LWCC上升多少  beta平均下降多少 LWCC上升多少
# TODO 随机攻击的结果要多次实验取平均


# # 并行级联模拟
# years = ["2017","2018","2019","2020"]
# if __name__ == "__main__":
#     with Pool(4) as p:
#         p.map(Main.cascade_attack_unload_ports, years)



