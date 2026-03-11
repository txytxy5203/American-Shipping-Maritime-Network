import json
import os
import pathlib

import networkx as nx
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm

from MyData.DirectedWeighted import DirectedWeighted
from MyData.Draw import Draw
from MyData.NullModel import NullModel
from MyData.Read import Read
from MyData.Robustness import Robustness
from MyData.Undirected import Undirected

class Main:
    """
    主类  所有出结果的函数全部放在这里面
    TODO 我的这些画图函数都需要增加一个检测有无csv文件的程序
    """
    #region网络生成器
    @classmethod
    def get_certain_networks_by_years(cls, year_str: str):
        """
        得到某个具体的network  通过年份
        例如： 2017
        :return:
        """
        years = range(2017, 2021)
        # 读取数据并构建网络
        for year in years:
            file_path = f'../Data/{year}/US/US{year}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            time = str(year)

            DiG = nx.read_graphml(file_path)
            G = nx.Graph(DiG)
            if time == year_str:
                return DiG, G
        return None, None
    @classmethod
    def get_certain_networks_by_seasons(cls, year_season: str):
        """
        得到某个具体的network  通过季节
        例如： 2017 Spring
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
                if time ==  year_season:
                    return DiG, G
        return None, None

    @classmethod
    def get_certain_networks_by_months(cls, year_month: str):
        """
        得到具体的network  通过月份
        :param year_month: 例如： "2017 01"
        :return:
        """
        years = range(2017, 2022)
        months = list(range(1, 13))
        # 读取数据
        for year in years:
            for month in months:
                month_str = f"{month:02d}"

                # 跳过2021年7月的数据  感觉7月的数据可能不全
                if year == 2021 and month == 7:
                    continue
                file_path = f'../Data/{year}/US/Month/{month_str}/US_{year}_{month_str}_Digraph.graphml'
                if not os.path.exists(file_path):
                    print(f'⚠️ 文件不存在: {file_path}')
                    continue
                time = f"{year} {month_str}"

                DiG = nx.read_graphml(file_path)
                G = nx.Graph(DiG)
                if time == year_month:
                    return DiG, G
        return None, None

    @classmethod
    def get_networks_by_years(cls):
        """
        网络生成器函数   months
        :return: 每次生成对应的 DiG  G  time
        """
        years = range(2017, 2021)       # 21年的数据不全 不使用
        for year in years:
            file_path = f'../Data/{year}/US/US{year}_Digraph.graphml'

            time = f"{year}"

            DiG = nx.read_graphml(file_path)
            G = nx.Graph(DiG)
            yield DiG, G, time
    @classmethod
    def get_networks_by_seasons(cls):
        """
        网络生成器函数   seasons
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

    @classmethod
    def get_networks_by_months(cls):
        """
        网络生成器函数   months
        :return: 每次生成对应的 DiG  G  time
        """
        years = range(2017, 2022)
        months = list(range(1, 13))
        for year in years:
            for month in months:
                month_str = f"{month:02d}"

                # 跳过2021年7月的数据  感觉7月的数据可能不全
                if year == 2021 and month == 7:
                    continue
                file_path = f'../Data/{year}/US/Month/{month_str}/US_{year}_{month_str}_Digraph.graphml'
                if not os.path.exists(file_path):
                    print(f'⚠️ 文件不存在: {file_path}')
                    continue

                time = f"{year} {month_str}"

                DiG = nx.read_graphml(file_path)
                G = nx.Graph(DiG)
                yield DiG, G, time
    #endregion

    #regionCCC论文
    @classmethod
    def nodes_and_edges(cls):
        """
        节点和边的数量变化趋势图
        :return:
        """
        data = {
            "Time":[],
            "Nodes":[],
            "Edges":[]
        }
        for DiG, G, time in cls.get_networks_by_months():
            data["Time"].append(time)
            data["Nodes"].append(G.number_of_nodes())
            data["Edges"].append(G.number_of_edges())
        df = pd.DataFrame(data)
        Draw.draw_dual_axis_plot(
            df,
            "Months/Undirected/NodesAndEdges/",
            "Nodes And Edges",
            "upper right"
        )

    @classmethod
    def average_shortest_length(cls):
        """
        平均最短路径长度的变化趋势
        :return:
        """
        data = {
            "Time":[],
            "Network":[],
            "Null Model":[]
        }
        for DiG, G, time in cls.get_networks_by_months():
            null_model = NullModel.create_edges_nodes_null_model(G)

            avg_shortest_length = Undirected.calculate_average_shortest_path_length(G)
            avg_shortest_length_null_model = Undirected.calculate_average_shortest_path_length(null_model)

            data["Time"].append(time)
            data["Network"].append(avg_shortest_length)
            data["Null Model"].append(avg_shortest_length_null_model)
        df = pd.DataFrame(data)
        Draw.draw_plot(
            df,
            "Months/Undirected/AverageShortestLength/",
            "Average Shortest Path Length",
            "Average Shortest Path Length",
            1
        )

    @classmethod
    def degree_and_strength_average(cls):
        """
        平均度和强度的变化趋势
        :return:
        """
        data = {
            "Time": [],
            "Average Degree": [],
            "Average Strength": []
        }
        for DiG, G, time in cls.get_networks_by_months():
            data["Time"].append(time)

            _, _, avg_degree = DirectedWeighted.calculate_average_degree(DiG)
            data["Average Degree"].append(
                avg_degree
            )
            _, _, avg_strength = DirectedWeighted.calculate_average_weighted_degree(DiG)
            data["Average Strength"].append(
                avg_strength
            )
        df = pd.DataFrame(data)
        Draw.draw_dual_axis_plot(df,
                                 "Months/DirectedWeighted/DegreeAndWeightedDegree/",
                                 "Average Degree And Strength",
                                 "upper right"
        )

    @classmethod
    def degree_and_strength_std(cls):
        """
        度和强度的标准差的变化
        :return:
        """
        data = {
            "Time": [],
            "Degree Standard Deviation": [],
            "Strength Standard Deviation": []
        }
        for DiG, G, time in cls.get_networks_by_months():

            data["Time"].append(time)
            _, _, degree_std = DirectedWeighted.calculate_degree_standard_deviation(DiG)
            data["Degree Standard Deviation"].append(
                degree_std
            )

            _, _, weighted_degree_std = DirectedWeighted.calculate_weighted_degree_standard_deviation(DiG)
            data["Strength Standard Deviation"].append(
                weighted_degree_std
            )
        df = pd.DataFrame(data)

        Draw.draw_dual_axis_plot(df,
                                 "Months/DirectedWeighted/DegreeAndWeightedDegree/",
                                 "Degree And Strength \'s Standard Deviation",
                                 "upper right"
        )

    @classmethod
    def degree_distribution(cls):
        """
        画网络的度分布  多个时间段在一起的
        :return:
        """
        times = ["2018 06", "2019 06", "2020 06", "2021 06"]    # 可以在这里修改要画的时间段
        data = {}

        for time in times:
            _, G = Main.get_certain_networks_by_months(time)
            degree_frequency = Undirected.get_degree_distribution(G)  # 返回 {度值: 频率} 的字典
            # 先获取所有可能的度值（确保后续索引统一）
            all_degrees = sorted(degree_frequency.keys())  # 该时间段存在的度值（排序后）
            time_frequency_dict = {deg: degree_frequency[deg] for deg in all_degrees}
            # 存储该时间段的频率字典（而非 (degree, frequency) 元组列表）
            data[time] = time_frequency_dict

        # 1. 收集所有时间段的所有度值（作为最终 DataFrame 的索引）
        all_unique_degrees = set()
        for time_dict in data.values():
            all_unique_degrees.update(time_dict.keys())
        all_unique_degrees = sorted(list(all_unique_degrees))  # 排序后的所有度值（统一索引）

        # 2. 构建规整的 DataFrame：每行是一个度值，每列是一个时间段，值为频率（缺失填 0）
        df_data = {}
        for time in times:
            # 对于每个时间段，按统一的度值索引填充频率（无该度值则填 0）
            df_data[time] = [(deg, data[time].get(deg, 0)) for deg in all_unique_degrees]

        # 3. 创建 DataFrame，度值作为索引
        df = pd.DataFrame(df_data)
        Draw.draw_scatter_list(
            df,
            "Months/Undirected/DegreeDistribution/",
            "Degree",
            "Frequency",
            f"DegreeDistribution",
            "loglog"
        )

    @classmethod
    def k_and_knn(cls):
        """
        画 k 与 knn(k) 的散点图
        :return:
        """
        for _, G, time in cls.get_networks_by_months():

            null_model = NullModel.create_degree_distribution_null_model(G)
            # 执行计算
            knn_dict = Undirected.calculate_knn(G)
            null_model_knn_dict = Undirected.calculate_knn(null_model)

            data = {
                "Origin Network": [(k, v) for k, v in knn_dict.items()],
                "Null Model": [(k, v) for k, v in null_model_knn_dict.items()]
            }
            df = pd.DataFrame(data)
            Draw.draw_scatter_list(
                df,
                "Months/Undirected/KAndKnn/",
                "k",
                "knn(k)",
                f"k and knn(k) {time}",
                'loglog',
                colors=2,
                markers=2
            )

    @classmethod
    def different_type_k_and_knn(cls):
        """
        针对于有向加权网络 但是不考虑权重只考虑有向
        TODO 针对于有向无权的网络的零模型
        :return:
        """
        for degree_type in ["Out", "In"]:
            for neighbors_type in ["Out", "In"]:
                for DiG, G, time in Main.get_networks_by_months():
                    # null_model = NullModel.create_degree_distribution_null_model(DiG)
                    # 3. 执行计算
                    knn_dict = DirectedWeighted.calculate_knn_degree(DiG,
                                                                     degree_type, neighbors_type)
                    # null_model_knn_dict = DirectedWeighted.calculate_knn_strength(null_model)

                    data = {
                        "Origin Network": [(k, v) for k, v in knn_dict.items()]
                        # "Null Model": [(k, v) for k,v in null_model_knn_dict.items()]
                    }
                    df = pd.DataFrame(data)
                    Draw.draw_scatter_list(
                        df,
                        f"Months/DirectedWeighted/KAndKnn/{degree_type}{neighbors_type}/",
                        "k",
                        "knn(k)",
                        f"k and knn(k) {degree_type} {neighbors_type} {time}",
                        'loglog'
                    )

    @classmethod
    def degree_assortativity_coefficient(cls):
        """
        度同配系数的演化趋势
        :return:
        """
        data = {
            "Time": [],
            "Network": [],
            "Null Model": []
        }
        for DiG, G, time in cls.get_networks_by_months():
            null_model = NullModel.create_degree_distribution_null_model(G)

            assortativity_coefficient = nx.degree_assortativity_coefficient(G)
            assortativity_coefficient_null_model = nx.degree_assortativity_coefficient(null_model)

            data["Time"].append(time)
            data["Network"].append(assortativity_coefficient)
            data["Null Model"].append(assortativity_coefficient_null_model)
        df = pd.DataFrame(data)
        Draw.draw_plot(
            df,
            "Months/Undirected/AssortativityCoefficient/",
            "r",
            "assortativity coefficient",
            0.5
        )

    @classmethod
    def strength_and_directed_betweenness(cls):
        """
        画每个港口 加权度和有向介数中心性之间的关系
        :return:
        """
        # TODO 可以使用那个库函数
        for DiG, G, time in cls.get_networks_by_months():
            data = {}
            bc_dict = nx.betweenness_centrality(DiG, normalized=True)  # 有向网络的介数中心性  不适用加权
            for node, attr in DiG.nodes(data=True):
                dc = attr['total_TEU']
                bc = bc_dict[node]
                data[node] = [(dc, bc)]
            df = pd.DataFrame(data)
            Draw.draw_scatter_ports(df,
                                   "Months/DirectedWeighted/WeightedDegreeAndDirectedBetweenness/",
                                   "Weighted Degree",
                                   "Directed Betweenness",
                                   f"Weighted Degree And Directed Betweenness {time}",
                                   label=True,
                                    legend=False
            )

    @classmethod
    def write_ports_centrality(cls):
        """
        把港口的节点中心性写入json文件
        度中心性
        有向介数中心性
        加权pagerank中心性
        :return:
        """
        weighted_dc_record = {}
        weighted_bc_record = {}
        weighted_pagerank_record = {}

        for DiG, G, time in cls.get_networks_by_months():

            weighted_degree = dict(DiG.degree(weight='volumeTEU'))
            weighted_in_degree = dict(DiG.in_degree(weight='volumeTEU'))
            weighted_out_degree = dict(DiG.out_degree(weight='volumeTEU'))

            # 这边都不需要除以 n-1 不需要归一化
            dc = {node: d for node, d in weighted_degree.items()}
            in_dc = {node: d for node, d in weighted_in_degree.items()}
            out_dc = {node: d for node, d in weighted_out_degree.items()}

            # weighted node centrality
            node_dc = {}
            for node in DiG.nodes():
                node_dc[node] = {
                    'dc': dc[node],
                    'in_dc': in_dc[node],
                    'out_dc': out_dc[node]
                }
            weighted_dc_record[time] = node_dc

            # weighted betweenness centrality
            weighted_bc_record[time] = nx.betweenness_centrality(DiG, normalized=True)

            # weighted pagerank scores
            weighted_pagerank_record[time] = nx.pagerank(
                DiG,
                alpha=0.85,
                weight='volumeTEU',
                tol=1e-6
            )

        pathlib.Path('Output/Months/DirectedWeighted/PortsWeightedDegree/ports_weighted_degree_centrality.json').write_text(
            json.dumps(weighted_dc_record, indent=2))
        pathlib.Path('Output/Months/DirectedWeighted/PortsDirectedBetweenness/ports_weighted_betweenness_centrality.json').write_text(
            json.dumps(weighted_bc_record, indent=2))
        pathlib.Path('Output/Months/DirectedWeighted/PortsWeightedPageRank/ports_weighted_pagerank_scores.json').write_text(
            json.dumps(weighted_pagerank_record, indent=2))

    @classmethod
    def write_ports_weighted_degree_centrality_rank(cls):
        """
        把度中心性的排名写入csv文件
        :return:
        """
        centrality_type = [
            ('dc', 'PortsWeightedDegree', 'ports_weighted_degree_centrality.json'),
            ('in_dc', 'PortsWeightedDegree', 'ports_weighted_degree_centrality.json'),
            ('out_dc', 'PortsWeightedDegree', 'ports_weighted_degree_centrality.json')
        ]
        for type in centrality_type:
            file_path = f'Output/Months/DirectedWeighted/{type[1]}/{type[2]}'
            degree_centrality = json.loads(pathlib.Path(file_path).read_text())
            # 1. 对每个时间段的港口按dc降序排序，提取港口名称列表
            sorted_ports_by_time = {}
            for time, data in degree_centrality.items():
                # 按dc降序排序，取港口名称（如['USLSA', 'USLGB', 'CNSHA']）
                sorted_ports = [port for port, metrics in sorted(data.items(), key=lambda x: x[1][type[0]], reverse=True)]

                # 如果要筛选国家就使用下面这个 而且后面的保存文件名要修改
                # sorted_ports = [port for port, metrics in
                #                 sorted(data.items(), key=lambda x: x[1][type[0]], reverse=True)
                #                 if port_info[port]["country_english"] == 'China']

                sorted_ports_by_time[time] = sorted_ports
            # 2. 确定最大排名数（即所有时间段中港口数量最多的那个，保证行数足够）
            max_rank = max(len(ports) for ports in sorted_ports_by_time.values())
            # 3. 构建数据：行=排名（1,2,3...），列=时间段，值=港口名称
            rank_data = {}
            for time, ports in sorted_ports_by_time.items():
                # 为每个时间段填充港口名称，不足max_rank的用空值补充
                rank_data[time] = ports + [None] * (max_rank - len(ports))
            # 4. 转为DataFrame，行索引设为排名（1开始）
            df = pd.DataFrame(rank_data, index=range(1, max_rank + 1))
            # 5. 保存为CSV（index_label='排名'，明确行含义）
            df.to_csv(f'Output/Months/DirectedWeighted/{type[1]}/weighted_{type[0]}_sorted_ports_by_time.csv',
                      index_label='排名')

    @classmethod
    def draw_ports_degree_centrality_change(cls,
                                            target_ports: str
        ):
        """
        画单个港口的 度 入度 出度 变化趋势图
        使用的时候记得自己改名字
        :param target_ports: 例如 ： target_ports = 'VNVUT'
        :return:
        """
        file_path = f'Output/Months/DirectedWeighted/PortsWeightedDegree/ports_weighted_degree_centrality.json'
        degree_centrality = json.loads(pathlib.Path(file_path).read_text())
        degree_centrality_metric = ['dc', 'in_dc', 'out_dc']

        data = {
            "Time": []
        }
        for metrics in degree_centrality_metric:
            data[metrics] = []  # 为每个港口初始化空列表，避免KeyError
        for time, port_info in degree_centrality.items():
            data["Time"].append(time)
            for metrics in degree_centrality_metric:
                data[metrics].append(port_info[target_ports][metrics])

        df = pd.DataFrame(data)
        Draw.draw_plot(
            df,
            'Months/DirectedWeighted/PortsCentralityChangeByTime/',
            f'degree centrality',
            f'{target_ports} dc in_dc out_dc change by time'
        )
    #endregion

    @classmethod
    def nodes_or_edges_attack(cls, time:str, target_metric:str):
        """
        鲁棒脆弱性的模拟函数
        有些参数使用的时候就自己调一下了
        :param time:  "2017"
        :param target_metric: "LWCC"
        :return:
        """
        fraction_removed_list = list(np.linspace(0, 0.1, 50))
        DiG, _ = cls.get_certain_networks_by_years(time)

        # attack_strategies = {
        #     "random": Robustness.edge_attack_random,
        #     "degree": Robustness.edge_attack_degree,
        #     "strength": Robustness.edge_attack_strength,
        #     "betweenness": Robustness.edge_attack_betweenness
        # }
        attack_strategies = {
            "random": Robustness.node_attack_random,
            "degree": Robustness.node_attack_degree,
            "strength": Robustness.node_attack_strength,
            "betweenness": Robustness.node_attack_betweenness
        }
        metric_funcs = {
            "LSCC": Robustness.LSCC,
            "LWCC": Robustness.LWCC,
            "Efficiency": Robustness.Global_Efficiency
        }

        attack_results = {}
        for name, attack_func in attack_strategies.items():
            print(f"{name}攻击开始：")
            attack_results[name] = Robustness.simulate_attack(
                DiG,
                attack_func,
                metric_funcs,
                fraction_removed_list
            )
        (pathlib.Path(f'Output/Robustness/Nodes/{time} node attack.json')
         .write_text(json.dumps(attack_results, indent=2)))

        data = {
            "Fraction": attack_results["random"]["Fraction"],
            "random": attack_results["random"][target_metric],
            "degree": attack_results["degree"][target_metric],
            "strength": attack_results["strength"][target_metric],
            "betweenness": attack_results["betweenness"][target_metric]
        }
        df = pd.DataFrame(data)
        Draw.draw_plot(
            df,
            'Robustness/Nodes/',
            target_metric,
            f'{time} {target_metric} nodes attack',
            margin_rate=0.1,
            is_label_step=False,
            colors=3,
            markers=3
        )

    @classmethod
    def cascade_attack(cls):
        """
        级联故障的模拟函数
        :param time:
        :return:
        """
        for DiG, G, time in cls.get_networks_by_years():

            alpha_list = np.linspace(0, 1, 10)
            DiG, _ = Main.get_certain_networks_by_years(time)

            configure = {
                "random": Robustness.node_attack_random,
                "degree": Robustness.node_attack_degree,
                "strength": Robustness.node_attack_strength,
                "betweenness": Robustness.node_attack_betweenness
            }

            data = {
                "Fraction": [frac for frac in alpha_list]
            }
            for attack, func in configure.items():
                print(f"{attack}级联开始：")
                result = Robustness.simulate_cascade(DiG, alpha_list, func, Robustness.LWCC, mode="node")
                data[attack] = list(result.values())

            df = pd.DataFrame(data)
            Draw.draw_plot(
                df,
                f'Robustness/Cascade/Classic/',
                "LWCC Node",
                f"{time} LWCC Node",
                colors=1,
                markers=1
            )

    @classmethod
    def cascade_attack_unload(cls, time:str):
        """
        具有欠载的攻击流程函数
        :param time:
        :return:
        """
        # [beta, alpha]  节点容量的上下限
        # 使用numpy输出干净的小数 不然会出现 0.6000000000001 这种
        # 调节alpha和beta的范围和密度
        alpha_list = np.round(np.linspace(1, 2, 101), 3)
        beta_list = np.round(np.linspace(0, 1, 101), 3)

        DiG, _ = Main.get_certain_networks_by_years(time)

        configure = {
            "random": Robustness.node_attack_random,
            "degree": Robustness.node_attack_degree,
            "strength": Robustness.node_attack_strength,
            "betweenness": Robustness.node_attack_betweenness
        }

        for beta in beta_list:
            print(f"beta = {beta} 开始：")
            data = {
                "Alpha": [],
                "random": [],
                "degree": [],
                "strength": [],
                "betweenness": []
            }
            for alpha in tqdm(alpha_list):
                data["Alpha"].append(alpha)
                for attack, func in configure.items():
                    result = Robustness.simulate_underload_cascade(DiG, alpha, beta, func, Robustness.LWCC)
                    value = float(result[(alpha, beta)])
                    data[attack].append(value)

            df = pd.DataFrame(data)
            Draw.draw_plot(
                df,
                f'Robustness/Cascade/Unload/',
                f"beta={beta} LWCC",
                f"{time}_LWCC_beta_{beta}",
                colors=1,
                markers=1
            )

    #regionbeta并行版本
    # @classmethod
    # def cascade_attack_unload(cls, time: str):
    #
    #     alpha_list = np.round(np.linspace(1, 2, 51), 3)
    #     beta_list = np.round(np.linspace(0, 1, 51), 3)
    #
    #     DiG, _ = Main.get_certain_networks_by_years(time)
    #
    #     configure = {
    #         "random": Robustness.node_attack_random,
    #         "degree": Robustness.node_attack_degree,
    #         "strength": Robustness.node_attack_strength,
    #         "betweenness": Robustness.node_attack_betweenness
    #     }
    #
    #     tasks = [
    #         (cls, DiG, time, beta, alpha_list, configure)
    #         for beta in beta_list
    #     ]
    #
    #     # CPU核心数
    #     workers = os.cpu_count() - 1
    #
    #     print(f"使用 {workers} 个进程并行计算")
    #
    #     with Pool(workers) as pool:
    #         pool.map(_cascade_single_beta, tasks)
    # @classmethod
    # def _cascade_single_beta(args):
    #     cls, DiG, time, beta, alpha_list, configure = args
    #
    #     data = {
    #         "Alpha": [],
    #         "random": [],
    #         "degree": [],
    #         "strength": [],
    #         "betweenness": []
    #     }
    #
    #     for alpha in alpha_list:
    #         data["Alpha"].append(alpha)
    #
    #         for attack, func in configure.items():
    #             result = cls.simulate_underload_cascade(
    #                 DiG, alpha, beta, func, cls.LWCC
    #             )
    #
    #             value = float(result[(alpha, beta)])
    #             data[attack].append(value)
    #
    #     df = pd.DataFrame(data)
    #
    #     Draw.draw_plot(
    #         df,
    #         'Robustness/Cascade/Unload/',
    #         f"beta={beta} LWCC",
    #         f"{time}_LWCC_beta_{beta}",
    #         colors=1,
    #         markers=1
    #     )
    #
    #     return beta
    #endregion

    @classmethod
    def different_strategies_lwcc_cdf(cls):
        """
        cdf图  目前没有适配Draw类 没办法只能这样了
        不同的攻击策略对于LWCC的影响
        :return:
        """
        times = ["2017", "2018", "2019", "2020"]
        for time in times:
            # 读取数据
            df = pd.read_csv(f"Output/Robustness/Cascade/Unload/{time}_LWCC_beta_0.8.csv")

            attacks = ["random", "degree", "strength", "betweenness"]

            plt.figure(figsize=(7, 5))

            for attack in attacks:
                data = df[attack].values
                data = np.sort(data)

                cdf = np.arange(len(data)) / len(data)

                plt.plot(data, cdf, label=attack.capitalize())

            plt.xlabel("LWCC")
            plt.ylabel("CDF")
            plt.legend()

            plt.grid(alpha=0.3)

            plt.tight_layout()

            for for_mat in ["png", "eps"]:  # png and eps
                plt.savefig(f'Output/Robustness/Cascade/Unload/Strategy/'
                            f'{time}_different_strategies_LWCC.{for_mat}',
                            format=for_mat,  # 显式指定格式（可选，但更稳妥）
                            dpi=300,
                            bbox_inches='tight'  # 去除图片周围多余空白
                            )

    @classmethod
    def different_years_lwcc_bar(cls):
        """
        所有alpha和beta可能的参数下  网络崩溃的概率
        不同的年份所有参数下网络崩溃的概率
        :return:
        """
        years = [2017, 2018, 2019, 2020]
        betas = np.arange(0, 1.01, 0.1)

        threshold = 0.1

        random_prob = []
        degree_prob = []
        strength_prob = []
        betweenness_prob = []

        for year in years:

            r_list = []
            d_list = []
            s_list = []
            b_list = []

            for beta in betas:
                file = f"Output/Robustness/Cascade/Unload/{year}_LWCC_beta_{beta:.1f}.csv"

                df = pd.read_csv(file)

                r_list.append(np.mean(df["random"] < threshold))
                d_list.append(np.mean(df["degree"] < threshold))
                s_list.append(np.mean(df["strength"] < threshold))
                b_list.append(np.mean(df["betweenness"] < threshold))

            # 对所有 beta 取平均
            random_prob.append(np.mean(r_list))
            degree_prob.append(np.mean(d_list))
            strength_prob.append(np.mean(s_list))
            betweenness_prob.append(np.mean(b_list))

        data = [random_prob, degree_prob, strength_prob, betweenness_prob]
        labels = ["Random", "Degree", "Strength", "Betweenness"]

        colors = ["#0072B2", "#E69F00", "#009E73", "#D55E00"]

        x = np.arange(len(years))
        width = 0.18

        plt.figure(figsize=(8, 6))

        bars = []

        for i in range(4):
            bars.append(
                plt.bar(x + (i - 1.5) * width, data[i], width,
                        label=labels[i],
                        color=colors[i])
            )

        plt.xticks(x, years)

        plt.xlabel("Year")
        plt.ylabel("Collapse Probability")

        plt.ylim(0, 1)

        plt.legend(frameon=False)

        plt.grid(axis="y", linestyle="--", alpha=0.5)

        ax = plt.gca()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # 标注数值
        for bar_group in bars:
            for bar in bar_group:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2,
                         height + 0.02,
                         f"{height:.2f}",
                         ha="center",
                         va="bottom",
                         fontsize=9)

        plt.tight_layout()
        for for_mat in ["png", "eps", "pdf"]:  # png and eps
            plt.savefig(f'Output/Robustness/Cascade/Unload/Year/'
                        f'collapse_probability_different_years.{for_mat}',
                        format=for_mat,  # 显式指定格式（可选，但更稳妥）
                        dpi=300,
                        bbox_inches='tight'  # 去除图片周围多余空白
                        )