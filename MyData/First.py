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





# years = [2017, 2018, 2019, 2020]
# threshold = 0.1
#
#
# random_prob = []
# degree_prob = []
# strength_prob = []
# betweenness_prob = []
#
# for year in years:
#
#     file = f"Output/Robustness/Cascade/Unload/{year}_LWCC_beta_0.1.csv"
#     df = pd.read_csv(file)
#
#     random_prob.append(np.mean(df["random"] < threshold))
#     degree_prob.append(np.mean(df["degree"] < threshold))
#     strength_prob.append(np.mean(df["strength"] < threshold))
#     betweenness_prob.append(np.mean(df["betweenness"] < threshold))
#
# # 攻击策略数据
# data = [random_prob, degree_prob, strength_prob, betweenness_prob]
# labels = ["Random", "Degree", "Strength", "Betweenness"]
#
# # 期刊风格配色
# colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B2"]
#
# x = np.arange(len(years))
# width = 0.18
#
# plt.figure(figsize=(8,6))
#
# bars = []
#
# for i in range(4):
#     bars.append(
#         plt.bar(x + (i-1.5)*width, data[i], width,
#                 label=labels[i],
#                 color=colors[i])
#     )
#
# plt.xticks(x, years, fontsize=11)
#
# plt.xlabel("Year", fontsize=12)
# plt.ylabel("Collapse Probability", fontsize=12)
#
# plt.ylim(0,1)
#
# plt.legend(frameon=False)
#
# plt.grid(axis="y", linestyle="--", alpha=0.5)
#
# # 去掉上右边框（期刊常见风格）
# ax = plt.gca()
# ax.spines["top"].set_visible(False)
# ax.spines["right"].set_visible(False)
#
# # 自动标注柱子数值
# for bar_group in bars:
#     for bar in bar_group:
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width()/2,
#                  height + 0.02,
#                  f"{height:.2f}",
#                  ha="center",
#                  va="bottom",
#                  fontsize=9)
#
# plt.tight_layout()
#
# # 保存论文图
# plt.savefig("collapse_probability_years.pdf")
# plt.savefig("collapse_probability_years.eps")

# plt.show()



# years = [2017, 2018, 2019, 2020]
#
# threshold = 0.1
#
# random_prob = []
# degree_prob = []
# strength_prob = []
# betweenness_prob = []
#
# for year in years:
#     file = f"Output/Robustness/Cascade/Unload/{year}_LWCC_beta_0.4.csv"
#
#     df = pd.read_csv(file)
#
#     random_prob.append(np.mean(df["random"] < threshold))
#     degree_prob.append(np.mean(df["degree"] < threshold))
#     strength_prob.append(np.mean(df["strength"] < threshold))
#     betweenness_prob.append(np.mean(df["betweenness"] < threshold))
#
# x = np.arange(len(years))
# width = 0.2
#
# plt.figure(figsize=(8, 6))
#
# plt.bar(x - 1.5 * width, random_prob, width, label="Random")
# plt.bar(x - 0.5 * width, degree_prob, width, label="Degree")
# plt.bar(x + 0.5 * width, strength_prob, width, label="Strength")
# plt.bar(x + 1.5 * width, betweenness_prob, width, label="Betweenness")
#
# plt.xticks(x, years)
#
# plt.xlabel("Year")
# plt.ylabel("Collapse Probability")
#
# plt.title("Collapse Probability across Years")
#
# plt.ylim(0, 1)
#
# plt.legend()
#
# plt.grid(axis="y", alpha=0.3)
#
# plt.tight_layout()
#
# plt.show()





# # 崩溃阈值
# threshold = 0.1
#
# data = df["strength"].values
# data = np.sort(data)
#
# cdf = np.arange(len(data)) / len(data)
#
# plt.plot(data, cdf)
# plt.show()

# # 提取不同攻击策略的数据
# data = [
#     df["random"].values,
#     df["degree"].values,
#     df["strength"].values,
#     df["betweenness"].values
# ]


# labels = ["Random", "Degree", "Strength", "Betweenness"]
#
# # 画图
# plt.figure(figsize=(8,6))
#
# plt.boxplot(
#     data,
#     labels=labels,
#     showmeans=True,
#     showfliers=False,
#     whis=(40,60)
# )
#
# plt.xlabel("Attack Strategy")
# plt.ylabel("LWCC")
# plt.title("Cascade robustness under different attack strategies")
#
# plt.grid(alpha=0.3)
#
# plt.tight_layout()
# plt.show()




# TODO  alpha平均上升多少 LWCC上升多少  beta平均下降多少 LWCC上升多少
# TODO 随机攻击的结果要多次实验取平均


# 并行
# years = ["2017","2018","2019","2020"]
# if __name__ == "__main__":
#     with Pool(4) as p:
#         p.map(Main.cascade_attack_unload, years)



