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




