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
from scipy.integrate import simpson # 使用辛普森积分

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




# --- 1. 数据读取与计算函数 ---
def get_phase_boundary(year):
    # 这里的路径请根据你的实际情况微调
    path_pattern = f"Output/Robustness/Cascade/Unload/step 1e-2/{year}_LWCC_beta_*.csv"
    files = sorted(glob.glob(path_pattern))
    if not files:
        print(f"Warning: No files found for {year}")
        return None, None, None

    beta_list = []
    matrix_strength = []
    alpha_values = None

    for file in files:
        b_val = float(file.split("_")[-1].replace(".csv", ""))
        beta_list.append(b_val)
        df = pd.read_csv(file)
        if alpha_values is None:
            alpha_values = df["Alpha"].values
        # 我们使用 strength 攻击的结果作为演示，你可以根据需要换成 degree 等
        matrix_strength.append(df["strength"].values)

    return np.array(alpha_values), np.array(beta_list), np.array(matrix_strength)
def calculate_resilience_area(alphas, betas, matrix):
    """计算相变线右上方的生存面积"""
    critical_heights = []
    valid_alphas = []
    for j in range(matrix.shape[1]):
        column = matrix[:, j]
        indices = np.where(column >= 0.5)[0]
        if len(indices) > 0:
            # 找到最稳健的临界点（由于纵轴反转，beta 越小，存活高度越高）
            beta_c = betas[np.min(indices)]
            critical_heights.append(1.0 - beta_c)
            valid_alphas.append(alphas[j])

    if len(valid_alphas) < 2: return 0.0
    return simpson(y=critical_heights, x=valid_alphas)


# --- 2. 核心执行逻辑 ---
years = [2017, 2018, 2019, 2020]
colors = ["#0072B2", "#E69F00", "#009E73", "#D55E00"]
linestyles = ['-', '--', '-.', ':']

area_results = {}
plot_data = {}

for year in years:
    alphas, betas, matrix = get_phase_boundary(year)
    if matrix is not None:
        area = calculate_resilience_area(alphas, betas, matrix)
        area_results[year] = area
        plot_data[year] = (alphas, betas, matrix)

# --- 3. 绘制主图与插图 ---
fig, ax = plt.subplots(figsize=(10, 8))

for i, year in enumerate(years):
    if year in plot_data:
        alphas, betas, matrix = plot_data[year]
        X_val, Y_val = np.meshgrid(alphas, betas)

        # 绘制主图等高线
        ax.contour(X_val, Y_val, matrix, levels=[0.5],
                   colors=colors[i], linestyles=linestyles[i], linewidths=2.5)

        # 在图例中显示面积数值
        area_val = area_results[year]
        ax.plot([], [], color=colors[i], linestyle=linestyles[i],
                label=f"{year}")

# 主图设置
ax.set_ylim(1.0, 0.0)  # 核心：反转纵轴，0在上，1在下
ax.set_xlim(1.0, 1.8)  # 聚焦相变区间
ax.set_title("Evolution of Network Resilience Boundaries (2017-2020)", fontsize=15, pad=15)
ax.set_xlabel(r"$\alpha$", fontsize=13)
ax.set_ylabel(r"$\beta$", fontsize=13)
ax.legend(frameon=False, loc='center right', fontsize=11)

# --- 修正后的插图 (Inset Plot) 绘制逻辑 ---
# 这里的 [0.08, 0.08, 0.35, 0.3] 分别对应 [左, 下, 宽, 高]
axins = ax.inset_axes([0.78, 0.74, 0.2, 0.2])

# 关键：使用数字索引 np.arange(len(years)) 避免 ConversionError
x_indices = np.arange(len(years))
y_areas = [area_results[y] for y in years]

bars = axins.bar(x_indices, y_areas, color=colors, edgecolor='black', alpha=0.8, width=0.6)

# 强制设置刻度并贴上年份标签
axins.set_xticks(x_indices)
axins.set_xticklabels([str(y) for y in years], fontsize=9)


# 添加插图的轴标签
axins.set_xlabel("Year", fontsize=9)
axins.set_ylabel("Resilience Area", fontsize=9)

# 插图美化
# axins.set_title("Total Survival Area", fontsize=11, fontweight='bold')
axins.set_ylim(0, max(y_areas) * 1.3)
axins.grid(axis='y', linestyle='--', alpha=0.4)
axins.tick_params(axis='y', labelsize=8)

# 在柱状图上方标出数值
for bar in bars:
    height = bar.get_height()
    axins.text(bar.get_x() + bar.get_width() / 2., height + 0.005,
               f'{height:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.tight_layout()

# 保存图像
save_dir = 'Output/Robustness/Cascade/Unload/Year/'
os.makedirs(save_dir, exist_ok=True)
for fmt in ['png', 'pdf', 'eps']:
    plt.savefig(f"{save_dir}integrated_phase_boundary.{fmt}",
                dpi=300,
                bbox_inches='tight'
    )





# def get_phase_boundary(year):
#     """提取特定年份的相变边界坐标"""
#     # 修改为你的实际路径
#     path_pattern = f"Output/Robustness/Cascade/Unload/step 1e-2/{year}_LWCC_beta_*.csv"
#     files = sorted(glob.glob(path_pattern))
#
#     if not files:
#         print(f"No files found for year {year}")
#         return None, None, None
#
#     beta_list = []
#     matrix_strength = []
#     alpha_values = None
#
#     for file in files:
#         # 提取 beta 值
#         b_val = float(file.split("_")[-1].replace(".csv", ""))
#         beta_list.append(b_val)
#
#         df = pd.read_csv(file)
#         if alpha_values is None:
#             alpha_values = df["Alpha"].values
#         matrix_strength.append(df["strength"].values)
#
#     return np.array(alpha_values), np.array(beta_list), np.array(matrix_strength)


# years = [2017, 2018, 2019, 2020]
# colors = ["#0072B2", "#E69F00", "#009E73", "#D55E00"]  # 专业的无障碍色板
# linestyles = ['-', '--', '-.', ':']
#
# plt.figure(figsize=(9, 7))
#
# for i, year in enumerate(years):
#     alphas, betas, matrix = get_phase_boundary(year)
#
#     if matrix is not None:
#         # 创建数值坐标网格（这次直接用 alpha 和 beta 的原始数值）
#         X_val, Y_val = np.meshgrid(alphas, betas)
#
#         # 使用 contour 提取 0.5 处的等值线
#         # 注意：我们不在 plot 上画，而是直接利用 contour 的路径
#         cs = plt.contour(X_val, Y_val, matrix, levels=[0.5],
#                          colors=colors[i], linestyles=linestyles[i], linewidths=2.5)
#
#         # 为图例手动创建代理
#         plt.plot([], [], color=colors[i], linestyle=linestyles[i], label=f"Year {year}")
#
# # 方式 A：直接设置 ylim 的顺序，从大到小即为反转
# plt.ylim(1.0, 0.0)
#
# # --- 图表美化 ---
# plt.title("Evolution of Network Resilience Boundaries (2017-2020)", fontsize=14)
# plt.xlabel(r"Capacity Upper Bound ($\alpha$)", fontsize=12)
# plt.ylabel(r"Capacity Lower Bound ($\beta$)", fontsize=12)
#
# # 设置网格，方便观察相变点的具体数值
# plt.grid(True, linestyle=':', alpha=0.6)
# plt.legend(title="Observation Period", frameon=True, loc='best')
# # 限制坐标轴范围以聚焦关键区域
# plt.xlim(1.0, 2.0)
#
# plt.tight_layout()
#
# # 保存高质量图像
# save_dir = 'Output/Robustness/Cascade/Unload/Year/'
# os.makedirs(save_dir, exist_ok=True)
# for fmt in ['png', 'pdf', 'eps']:
#     plt.savefig(f"{save_dir}phase_boundary_evolution.{fmt}", dpi=300, bbox_inches='tight')
#
# plt.show()
#
#
# def calculate_resilience_area(alphas, betas, matrix):
#     """
#     计算相变线右上方的面积
#     逻辑：对每个 alpha，寻找第一个使 LWCC > 0.5 的 beta_c
#     面积 = sum( (1 - beta_c) * d_alpha )
#     """
#     critical_betas = []
#     valid_alphas = []
#
#     # 遍历每个 Alpha 列
#     for j in range(matrix.shape[1]):
#         column = matrix[:, j]
#         # 寻找相变点（从 beta=1 向上找，或者找第一个 > 0.5 的索引）
#         # 因为我们要的是 0.5 以上的部分，即 (1 - beta_c)
#         indices = np.where(column >= 0.5)[0]
#
#         if len(indices) > 0:
#             # 找到最靠上的那个 beta 索引（因为我们反转了，
#             # 实际上在矩阵里是找 LWCC 较大的区域对应的 beta 值）
#             # 这里假设 beta 越小 LWCC 越大，所以找最小的索引
#             beta_c = betas[np.min(indices)]
#             critical_betas.append(1.0 - beta_c)  # 存活高度
#             valid_alphas.append(alphas[j])
#
#     # 使用辛普森积分计算面积
#     area = simpson(critical_betas, valid_alphas)
#     return area
#
#
# # --- 执行计算 ---
# years = [2017, 2018, 2019, 2020]
# area_results = {}
#
# for year in years:
#     alphas, betas, matrix = get_phase_boundary(year)  # 使用你之前的函数
#     if matrix is not None:
#         area = calculate_resilience_area(alphas, betas, matrix)
#         area_results[year] = area
#
# # --- 3. 绘制对比柱状图 ---
# plt.figure(figsize=(8, 5))
# bars = plt.bar([str(y) for y in years], area_results.values(),
#                color=["#0072B2", "#E69F00", "#009E73", "#D55E00"],
#                edgecolor='black', alpha=0.8)
#
# # 标注数值
# for bar in bars:
#     height = bar.get_height()
#     plt.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
#              f'{height:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
#
# plt.title("Quantitative Comparison: Total Resilience Area (Survival Zone)", fontsize=13)
# plt.ylabel("Area Size (Resilience Score)", fontsize=11)
# plt.ylim(0, max(area_results.values()) * 1.2)  # 留出标注空间
# plt.grid(axis='y', linestyle='--', alpha=0.7)
#
# plt.tight_layout()
# plt.show()
#
# print("各年份韧性面积（数值越高越稳健）:", area_results)



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
# # --- 3. 提取并绘制全向相变边界 ---
# # 我们取 LWCC = 0.5 作为相变的临界阈值（即生死线）
# # levels=[0.5] 表示只画出存活率从 0 跳变到 1 的中间线
# CS = plt.contour(
#     X, Y, matrix_strength,
#     levels=[0.5],
#     colors='red',
#     linewidths=3,
#     linestyles='--'
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
# # 如果你想在图例中显示这条红线
# from matplotlib.lines import Line2D
# custom_lines = [Line2D([0], [0], color='red', lw=3, linestyle='--')]
# plt.legend(custom_lines, ['Complete Phase Boundary'], loc='upper right')
#
# plt.tight_layout()
# plt.show()
#
#
#
#
#
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



