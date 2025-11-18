import heapq
import json
import pathlib
import random
import re
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
from Algorithm.ConstructNetwork import ConstructNetwork
from sklearn.preprocessing import minmax_scale
from matplotlib import patheffects
from scipy import stats  # 用于线性回归拟合
from heapq import nlargest
from collections import deque
from collections import defaultdict
from matplotlib.path import Path
import matplotlib.patches as patches
import sys
from MyData.Draw import Draw
from MyData.NullModel import NullModel
from MyData.DirectedWeighted import DirectedWeighted
from MyData.Undirected import Undirected
from MyData.Read import Read
from MyData.Main import Main
sys.path.append('../Algorithm')

#regionTools
def get_common_and_unique(last:list, next:list):
    # 转换为集合
    last_set = set(last)
    next_set = set(next)

    # 重合的元素（交集）
    common_elements = last_set & next_set

    # last独有的元素（差集）
    last_unique = last_set - next_set

    # next独有的元素（差集）
    next_unique = next_set - last_set

    return common_elements, last_unique, next_unique
#endregion

#regionMain
def k_and_knn():
    """
    画 k 与 knn(k) 的散点图
    :return:
    """
    for _, G, time in get_network():
        null_model = NullModel.create_degree_distribution_null_model(G)

        # 3. 执行计算
        knn_dict = Undirected.calculate_knn(G)
        null_model_knn_dict = Undirected.calculate_knn(null_model)

        data = {
            "Origin Network": [(k, v) for k,v in knn_dict.items()],
            "Null Model": [(k, v) for k,v in null_model_knn_dict.items()]
        }
        df = pd.DataFrame(data)
        Draw.draw_scatter_list(
            df,
            "Undirected/KAndKnn/",
            "k",
            "knn(k)",
            f"k and knn(k) {time}",
            'loglog'
        )
def nodes_or_edges_and_avg_path_length():
    """
    nodes or edges and avg path length 的 关系
    :return:
    """
    data = {
        "network": []
    }
    for _, G, time in get_network():
        data["network"].append((
            G.number_of_nodes(),
            Undirected.calculate_average_shortest_path_length(G))
        )
    df = pd.DataFrame(data)
    Draw.draw_scatter_list(df,
                      "Undirected/EdgesOrNodesAndAvgPathLength/",
                      "Nodes",
                      "Average shortest path length",
                      "Nodes And Avg Shortest Path Length"
                           )
def degree_and_weighted_std():
    """
    度和加权度的平均值or标准差的变化
    :return:
    """
    data = {
        "time":[],
        "degree standard deviation":[],
        "weighted degree standard deviation": []
    }
    for DiG, G, time in get_network():
        data["time"].append(time)

        _,_,degree_std = DirectedWeighted.calculate_degree_standard_deviation(DiG)
        data["degree standard deviation"].append(
            degree_std
        )
        _,_,weighted_degree_std = DirectedWeighted.calculate_weighted_degree_standard_deviation(DiG)
        data["weighted degree standard deviation"].append(
            weighted_degree_std
        )
    df = pd.DataFrame(data)

    Draw.draw_dual_axis_plot(df,
                      "DirectedWeighted/DegreeAndWeightedDegree/",
                      "Degree And Weighted Degree \'s Standard Deviation",
                      "lower left"
    )
def degree_and_weighted_average():
    """
    度和加权度的平均值or标准差的变化
    :return:
    """
    data = {
        "time":[],
        "average degree":[],
        "average weighted degree": []
    }
    for DiG, G, time in get_network():
        data["time"].append(time)

        _,_,avg_degree = DirectedWeighted.calculate_average_degree(DiG)
        data["average degree"].append(
            avg_degree
        )
        _,_,avg_weighted_degree = DirectedWeighted.calculate_average_weighted_degree(DiG)
        data["average weighted degree"].append(
            avg_weighted_degree
        )
    df = pd.DataFrame(data)

    Draw.draw_dual_axis_plot(df,
                      "DirectedWeighted/DegreeAndWeightedDegree/",
                      "Average Degree And Weighted Degree",
                      "upper left"
    )
def degree_and_weighted_degree():
        """
        度和加权度的关系
        :return:
        """
        for DiG, G, time in get_network():
            data = {
                "Ports": [(DiG.degree(port), attr['total_TEU']) for port, attr in DiG.nodes(data=True)]
            }
            df = pd.DataFrame(data)

            Draw.draw_scatter_list(df,
                              "DirectedWeighted/DegreeAndWeightedDegree/",
                              "Degree",
                              "Weighted Degree",
                              f"Degree And Weighted Degree {time} loglog",
                              "loglog"
                                   )
def weighted_degree_and_directed_betweenness():
    """
    画每个港口 加权度和有向介数中心性之间的关系
    :return:
    """
    for DiG, G, time in get_network():
        data = {}
        bc_dict = nx.betweenness_centrality(DiG, normalized=True)  # 有向网络的介数中心性  不适用加权
        for node,attr in DiG.nodes(data=True):
            dc = attr['total_TEU']
            bc = bc_dict[node]
            data[node] = [(dc, bc)]
        df = pd.DataFrame(data)
        Draw.draw_scatter_list(df,
                          "DirectedWeighted/WeightedDegreeAndDirectedBetweenness/",
                          "Weighted Degree",
                          "Directed Betweenness",
                                        f"Weighted Degree And Directed Betweenness {time}",
                               mode='ports',
                               label=True
                               )
def degree_distribution():
    """
    画网络的度分布
    :return:
    """
    for DiG, G, time in get_network():
        # 1. 初始化数据结构
        degree_counts = defaultdict(int)
        degree_to_ports = defaultdict(list)  # 度值 → 港口列表
        port_to_degree = {}  # 新增：港口 → 度值（快速查询每个港口的度）

        # 2. 遍历节点，统计度值、港口对应关系
        for port, degree in G.degree():
            degree_counts[degree] += 1
            degree_to_ports[degree].append(port)
            port_to_degree[port] = degree  # 记录每个港口的度值

        # 3. 计算排序的度值、频率，并建立“度值→频率”映射
        degrees_sorted = sorted(degree_counts.keys())
        counts = [degree_counts[d] for d in degrees_sorted]
        total_nodes = G.number_of_nodes()
        frequencies = [count / total_nodes for count in counts]

        # 关键：建立“度值→频率”的字典（一个度值对应一个频率）
        degree_to_frequency = dict(zip(degrees_sorted, frequencies))

        # 4. 构建最终数据：港口 → [度值, 频率]（每个港口唯一对应一组数据）
        data = {}
        for port in G.nodes():  # 遍历所有港口，确保不遗漏
            degree = port_to_degree[port]  # 获取该港口的度值
            frequency = degree_to_frequency[degree]  # 通过度值获取对应频率
            data[port] = [(degree, frequency)]  # 每个港口对应唯一的[(度值, 频率)]

        # TODO 最后只能人工打上标签
        df = pd.DataFrame(data)
        Draw.draw_scatter_list(
            df,
            "Undirected/DegreeDistribution/",
            "Degree",
            "Frequency",
            f"DegreeDistribution {time}",
            "loglog",
            "ports"
        )
def write_network_structure_metric():
    """
    将网络和null model的结构指标写入csv文件
    :return:
    """
    origin_data = {}
    null_model_data = {}        # 0阶零模型
    one_null_model_data = {}    # 1阶零模型
    for DiG, G, time in Read.get_network():
        null_model = NullModel.create_edges_nodes_null_model(G)
        one_null_model = NullModel.create_degree_distribution_null_model(G)

        # 计算拓扑指标
        origin_metrics_dict = Undirected.get_network_structure_metrics(G)
        null_model_metrics_dict = Undirected.get_network_structure_metrics(null_model)
        one_null_model_metrics_dict = Undirected.get_network_structure_metrics(one_null_model)

        metrics = list(origin_metrics_dict.keys())

        origin_data[time] = list(origin_metrics_dict.values())
        null_model_data[time] = list(null_model_metrics_dict.values())
        one_null_model_data[time] = list(one_null_model_metrics_dict.values())

    origin_df = pd.DataFrame(origin_data, index=metrics)
    origin_df.to_csv('Output/Undirected/StructureMetrics/network_structure_metrics.csv')

    null_model_df = pd.DataFrame(null_model_data, index=metrics)
    null_model_df.to_csv('Output/Undirected/StructureMetrics/null_model_structure_metrics.csv')

    one_null_model_df = pd.DataFrame(one_null_model_data, index=metrics)
    one_null_model_df.to_csv('Output/Undirected/StructureMetrics/one_null_model_structure_metrics.csv')
def k_core_and_nodes():
    """
    画每个k core含有的nodes个数
    :return:
    """
    for DiG, G, time in get_network():
        # 计算所有节点的核数（核心步骤，避免重复计算）
        core_numbers = nx.core_number(G)

        # 确定最大k值（所有节点核数的最大值）
        max_k = max(core_numbers.values())

        # 存储每个k对应的数量
        k_core_counts = {}

        # 遍历k从1到max_k
        for k in range(1, max_k + 1):
            # 提取k核（复用已计算的核数，提高效率）
            k_core = nx.k_core(G, k=k, core_number=core_numbers)
            k_core_counts[k] = len(k_core.nodes())

        # 调整数据格式：转为包含 'k' 和 'nodes' 列的DataFrame（适合绘图）
        df = pd.DataFrame(
            list(k_core_counts.items()),
            columns=['k', 'nodes']  # 明确列名：k值、节点数
        )


        Draw.draw_step(
                        df,
            "Undirected/KCore/",
            "K Core",
            "Nodes",
            f"K core numbers {time}",
        )
def center_ports_map():
    """
    保存和画出 每个网络的Center Ports
    目前定义的是 k-core最大的节点 && 加权中心性 > 10 0000
    :return:
    """
    for DiG, G, time in get_network():
        core_numbers = nx.core_number(G)
        # 确定最大k值（所有节点核数的最大值）
        max_k = max(core_numbers.values())

        k_core = nx.k_core(G, k=max_k, core_number=core_numbers)

        center_nodes = [node for node, attr in k_core.nodes(data=True) if attr['total_TEU'] > 100000]

        data = {
            "Port": [],
            "TEU": [],
            "Continent": [],
            "Colors":[]
        }
        for node in center_nodes:
            data["Port"].append(node)
            data["TEU"].append(DiG.nodes[node]['total_TEU'])

            continent = DiG.nodes[node]['continent']
            data["Continent"].append(continent)
            data["Colors"].append(Draw.continent_color_mapping[continent])

        df = pd.DataFrame(data)
        df.to_csv(f'Output/WorldMap/CenterPorts/CenterPort{time}.csv',
                  index=False)
        Draw.draw_world_ports_map(df,
                                  "WorldMap/CenterPorts/",
                                  f"Center Ports {time}"
        )
def center_ports_change_map(last_time:str, next_time:str):
    """
    画center ports的变化
    但是还是很粗糙   画图函数中的图例颜色要一样
    :param last_time: 例如："2017 Spring"
    :param next_time: 例如："2021 Spring"
    :return:
    """
    df_last = pd.read_csv(f"Output/WorldMap/CenterPorts/CenterPort{last_time}.csv",
                          dtype={
                         'Port': 'string',
                         'TEU': 'float64',
                         'Continent': 'string',  # 或者 'object'
                         'Colors': 'string'
                          },
                          keep_default_na=False  # 不使用默认的缺失值识别    因为它会把NA识别成缺失
    )
    last_list = list(df_last["Port"])
    df_next = pd.read_csv(f"Output/WorldMap/CenterPorts/CenterPort{next_time}.csv",
                         dtype={
                         'Port': 'string',
                         'TEU': 'float64',
                         'Continent': 'string',  # 或者 'object'
                         'Colors': 'string'
                         },
                         keep_default_na=False  # 不使用默认的缺失值识别    因为它会把NA识别成缺失
    )
    next_list = list(df_next["Port"])
    data = {
        "Port":[],
        "TEU":[],
        "Continent":[],
        "Colors":[]
    }
    lastDiG, _ = get_network_certain_time(last_time)
    nextDiG, _ = get_network_certain_time(next_time)

    common_elements_ports, last_unique_ports, next_unique_ports = get_common_and_unique(last_list, next_list)
    # 共有的港口到底要不要加
    # for port in common_elements_ports:
    #     last_teu = lastDiG.nodes[port]['total_TEU']
    #     next_teu = nextDiG.nodes[port]['total_TEU']
    #     data['Port'].append(port)
    #     # data['TEU'].append(next_teu - last_teu)
    #     data['TEU'].append(1000)
    #     data['Continent'].append(lastDiG.nodes[port]['continent'])
    #     data['Colors'].append('grey')
    for port in last_unique_ports:
        last_teu = lastDiG.nodes[port]['total_TEU']
        next_teu = nextDiG.nodes[port]['total_TEU']
        data['Port'].append(port)
        # data['TEU'].append(next_teu - last_teu)
        data['TEU'].append(10000)                                       # 节点大小固定
        data['Continent'].append(lastDiG.nodes[port]['continent'])
        data['Colors'].append('red')
    for port in next_unique_ports:
        last_teu = lastDiG.nodes[port]['total_TEU']
        next_teu = nextDiG.nodes[port]['total_TEU']
        data['Port'].append(port)
        # data['TEU'].append(next_teu - last_teu)
        data['TEU'].append(10000)
        data['Continent'].append(lastDiG.nodes[port]['continent'])
        data['Colors'].append('blue')
    df = pd.DataFrame(data)

    Draw.draw_world_ports_map(
                df,
        "WorldMap/CenterPortsChanges/",
        f"Center Port {last_time} To {next_time} Change"
    )
#endregion


#regionTemp
# TODO 这个画WorldMap的工作之后再处理 有点乱
# last_time = "2017 Spring"
# next_time = "2020 Summer"
# lastDiG, _ = get_network_certain_time(last_time)
# nextDiG, _ = get_network_certain_time(next_time)
# last_list = list(lastDiG.nodes)
# next_list = list(nextDiG.nodes)
#
# data = {
#         "Port":[],
#         "TEU":[],
#         "Continent":[],
#         "Colors":[]
# }
#
#
# common_elements_ports, last_unique_ports, next_unique_ports = get_common_and_unique(last_list, next_list)
# for port in last_unique_ports:
#     teu = lastDiG.nodes[port]['total_TEU']
#     # 因为有些港口后面的时候没有了 所以就别计算TEU了
#     data['Port'].append(port)
#     data['TEU'].append(teu)                                       # 节点大小固定
#     data['Continent'].append(lastDiG.nodes[port]['continent'])
#     data['Colors'].append('red')
# for port in next_unique_ports:
#     teu = nextDiG.nodes[port]['total_TEU']
#     data['Port'].append(port)
#     data['TEU'].append(teu)
#     data['Continent'].append(nextDiG.nodes[port]['continent'])
#     data['Colors'].append('blue')
# df = pd.DataFrame(data)
#
# Draw.draw_world_ports_map(
#             df,
#     "WorldMap/PortsChanges/",
#     f"Ports {last_time} To {next_time} Change"
# )
#endregion

def directed_weighted_edge_swap_null_model(
        original_digraph: nx.DiGraph,
        num_iterations: int = None,
        weight_tolerance: float = 0.1  # 权重近似相等的容忍度（0=严格相等，0.1=±10%）
) -> nx.MultiDiGraph:
    """
    有向加权网络零模型：等权重边交换算法（拓扑变，强度+权重分布不变）
    :param original_digraph: 原网络（nx.DiGraph，边属性含'weight'）
    :param num_iterations: 迭代次数（默认=边数×20，确保充分随机）
    :param weight_tolerance: 权重近似相等的容忍度（相对误差）
    :return: 零模型网络（nx.DiGraph）
    """
    # 1. 复制原网络（避免修改原始数据）
    null_digraph = original_digraph.copy()
    null_digraph = nx.MultiDiGraph(null_digraph)        #转化成允许多边的图
    num_edges = null_digraph.number_of_edges()

    # 若未指定迭代次数，设为边数×20（经验值，确保拓扑充分随机）
    if num_iterations is None:
        num_iterations = num_edges * 10

    # 2. 按权重分组（便于快速找到近似等权的边对）
    # 键：权重区间（如权重5.2→5.0-5.5区间，步长=weight_tolerance×2），值：该区间的边列表
    weight_bins = defaultdict(list)
    weight_step = 0.3  # 权重分组步长（可调整，越小分组越精细）
    for u, v, data in null_digraph.edges(data=True):
        w = data['volumeTEU']
        # 按步长分箱（确保近似等权的边在同一组）
        bin_key = round(w / weight_step) * weight_step
        weight_bins[bin_key].append((u, v, w))

    # 过滤掉只有1条边的组（无法形成边对）
    valid_bins = [bin_edges for bin_edges in weight_bins.values() if len(bin_edges) >= 2]
    if not valid_bins:
        raise ValueError("无足够的等权边对用于交换，无法生成零模型")
    # print(valid_bins)
    d = {}
    for a in valid_bins:
        d[a[0][2]] = len(a)
    c = sorted(d.items(), key=lambda x: x[0], reverse=True)
    print(c)

    # 3. 迭代执行边交换
    np.random.seed(42)  # 固定种子，结果可复现（可删除）
    swap_count = 0  # 记录成功交换次数

    for _ in range(num_iterations):
        # 3.1 随机选一个有足够边的权重组
        bin_edges = random.choice(valid_bins)
        if len(bin_edges) < 2:
            continue  # 组内边数不足，跳过

        # 3.2 从组中随机选两条不同的边（A→C 和 B→D）
        idx1, idx2 = np.random.choice(len(bin_edges), 2, replace=False)
        (A, C, w1), (B, D, w2) = bin_edges[idx1], bin_edges[idx2]

        # 3.3 检查权重是否近似相等（相对误差≤tolerance）
        if abs(w1 - w2) / max(w1, w2) > weight_tolerance:
            continue

        # 3.4 检查交换条件：无自环、但是允许多边的存在
        if A == D or B == C:  # 避免自环（A→D 或 B→C 是自环）
            continue

        # 3.5 执行交换：删除原边，添加新边
        # 删除原边（注意：bin_edges 是原边的引用，需同步更新）
        null_digraph.remove_edge(A, C)
        null_digraph.remove_edge(B, D)
        # 添加新边（权重与原边相同）
        null_digraph.add_edge(A, D, weight=w1)
        null_digraph.add_edge(B, C, weight=w2)

        # 3.6 更新权重组（同步删除原边、添加新边）
        if idx1 > idx2:             # 删除的时候先删除大的
            del bin_edges[idx1]
            del bin_edges[idx2]
        else:
            del bin_edges[idx2]
            del bin_edges[idx1]
        bin_edges.append((A, D, w1))
        bin_edges.append((B, C, w2))

        swap_count += 1

    # 4. 打印交换统计信息
    print(f"✅ 边交换完成：总迭代{num_iterations}次，成功交换{swap_count}次")
    print(f"   交换成功率：{swap_count / num_iterations:.2%}（≥30% 说明拓扑充分随机）")

    return null_digraph


def _validate_null_model(original: nx.DiGraph, null: nx.DiGraph):
    """验证零模型的约束条件：强度序列、权重分布不变"""
    # 验证节点强度（入强度+出强度）
    orig_out_strength = dict(nx.out_degree_centrality(original, weight='weight'))
    orig_in_strength = dict(nx.in_degree_centrality(original, weight='weight'))
    null_out_strength = dict(nx.out_degree_centrality(null, weight='weight'))
    null_in_strength = dict(nx.in_degree_centrality(null, weight='weight'))

    assert np.allclose(list(orig_out_strength.values()), list(null_out_strength.values()), rtol=1e-3), \
        "出强度序列不匹配！"
    assert np.allclose(list(orig_in_strength.values()), list(null_in_strength.values()), rtol=1e-3), \
        "入强度序列不匹配！"

    # 验证权重分布（权重数值+频次）
    orig_weights = sorted([d['weight'] for _, _, d in original.edges(data=True)])
    null_weights = sorted([d['weight'] for _, _, d in null.edges(data=True)])
    assert np.allclose(orig_weights, null_weights, rtol=1e-3), \
        "权重分布不匹配！"

    print("✅ 零模型验证通过：强度序列和权重分布与原网络完全一致")

# 1. 生成10节点有向加权网络（复用之前的生成函数）
def generate_simple_weighted_digraph(num_nodes=10, weight_range=(1,10), edge_density=0.3):
    DiG = nx.DiGraph()
    DiG.add_nodes_from(range(num_nodes))
    np.random.seed(42)
    for u in range(num_nodes):
        for v in range(num_nodes):
            if u != v and np.random.random() < edge_density:
                DiG.add_edge(u, v, weight=np.random.randint(*weight_range))
    return DiG


# a = []
# original_DiG,_ = get_network_certain_time("2017 Spring")
# for u, v, data in original_DiG.edges(data=True):
#     teu = data.get('volumeTEU', 0)
#     a.append(teu)
# sorted_a = sorted(a, reverse=True)
# print(sorted_a)
# null_model_Multi = directed_weighted_edge_swap_null_model(original_DiG, weight_tolerance=0.3)
#
#
# # 假设 G 是 MultiDiGraph，边有 total_TEU 属性
# null_model = nx.DiGraph()
# null_model.add_nodes_from(null_model_Multi.nodes(data=True))  # 1. 先拷节点属性
#
# # 2. 把平行边的 TEU 累加
# for u, v, data in null_model_Multi.edges(data=True):
#     teu = data.get('volumeTEU', 0)
#     if null_model.has_edge(u, v):
#         null_model[u][v]['volumeTEU'] += teu
#     else:
#         null_model.add_edge(u, v, volumeTEU=teu)
#
#
# data = {
#     "Network":[],
#     "Null Model":[]
# }
# bc_dict = nx.betweenness_centrality(original_DiG, normalized=True)  # 有向网络的介数中心性
# for node,attr in original_DiG.nodes(data=True):
#     dc = attr['total_TEU']
#     bc = bc_dict[node]
#     data["Network"].append((dc, bc))
# for node,attr in null_model.nodes(data=True):
#     dc = attr['total_TEU']
#     bc = bc_dict[node]
#     data["Null Model"].append((dc, bc))
#
# df = pd.DataFrame(data)
# Draw.draw_scatter(df,
#                   "DirectedWeighted/WeightedDegreeAndDirectedBetweennessNullModel/",
#                   "Weighted Degree",
#                   "Directed Betweenness",
#                   f"Weighted Degree And Directed Betweenness 2017 Spring",
#                   mode='normal',
#                   label=True
# )

#region出出、出入、入出、入入
# strength_type = "out"
# neighbors_strength_type = "out"
#
# for DiG, G, time in Read.get_network():
#     # 3. 执行计算
#     knn_dict = DirectedWeighted.calculate_knn_strength(DiG)
#     # null_model_knn_dict = DirectedWeighted.calculate_knn_strength(null_model)
#
#     data = {
#         "Origin Network": [(k, v) for k,v in knn_dict.items()]
#         # "Null Model": [(k, v) for k,v in null_model_knn_dict.items()]
#     }
#     df = pd.DataFrame(data)
#     Draw.draw_scatter_list(
#         df,
#         "Undirected/KAndKnn/",
#         "k",
#         "knn(k)",
#         f"k and knn(k) {time}",
#         'loglog'
#     )
#endregion

Main.degree_and_strength_average()
