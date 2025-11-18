import os
import networkx as nx


class Main:
    """
    主类  所有出结果的函数全部放在这里面
    """
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