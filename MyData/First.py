import heapq
import json
import pathlib
import random
import sys
sys.path.append('../Algorithm')
import os
import networkx as nx
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.special import comb
from Algorithm.ConstructNetwork import ConstructNetwork
from Algorithm.Read import Read
from collections import Counter
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from sklearn.preprocessing import minmax_scale
from matplotlib.ticker import ScalarFormatter
from matplotlib import patheffects
from scipy.stats import entropy
from heapq import nlargest

# ---------- 工具函数 ----------
def rich_club_phi(G, k):
    """无权无向 rich-club coefficient @ degree k"""
    rich = [n for n, d in G.weighted_degree() if d >= k]
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
    degrees = [d for _, d in G.weighted_degree()]
    strengths = [d for _, d in G.weighted_degree(weight='weight')]
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

#region未处理的函数
def draw_nodes_edges_picture():
    '''
    绘制网络nodes，edges数量演化图
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
    plt.savefig('Figure/nodes_edges.png', dpi=300, bbox_inches='tight')
    plt.show()
def get_numbers_of_connect_countries_to_US(G, year):
    # 统计与美国直接相连的非美国国家数
    connected_countries = {
        G.nodes[n]['Country']
        for n in G.nodes
        if G.nodes[n].get('Country') != 'United States'
    }
    print(year)
    print(f'与美国连接的国家（去重）个数 = {len(connected_countries)}')
def the_degree_of_connection_of_all_countries_to_the_US():
    '''
    得到 Figure/US_top10_TEU_bilateral.csv  Figure/US_top10_Times_bilateral.csv  每年和美国联系程度的top10
    :return:
    '''
    years = range(2017, 2022)
    teu_rows, trips_rows = [], []

    for year in years:
        G = nx.read_graphml(f'../Data/{year}/US/US{year}.graphml')

        country_stats = {}
        for u, v, d in G.edges(data=True):
            c_u = G.nodes[u].get('Country', 'Unknown')
            c_v = G.nodes[v].get('Country', 'Unknown')
            if 'United States' in [c_u, c_v] and c_u != c_v:
                teu = float(d.get('volumeTEU', 1.0))
                trips = 1.0
                partner = c_u if c_v == 'United States' else c_v
                country_stats.setdefault(partner, {'TEU': 0, 'Trips': 0})
                country_stats[partner]['TEU'] += teu
                country_stats[partner]['Trips'] += trips

        # 每年两张榜单
        for metric, label in [('TEU', 'TEU'), ('Trips', 'Trips')]:
            top = (
                pd.Series({k: v[label] for k, v in country_stats.items()})
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
                .rename(columns={'index': 'country', 0: metric})
                .assign(year=year)
            )
            (teu_rows if label == 'TEU' else trips_rows).append(top)

    # 导出
    pd.concat(teu_rows).to_csv('Figure/US_top10_TEU_bilateral.csv', index=False)
    pd.concat(trips_rows).to_csv('Figure/US_top10_Times_bilateral.csv', index=False)

    print('✅ 已生成双边统计：')
    print(pd.concat(teu_rows).head())
def draw_degree_of_connection_of_all_countries_to_the_US():
    # 1) 读数据（TEU 或 Times 均可）
    metrics = 'Times'
    df = pd.read_csv(f'Figure/US_top10_{metrics}_bilateral.csv')  # 或 Trips 文件

    # 2) 计算年度排名（1 最高）
    df['rank'] = df.groupby('year')[metrics].rank(method='min', ascending=False)

    # 3) 绘图
    plt.figure(figsize=(7, 4.2))
    # 2. 设置出版级样式
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11
    plt.rcParams['legend.fontsize'] = 10
    sns.set_style('whitegrid')  # 带方框边框
    sns.lineplot(
        data=df,
        x='year',
        y='rank',
        hue='country',
        marker='o',
        linewidth=2.5,
        palette='tab10'
    )

    # 4) 倒序 y 轴（1 在上）
    plt.gca().invert_yaxis()
    plt.xticks(range(2017, 2022))
    plt.yticks(range(1, 11))
    plt.ylim(10.5, 0.5)

    # 5) 坐标轴
    plt.xlabel('Year')
    plt.ylabel('Rank')
    plt.title('Top 10 Countries Ranked by U.S. Connection (2017–2021)', pad=15)

    # 6) 图例放在右下角，不挡折线
    plt.legend(
        title='Country',
        loc='lower right',  # 右下角
        frameon=True,
        fancybox=True,
        shadow=False
    )

    plt.tight_layout()
    plt.savefig(f'Figure/top10_rank_{metrics}.png', dpi=300, bbox_inches='tight')
    plt.show()
def calculate_spectral_radius():
    years = range(2017, 2022)
    records = []

    for year in years:
        path = f'../Data/{year}/US/US{year}.graphml'
        if not os.path.exists(path):
            print(f'⚠️ 文件不存在: {path}')
            continue

        Mul_G = nx.read_graphml(path)
        G = nx.Graph(Mul_G)

        # 1) 无权谱半径
        A = nx.adjacency_matrix(G).astype(float).astype(float)


        rho_unw = max(abs(np.linalg.eigvals(A.toarray())))

        # 2) TEU 加权谱半径（把邻接矩阵元素换成 volumeTEU）
        # A_w = nx.adjacency_matrix(G, weight='volumeTEU').astype(float)
        # rho_w = max(abs(np.linalg.eigvals(A_w.toarray())))

        records.append({'year': year,
                        'unweighted_rho': rho_unw})
        # records.append({'year': year,
        #                 'unweighted_rho': rho_unw,
        #                 'weighted_rho': rho_w})

    # 保存
    df = pd.DataFrame(records)
    df.to_csv('Figure/spectral_radius_year.csv', index=False)
    print(df)
def calculate_structural_homogeneity():
    '''
    结构同质性
    :return:
    '''
    YEARS = range(2017, 2022)

    records = []

    DATA_DIR = 'Data'
    OUTPUT_DIR = 'Figure'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    def calc_structural_homogeneity(values):
        if len(values) <= 1:
            return np.nan
        pd.Series(values, name='col').to_csv('list.csv', index=False)
        avg = np.mean(values)
        std = np.std(values, ddof=0)
        return 1 - std / avg if avg else np.nan
        print("-------------")

    for y in YEARS:
        path = f'../{DATA_DIR}/{y}/US/US{y}.graphml'
        if not os.path.exists(path):
            print(f'⚠️ 文件不存在: {path}')
            continue
        G = nx.Graph(nx.read_graphml(path))

        rec = {
            'year': y,
            'unweighted': calc_structural_homogeneity(
                [G.degree(n) for n in G.nodes]),
        }
        records.append(rec)
    df = pd.DataFrame(records)
    df.to_csv(f'{OUTPUT_DIR}/structural_homogeneity_year.csv', index=False)
    print(df)
def calculate_assortativity():
    '''
    计算同配性
    :return:
    '''
    YEARS = range(2017, 2022)
    DATA_DIR = '../Data'
    OUTPUT_DIR = '../Figure'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    def calc_assortativity(G, weight=None, attr=None):
        """返回三种同配系数"""
        if attr is not None:
            return nx.attribute_assortativity_coefficient(G, attr)
        if weight is not None:
            return nx.degree_pearson_correlation_coefficient(G, weight=weight)
        return nx.degree_assortativity_coefficient(G)

    records = []
    for y in YEARS:
        G = nx.Graph(nx.read_graphml(f'{DATA_DIR}/{y}/US/US{y}.graphml'))
        rec = {
            'year': y,
            'degree_assort': calc_assortativity(G),
            'weighted_TEU': calc_assortativity(G, weight='volumeTEU'),
        }
        records.append(rec)

    df = pd.DataFrame(records)
    df.to_csv(f'{OUTPUT_DIR}/US_assortativity_year.csv', index=False)
    print(df)
def draw_density_avgDegree_picture():
    # 1. 读数据
    df = pd.read_csv('network_evolution_14metrics.csv')

    # 2. 出版级样式
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11

    # 3. 画图
    fig, ax1 = plt.subplots(figsize=(6.5, 3.8))
    ax1.plot(df['year'], df['density'], marker='o', color='#1f77b4', lw=2.5, label='Density')

    ax1.set_ylabel('density', color='black')
    ax1.tick_params(axis='y')


    ax2 = ax1.twinx()
    ax2.plot(df['year'], df['avg_degree'], marker='s', color='#ff7f0e', lw=2.5, label='avg degree')
    ax2.set_ylabel('avg degree', color='black')
    ax2.tick_params(axis='y')

    # 4. 横坐标整年刻度
    ax1.set_xlabel('Year')
    ax1.set_xticks(df['year'])
    ax1.set_xticklabels(df['year'])

    # 5. 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')

    plt.tight_layout()
    # 不加 ./ 也可以   加了就相当于是显式的
    plt.savefig('./Figure/scale_evolution.png', dpi=300, bbox_inches='tight')
    plt.show()
    # 单独画density
    # # 4. 去网格、整年刻度
    # ax1.grid(False)
    # ax1.set_xticks(df['year'])
    # ax1.set_xticklabels(df['year'])
    # ax1.set_xlabel('Year')
    # ax1.set_ylabel('Density')
    # ax1.set_title('Network Density Evolution (2017–2021)', pad=15)
    # ax1.legend(frameon=False, loc='upper right')   # 图例
    # # 5. 保存
    # plt.tight_layout()
    # plt.savefig('density_evolution.png', dpi=300, bbox_inches='tight')
    # plt.show()
def draw_length_efficiency_picture():
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
    ax1.plot(df['year'], df['avg_path_length'], marker='o', color='#1f77b4', lw=2.5, label='avg path length')
    ax1.set_ylabel('avg path length', color='black')
    ax1.tick_params(axis='y')

    # 右轴：edges（量级大）
    ax2 = ax1.twinx()
    ax2.plot(df['year'], df['global_efficiency'], marker='s', color='#ff7f0e', lw=2.5, label='global efficiency')
    ax2.set_ylabel('global efficiency', color='black')
    ax2.tick_params(axis='y')

    # 4. 横坐标整年刻度
    ax1.set_xlabel('Year')
    ax1.set_xticks(df['year'])
    ax1.set_xticklabels(df['year'])

    # 5. 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')
    # 在绘图后、保存前插入


    # 6. 保存
    plt.savefig('path_efficiency_evolution.png', dpi=300, bbox_inches='tight')
    plt.show()
#endregion




#regionNetwork Structure
def all_in_one(g, year, season) -> dict:
    """
    统一计算相应的基础指标
    :param g: 是一个无向无多边的简单图
    :param year:  图的年份
    :return: 基础信息的表格
    """

    # 先算能够直接计算的
    N = g.number_of_nodes()
    M = g.number_of_edges()
    density = nx.density(g)
    avg_clustering = nx.average_clustering(g)                               # 平均聚类系数
    max_connected_component = max(nx.connected_components(g), key=len)      # 最大连通分量
    mcc_sizes = len(max_connected_component)                                # 最大连通分量的大小
    avg_degrees = 2 * M / N                                                 # 平均度

    # 无权谱半径
    A = nx.adjacency_matrix(g)
    spectral_radius = max(abs(np.linalg.eigvals(A.toarray())))              # 无权谱半径


    # 平均路径长度 and 全局效率
    if nx.is_connected(g):
        avg_length = nx.average_shortest_path_length(g)
        efficiency = nx.global_efficiency(g)
    else:
        h = g.subgraph(max_connected_component)                             # 最大连通分量的那个子图
        avg_length = nx.average_shortest_path_length(h)
        efficiency = nx.global_efficiency(h)


    # 结构同质性
    degrees = dict(nx.degree(g))
    degrees_list = list(degrees.values())
    std_degrees = np.std(degrees_list, ddof=0)
    homogeneity = 1 - std_degrees / avg_degrees                             # 结构同质性


    strength_TEU = {n : 0.0 for n in g.nodes}                   # 存放每个节点的TEU强度
    # 遍历图（主循环）
    for u, v, d in g.edges(data=True):
        w = float(d.get('volumeTEU', 1.0))
        strength_TEU[u] += w
        strength_TEU[v] += w

    total_TEU = sum(strength_TEU.values())
    if total_TEU != 0:
        p = np.array(list(strength_TEU.values())) / total_TEU
        entropy = -np.sum(p * np.log2(p + 1e-12))
    else:
        entropy = np.nan

    return {
        "time": f"{year}{season}",
        "N": N,
        "M": M,
        "avg_clustering": avg_clustering,
        "avg_degrees": avg_degrees,
        "avg_length": avg_length,
        "efficiency": efficiency,
        "homogeneity": homogeneity,
        "entropy": entropy,
        "density": density,
        "spectral_radius": spectral_radius,
        "mcc_sizes": mcc_sizes
    }
def draw_edges_nodes_time_series():
    """
    根据 all in one 的数据画出 edges和nodes变化图
    :return:
    """
    # 1. 读取数据
    df = pd.read_csv('Figure/all_in_one_Digraph.csv')
    # 4. 创建画布和坐标轴
    fig, ax1 = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 2. 创建右侧Y轴（与左侧Y轴共享X轴，实现双轴对齐）
    ax2 = ax1.twinx()  # 关键：生成与ax1共享X轴的第二个Y轴

    # -------------------------- 4. 绘制双折线（分别绑定左右Y轴） --------------------------
    # -------------------------- 左侧Y轴：Nodes（假设N列是Nodes数量） --------------------------
    ax1.plot(
        df['time'],  # X轴：时间
        df['N'],     # Y轴：Nodes数量（绑定左侧ax1）
        label='Nodes',  # 图例名称
        color='red',  # 颜色（可选：用十六进制色更精准，这里是深蓝色）
        marker='o',       # 数据点标记（圆形）
        linestyle='-',    # 线条样式（实线）
        linewidth=2.5,    # 线条宽度（加粗更清晰）
        markersize=7      # 数据点大小
    )

    # -------------------------- 右侧Y轴：Edges（假设M列是Edges数量） --------------------------
    ax2.plot(
        df['time'],  # X轴：时间（与左侧共享，无需重复设置）
        df['M'],     # Y轴：Edges数量（绑定右侧ax2）
        label='Edges',  # 图例名称
        color='blue',  # 颜色（深红色，与左侧区分明显）
        marker='s',       # 数据点标记（方形，与圆形区分）
        linestyle='--',   # 线条样式（虚线，与实线区分）
        linewidth=2.5,    # 线条宽度（与左侧一致，保持美观）
        markersize=7      # 数据点大小（与左侧一致）
    )

    # -------------------------- 5. 美化双轴标签与标题 --------------------------
    # -------------------------- 左侧Y轴（ax1）设置 --------------------------
    ax1.set_xlabel('Time', fontsize=12, fontweight='bold')  # X轴标签（加粗）
    ax1.set_ylabel('Number of Nodes',  # 左侧Y轴标签（明确对应Nodes）
                   color='red',    # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax1.tick_params(axis='y',  # 左侧Y轴刻度设置
                    colors='red',  # 刻度颜色与线条一致
                    labelsize=10)      # 刻度文字大小

    # -------------------------- 右侧Y轴（ax2）设置 --------------------------
    ax2.set_ylabel('Number of Edges',  # 右侧Y轴标签（明确对应Edges）
                   color='blue',    # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax2.tick_params(axis='y',  # 右侧Y轴刻度设置
                    colors='blue',  # 刻度颜色与线条一致
                    labelsize=10)      # 刻度文字大小

    # -------------------------- 标题与X轴刻度 --------------------------
    ax1.set_title(
        'Changes in the Number of Edges and Nodes in the Network Over Time',
        fontsize=14,
        fontweight='bold',
        pad=20  # 标题与图表的间距（避免拥挤）
    )
    ax1.tick_params(axis='x', rotation=45)  # X轴时间标签旋转45度，避免文字重叠

    # -------------------------- 6. 合并双轴图例（关键：避免图例重复） --------------------------
    # 提取左右轴的图例，合并为一个（放在图表右侧，不遮挡数据）
    lines1, labels1 = ax1.get_legend_handles_labels()  # 左侧轴图例
    lines2, labels2 = ax2.get_legend_handles_labels()  # 右侧轴图例
    ax1.legend(
        lines1 + lines2,  # 合并图例线条
        labels1 + labels2,  # 合并图例文字
        fontsize=11,
        loc='upper right',  # 图例位置（右上，不遮挡数据）
        frameon=True,       # 显示图例边框
        fancybox=True,      # 边框圆角
        shadow=True         # 边框阴影（更立体）
    )

    # -------------------------- 7. 调整布局与保存 --------------------------
    # 自动调整布局（避免标签、图例被截断）
    plt.tight_layout()

    # 保存图片（dpi=300为高清，bbox_inches='tight'避免裁剪边缘）
    plt.savefig(
        'Figure/Season/edges_nodes_time_series.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'  # 背景色为白色（避免保存后背景透明）
    )

    # 显示图表（运行时弹出窗口）
    plt.show()
def draw_total_teu():
    """
    画出总的TEU变化图
    :return:
    """
    years = range(2017, 2022)  # 一年一个单位
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    records = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':  # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)
            total_teu = sum(float(d.get('volumeTEU', 0)) for _, _, d in G.edges(data=True))
            records.append({'time': f"{year}_{season}", 'total_TEU': total_teu})

    df = pd.DataFrame(records)

    # 4. 创建画布和坐标轴
    fig, ax = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 5. 绘制折线图
    ax.plot(df['time'], df['total_TEU'],
            label='TEU',
            color='blue',
            marker='o',  # 数据点标记
            linestyle='-',  # 线条样式
            linewidth=2,  # 线条宽度
            markersize=6)  # 标记大小
    # 6. 设置坐标轴标签和标题
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('TEU', fontsize=12)
    ax.set_title('Changes in the TEU in the network over time', fontsize=14, pad=20)
    # 7. 设置坐标轴刻度
    ax.tick_params(axis='x', rotation=45)  # x轴标签旋转45度，避免重叠
    ax.tick_params(axis='both', which='major', labelsize=10)
    # 9. 添加图例
    ax.legend(fontsize=10, loc='best')  # loc='best' 自动选择最佳位置
    # 10. 调整布局，避免标签被截断
    plt.tight_layout()
    # 11. 保存图片（可选）
    plt.savefig('Figure/Season/teu_time_series.png', dpi=300, bbox_inches='tight')
    # 12. 显示图表
    plt.show()
def draw_total_teu_and_us_cn_teu():
    """
    美国的总体teu 和 与中国交易的teu 变化趋势图
    :return:
    """
    # 中美贸易变化图
    years = range(2017, 2022)  # 一年一个单位
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    us_cn_records = []
    total_records = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':  # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)
            us_cn_teu = 0
            total_teu = 0
            for u, v, data in G.edges(data=True):
                u_country = G.nodes[u].get('Country', 'Unknown')
                v_country = G.nodes[v].get('Country', 'Unknown')
                # 总量teu
                total_teu += data['volumeTEU']
                # 中美teu
                if (u_country == 'United States' and v_country == 'China' or
                        u_country == 'China' and v_country == 'United States'):
                    us_cn_teu += data['volumeTEU']

            total_records.append({
                'time': f"{year}_{season}",
                'total_teu': total_teu}
            )
            us_cn_records.append({
                'time': f"{year}_{season}",
                'us_cn_teu': us_cn_teu
            })
    df_us_cn = pd.DataFrame(us_cn_records)
    df = pd.DataFrame(total_records)
    # 4. 创建画布和坐标轴
    fig, ax = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 5. 绘制折线图
    ax.plot(df_us_cn['time'], df_us_cn['us_cn_teu'],
            label='us and cn teu',
            color='blue',
            marker='o',  # 数据点标记
            linestyle='-',  # 线条样式
            linewidth=2,  # 线条宽度
            markersize=6)  # 标记大小
    ax.plot(df['time'], df['total_teu'],
            label='total teu',
            color='red',
            marker='o',  # 数据点标记
            linestyle='-',  # 线条样式
            linewidth=2,  # 线条宽度
            markersize=6)  # 标记大小
    # 6. 设置坐标轴标签和标题
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('TEU', fontsize=12)
    ax.set_title('Changes in the TEU', fontsize=14, pad=20)
    # 7. 设置坐标轴刻度
    ax.tick_params(axis='x', rotation=45)  # x轴标签旋转45度，避免重叠
    ax.tick_params(axis='both', which='major', labelsize=10)
    # 9. 添加图例
    ax.legend(fontsize=10, loc='best')  # loc='best' 自动选择最佳位置
    # 10. 调整布局，避免标签被截断
    plt.tight_layout()
    # 11. 保存图片（可选）
    plt.savefig('Figure/Season/total_teu_and_us_cn_teu_time_series.png', dpi=300, bbox_inches='tight')
    # 12. 显示图表
    plt.show()
def write_country_teu():
    years = range(2017, 2022)  # 一年一个单位
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    records = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':  # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)

            country_teu = {}
            for u, v, data in G.edges(data=True):
                u_country = G.nodes[u].get('Country', 'Unknown')
                v_country = G.nodes[v].get('Country', 'Unknown')

                # 只处理涉及美国的边
                if u_country == 'United States' and v_country != 'United States':
                    target_country = v_country
                elif v_country == 'United States' and u_country != 'United States':
                    target_country = u_country
                else:
                    # 跳过不涉及美国的边或美国与美国之间的边
                    print("均不是美国")
                    continue

                # 确保volumeTEU是数值类型
                try:
                    teu = float(data.get('volumeTEU', 0))
                except (ValueError, TypeError):
                    print("数值有问题")
                    teu = 0  # 处理无效数值的情况

                # 关键修正：检查字典中是否已有该国家，没有则初始化
                if target_country in country_teu:
                    country_teu[target_country] += teu
                else:
                    country_teu[target_country] = teu
            # 将结果添加到记录中
            records.append({
                'time': f"{year}_{season}",
                'country_teu': country_teu
            })
            print(f"✅ 已处理: {year}_{season}")
    for record in records:
        print(record)
    # 1. 处理每条记录，将国家-TEU字典拆分为键值对
    expanded_records = []
    for record in records:
        # 以time为基础创建新字典
        expanded = {'time': record['time']}
        # 加入每个国家的TEU数据
        for country, teu in record['country_teu'].items():
            expanded[country] = teu
        expanded_records.append(expanded)

    # 2. 转换为DataFrame（缺失的国家数据会自动填充为NaN）
    df = pd.DataFrame(expanded_records)

    # 3. 将NaN填充为0（表示该季节与该国无贸易数据）
    df = df.fillna(0)

    # 4. 调整列顺序：确保time在第一列
    columns = ['time'] + [col for col in df.columns if col != 'time']
    df = df[columns]

    # 5. 显示结果
    print("转换后的DataFrame：")
    print(df.head())

    # 6. 保存为CSV（可选）
    df.to_csv('InputData/country_teu.csv', index=False)
def draw_top5_countries_trading_with_the_US():
    """
    与美国交易TEU最多的top5国家除了中国
    :return:
    """
    df = pd.read_csv('InputData/country_teu.csv')
    record = {}
    # 定义函数：获取每行最大的n个值（最多5个）及其列名
    def get_top5(row):
        # 排除第一列（time列），处理剩余数值列
        value_columns = row.index[1:]  # 获取除time外的列名
        values = row[value_columns]  # 获取对应的值

        # 按值降序排序，取前5个（不足5个则取全部）
        sorted_values = values.sort_values(ascending=False).head(5)

        # 提取列名和值，用NaN填充不足5个的位置
        top_names = list(sorted_values.index) + [np.nan] * (5 - len(sorted_values))
        top_values = list(sorted_values.values) + [np.nan] * (5 - len(sorted_values))

        top = {key: value for key, value in zip(top_names, top_values)}

        record[row['time']] = top


    # 应用函数到每一行
    df.apply(get_top5, axis=1)

    # -------------------------- 1. 国家样式配置 --------------------------
    country_styles = {
        'China': {'color': '#E74C3C', 'marker': 'o', 'linestyle': '-'},  # 红色+圆形+实线
        'South Korea': {'color': '#3498DB', 'marker': 's', 'linestyle': '--'},  # 蓝色+方形+虚线
        'Japan': {'color': '#F39C12', 'marker': '^', 'linestyle': '-.'},  # 橙色+三角形+点线
        'Germany': {'color': '#2ECC71', 'marker': 'D', 'linestyle': ':'},  # 绿色+菱形+点线
        'Belgium': {'color': '#9B59B6', 'marker': 'p', 'linestyle': '-'},  # 紫色+五边形+实线
        'Vietnam': {'color': '#1ABC9C', 'marker': '*', 'linestyle': '--'},  # 青色+星形+虚线
        'Canada': {'color': '#F1C40F', 'marker': 'h', 'linestyle': '-.'},  # 黄色+六边形+点线
        'Singapore': {'color': '#34495E', 'marker': 'X', 'linestyle': '-'}  # 深灰色+X形标记+实线
    }
    fig, ax = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    for country, attr in country_styles.items():
        if country == 'China':
            continue
        time_line = []
        value_line = []
        for year in years:
            for season in seasons:
                if (year == 2021 and
                        (season == 'Summer' or season == 'Autumn' or season == 'Winter')):
                    continue
                time = f'{year}_{season}'
                if country in record[time]:
                    time_line.append(time)
                    value_line.append(record[time][country])
                # 5. 绘制折线图
                # 绘制edges折线
        ax.plot(time_line, value_line,
                label=country,
                color=country_styles[country]['color'],
                marker=country_styles[country]['marker'],  # 数据点标记
                linestyle=country_styles[country]['linestyle'],  # 线条样式
                linewidth=2,    # 线条宽度
                markersize=6)   # 标记大小
    # 6. 设置坐标轴标签和标题
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('TEU', fontsize=12)
    ax.set_title('Chart of TEU changes for the top five countries trading with the United States', fontsize=14, pad=20)
    # 7. 设置坐标轴刻度
    ax.tick_params(axis='x', rotation=45)  # x轴标签旋转45度，避免重叠
    ax.tick_params(axis='both', which='major', labelsize=10)
    # 9. 添加图例
    ax.legend(fontsize=10, loc='best')  # loc='best' 自动选择最佳位置
    # 10. 调整布局，避免标签被截断
    plt.tight_layout()
    plt.savefig('Figure/Season/Chart of TEU changes for the top five countries trading with the United States.png', dpi=300, bbox_inches='tight')
    plt.show()
def calculate_US_top10_node_pairs_by_TEU_year():
    """
    计算出每一个时间段的的TEU最大的edges （nodes之间的TEU 包含了两个方向）
    :return:
    """
    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    top_edges = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)


            # 按节点对累加 TEU
            flows = {}
            for u, v, d in G.edges(data=True):
                pair = tuple(sorted([u, v]))  # 无向，排序去重
                flows[pair] = flows.get(pair, 0) + float(d.get('volumeTEU', 0))

            # 转成 DataFrame
            data = [{'time': f"{year}_{season}", 'from': pair[0], 'to': pair[1], 'total_TEU': teu}
                    for pair, teu in flows.items()]

            # 当年 Top
            top = pd.DataFrame(data).sort_values('total_TEU', ascending=False).head(30)
            top_edges.append(top)
    df = pd.concat(top_edges, ignore_index=True)
    df.to_csv(f'InputData/US_top_edges_by_TEU.csv', index=False)
def draw_top10_TEU_edges_map():
    def draw_year(time):
        """
        绘图函数（只建一次地图，复用）
        :param time:
        :return:
        """
        fig, ax = plt.subplots(figsize=(10, 7))
        world_map = Basemap(resolution='l', projection='cyl', lon_0=-100, ax=ax)
        world_map.drawmapboundary(fill_color='#D0CFD4')
        world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
        world_map.drawcoastlines()

        # ---------- 画港口 ----------
        ports = year_to_ports.get(time, set())
        if ports:
            lon = [shift_lon(port_coords[p][0]) for p in ports]
            lat = [port_coords[p][1] for p in ports]
            x, y = world_map(lon, lat)
            # 按 TEU 总和决定大小
            sizes = [year_to_node_size[time].get(p, base_sz) for p in ports]

            # 拆成两套索引
            us_idx = [i for i, p in enumerate(ports) if p.startswith('US')]
            fore_idx = [i for i, p in enumerate(ports) if not p.startswith('US')]
            # 美国港口
            if us_idx:
                world_map.scatter([x[i] for i in us_idx],
                                  [y[i] for i in us_idx],
                                  s=[sizes[i] for i in us_idx],
                                  marker='o', color='#FF6A00',  # 亮橙
                                  edgecolor='white', linewidth=0.5,
                                  zorder=10, label='US Port')
                # 外国港口
                if fore_idx:
                    world_map.scatter([x[i] for i in fore_idx],
                                      [y[i] for i in fore_idx],
                                      s=[sizes[i] for i in fore_idx],
                                      marker='o', color='#00BFFF',  # 深天蓝
                                      edgecolor='white', linewidth=0.5,
                                      zorder=10, label='Foreign Port')

        # ---------- 画边（带 TEU→透明度映射） ----------
        edges = year_to_edges.get(time, [])
        widths = year_to_edge_width[time]  # 线宽 Series
        teus = edges['total_TEU']  # 原始 TEU
        # 透明度映射：TEU 最小→0.35，最大→1.0
        alphas = 0.5 + 0.5 * (teus - teus.min()) / (
                    teus.max() - teus.min()) if teus.max() != teus.min() else np.full_like(teus, 0.8, dtype=float)
        for index, row in edges.iterrows():
            lon1, lat1 = shift_lon(port_coords[row['from']][0]), port_coords[row['from']][1]
            lon2, lat2 = shift_lon(port_coords[row['to']][0]), port_coords[row['to']][1]
            x1, y1 = world_map(lon1, lat1)
            x2, y2 = world_map(lon2, lat2)
            w = widths[index]  # 取出该行对应的线宽
            alpha = alphas[index]

            # 从列表中随机选择一个元素
            random_list = [-20, 20]     # 贝塞尔曲线的弯曲程度
            delta = random.choice(random_list)
            (cx1, cy1), (cx2, cy2) = auto_control_points(x1, y1, x2, y2, delta)

            # 3. 生成曲线点
            bx, by = bezier([x1, y1], [cx1, cy1], [cx2, cy2], [x2, y2], num=100)
            world_map.plot(bx, by, linewidth=w, color='blue', zorder=5, alpha=alpha)

        ax.set_title(f'Top 30 TEU Links – {time}')
        ax.legend()
        fig.savefig(f'Figure/Season/TopTeuEdges/US_top30_edges_worldmap_{time}.svg',
                    dpi=300, bbox_inches='tight')
        # plt.show()
        plt.close(fig)  # 防止内存泄漏
    def auto_control_points(x1, y1, x2, y2, delta=30):
        """
        给定起点、终点，返回自动生成的一组三次贝塞尔控制点
        delta : 偏移像素，>0 向上弯，<0 向下弯
        """
        t = 1 / 3
        # 1/3 处
        p1x = x1 + t * (x2 - x1)
        p1y = y1 + t * (y2 - y1)
        # 2/3 处
        p2x = x1 + 2 * t * (x2 - x1)
        p2y = y1 + 2 * t * (y2 - y1)
        # 垂直偏移
        dx, dy = x2 - x1, y2 - y1
        lenAB = np.hypot(dx, dy)
        nx, ny = -dy / lenAB, dx / lenAB
        c1x = p1x + delta * nx
        c1y = p1y + delta * ny
        c2x = p2x + delta * nx
        c2y = p2y + delta * ny
        return (c1x, c1y), (c2x, c2y)
    def shift_lon(lon):
        """把经度压到 [-180,180]，解决跨中央经线问题"""
        return lon - 360 if lon > 70 else lon
    def bezier(p0, p1, p2, p3, num=100):
        """
        三阶贝塞尔插值
        :param p0:
        :param p1:
        :param p2:
        :param p3:
        :param num:
        :return:
        """
        t = np.linspace(0, 1, num)
        b = lambda i, t: comb(3, i) * (t ** i) * ((1 - t) ** (3 - i))
        pts = (np.outer(b(0, t), p0) + np.outer(b(1, t), p1) +
               np.outer(b(2, t), p2) + np.outer(b(3, t), p3))
        return pts[:, 0], pts[:, 1]
        # 1. 读 Top10 边


    top30_edges = pd.read_csv('InputData/US_top_edges_by_TEU.csv')
    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(info["longitude"]), float(info["latitude"]))
        for node, info in Port_Data.items()
        if "longitude" in info and "latitude" in info
    }

    # 按年份分组，提前建好 {year: set_of_ports} 和 {year: edges}
    year_to_ports = {}
    year_to_edges = {}

    # 预先算好每年「边」和「节点」的 TEU 比例
    year_to_edge_width = {}  # {year: Series(index=原始行号, 值=线宽)}
    year_to_node_size = {}  # {year: Series(index=港口名, 值=点大小)}

    base_lw = 0.5  # 最细线宽
    max_lw = 3  # 最粗线宽
    base_sz = 20  # 最小点
    max_sz = 200  # 最大点

    for season, group in top30_edges.groupby('time'):  # 按照time分成若干份DataFrame
        # 港口和连接
        ports = set(group['from']).union(set(group['to']))
        year_to_ports[season] = {p for p in ports if p in port_coords}
        year_to_edges[season] = group[
            (group['from'].isin(port_coords)) & (group['to'].isin(port_coords))
            ]

        # 节点和连接的大小
        # 1. 边宽：按 TEU 占比线性映射
        teu = group['total_TEU']
        share = (teu - teu.min()) / (teu.max() - teu.min()) if teu.max() != teu.min() else 0
        year_to_edge_width[season] = base_lw + share * (max_lw - base_lw)

        # 2. 节点大小：把每条边的 TEU 累加到两端港口
        node_teus = {}
        for _, row in group.iterrows():
            for node in (row['from'], row['to']):
                node_teus[node] = node_teus.get(node, 0) + row['total_TEU']
        # 同样归一化
        if node_teus:
            max_t = max(node_teus.values())
            min_t = min(node_teus.values())
            for n in node_teus:
                sh = (node_teus[n] - min_t) / (max_t - min_t) if max_t != min_t else 0
                node_teus[n] = base_sz + sh * (max_sz - base_sz)
        year_to_node_size[season] = node_teus

    # 主循环（支持多年）
    for year in range(2017, 2022):
        for season in ['Spring','Summer','Autumn','Winter']:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            draw_year(f"{year}_{season}")
def write_adjlist_attr(G, path, attr='volumeTEU', encoding='utf-8'):
    """
    将 DiGraph 导出成邻接表
    """
    path = pathlib.Path(path)
    with path.open('w', encoding=encoding) as f:
        f.write('source,target,weight\n')                       # 1. 属性声明
        for u, v, d in G.edges(data=True):
            f.write(f'{u},{v},{d.get(attr, 0)}\n')              # 2. 源 目标 值
def write_US_TEU_change_value():
    """
    保存美国2017和2021的港口TEU变化量
    :return:
    """
    DiGraph_2017 = nx.read_graphml('../Data/2017/US/US2017_Digraph.graphml')
    DiGraph_2021 = nx.read_graphml('../Data/2021/US/US2021_Digraph.graphml')

    US_TEU_change_value = {}        # 美国的节点TEU变化的量
    for node, attr in DiGraph_2017.nodes(data=True):
        if attr.get("Country", None) == "United States":
            if DiGraph_2021.has_node(node):
                # 2017年 2021年 都有的
                US_TEU_change_value[node] = DiGraph_2021.nodes[node]["total_TEU"] - DiGraph_2017.nodes[node]["total_TEU"]
            else:
                # 2017年有的  2021年没有的
                US_TEU_change_value[node] = - DiGraph_2017.nodes[node]["total_TEU"]
    for node, attr in DiGraph_2021.nodes(data=True):
        if attr.get("Country", None) == "United States" and not DiGraph_2017.has_node(node):
            # 2017年没有的  2021年有的
            US_TEU_change_value[node] = DiGraph_2021.nodes[node]["total_TEU"]
    pathlib.Path('Figure/US_TEU_change_value.json').write_text(json.dumps(US_TEU_change_value, indent=2))
def draw_US_TEU_change_value():
    """
    画出美国2017和2021的港口TEU变化量
    :return:
    """
    delta_file = 'Figure/US_TEU_change_value.json'
    US_TEU_change_value = json.loads(pathlib.Path(delta_file).read_text())

    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(d["longitude"]), float(d["latitude"]))
        for node, d in Port_Data.items()
        if "longitude" in d and "latitude" in d
    }

    # 1. 画布（你的原代码）
    fig, ax = plt.subplots(figsize=(10, 7))
    world_map = Basemap(resolution='l', projection='cyl', lon_0=-100, ax=ax)
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    # 2. 只画美国港口（颜色+大小）
    vals = np.array(list(US_TEU_change_value.values()))
    sizes = minmax_scale(np.abs(vals),feature_range=(50, 800))  # 节点面积范围
    colors = ['#FF4E50' if v > 0 else '#1B1B1B' for v in vals]

    #region只画top10
    # N = 10  # 可调        只画变化量前十的港口
    # top_nodes = nlargest(N, US_TEU_change_value.items(), key=lambda item: abs(item[1]))
    # for node, delta in top_nodes:
    #     if node not in port_coords:  # 跳过无坐标的孤立节点
    #         continue
    #     lon, lat = port_coords[node]
    #     x, y = world_map(lon, lat)
    #     idx = list(US_TEU_change_value.keys()).index(node)  # 原索引不变
    #     world_map.scatter(x, y, s=sizes[idx],
    #                       c=colors[idx],
    #                       edgecolors='white', linewidths=0.5, zorder=10)
    #endregion

    # 只画 ΔTEU > 0 或则 < 0 的所有美国港口
    for node, delta in US_TEU_change_value.items():
        if delta < 0:  # 负增长或零变化，跳过
            continue
        if node not in port_coords:  # 无坐标，跳过
            continue
        lon, lat = port_coords[node]
        x, y = world_map(lon, lat)
        idx = list(US_TEU_change_value.keys()).index(node)
        world_map.scatter(x, y, s=sizes[idx],
                          c=colors[idx],  # 正增长颜色（红）
                          edgecolors='white', linewidths=0.5, zorder=10)
    # 3. 图例 & 保存
    ax.scatter([], [], c='#FF4E50', s=200, label='TEU increase')
    ax.scatter([], [], c='#1B1B1B', s=200, label='TEU decrease')



    ax.legend(loc='lower left')
    plt.title('US Port TEU Change 2017→2021', fontsize=14, pad=10)
    fig.savefig('Figure/US_TEU_change_map_1.png', dpi=300, bbox_inches='tight')
    plt.show()
def write_US_BC_change_value():
    # 读取图数据
    DiGraph_2017 = nx.read_graphml('../Data/2017/US/US2017_Digraph.graphml')
    DiGraph_2021 = nx.read_graphml('../Data/2021/US/US2021_Digraph.graphml')

    # 计算介数中心性
    betweenness_2017 = nx.betweenness_centrality(DiGraph_2017)
    betweenness_2021 = nx.betweenness_centrality(DiGraph_2021)

    # 计算介数中心性的变化
    betweenness_change = {}
    for node in set(betweenness_2017.keys()) | set(betweenness_2021.keys()):
        if node in betweenness_2017 and node in betweenness_2021:
            betweenness_change[node] = betweenness_2021[node] - betweenness_2017[node]
        elif node in betweenness_2017:
            betweenness_change[node] = -betweenness_2017[node]
        else:
            betweenness_change[node] = betweenness_2021[node]

    # 找出变化最大的几个节点
    N = 10  # 你可以根据需要修改这个数字
    top_nodes = sorted(betweenness_change.items(), key=lambda item: abs(item[1]), reverse=True)[:N]

    # 保存结果
    pathlib.Path('Figure/US_BC_change_value.json').write_text(json.dumps(dict(top_nodes), indent=2))
def draw_US_BC_change_value():

    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(d["longitude"]), float(d["latitude"]))
        for node, d in Port_Data.items()
        if "longitude" in d and "latitude" in d
    }
    delta_file = 'Figure/US_BC_change_value.json'
    US_Betweenness_change_value = json.loads(pathlib.Path(delta_file).read_text())
    # 画布
    fig, ax = plt.subplots(figsize=(10, 7))
    world_map = Basemap(resolution='l', projection='cyl', lon_0=-100, ax=ax)
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()


    # 只画美国港口（颜色+大小）
    vals = np.array(list(US_Betweenness_change_value.values()))
    sizes = minmax_scale(np.abs(vals),feature_range=(50, 800))  # 节点面积范围
    colors = ['#FF4E50' if v > 0 else '#1B1B1B' for v in vals]

    N = 10  # 可调        只画变化量前十的港口
    top_nodes = nlargest(N, US_Betweenness_change_value.items(), key=lambda item: abs(item[1]))
    for node, delta in top_nodes:
        if node not in port_coords:  # 跳过无坐标的孤立节点
            continue
        lon, lat = port_coords[node]
        x, y = world_map(lon, lat)
        idx = list(US_Betweenness_change_value.keys()).index(node)  # 原索引不变
        world_map.scatter(x, y, s=sizes[idx],
                          c=colors[idx],
                          edgecolors='white', linewidths=0.5, zorder=10)
        # 在循环里
        dx = 6
        dy = 4
        x_text, y_text = world_map(lon + dx, lat - dy)
        ax.text(x_text, y_text, node, color='white', fontsize=8, ha='center', va='center',
                path_effects=[patheffects.withStroke(linewidth=2, foreground='black')])

    # 图例 & 保存
    ax.scatter([], [], c='#FF4E50', s=200, label='Betweenness increase')
    ax.scatter([], [], c='#1B1B1B', s=200, label='Betweenness decrease')
    ax.legend(loc='lower left')
    plt.title('Port Betweenness Change 2017→2021', fontsize=14, pad=10)
    fig.savefig('Figure/Betweenness_change_map.png', dpi=300, bbox_inches='tight')
    plt.show()
def draw_US_top5_port_TEU_change():
    """
    美国TEU top5港口的TEU随时间变化的趋势图
    """

    # 初始化存储每个港口每年的TEU值
    top_teu_nodes_teu_over_years = {}

    # 定义年份范围
    years = range(2017, 2022)

    # 遍历每个年份
    for year in years:
        file_path = f'../Data/{year}/US/US{year}_Digraph.graphml'
        if not os.path.exists(file_path):
            print(f'⚠️ 文件不存在: {file_path}')
            continue

        # 读取图
        DiGraph = nx.read_graphml(file_path)

        # 获取图中所有美国节点的TEU值
        teu_values = {node: data['total_TEU'] for node, data in DiGraph.nodes(data=True) if
                      data.get("Country") == "United States"}

        # 找出TEU最大的5个节点
        top_teu_nodes = heapq.nlargest(5, teu_values, key=teu_values.get)

        # 更新字典，记录每个节点每年的TEU
        for node in top_teu_nodes:
            if node not in top_teu_nodes_teu_over_years:
                top_teu_nodes_teu_over_years[node] = []
            top_teu_nodes_teu_over_years[node].append(teu_values[node])

    # 绘制Top 5 港口的TEU变化图
    fig = plt.figure(figsize=(12, 8))
    markers = ['o', 's', '^', 'D', 'x']  # 不同的形状
    colors = ['b', 'g', 'r', 'c', 'm']  # 不同的颜色

    # 准备绘图数据
    for i, node in enumerate(top_teu_nodes):
        teu_values = top_teu_nodes_teu_over_years[node]
        plt.plot(years, teu_values, marker=markers[i % len(markers)], color=colors[i % len(colors)], label=node)

    plt.title('Top 5 US Ports TEU Over Years')
    plt.xlabel('Year')
    plt.ylabel('Total TEU')
    plt.legend()
    plt.box(True)  # 去除边框
    plt.xticks(years)  # 设置横坐标刻度

    fig.savefig('Figure/US_top5_port_TEU_change.png', dpi=300, bbox_inches='tight')
    plt.show()
#endregion

#region Node Centrality
def write_US_port_centrality():
    """
    每一年美国港口的中心性指标json文件
    包括：   'degree_in',
            'degree_out',
            'degree_total',
            'teu_in',
            'teu_out',
            'teu_total',
            'bc_unweighted',
            'bc_weighted',
            'cc_unweighted'
    :return:
    """
    result = {}
    years = range(2017, 2022)
    for year in years:
        G = nx.read_graphml(f'../Data/{year}/US/US{year}_Digraph.graphml')
        metrics = {}

        bc_unweighted = nx.betweenness_centrality(G)
        bc = nx.betweenness_centrality(G, weight='volumeTEU')
        cc_unweighted = nx.closeness_centrality(G)

        for node, attr in G.nodes(data=True):
            if attr.get('Country') != 'United States':
                continue
            deg_in = G.in_degree(node)
            deg_out = G.out_degree(node)
            deg_total = G.weighted_degree(node)
            teu_in = G.nodes[node]['in_TEU']
            teu_out = G.nodes[node]['out_TEU']
            teu_total = G.nodes[node]['total_TEU']
            metrics[node] = {
                'degree_in': deg_in,
                'degree_out': deg_out,
                'degree_total': deg_total,
                'teu_in': teu_in,
                'teu_out': teu_out,
                'teu_total': teu_total,
                'bc_unweighted': bc_unweighted[node],
                'bc_weighted': bc[node],
                'cc_unweighted': cc_unweighted[node]
            }
        result[year] = metrics
    # 3. 保存 JSON
    out_file = 'Figure/US_port_centrality.json'
    pathlib.Path(out_file).write_text(json.dumps(result, indent=2))
    print(f'✅ 已保存 → {out_file}')
#endregion


# 把所有的度分布图都放在一起
# 节点中信心指标全部列表



#regionMain
# structure_metrics = []
# years = range(2017, 2022)
# seasons = ['Spring','Summer','Autumn','Winter']
# for year in years:
#     for season in seasons:
#         if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
#             continue
#         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
#         if not os.path.exists(file_path):
#             print(f'⚠️ 文件不存在: {file_path}')
#             continue
#         DiGraph = nx.read_graphml(file_path)
#         G = nx.Graph(DiGraph)
#
#         # G_null = G.copy()
#         # nx.double_edge_swap(G_null, nswap=20000, max_tries=100000)
#         # G_null.remove_edges_from(nx.selfloop_edges(G_null))
#
#         result_year = all_in_one(G, year, season)
#         structure_metrics.append(result_year)
#         print(f"{year} is already down!")
#
# # 保存成csv
# df = pd.DataFrame(structure_metrics)
# df.to_csv(f'Figure/all_in_one_Digraph.csv', index=False)
#endregion

def physical_network_layer():
    """
    考虑无向无权的拓扑网络  计算dc bc cc
    :return:
    """
    dc_record = {}
    bc_record = {}
    cc_record = {}
    core_number_record = {}
    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            time = f"{year}_{season}"
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            DiGraph = nx.read_graphml(file_path)
            G = nx.Graph(DiGraph)

            dc_dict = nx.degree_centrality(G)
            bc_dict = nx.betweenness_centrality(G)
            cc_dict = nx.closeness_centrality(G)
            dc_record[time] = dc_dict
            bc_record[time] = bc_dict
            cc_record[time] = cc_dict
            core_number_record[time] = nx.core_number(G)

    pathlib.Path('InputData/ports_degree_centrality.json').write_text(json.dumps(dc_record, indent=2))
    pathlib.Path('InputData/ports_betweenness_centrality.json').write_text(json.dumps(bc_record, indent=2))
    pathlib.Path('InputData/ports_closeness_centrality.json').write_text(json.dumps(cc_record, indent=2))
    pathlib.Path('InputData/ports_core_number_centrality.json').write_text(json.dumps(record, indent=2))

def freight_traffic_network_layer():
    """
    考虑一个DiGraph网络  权重为TEU
    :return:
    """
    weighted_dc_record = {}
    weighted_bc_record = {}
    weighted_ec_record = {}

    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            time = f"{year}_{season}"
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            DiGraph = nx.read_graphml(file_path)

            N = DiGraph.number_of_nodes()
            weighted_degree = dict(DiGraph.degree(weight='volumeTEU'))
            weighted_in_degree = dict(DiGraph.in_degree(weight='volumeTEU'))
            weighted_out_degree = dict(DiGraph.out_degree(weight='volumeTEU'))

            dc = {node: d / (N - 1) for node, d in weighted_degree.items()}
            in_dc = {node: d / (N - 1) for node, d in weighted_in_degree.items()}
            out_dc = {node: d / (N - 1) for node, d in weighted_out_degree.items()}

            # weighted node centrality
            node_dc = {}
            for node in DiGraph.nodes():
                node_dc[node] = {
                    'dc': dc[node],
                    'in_dc': in_dc[node],
                    'out_dc': out_dc[node]
                }
            weighted_dc_record[time] = node_dc

            # weighted betweenness centrality
            weighted_bc_record[time] = nx.betweenness_centrality(DiGraph, weight='volumeTEU')

            # # weighted eigen centrality  加权特征向量中心性 暂时计算不了  迭代不出来解
            # weighted_ec_record = nx.eigenvector_centrality(DiGraph, weight='volumeTEU', max_iter=100000, tol= 1e-5)

    pathlib.Path('InputData/ports_weighted_degree_centrality.json').write_text(json.dumps(weighted_dc_record, indent=2))
    pathlib.Path('InputData/ports_weighted_betweenness_centrality.json').write_text(json.dumps(weighted_bc_record, indent=2))
    # pathlib.Path('InputData/ports_weighted_eigenvector_centrality.json').write_text(json.dumps(weighted_ec_record, indent=2))
freight_traffic_network_layer()
# record = {}
# years = range(2017, 2022)
# seasons = ['Spring','Summer','Autumn','Winter']
# for year in years:
#     for season in seasons:
#         if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
#             continue
#         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
#         time = f"{year}_{season}"
#         if not os.path.exists(file_path):
#             print(f'⚠️ 文件不存在: {file_path}')
#             continue
#         DiGraph = nx.read_graphml(file_path)
#         G = nx.Graph(DiGraph)
#         record[time] = nx.core_number(G)
#
# pathlib.Path('InputData/ports_core_number_centrality.json').write_text(json.dumps(record, indent=2))
