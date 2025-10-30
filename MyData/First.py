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
def k_and_knn():
    """
    画 k 与 knn(k) 的散点图
    :return:
    """
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

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
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

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
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

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
        years = range(2017, 2022)
        seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

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
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

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
            G = nx.Graph(nx.read_graphml(file_path))

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
#endregion

def write_network_structure_metric():
    """
    将网络和null model的结构指标写入csv文件
    :return:
    """
    origin_data = {}
    null_model_data = {}
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

            # 导入网络 生成零模型
            G = nx.Graph(nx.read_graphml(file_path))
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