import heapq
import json
import pathlib
import random
from matplotlib.lines import Line2D
import os
import networkx as nx
import seaborn as sns
import pandas as pd
import numpy as np
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
sys.path.append('../Algorithm')


#regionMain
def get_network():
    """
    网络生成器函数
    :return: 每次生成对应的 DiG  G  time
    """
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    # 读取数据并构建网络
    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后（数据不全）
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            time = f"{year} {season}"

            DiG = nx.read_graphml(file_path)
            G = nx.Graph(DiG)
            yield DiG, G, time
def get_network_certain_time(year_season:str):
    """
    得到某个时间段具体的network
    :param year_season:
    :return:
    """
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    # 读取数据并构建网络
    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后（数据不全）
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            time = f"{year} {season}"

            DiG = nx.read_graphml(file_path)
            G = nx.Graph(DiG)
            if time == year_season:
                return DiG, G, time
    return None, None
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
        Draw.draw_scatter(
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
    Draw.draw_scatter(df,
                      "Undirected/EdgesOrNodesAndAvgPathLength/",
                      "Nodes",
                      "Average shortest path length",
                      "Nodes And Avg Shortest Path Length"
    )
def degree_and_weighted_average_or_std():
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
                      "DirectedWeighted/AverageDegreeAndWeightedDegree/",
                      "Degree And Weighted Degree \'s Standard Deviation"
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

            Draw.draw_scatter(df,
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
        bc_dict = nx.betweenness_centrality(DiG, normalized=True)  # 有向网络的介数中心性
        for node,attr in DiG.nodes(data=True):
            dc = attr['total_TEU']
            bc = bc_dict[node]
            data[node] = [(dc, bc)]
        df = pd.DataFrame(data)
        Draw.draw_scatter(df,
                          "DirectedWeighted/WeightedDegreeAndDirectedBetweenness/",
                          "Weighted Degree",
                          "Directed Betweenness",
                          f"Weighted Degree And Directed Betweenness {time}",
                          mode='ports'
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
        Draw.draw_scatter(
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
    null_model_data = {}
    for DiG, G, time in get_network():
        null_model = NullModel.create_edges_nodes_null_model(G)
        # 计算拓扑指标
        origin_metrics_dict = Undirected.get_network_structure_metrics(G)
        null_model_metrics_dict = Undirected.get_network_structure_metrics(null_model)
        metrics = list(origin_metrics_dict.keys())

        origin_data[time] = list(origin_metrics_dict.values())
        null_model_data[time] = list(null_model_metrics_dict.values())
    origin_df = pd.DataFrame(origin_data, index=metrics)
    origin_df.to_csv('Output/Undirected/StructureMetrics/network_structure_metrics.csv')
    null_model_df = pd.DataFrame(null_model_data, index=metrics)
    null_model_df.to_csv('Output/Undirected/StructureMetrics/null_model_structure_metrics.csv')
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
#endregion





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

def center_ports_change_map(last_time:str, next_time:str):
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
    lastDiG = nx.read_graphml(f'../Data/2017/US/Season/Spring/US2017_Spring_Digraph.graphml')
    nextDiG = nx.read_graphml(f'../Data/2021/US/Season/Spring/US2021_Spring_Digraph.graphml')

    common_elements_ports, last_unique_ports, next_unique_ports = get_common_and_unique(last_list, next_list)
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
        data['TEU'].append(10000)
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
        "Center Port 2017Spring To 2021Spring Change"
    )
