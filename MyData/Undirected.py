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