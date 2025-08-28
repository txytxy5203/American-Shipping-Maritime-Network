import os
import numpy as np
import networkx as nx
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
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
def calculate_graph_entrogy():

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
# ---------- 参数 ----------
draw_degree_of_connection_of_all_countries_to_the_US()
# all_rows = []  # 用于收集所有年份的 TOP10 结果
# years = list(range(2017, 2022))
# for year in years:
#     file_path = f'../Data/{year}/US/US{year}.graphml'
#     if not os.path.exists(file_path):
#         print(f'⚠️ 文件不存在: {file_path}')
#         continue
#     Multi_G = nx.read_graphml(file_path)
#     get_numbers_of_connect_countries_to_US(Multi_G, year)
#     print("---------------")
# result = pd.concat(all_rows, ignore_index=True)
# result.to_csv('Figure/centrality_top10.csv', index=False)
# print('✅ 已保存 centrality_top10.csv')
# print(result.head(15))



# 把 Macau HongKong Taiwan 改成China
# regions = {'Macau', 'Hong Kong', 'Taiwan'}
# for year in years:
#     path = f'../Data/{year}/US/US{year}.graphml'
#     if not os.path.exists(path):
#         print(f'⚠️ 文件不存在: {path}')
#         continue
#
#     G = nx.read_graphml(path)
#
#     # 就地修改
#     for n in G.nodes:
#         if G.nodes[n].get('Country') in regions:
#             G.nodes[n]['Country'] = 'China'
#
#     # 直接覆盖原文件
#     nx.write_graphml(G, path)
#     print(f'✅ 已覆盖 {path}')