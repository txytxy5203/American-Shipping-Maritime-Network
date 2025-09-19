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

        # 当年 Top
        top = pd.DataFrame(data).sort_values('total_TEU', ascending=False).head(30)
        all_rows.append(top)
    df = pd.concat(all_rows, ignore_index=True)
    df.to_csv(f'{OUTPUT_DIR}/US_top10_node_pairs_by_TEU_year.csv', index=False)
def draw_top10_TEU_edges_map():
    # 绘图函数（只建一次地图，复用）
    # def draw_year(year):
    #     fig, ax = plt.subplots(figsize=(8, 5))
    #     world_map = Basemap(resolution='l', projection='cyl', lon_0=-100, ax=ax)
    #     world_map.drawmapboundary(fill_color='#D0CFD4')
    #     world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    #     world_map.drawcoastlines()
    #
    #     # ---------- 画港口 ----------
    #     ports = year_to_ports.get(year, set())
    #     if ports:
    #         lon = [shift_lon(port_coords[p][0]) for p in ports]
    #         lat = [port_coords[p][1] for p in ports]
    #         x, y = world_map(lon, lat)
    #         # 按 TEU 总和决定大小
    #         sizes = [year_to_node_size[year].get(p, base_sz) for p in ports]
    #         world_map.scatter(x, y, s=sizes, marker='o', color='red', zorder=10, label='Port')
    #
    #     # ---------- 画边 ----------
    #     edges = year_to_edges.get(year, [])
    #     widths = year_to_edge_width[year]  # Series，行号与 edges 一致
    #     for index, row in edges.iterrows():
    #         lon1, lat1 = shift_lon(port_coords[row['from']][0]), port_coords[row['from']][1]
    #         lon2, lat2 = shift_lon(port_coords[row['to']][0]), port_coords[row['to']][1]
    #         x1, y1 = world_map(lon1, lat1)
    #         x2, y2 = world_map(lon2, lat2)
    #         w = widths[index]  # 取出该行对应的线宽
    #
    #         # 从列表中随机选择一个元素
    #         random_list = [-20, 20]
    #         delta = random.choice(random_list)
    #         (cx1, cy1), (cx2, cy2) = auto_control_points(x1, y1, x2, y2, delta)
    #
    #         # 3. 生成曲线点
    #         bx, by = bezier([x1, y1], [cx1, cy1], [cx2, cy2], [x2, y2], num=100)
    #         world_map.plot(bx, by, linewidth=w, color='blue', zorder=5)
    #
    #     ax.set_title(f'Top 30 TEU Links – {year}')
    #     ax.legend()
    #     fig.savefig(f'Figure/Top10/US_top30_edges_worldmap_{year}.png',
    #                 dpi=300, bbox_inches='tight')
    #     plt.show()
    #     plt.close(fig)  # 防止内存泄漏
    def draw_year(year):
        # ---------------- 1. 画布与投影 ----------------
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['mathtext.fontset'] = 'stix'
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.Robinson(central_longitude=-100))
        ax.set_global()

        # 高分辨率自然地表 + 海岸线
        ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                                    facecolor=sns.color_palette("mako", as_cmap=True)(0.15)),
                       zorder=1)
        ax.add_feature(cfeature.NaturalEarthFeature('physical', 'ocean', '50m',
                                                    facecolor='#0b1b2b'), zorder=1)
        ax.coastlines('50m', color='#ffffff', linewidth=0.3, zorder=2)

        # ---------------- 2. 节点大小与颜色 ----------------
        ports = year_to_ports.get(year, set())
        if ports:
            lon = [shift_lon(port_coords[p][0]) for p in ports]
            lat = [port_coords[p][1] for p in ports]
            # 面积 ∝ TEU（归一化）
            sizes = np.array([year_to_node_size[year].get(p, base_sz) for p in ports])
            sizes = minmax_scale(sizes, feature_range=(base_sz, max_sz)) ** 1.5
            # 颜色 ∝ TEU
            colors = minmax_scale(sizes)
            cmap = sns.color_palette("flare", as_cmap=True)

            ax.scatter(lon, lat, s=sizes, c=colors, cmap=cmap,
                       edgecolors='white', linewidths=0.5,
                       transform=ccrs.PlateCarree(), zorder=10, label='Port')

        # ---------------- 3. 贝塞尔曲线边 + 颜色映射 ----------------
        edges = year_to_edges.get(year, [])
        widths = year_to_edge_width[year]
        # 边颜色映射（蓝→橙）
        edge_colors = minmax_scale(widths, feature_range=(0, 1))
        cmap_edge = sns.color_palette("blend:blue,orange", as_cmap=True)

        for idx, row in edges.iterrows():
            lon1 = shift_lon(port_coords[row['from']][0])
            lat1 = port_coords[row['from']][1]
            lon2 = shift_lon(port_coords[row['to']][0])
            lat2 = port_coords[row['to']][1]
            w = widths[idx]

            # 画布坐标（Robinson 投影）
            x1, y1 = ax.projection.transform_point(lon1, lat1, ccrs.PlateCarree())
            x2, y2 = ax.projection.transform_point(lon2, lat2, ccrs.PlateCarree())

            # 贝塞尔
            delta = -80 if {row['from'], row['to']} in \
                           [{'Shanghai', 'Los Angeles'}, {'Hong Kong', 'Long Beach'}] else 80
            (cx1, cy1), (cx2, cy2) = smooth_control_points(x1, y1, x2, y2, delta)
            bx, by = bezier([x1, y1], [cx1, cy1], [cx2, cy2], [x2, y2], num=150)

            # 颜色随 TEU
            color = cmap_edge(edge_colors[idx])
            ax.plot(bx, by, linewidth=w, color=color,
                    alpha=0.85, solid_capstyle='round', zorder=4)

        # ---------------- 4. 标题 & 出图 ----------------
        plt.title(f'Top 30 TEU Links – {year}', fontsize=14, fontweight='bold', pad=15)
        fig.savefig(f'Figure/Top10/US_top30_edges_worldmap_{year}.png',
                    dpi=600, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.show()
        plt.close(fig)
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
    # 三阶贝塞尔插值
    def bezier(p0, p1, p2, p3, num=100):
        t = np.linspace(0, 1, num)
        b = lambda i, t: comb(3, i) * (t ** i) * ((1 - t) ** (3 - i))
        pts = (np.outer(b(0, t), p0) + np.outer(b(1, t), p1) +
               np.outer(b(2, t), p2) + np.outer(b(3, t), p3))
        return pts[:, 0], pts[:, 1]
        # 1. 读 Top10 边



    top30_edges = pd.read_csv('Figure/US_top10_node_pairs_by_TEU_year.csv')
    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(d["longitude"]), float(d["latitude"]))
        for node, d in Port_Data.items()
        if "longitude" in d and "latitude" in d
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
    max_sz = 100  # 最大点

    for year, group in top30_edges.groupby('year'):  # 按照year分成若干份DataFrame
        # 港口和连接
        ports = set(group['from']).union(set(group['to']))
        year_to_ports[year] = {p for p in ports if p in port_coords}
        year_to_edges[year] = group[
            (group['from'].isin(port_coords)) & (group['to'].isin(port_coords))
            ]

        # 节点和连接的大小
        # 1. 边宽：按 TEU 占比线性映射
        teu = group['total_TEU']
        share = (teu - teu.min()) / (teu.max() - teu.min()) if teu.max() != teu.min() else 0
        year_to_edge_width[year] = base_lw + share * (max_lw - base_lw)

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
        year_to_node_size[year] = node_teus

    # 主循环（支持多年）
    for year in range(2017, 2018):  # 现在只 2017，但你可以扩到 2017–2023
        draw_year(year)


draw_top10_TEU_edges_map()
#regionMain
# structure_metrics = []
# years = range(2017, 2022)
#
# for year in years:
#     file_path = f'../Data/{year}/US/US{year}.graphml'
#     if not os.path.exists(file_path):
#         print(f'⚠️ 文件不存在: {file_path}')
#         continue
#     Multi_G = nx.read_graphml(file_path)
#     G = nx.Graph(Multi_G)
#
#
#     G_null = G.copy()
#     nx.double_edge_swap(G_null, nswap=20000, max_tries=100000)
#     G_null.remove_edges_from(nx.selfloop_edges(G_null))
#
#     result_year = all_in_one(G_null, year)
#     structure_metrics.append(result_year)
#     print(f"{year} is already down!")
#
# # 保存成csv
# df = pd.DataFrame(structure_metrics)
# df.to_csv(f'Figure/all_in_one_zero_model.csv')
#endregion

#region 弃用
# def draw_top10_TEU_edges_map():
#     # 1. 读 Top10 边
#     top10_edges = pd.read_csv('Figure/US_top10_node_pairs_by_TEU_year.csv')
#
#     # 2. 读港口坐标
#     Port_Data = ConstructNetwork.Read_Port_Data()
#     port_coords = {
#         node: (float(Port_Data[node]["longitude"]),
#                float(Port_Data[node]["latitude"]))
#         for node in Port_Data
#         if "longitude" in Port_Data[node] and "latitude" in Port_Data[node]
#     }
#
#     years = range(2017, 2018)
#     for year in years:
#         curr_year_port = set()
#         for idx, row in top10_edges.iterrows():
#             from_port = row['from']
#             to_port   = row['to']
#             teu       = row['total_TEU']
#             y = row['year']
#             if y == year:
#                 curr_year_port.add(from_port)
#                 curr_year_port.add(to_port)
#
#
#         # ------------ 3  绘制世界地图 ------------
#         world_map = Basemap(resolution='l')
#
#         world_map.drawmapboundary(fill_color='#D0CFD4')
#         world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
#         world_map.drawcoastlines()
#
#         # ------------ 4  画港口 ------------
#         port_lon = [port_coords[node][0] for node in curr_year_port]
#         port_lat = [port_coords[node][1] for node in curr_year_port]
#         px, py = world_map(port_lon, port_lat)
#         world_map.scatter(px, py, marker='o', color='red', zorder=10, label='Port')
#
#         # ------------ 5  画 Top10 边 ------------
#         for _, row in top10_edges.iterrows():
#             from_port, to_port = row['from'], row['to']
#             if from_port in port_coords and to_port in port_coords:
#                 x1, y1 = world_map(port_coords[from_port][0], port_coords[from_port][1])
#                 x2, y2 = world_map(port_coords[to_port][0], port_coords[to_port][1])
#                 world_map.plot([x1, x2], [y1, y2],
#                                linewidth=2,
#                                color='blue',
#                                zorder=5)
#
#         # ------------ 6  保存并展示 ------------
#         plt.title('Top 10 TEU Links on World Map')
#         plt.legend()
#         plt.savefig(f'Figure/Top10/US_top10_edges_worldmap_{year}.png', dpi=300, bbox_inches='tight')
#         plt.show()