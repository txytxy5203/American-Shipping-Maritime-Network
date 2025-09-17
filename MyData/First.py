import sys
sys.path.append('../Algorithm')
import os
import networkx as nx
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import geopandas as gpd
from shapely.geometry import Point, LineString
from geopy.distance import great_circle
from geopy.point import Point as GeopyPoint
# from geosphere import intermediate_points  # 用于生成大圆路径点
from Algorithm.ConstructNetwork import ConstructNetwork
from Algorithm.Read import Read
from collections import Counter

from matplotlib.ticker import ScalarFormatter
from scipy.stats import entropy

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

#region Network Structure
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


def calculate_US_top10_node_pairs_by_TEU_year():
    YEARS = range(2017, 2022)
    DATA_DIR = '../Data'
    OUTPUT_DIR = 'Figure'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_rows = []

    for y in YEARS:
        G = nx.read_graphml(f'{DATA_DIR}/{y}/US/US{y}.graphml')

        # 用 MultiGraph 方便累加
        MG = nx.MultiGraph(G)

        # 按节点对累加 TEU
        flows = {}
        for u, v, d in MG.edges(data=True):
            pair = tuple(sorted([u, v]))  # 无向，排序去重
            flows[pair] = flows.get(pair, 0) + float(d.get('volumeTEU', 0))

        # 转成 DataFrame
        data = [{'year': y, 'from': pair[0], 'to': pair[1], 'total_TEU': teu}
                for pair, teu in flows.items()]

        # 当年 Top10
        top10 = pd.DataFrame(data).sort_values('total_TEU', ascending=False).head(10)
        all_rows.append(top10)

    df = pd.concat(all_rows, ignore_index=True)
    df.to_csv(f'{OUTPUT_DIR}/US_top10_node_pairs_by_TEU_year.csv', index=False)
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

#region Node Centrality
def top10_df(Multi_G, year):
    G = nx.Graph(Multi_G)  # 无向加权简单图
    # 度中心性
    deg = nx.degree_centrality(G)
    # 介数中心性
    betw = nx.betweenness_centrality(Multi_G)
    # 接近中心性
    close = nx.closeness_centrality(Multi_G)
    # PageRank
    pr = nx.pagerank(Multi_G)

    # 强度   1.TEU作为强度   2.交易次数作为强度
    # 1.TEU
    total_TEU_strength   = {}   # 所有邻边
    out_TEU_strength     = {}   # 仅起点
    in_TEU_strength      = {}   # 仅终点

    # 2.交易次数
    total_times_strength = {}
    out_times_strength = {}
    in_times_strength = {}
    for n in Multi_G.nodes:
        total_TEU_strength[n] = 0.
        out_TEU_strength[n]   = 0.
        in_TEU_strength[n]    = 0.

        total_times_strength[n] = 0.
        out_times_strength[n]   = 0.
        in_times_strength[n]    = 0.
    # 遍历所有多重边
    for u, v, key, data in Multi_G.edges(keys=True, data=True):
        # 1.TEU
        w = data.get('volumeTEU', 1.0)
        total_TEU_strength[u] += w
        total_TEU_strength[v] += w
        out_TEU_strength[u]   += w
        in_TEU_strength[v]    += w

        # 2.交易次数
        total_times_strength[u] += 1
        total_times_strength[v] += 1
        out_times_strength[u]   += 1
        in_times_strength[v]    += 1

    # ---------- 统一 DataFrame ----------
    df = pd.DataFrame({
        'year': year,
        'port': list(deg.keys()),
        'degree': list(deg.values()),
        'total_TEU_strength': [total_TEU_strength[n] for n in deg],
        'out_TEU_strength': [out_TEU_strength[n] for n in deg],
        'in_TEU_strength': [in_TEU_strength[n] for n in deg],
        'total_times_strength': [total_times_strength[n] for n in deg],
        'out_times_strength': [out_times_strength[n] for n in deg],
        'in_times_strength': [in_times_strength[n] for n in deg],
        'betweenness': list(betw.values()),
        'closeness': list(close.values()),
        'pagerank': list(pr.values())
    })

    # 对每种中心性取 TOP10
    top10_list = []
    cols = ['degree', 'total_TEU_strength', 'out_TEU_strength','in_TEU_strength',
            'total_times_strength', 'out_times_strength', 'in_times_strength',
            'betweenness', 'closeness', 'pagerank']
    for col in cols:
        top10 = (df[['year', 'port', col]]
                 .rename(columns={col: 'value'})
                 .assign(metric=col)
                 .sort_values('value', ascending=False)
                 .head(10))
        top10_list.append(top10)

    return pd.concat(top10_list, ignore_index=True)
def port_appearance_in_top10_across_centrality_metrics():
    # 1. 读入真实 top10 表（列：year, port, metric）
    df = pd.read_csv('Figure/centrality_top10.csv')

    # 2. 10 个真实指标列表（与你的列名完全一致）
    real_metrics = [
        'degree', 'total_TEU_strength', 'out_TEU_strength', 'in_TEU_strength',
        'total_times_strength', 'out_times_strength', 'in_times_strength',
        'betweenness', 'closeness', 'pagerank'
    ]

    # 3. 过滤 + 统计出现次数
    heatmap_df = (
        df[df['metric'].isin(real_metrics)]  # 只保留 10 个真指标
        .assign(count=1)  # 每行算 1 次出现
        .pivot_table(index='port', columns='year', values='count',
                     aggfunc='sum', fill_value=0)
    )

    # 4. 按出现总频次降序排列，方便阅读
    heatmap_df = heatmap_df.loc[
        heatmap_df.sum(axis=1).sort_values(ascending=False).index
    ]

    # 5. 画热力图
    plt.figure(figsize=(10, 6))
    sns.heatmap(
        heatmap_df,
        cmap='Blues',
        linewidths=.5,
        linecolor='gray',
        annot=True,
        fmt='g',
        cbar_kws={'label': 'Times in Top10'}
    )
    plt.title('Top10 Port Presence Across 10 Centrality Metrics (2017–2021)', fontsize=14, pad=15)
    plt.xlabel('Year')
    plt.ylabel('Port')
    plt.tight_layout()
    plt.savefig('Figure/real_port_top10_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 6. 导出频次汇总表（港口 × 总出现次数）
    freq_summary = (
        heatmap_df.sum(axis=1)
        .rename('total_times')
        .to_frame()
        .sort_values('total_times', ascending=False)
    )
    freq_summary.to_csv('real_port_top10_frequency.csv', index=True)
    print(freq_summary.head())
#endregion

def world_ports_map2():
    # 利用matplotlib内置函数生成贝塞尔曲线
    def draw_bezier_route(m, ax, start_lonlat, end_lonlat, control_factor=0.3, **kwargs):
        """
        使用matplotlib.path绘制贝塞尔曲线航线
        m: Basemap实例
        ax: 绘图轴对象
        start_lonlat: 起点经纬度 (lon, lat)
        end_lonlat: 终点经纬度 (lon, lat)
        control_factor: 控制点偏移因子（控制弯曲程度，0-1之间）
        """
        # 转换经纬度到投影坐标
        start_x, start_y = m(*start_lonlat)
        end_x, end_y = m(*end_lonlat)

        # 计算中间控制点（基于两点连线的垂直方向偏移）
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2

        # 计算垂直偏移方向
        dx = end_x - start_x
        dy = end_y - start_y
        offset_x = -dy * control_factor  # 垂直方向x偏移
        offset_y = dx * control_factor  # 垂直方向y偏移

        # 贝塞尔曲线的控制点
        control_x = mid_x + offset_x
        control_y = mid_y + offset_y

        # 定义贝塞尔曲线路径（Path对象支持贝塞尔曲线指令）
        # 路径指令：MOVETO -> CURVE3（二次贝塞尔曲线）-> LINETO
        vertices = [
            (start_x, start_y),  # 起点
            (control_x, control_y),  # 控制点
            (end_x, end_y)  # 终点
        ]
        codes = [
            Path.MOVETO,  # 移动到起点
            Path.CURVE3,  # 二次贝塞尔曲线到终点（使用控制点）
            Path.LINETO  # 确保终点连接
        ]

        # 创建路径并绘制
        path = Path(vertices, codes)
        patch = patches.PathPatch(path, **kwargs)
        ax.add_patch(patch)
        return patch

    # 1. 读 Top10 边
    edges = pd.read_csv('Figure/US_top10_node_pairs_by_TEU_year.csv')

    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(Port_Data[node]["longitude"]),
               float(Port_Data[node]["latitude"]))
        for node in Port_Data
        if "longitude" in Port_Data[node] and "latitude" in Port_Data[node]
    }

    # 3. 只保留 Top10 用到的港口
    needed_ports = set(edges['from']).union(set(edges['to']))
    coords = {p: port_coords[p] for p in needed_ports if p in port_coords}

    # 4. 创建地图
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)  # 获取轴对象用于添加曲线

    m = Basemap(projection='ortho',
                lat_0=90, lon_0=0,
                resolution='c')

    m.drawmapboundary(fill_color='#D0CFD4')
    m.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    m.drawcoastlines()
    m.drawcountries(linewidth=0.5, color='black')

    # 5. 画港口
    px, py = m([c[0] for c in coords.values()], [c[1] for c in coords.values()])
    m.scatter(px, py, marker='o', color='red', zorder=10, label='Top-10 Ports')

    # # 6. 用matplotlib内置函数画贝塞尔曲线航线
    # for _, row in edges.iterrows():
    #     u, v = row['from'], row['to']
    #     if u not in coords or v not in coords:
    #         continue
    #
    #     start_lonlat = coords[u]
    #     end_lonlat = coords[v]
    #
    #     # 调用封装好的贝塞尔曲线绘制函数
    #     draw_bezier_route(
    #         m, ax,
    #         start_lonlat,
    #         end_lonlat,
    #         control_factor=0.8,  # 调整弯曲程度（值越小越接近直线）
    #         linewidth=2,
    #         color='blue',
    #         zorder=5,
    #         fill=False  # 曲线不需要填充
    #     )
    #
    plt.title('Top 10 TEU Routes with Matplotlib Bezier Curves')
    plt.legend()
    plt.savefig('Figure/US_top10_bezier_routes_matplotlib.png', dpi=300, bbox_inches='tight')
    plt.show()



# 处理过的函数
def all_in_one(g, year) -> dict:
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
        "year": year,
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
def draw_total_TEU():
    """
    画出总的TEU变化图   有点丑下次记得修改
    :return:
    """
    YEARS = range(2017, 2022)  # 一年一个单位
    DATA_DIR = '../Data'
    OUTPUT_DIR = 'Figure'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    records = []
    for y in YEARS:
        path = f'{DATA_DIR}/{y}/US/US{y}.graphml'
        if not os.path.exists(path):
            print(f'⚠️ 文件不存在: {path}')
            continue
        G = nx.read_graphml(path)
        total_teu = sum(float(d.get('volumeTEU', 0)) for _, _, d in G.edges(data=True))
        records.append({'year': y, 'total_TEU': total_teu})

    df = pd.DataFrame(records)
    df.to_csv(f'{OUTPUT_DIR}/US_total_TEU_year.csv', index=False)

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.set_style('whitegrid')
    sns.lineplot(data=df, x='year', y='total_TEU', marker='o', lw=2.5)

    # 1. 强制整年横坐标
    ax.set_xticks(list(YEARS))

    # 2. 纵轴刻度：2×10⁷、3×10⁷ …
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(7, 7))

    # 3. 其余不变
    plt.title('Total TEU Flow of U.S. Port Network (2017–2021)', fontsize=14)
    plt.xlabel('Year')
    plt.ylabel('Total TEU')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/US_total_TEU_year.png', dpi=300, bbox_inches='tight')

    plt.show()
def draw_top10_TEU_edges_map():
    # 1. 读 Top10 边
    edges = pd.read_csv('Figure/US_top10_node_pairs_by_TEU_year.csv')

    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(Port_Data[node]["longitude"]),
               float(Port_Data[node]["latitude"]))
        for node in Port_Data
        if "longitude" in Port_Data[node] and "latitude" in Port_Data[node]
    }

    # 3. 只保留 Top10 用到的港口
    needed_ports = set(edges['from']).union(set(edges['to']))
    coords = {p: port_coords[p] for p in needed_ports}

    # 4. 创建地图
    fig = plt.figure(figsize=(10, 6))

    m = Basemap(projection='ortho',
                lat_0=90, lon_0=0,  # 中心点为北极点，经度0°
                resolution='c')

    m.drawmapboundary(fill_color='#D0CFD4')
    m.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    m.drawcoastlines()
    m.drawcountries(linewidth=0.5, color='black')  # 绘制国家边界，设置线宽和颜色

    # 5. 画港口
    px, py = m([c[0] for c in coords.values()],
               [c[1] for c in coords.values()])
    m.scatter(px, py, marker='o', color='red', zorder=10, label='Top-10 Ports')

    # 6. 画 Top10 航线（大圆航线）
    for _, row in edges.iterrows():
        u, v = row['from'], row['to']
        lon1, lat1 = coords[u]
        lon2, lat2 = coords[v]

        # 大圆航线：将路径拆成 50 段，避免直线
        m.drawgreatcircle(lon1, lat1, lon2, lat2,
                          linewidth=2,
                          color='blue',
                          zorder=5)

    plt.title('Top 10 TEU Great-Circle Routes on World Map')
    plt.legend()
    plt.savefig('Figure/US_top10_links_worldmap.png', dpi=300, bbox_inches='tight')
    plt.show()


# Main
structure_metrics = []
years = range(2017, 2022)

for year in years:
    file_path = f'../Data/{year}/US/US{year}.graphml'
    if not os.path.exists(file_path):
        print(f'⚠️ 文件不存在: {file_path}')
        continue
    Multi_G = nx.read_graphml(file_path)
    G = nx.Graph(Multi_G)


    G_null = G.copy()
    nx.double_edge_swap(G_null, nswap=20000, max_tries=100000)
    G_null.remove_edges_from(nx.selfloop_edges(G_null))

    result_year = all_in_one(G_null, year)
    structure_metrics.append(result_year)
    print(f"{year} is already down!")

# 保存成csv
df = pd.DataFrame(structure_metrics)
df.to_csv(f'Figure/all_in_one_zero_model.csv')

