import os
import networkx as nx
import pandas as pd

from MyData.DirectedWeighted import DirectedWeighted
from MyData.Draw import Draw
from MyData.NullModel import NullModel
from MyData.Undirected import Undirected

class Main:
    """
    主类  所有出结果的函数全部放在这里面
    TODO 我的这些画图函数都需要增加一个检测有无csv文件的程序
    """
    #region网络生成器
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

    @classmethod
    def nodes_and_edges(cls):
        """
        节点和边的数量变化趋势图
        :return:
        """
        data = {
            "time":[],
            "nodes":[],
            "edges":[]
        }
        for DiG, G, time in cls.get_networks_by_months():
            data["time"].append(time)
            data["nodes"].append(G.number_of_nodes())
            data["edges"].append(G.number_of_edges())
        df = pd.DataFrame(data)
        Draw.draw_dual_axis_plot(
            df,
            "Months/Undirected/NodesAndEdges/",
            "Nodes And Edges",
            "lower left"
        )

    @classmethod
    def average_shortest_length(cls):
        """
        平均最短路径长度的变化趋势
        :return:
        """
        data = {
            "time":[],
            "Network":[],
            "Null Model":[]
        }
        for DiG, G, time in cls.get_networks_by_months():
            null_model = NullModel.create_edges_nodes_null_model(G)

            avg_shortest_length = Undirected.calculate_average_shortest_path_length(G)
            avg_shortest_length_null_model = Undirected.calculate_average_shortest_path_length(null_model)

            data["time"].append(time)
            data["Network"].append(avg_shortest_length)
            data["Null Model"].append(avg_shortest_length_null_model)
        df = pd.DataFrame(data)
        Draw.draw_plot(
            df,
            "Months/Undirected/AverageShortestLength/",
            "<L>",
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
            "time": [],
            "degree average": [],
            "strength average": []
        }
        for DiG, G, time in cls.get_networks_by_months():
            data["time"].append(time)

            _, _, avg_degree = DirectedWeighted.calculate_average_degree(DiG)
            data["degree average"].append(
                avg_degree
            )
            _, _, avg_strength = DirectedWeighted.calculate_average_weighted_degree(DiG)
            data["strength average"].append(
                avg_strength
            )
        df = pd.DataFrame(data)
        Draw.draw_dual_axis_plot(df,
                                 "Months/DirectedWeighted/DegreeAndWeightedDegree/",
                                 "Average Degree And Strength",
                                 "lower left"
        )

    @classmethod
    def degree_and_strength_std(cls):
        """
        度和强度的标准差的变化
        :return:
        """
        data = {
            "time": [],
            "degree standard deviation": [],
            "strength standard deviation": []
        }
        for DiG, G, time in cls.get_networks_by_months():

            data["time"].append(time)
            _, _, degree_std = DirectedWeighted.calculate_degree_standard_deviation(DiG)
            data["degree standard deviation"].append(
                degree_std
            )

            _, _, weighted_degree_std = DirectedWeighted.calculate_weighted_degree_standard_deviation(DiG)
            data["strength standard deviation"].append(
                weighted_degree_std
            )
        df = pd.DataFrame(data)

        Draw.draw_dual_axis_plot(df,
                                 "Months/DirectedWeighted/DegreeAndWeightedDegree/",
                                 "Degree And Strength \'s Standard Deviation",
                                 "lower left"
        )

    @classmethod
    def degree_distribution(cls):
        """
        画网络的度分布
        :return:
        """
        for DiG, G, time in cls.get_networks_by_months():
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



