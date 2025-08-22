import os
import numpy as np
import networkx as nx
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
from scipy.stats import entropy

# ---------- 参数 ----------
years = list(range(2017, 2022))
records = []

# ---------- 工具函数 ----------
def rich_club_phi(G, k):
    """无权无向 rich-club coefficient @ degree k"""
    rich = [n for n, d in G.degree() if d >= k]
    H = G.subgraph(rich)
    nk = len(rich)
    if nk < 2:
        return np.nan
    return 2 * H.number_of_edges() / (nk * (nk - 1))

def calc_metrics(G):
    """计算 14 个网络基本指标"""
    # 基础规模
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    density = nx.density(G)

    # 最大连通分量
    gcc_nodes = len(max(nx.connected_components(G), key=len))

    # 度 & 强度（交易次数）
    # 后续再加上交易TEU的强度
    degrees = [d for _, d in G.degree()]
    strengths = [d for _, d in G.degree(weight='weight')]
    avg_degree = np.mean(degrees)
    avg_strength = np.mean(strengths)

    # 度分布熵
    cnt = Counter(degrees)
    probs = np.array(list(cnt.values())) / sum(cnt.values())
    deg_entropy = entropy(probs, base=2)

    # 聚类系数
    avg_clustering = nx.average_clustering(G, weight='weight')

    # 介数中心性最大值
    btw = nx.betweenness_centrality(G, weight='weight')
    max_betweenness = max(btw.values())

    # Rich-club 系数（取 k=富人阈值，这里简单地取节点度的 90 分位）
    if degrees:
        k90 = np.percentile(degrees, 90)
        rc_phi = rich_club_phi(G, k90)
    else:
        rc_phi = np.nan

    # 模块化度 Q（Louvain 社团）
    try:
        import community
        partition = community.best_partition(G, weight='weight')
        modularity = community.modularity(partition, G, weight='weight')
    except ImportError:
        modularity = np.nan

    # 平均路径长度 & 全局效率（对最大连通子图）
    if nx.is_connected(G):
        L = nx.average_shortest_path_length(G, weight='weight')
        eff = nx.global_efficiency(G)
    else:
        gcc = max(nx.connected_components(G), key=len)
        H = G.subgraph(gcc)
        L = nx.average_shortest_path_length(H, weight='weight')
        eff = nx.global_efficiency(H)

    total_strength = sum(strengths)

    return {
        'year': None,
        'nodes': n_nodes,
        'edges': n_edges,
        'gcc_size': gcc_nodes,
        'density': density,
        'avg_degree': avg_degree,
        'avg_strength': avg_strength,
        'degree_entropy': deg_entropy,
        'avg_clustering': avg_clustering,
        'max_betweenness': max_betweenness,
        'richclub_phi': rc_phi,
        'modularity': modularity,
        'avg_path_length': L,
        'global_efficiency': eff,
        'total_strength': total_strength
    }

# # ---------- 主循环 ----------
# for year in years:
#     file_path = f'../Data/{year}/US/US{year}.graphml'
#     if not os.path.exists(file_path):
#         print(f'⚠️ 文件不存在: {file_path}')
#         continue
#     Multi_G = nx.read_graphml(file_path)
#     G = nx.Graph(Multi_G)  # 无向简单图，保留权重
#
#     res = calc_metrics(G)
#     res['year'] = year
#     records.append(res)
#
# # ---------- 保存 ----------
# df = pd.DataFrame(records)
# df.to_csv('network_evolution_14metrics.csv', index=False)
# print('✅ 已写入 network_evolution_14metrics.csv')
# print(df)

# df = pd.read_csv('network_evolution_14metrics.csv')
#
# # ---------- 画图 ----------
# plt.style.use('ggplot')
# metrics = df.columns.drop('year')
# n = len(metrics)
# cols = 3
# rows = (n + cols - 1) // cols
# fig, axs = plt.subplots(rows, cols, figsize=(15, 5*rows))
# fig.suptitle('US Port Network Evolution ‑ 14 Metrics', fontsize=16)
#
# for ax, col in zip(axs.ravel(), metrics):
#     ax.plot(df['year'], df[col], marker='o')
#     ax.set_title(col.replace('_', ' ').title())
#     ax.set_xlabel('Year')
#     ax.set_ylabel(col)
#     ax.grid(alpha=0.3)
#
# # 隐藏多余的空子图
# for ax in axs.ravel()[n:]:
#     ax.set_visible(False)
#
# plt.tight_layout(rect=[0, 0.03, 1, 0.97])
# plt.savefig('network_evolution_14curves.png', dpi=300)
# plt.show()

def scale_picture():
    '''
    绘制网络规模演化图
    :return:
    '''
    # 1. 读取数据
    df = pd.read_csv('network_evolution_14metrics.csv')

    # 2. 设置出版级样式
    sns.set_style('white')  # 无网格
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11
    plt.rcParams['legend.fontsize'] = 10

    # 3. 绘制
    fig, ax1 = plt.subplots(figsize=(6.5, 3.8))

    # 左轴：nodes
    ax1.plot(df['year'], df['nodes'], marker='o', color='#1f77b4', lw=2.5, label='Nodes')
    ax1.set_ylabel('Nodes', color='black')
    ax1.tick_params(axis='y')

    # 右轴：edges（量级大）
    ax2 = ax1.twinx()
    ax2.plot(df['year'], df['edges'], marker='s', color='#ff7f0e', lw=2.5, label='Edges')
    ax2.set_ylabel('Edges', color='black')
    ax2.tick_params(axis='y')

    # 4. 横坐标整年刻度
    ax1.set_xlabel('Year')
    ax1.set_xticks(df['year'])
    ax1.set_xticklabels(df['year'])

    # 5. 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')

    # 6. 保存
    plt.tight_layout()
    plt.savefig('scale_evolution.png', dpi=300, bbox_inches='tight')
    plt.show()

