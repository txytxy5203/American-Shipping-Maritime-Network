import networkx as nx
import numpy as np
from collections import defaultdict


class Undirected:
    """
    专门用于计算无向无权的网络的相关参数的 class
    """
    @classmethod
    def calculate_knn(cls, g:nx.Graph):
        """
        计算网络的 knn(k)
        :param g:
        :return: 返回 {k: knn(k)} 的字典
        """
        # 计算每个节点的度
        node_degrees = dict(g.degree())  # {节点: 度k}

        # 按节点度 k 分组，收集所有邻居的度
        degree_groups = defaultdict(list)  # {k: [邻居的度列表]}
        for node in g.nodes:
            k = node_degrees[node]  # 当前节点的度
            # 获取所有邻居的度
            neighbors = g.neighbors(node)
            neighbor_degrees = [node_degrees[neigh] for neigh in neighbors]
            # 加入对应分组
            degree_groups[k].extend(neighbor_degrees)

        # 计算每个 k 对应的 knn(k)（邻居度的平均值）
        knn_dict = {}
        for k, neighbor_degrees in degree_groups.items():
            if neighbor_degrees:  # 避免空列表（孤立节点）
                knn_dict[k] = np.mean(neighbor_degrees)
        return knn_dict

    @classmethod
    def calculate_diameter(cls, g:nx.Graph):
        """
        计算网络（或者是最大连通分量）的直径
        :param g:
        :return: 网络（或者是最大连通分量）的直径
        """
        # 2. 检查网络是否连通（直径仅对连通网络有意义）
        if nx.is_connected(g):
            # 3. 计算直径
            diameter = nx.diameter(g)
        else:
            print("网络不连通，使用最大连通分量计算直径")
            components = list(nx.connected_components(g))  # 转为列表便于处理

            # 3. 找到节点数最多的最大连通分量
            largest_component = max(components, key=len)  # 按节点数取最大值

            # 4. 提取最大连通分量的子图（保留边和节点属性）
            g_largest = g.subgraph(largest_component).copy()  # .copy() 确保可修改
            diameter = nx.diameter(g_largest)
        return diameter

    @classmethod
    def calculate_average_shortest_path_length(cls, g:nx.Graph):
        """
        计算网络（或者最大连通分量）的平均最短路径
        :param g:
        :return:
        """
        components = list(nx.connected_components(g))  # 转为列表便于处理

        # 3. 找到节点数最多的最大连通分量
        largest_component = max(components, key=len)  # 按节点数取最大值

        # 4. 提取最大连通分量的子图（保留边和节点属性）
        g_largest = g.subgraph(largest_component).copy()  # .copy() 确保可修改
        return nx.average_shortest_path_length(g_largest)