from collections import Counter
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import powerlaw
from networkx.algorithms.bipartite.centrality import betweenness_centrality, closeness_centrality

# 定义幂律函数
def power_law(x, a, b):
    return a * np.power(x, b)
def read_data():
    # Read the data
    path_to_data = 'C:/Users/Rong/Downloads/ca-GrQc/ca-GrQc.mtx'
    data = pd.read_csv(path_to_data, sep='\\s+', skiprows=2, header=None)
    data = data.astype(int)

    # Add edges
    g = nx.Graph()
    for index, row in data.iterrows():
        g.add_edge(row[0], row[1])
    return g
def draw_degree_frequency_distribution(g):

    N = g.number_of_nodes()
    degree_frequency_numbers = nx.degree_histogram(g)  # 度的频数
    # [0, 675, 789, 676, 428, 258, 205, 153, 140, 99, 92, 65, 45, 57, 38, 48, 25, 44, 20, 18, 28, 16, 12, ...]
    # print(len(nx.degree_histogram(G)))  # 82
    x_degree = list(range(len(degree_frequency_numbers)))  # 所有的度数 作为下面画图的x坐标

    # 删去 度为0的元素
    for i in sorted(x_degree, reverse=True):  # 注意这里要反向遍历 不然索引会出问题
        if degree_frequency_numbers[i] == 0:
            del degree_frequency_numbers[i]
            del x_degree[i]

    degree_frequency = [x / N for x in degree_frequency_numbers]  # 度的频率

    # 初始化幂律拟合对象
    fit = powerlaw.Fit(x_degree, xmin=min(x_degree))

    # 获取拟合参数
    alpha = fit.power_law.alpha
    x_min = fit.power_law.xmin

    # 绘制原始数据点
    plt.scatter(x_degree, degree_frequency, color='blue', label='Ports')

    # 绘制拟合得到的幂律分布曲线
    pdf = fit.power_law.pdf(x_degree)
    plt.plot(x_degree, pdf, color='red', linestyle='--', label=f'Fit $k^{{{-alpha:.3f}}}$')

    # 设置对数坐标轴
    plt.xscale("log")
    plt.yscale("log")

    # 设置坐标轴范围
    plt.xlim([min(x_degree) * 0.6, max(x_degree) * 1.7])  # 设置x轴范围为数据的最小值到最大值的1.1倍
    plt.ylim([min(degree_frequency) * 0.6, max(degree_frequency) * 1.7])  # 设置y轴范围为数据的最小值到最大值的1.1倍

    # 添加图例和标题
    plt.legend()
    plt.title("Degree Distribution")
    plt.xlabel("Degree")
    plt.ylabel("Degree Frequency")
    plt.show()
def draw_degree_frequency_cumulative_distribution(g):

    N = g.number_of_nodes()
    degree_frequency_numbers = nx.degree_histogram(g)  # 度的频数
    # [0, 675, 789, 676, 428, 258, 205, 153, 140, 99, 92, 65, 45, 57, 38, 48, 25, 44, 20, 18, 28, 16, 12, ...]
    # print(len(nx.degree_histogram(G)))  # 82
    x_degree = list(range(len(degree_frequency_numbers)))  # 所有的度数 作为下面画图的x坐标

    # 删去 度为0的元素
    for i in sorted(x_degree, reverse=True):  # 注意这里要反向遍历 不然索引会出问题
        if degree_frequency_numbers[i] == 0:
            del degree_frequency_numbers[i]
            del x_degree[i]

    degree_frequency = [x / N for x in degree_frequency_numbers]  # 度的频率

    # 累计度分布
    cumulative_degree_frequency = [1 - degree_frequency[0]]     # 累计度分布的第一个元素是1-degree_frequency[0]
    # 累计就这么算
    for i in degree_frequency[1:]:
        cumulative_degree_frequency.append(cumulative_degree_frequency[-1] - i)

    # 这里画图时 两个list的最后一个元素不要  最后一个累积的频率为0了 画图会出问题
    plt.scatter(x_degree[:-2], cumulative_degree_frequency[:-2], c='darkblue', label='Nodes')
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("K")
    plt.ylabel("P(K>k)")
    plt.title("Cumulative Degree Frequency Distribution")
    plt.legend()
    plt.show()
def draw_length_frequency_distribution(g):
    '''
    :param g: 传入图 graph
    计算两点之间的距离所占比例 的分布图

    '''
    lengths_all_pairs = dict(nx.all_pairs_shortest_path_length(g))
    # 列子
    # {0: {0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 10: 1},
    #  1: {11: 1, 12: 1, 13: 1, 17: 1, 19: 1, 21: 1, 31: 1, 30: 2, 9: 2},
    #  2: {0: 1, 2: 1, 3: 1, 7: 1, 13: 1, 17: 1, 19: 1, 21: 1, 30: 1}}
    lengths_value = []
    # 遍历 lengths_all_pairs
    for i in lengths_all_pairs.values():
        for j in i.values():
            lengths_value.append(j)

    # 使用 Counter 统计每个值的出现次数
    lengths_value_counts = Counter(lengths_value)
    del lengths_value_counts[0]  # 删去距离为0的
    lengths_value_counts = {key: value / 2 for key, value in lengths_value_counts.items()}  # 这里要除以2 因为上面计算了两次
    lengths_value_counts_rate = {key: value / sum(lengths_value_counts.values()) for key, value in
                                 lengths_value_counts.items()}

    plt.scatter(lengths_value_counts.keys(), lengths_value_counts_rate.values(), c='red', marker='s')
    plt.yscale("log")
    plt.xlabel("Length")
    plt.ylabel("P(L)")
    plt.title("Length Frequency Distribution")
    plt.show()
def draw_degree_cluster(g, is_mean=False):
    '''
    度 和 聚类系数 之间的关系图
    :param is_mean: 是否计算平均集聚系数
    :param g: 传入 图
    '''
    if is_mean:
        # 存放 度 和 聚类系数 之间的关系
        degree_cluster = {}
        for node in g:
            if g.weighted_degree(node) in degree_cluster.keys():
                degree_cluster[g.weighted_degree(node)] += nx.clustering(g, node)
            else:
                degree_cluster[g.weighted_degree(node)] = nx.clustering(g, node)

        degree_frequency_numbers = nx.degree_histogram(g)  # 度的频数
        degree_cluster = {key: value / degree_frequency_numbers[key] for key, value in degree_cluster.items()}
        # print(degree_cluster)
        plt.scatter(degree_cluster.keys(), degree_cluster.values(), marker='^', c='blue')
        plt.xlabel("K")
        plt.ylabel("C(K)")
        plt.yscale("log")
        plt.title("Degree——C(k)")
        plt.show()
    else:
        degree = []
        cluster = []
        for node in g:
            degree.append(g.weighted_degree[node])
            cluster.append(nx.clustering(g, node))

        plt.scatter(degree, cluster, marker='^', c='blue')
        plt.xlabel("K")
        plt.ylabel("C(node)")
        plt.yscale("log")
        plt.title("Node——Cluster")
        plt.show()
def draw_degree_knn(g, is_mean=False):
    if is_mean:
        degree_knn = nx.average_degree_connectivity(g)
        plt.scatter(degree_knn.keys(), degree_knn.values(), marker='s', c='red')
        plt.xlabel("K")
        plt.ylabel(r"$K_{nn}(k)$")
        plt.yscale("log")
        plt.title("Degree--Knn")
        plt.show()
    else:
        node_knn = nx.average_neighbor_degree(g)
        # 一个由 tuple 组成的 list   tuple中的第一个元素表示度值 第二个为Knn
        degree_knn = [(g.weighted_degree[key], value) for key, value in node_knn.items()]

        plt.scatter([data[0] for data in degree_knn], [data[1] for data in degree_knn], marker='s', c='red')
        plt.xlabel("K")
        plt.ylabel(r"$K_{nn}(k)$")
        plt.title("Node--Knn")
        plt.xscale("log")
        plt.yscale("log")
        plt.show()
def draw_degree_betweenness_centrality(g, is_mean=False):
    '''
    度 和 中介中心性 之间的关系
    :param g:
    :return:
    '''
    if is_mean:
        degree_betweenness = nx.betweenness_centrality(g)
        # 存放 度 和 中介中心性 之间的关系
        degree_betweenness_centrality = {}
        for node in g:
            if g.weighted_degree(node) in degree_betweenness_centrality.keys():
                degree_betweenness_centrality[g.weighted_degree(node)] += degree_betweenness[node]
            else:
                degree_betweenness_centrality[g.weighted_degree(node)] = degree_betweenness[node]

        degree_frequency_numbers = nx.degree_histogram(g)  # 度的频数
        degree_betweenness_centrality = {key: value / degree_frequency_numbers[key] for key, value in
                                         degree_betweenness_centrality.items()}
        plt.scatter(degree_betweenness_centrality.keys(), degree_betweenness_centrality.values(), marker='^', c='blue')
        plt.xlabel("K")
        plt.ylabel("BC")
        plt.title("Degree--BC")
        plt.yscale("log")
        plt.show()
    else:
        degree_betweenness = nx.betweenness_centrality(g)
        node_BC = [(g.weighted_degree[key], value) for key, value in degree_betweenness.items()]

        plt.scatter([data[0] for data in node_BC], [data[1] for data in node_BC], marker='^', c='blue')
        plt.xlabel("K")
        plt.ylabel("BC")
        plt.title("Node--BC")
        plt.yscale("log")
        plt.show()
def draw_betweenness_centrality_cumulative_distribution(g1, g2):
    '''
    中介中心性 的 累计概率分布图
    :param g:
    '''
    def calculate_BC_values_cumulative_distribution(g):
        '''
        计算BC_value_not_repeat 和 BC_values_cumulative_distribution
        :param g:
        :return:
        '''
        BC = nx.betweenness_centrality(g)
        BC_values = list(BC.values())
        BC_values.sort()

        # 用 set 排除重复  extend：将list添加到末尾
        BC_values_not_repeat.extend(list(set(BC_values)))
        BC_values_not_repeat.sort()

        # 遍历set 统计BC_values 中 大于 某个BC值的比例
        # BC_values_cumulative_distribution = []
        for i in BC_values_not_repeat:
            BC_values_cumulative_distribution.append(len([x for x in BC_values if x > i]) / len(BC_values))

    BC_values_not_repeat = []
    BC_values_cumulative_distribution = []
    calculate_BC_values_cumulative_distribution(g2)
    plt.scatter(BC_values_not_repeat, BC_values_cumulative_distribution, c='gray', label='Random', s=5)
    # print(BC_values_not_repeat)

    BC_values_not_repeat = []
    BC_values_cumulative_distribution = []
    calculate_BC_values_cumulative_distribution(g1)
    plt.scatter(BC_values_not_repeat, BC_values_cumulative_distribution, c='darkblue', label='Nodes', s=5)
    # print(BC_values_not_repeat)

    plt.title("Betweenness Centrality Cumulative Distribution")
    plt.yscale("log")
    plt.xlabel("BC")
    plt.ylabel("P(BC>bc)")
    plt.legend()
    plt.show()
def zero_model(g):
    '''
    已经弃用
    :param g: 传入一个图
    :return:  返回一个零模型随机图  近似拥有相同度分布 因为删去了 平行边 和 自环
    '''
    degree = list(dict(g.weighted_degree()).values())

    # 零模型
    g1 = nx.configuration_model(degree)  # 保持度分布不变 随机重连
    # 删除平行边 和 自环  会导致度分布有一些不同
    g1 = nx.Graph(g1)
    g1.remove_edges_from(nx.selfloop_edges(g1))
    return g1
def draw_closeness_centrality_cumulative_distribution(g1,g2):
    CC = list(nx.closeness_centrality(g1).values())
    CC.sort()
    P_value = [(len(CC) - x) / len(CC) for x in range(len(CC))]

    CC_zero = list(nx.closeness_centrality(g2).values())
    CC_zero.sort()
    P_zero_value = [(len(CC_zero) - x) / len(CC_zero) for x in range(len(CC_zero))]

    # 从第 2 个开始算起
    plt.scatter(CC_zero[2:], P_zero_value[2:], c='gray', label='Random', s=5)
    plt.scatter(CC[2:], P_value[2:], c='darkblue', label='Nodes', s=5)

    plt.title("Closeness Centrality Cumulative Distribution")
    plt.yscale("log")
    plt.xlabel("CC")
    plt.ylabel("P(CC>cc)")
    plt.legend()
    plt.show()
def draw_participation_coefficient(g,communities):
    '''
    画出 图的P值 图
    :param g: 要计算的图
    :param communities: 图的社团划分
    :return:
    '''
    # 给节点添加 社团ID属性
    com_ID = 0  # 社团ID
    for com in communities:
        for node in com:
            g.nodes[node]['comID'] = com_ID
        com_ID += 1

    # 存放每个节点的 P值
    P_dict = dict.fromkeys(g.nodes(), 0)
    for com in communities:
        for node in com:
            temp = [0] * 8
            for neighbor in g.neighbors(node):
                temp[g.nodes[neighbor]['comID']] += 1

            P = 1
            # 这里是P值的公式 其实就是 熵的概念
            for i in temp:
                P -= (i / g.weighted_degree[node]) ** 2
            P_dict[node] = P

    P_value = list(P_dict.values())
    P_value.sort(reverse=True)
    plt.scatter(range(len(P_value)), P_value, s=2, c='darkblue')
    plt.ylabel("P")
    plt.show()
def draw_inside_outside_degree(g,communities):
    '''
    画出 inside outside degree 的分布图
    标准化之后的
    :param communities:
    :param g:
    :return:
    '''
    # 创建dict 存放每个节点的 Z值和B值 默认值为0
    inside_module_degree = dict.fromkeys(g.nodes(), 0)
    outside_module_degree = dict.fromkeys(g.nodes(), 0)

    # 遍历社团
    for com in communities:
        # 遍历节点
        for node in com:
            # 遍历节点的邻居
            for neighbor in g.neighbors(node):
                # 邻居在社团内就inside＋1   不在就outside＋1
                if neighbor in com:
                    inside_module_degree[node] += 1
                else:
                    outside_module_degree[node] += 1

    # 减去平均值 再除以标准差
    inside_module_degree_mean = np.mean(list(inside_module_degree.values()))
    inside_module_degree_std_dev = np.std(list(inside_module_degree.values()))
    Z = inside_module_degree.copy()
    Z = {key: (value - inside_module_degree_mean) / inside_module_degree_std_dev for key, value in Z.items()}

    outside_module_degree_mean = np.mean(list(outside_module_degree.values()))
    outside_module_degree_std_dev = np.std(list(outside_module_degree.values()))
    B = outside_module_degree.copy()
    B = {key: (value - outside_module_degree_mean) / outside_module_degree_std_dev for key, value in B.items()}

    B_values = list(B.values())
    B_values.sort(reverse=True)

    plt.figure()
    plt.scatter(range(len(B_values)), B_values, s=2, c='darkblue')
    plt.xticks([])  # 隐藏刻度线
    plt.ylabel("B")
    plt.show()

    Z_values = list(Z.values())
    Z_values.sort(reverse=True)

    plt.figure()
    plt.scatter(range(len(Z_values)), Z_values, s=2, c='darkblue')
    plt.xticks([])  # 隐藏刻度线
    plt.ylabel("Z")
    plt.show()
def basic_topology_metrics(g):
    '''
    网络的基础拓扑指标
    :param g:
    :return:
    '''
    N = g.number_of_nodes()
    M = g.number_of_edges()
    R = nx.degree_assortativity_coefficient(g)
    C = nx.average_clustering(g)
    # L = nx.average_shortest_path_length(g)
    L = average_shortest_path_length_largest_component(g)  # 最大连通分支的平均最短路径
    print("N:", N)
    print("M:", M)
    print("<Knn>:", R)
    print("<C>:", C)
    print("<L>", L)
def average_shortest_path_length_largest_component(g):
    '''

    :param g: 传入图
    :return:  最大连通分量的平均最短路径
    '''
    largest_component = max(nx.connected_components(g), key=len)  # 提取最大连通分量
    largest_subgraph = g.subgraph(largest_component)
    return nx.average_shortest_path_length(largest_subgraph)
def draw_degree_strength(g1:nx.Graph, g2:nx.MultiDiGraph) -> None:
    '''
    注意传入的两个图的 节点 一定是一样的
    得到度值和强度的关系图
    :param g1: 无向无多边的简单图
    :param g2: 有向有多边的图
    :return:
    '''

    degree_strength = [(g1.degree(node), g2.degree(node)) for node in g1.nodes()]

    degree_list = [data[0] for data in degree_strength]
    strength_list = [data[1] for data in degree_strength]

    correlation = np.corrcoef([degree_list, strength_list])

    # 获取两个列表之间的相关系数
    correlation_value = correlation[0, 1]

    # plt.plot(list(range(1,len(degree_list))), list(range(1,len(strength_list))), color='red', linestyle='--')
    plt.scatter(degree_list, strength_list, s=2, color='darkblue', label=f'correlation={correlation_value:.3f}')
    plt.xlabel('Degree')
    plt.ylabel('Strength')
    plt.title('Degree--Strength')
    plt.yscale('log')
    plt.xscale('log')
    plt.legend()
    plt.show()
def draw_strength_frequency_distribution(g):
    '''
    以前的版本 使用 Graph 中的weight属性计算
    :param g:
    :return:
    '''
    N = g.number_of_nodes()
    # 计算每个节点的强度
    port_strengths = {node: val for (node, val) in g.weighted_degree(weight='weight')}

    strengths = port_strengths.values()
    # 统计每个强度出现的次数
    strengths_counts = Counter(strengths)
    sorted_strengths_counts = sorted(strengths_counts.items(), key=lambda item: item[0])
    strengths_counts_frequency = {key: value / N for key, value in strengths_counts.items()}

    plt.scatter(list(strengths_counts_frequency.keys()), list(strengths_counts_frequency.values()), s=2, c='darkblue')
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("strength")
    plt.ylabel("P(K=k)")
    plt.show()
def draw_strength_distribution(g):
    '''
    画强度分布图
    :param g:
    :return:
    '''
    degree_frequency_numbers = nx.degree_histogram(g)  # 度的频数

    N = g.number_of_nodes()
    # [0, 675, 789, 676, 428, 258, 205, 153, 140, 99, 92, 65, 45, 57, 38, 48, 25, 44, 20, 18, 28, 16, 12, ...]
    # print(len(nx.degree_histogram(G)))  # 82
    x_degree = list(range(len(degree_frequency_numbers)))  # 所有的度数 作为下面画图的x坐标

    # 删去 度为0的元素
    for i in sorted(x_degree, reverse=True):  # 注意这里要反向遍历 不然索引会出问题
        if degree_frequency_numbers[i] == 0:
            del degree_frequency_numbers[i]
            del x_degree[i]

    degree_frequency = [x / N for x in degree_frequency_numbers]  # 度的频率

    # 绘制原始数据点
    plt.scatter(x_degree, degree_frequency, color='blue', label='Ports')

    # 设置对数坐标轴
    plt.xscale("log")
    plt.yscale("log")

    # 设置坐标轴范围
    plt.xlim([min(x_degree) * 0.6, max(x_degree) * 1.7])  # 设置x轴范围为数据的最小值到最大值的1.1倍
    plt.ylim([min(degree_frequency) * 0.6, max(degree_frequency) * 1.7])  # 设置y轴范围为数据的最小值到最大值的1.1倍

    # 添加图例和标题
    plt.legend()
    plt.title("Strength Distribution")
    plt.xlabel("Strength")
    plt.ylabel("Strength Frequency")
    plt.show()
def draw_degree_bc_cc(g, value:str) -> None:
    '''
    查看三种中心性指标之间的关系
    :param g: 传入要计算的 Graph
    :param value: 有 Degree——BC，Degree——CC，BC--CC三种模式
    :return:
    '''
    bc = nx.betweenness_centrality(g)
    degree = nx.degree_centrality(g)
    cc = nx.closeness_centrality(g)
    degree_bc_cc = [(degree[node], bc[node], cc[node], node) for node in g.nodes()]

    if value == "DB":
        plt.scatter([data[0] for data in degree_bc_cc], [data[1] for data in degree_bc_cc], marker='s', c='red')
        plt.xlabel("degree")
        plt.ylabel("BC")
        plt.title("degree--BC")
        plt.savefig('../Figure/节点度值与BC的关系.svg')
        plt.show()
    elif value == "DC":
        plt.scatter([data[0] for data in degree_bc_cc], [data[2] for data in degree_bc_cc], marker='s', c='red')
        plt.xlabel("degree")
        plt.ylabel("CC")
        plt.title("degree--CC")
        plt.savefig('../Figure/节点度值与CC的关系.svg')
        plt.show()
    elif value == "BC":
        plt.scatter([data[1] for data in degree_bc_cc], [data[2] for data in degree_bc_cc], marker='s', c='red')
        plt.xlabel("BC")
        plt.ylabel("CC")
        plt.title("BC--CC")
        plt.savefig('../Figure/节点BC与CC的关系.svg')
        plt.show()