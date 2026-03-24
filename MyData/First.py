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
from matplotlib import cm # 引入颜色映射
import matplotlib.colors as mcolors
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

Main.different_alpha_beta_lwcc("2017")
Main.different_alpha_beta_lwcc("2018")
Main.different_alpha_beta_lwcc("2019")
Main.different_alpha_beta_lwcc("2020")


# beta = 0.4
# time = 2020
# # 1. 读取数据
# # 请确保文件名与实际路径一致，注意文件名中可能存在的空格
# file_path = f"Output/Robustness/Cascade/Unload/step 2e-2/{time}_LWCC_beta_{beta} .csv"
# df = pd.read_csv(file_path)
#
# # 2. 创建画布
# fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
#
# # 3. 绘制四条折线
# # 使用不同的颜色、线型和标记，并错开 zorder 防止遮挡
# ax.plot(df['Alpha'], df['random'],
#         label='Random', color='#3498DB', linewidth=2,
#         marker='o', markersize=5, alpha=0.8, zorder=4)
#
# ax.plot(df['Alpha'], df['degree'],
#         label='Degree', color='#E67E22', linewidth=2, linestyle='--',
#         marker='s', markersize=5, alpha=0.9, zorder=3)
#
# ax.plot(df['Alpha'], df['strength'],
#         label='Strength', color='#2ECC71', linewidth=2,
#         marker='^', markersize=6, alpha=0.8, zorder=2)
#
# ax.plot(df['Alpha'], df['betweenness'],
#         label='Betweenness', color='#E74C3C', linewidth=2,
#         marker='D', markersize=5, alpha=0.8, zorder=1)
#
# # 4. 坐标轴与图表美化
# ax.set_xlabel(r"$\alpha$", fontsize=13, fontweight='bold', labelpad=10)
# ax.set_ylabel(fr"$\beta$={beta}  LWCC", fontsize=13, fontweight='bold', labelpad=10)
# # ax.set_title(r"Network Resilience under Different Attack Strategies ($\beta=0.4$, 2020)", fontsize=15, pad=15, fontweight='bold')
#
# # 设置刻度字体大小
# ax.tick_params(axis='both', which='major', labelsize=11)
#
# # 5. 图例设置
# # 将图例放在右下角，避免遮挡相变的关键区域 (左下角)
# ax.legend(loc='lower right', fontsize=11, frameon=True, shadow=False, edgecolor='black')
#
# # 紧凑布局并显示
# plt.tight_layout()
# for for_mat in ["png", "eps"]:  # png and eps
#         plt.savefig(f'Output/Robustness/Cascade/Unload/Strategy/'
#                     f'{time}_different_strategies_beta_{beta}_LWCC.{for_mat}',
#                     format=for_mat,  # 显式指定格式（可选，但更稳妥）
#                     dpi=300,
#                     bbox_inches='tight'  # 去除图片周围多余空白
#         )





#endregion








# #region 找相变的alpha和beta值
# # 所有beta文件
# files = sorted(glob.glob("Output/Robustness/Cascade/Unload/step 1e-2/2017_LWCC_beta_*.csv"))
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
#
#
# # --- 1. 准备数据坐标 ---
# # 必须让坐标的形状与 matrix_strength 一致
# # Heatmap 的中心坐标是从 0.5 到 len-0.5
# X, Y = np.meshgrid(np.arange(len(alpha_list)) + 0.5,
#                    np.arange(len(beta_list)) + 0.5)
#
# plt.figure(figsize=(10, 8))
#
# # --- 2. 绘制底层热力图 ---
# ax = sns.heatmap(
#     matrix_strength,
#     xticklabels=np.round(alpha_list, 2),
#     yticklabels=np.round(beta_list, 2),
#     cmap="viridis",
#     cbar_kws={'label': 'LWCC'}
# )
#
# # --- 4. 坐标轴美化 ---
# # 保持每 10 个刻度显示一个标签
# step = 10
# ax.set_xticks(np.arange(0, len(alpha_list), step))
# ax.set_xticklabels(np.round(alpha_list[::step], 2), rotation=45)
# ax.set_yticks(np.arange(0, len(beta_list), step))
# ax.set_yticklabels(np.round(beta_list[::step], 2), rotation=0)
#
# plt.xlabel(r"$\alpha$ (Overload Threshold)")
# plt.ylabel(r"$\beta$ (Underload Threshold)")
# plt.title("Integrated Phase Boundary (Overload & Underload Effects)")
#
# plt.tight_layout()
# plt.show()

# # # 确保 alpha_list 和 beta_list 是一维的 numpy 数组，方便索引
# # alpha_array = np.array(alpha_list)
# # beta_array = np.array(beta_list)
# #
# # # ==========================================
# # # 1. 提取相变边界 (临界 Alpha_c)
# # # ==========================================
# # # 沿 alpha 轴计算差分。注意：np.diff 后的长度会减 1
# # diff_alpha = np.diff(matrix_strength, axis=1)
# #
# # y_coords = []
# # x_coords = []
# #
# # # 2. 逐行提取相变点
# # for i in range(matrix_strength.shape[0]):
# #     row_diff = diff_alpha[i, :]
# #
# #     # 只有当这一行存在明显的 LWCC 跳变时（阈值设为 0.1）才记录
# #     if np.max(row_diff) > 0.1:
# #         # 寻找差分最大的位置索引
# #         idx = np.argmax(row_diff)
# #
# #         # 记录对应的 y (beta 索引) 和 x (alpha 索引)
# #         y_coords.append(i)
# #         x_coords.append(idx)
# #
# # # 3. 绘图
# # plt.figure(figsize=(10, 8))
# # ax = sns.heatmap(matrix_strength,
# #                  xticklabels=np.round(alpha_list, 2),
# #                  yticklabels=np.round(beta_list, 2),
# #                  cmap="viridis")
# #
# # # 4. 叠加红线
# # # 注意：x_coords + 1 是因为 diff 会导致索引偏移一位
# # if x_coords:
# #     plt.plot(np.array(x_coords) + 1.0,  # 偏移补偿，使线位于颜色变化边缘
# #              np.array(y_coords) + 0.5,
# #              color='red',
# #              linewidth=3,
# #              linestyle='--',
# #              label='Phase Boundary')
# #
# # # 5. 坐标轴美化 (每 10 个显示一个标签)
# # step = 10
# # plt.xticks(np.arange(0, len(alpha_list), step), np.round(alpha_list[::step], 2), rotation=45)
# # plt.yticks(np.arange(0, len(beta_list), step), np.round(beta_list[::step], 2), rotation=0)
# #
# # plt.legend()
# # plt.show()
# #endregion




# # 并行级联模拟
# years = ["2017","2018","2019","2020"]
# if __name__ == "__main__":
#     with Pool(4) as p:
#         p.map(Main.cascade_attack_unload_ports, years)



