import networkx as nx
import numpy as np
from collections import defaultdict


class Undirected:
    """
    专门用于计算无向无权的网络的相关参数的 class
    """
    @classmethod
    def get_largest_connected_component(cls, g: nx.Graph) -> nx.Graph:
        """
        返回网络的最大连通分量的 拷贝
        :param g:
        :return:
        """
        print("网络不连通，使用最大连通分量计算")

        components = list(nx.connected_components(g))  # 转为列表便于处理
        # 找到节点数最多的最大连通分量
        largest_component = max(components, key=len)  # 按节点数取最大值
        # 提取最大连通分量的子图（保留边和节点属性）
        g_largest = g.subgraph(largest_component).copy()  # .copy() 确保可修改
        return g_largest
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
            g_largest = cls.get_largest_connected_component(g)
            diameter = nx.diameter(g_largest)
        return diameter

    @classmethod
    def calculate_average_shortest_path_length(cls, g:nx.Graph):
        """
        计算网络（或者最大连通分量）的平均最短路径
        :param g:
        :return:
        """
        if nx.is_connected(g):
            return nx.average_shortest_path_length(g)
        else:
            g_largest = cls.get_largest_connected_component(g)
            return nx.average_shortest_path_length(g_largest)

    @classmethod
    def calculate_algebraic_connectivity(cls, g:nx.Graph):
        """
        基于 laplcian 矩阵计算图的 代数连通性
        :param g:
        :return:
        """
        # 1. 计算拉普拉斯矩阵
        laplacian = nx.laplacian_matrix(g).todense()  # 转为稠密矩阵（便于计算特征值）

        # 2. 求解拉普拉斯矩阵的特征值，并排序
        eigenvalues = np.linalg.eigvals(laplacian)
        eigenvalues_sorted = np.sort(np.real(eigenvalues))  # 取实部并排序（避免数值误差）

        # 3. 代数连通性 = 第二小的特征值（lambda_1）
        algebraic_connectivity = eigenvalues_sorted[1]
        return algebraic_connectivity

    @classmethod
    def get_network_structure_metrics(cls, g:nx.Graph) -> dict:
        """
        网络的一些拓扑指标
        :param g:
        :return: 返回字典  key为不同的指标  value为不同的值
        """
        # 先算能够直接计算的
        N = g.number_of_nodes()
        M = g.number_of_edges()
        density = nx.density(g)
        avg_clustering = nx.average_clustering(g)  # 平均聚类系数

        avg_degrees = 2 * M / N  # 平均度

        # 无权谱半径
        A = nx.adjacency_matrix(g)
        spectral_radius = max(abs(np.linalg.eigvals(A.toarray())))  # 无权谱半径

        # 平均路径长度 and 全局效率
        if nx.is_connected(g):
            avg_length = nx.average_shortest_path_length(g)
            efficiency = nx.global_efficiency(g)
        else:
            h = cls.get_largest_connected_component(g)
            avg_length = nx.average_shortest_path_length(h)
            efficiency = nx.global_efficiency(h)

        mcc_sizes = len(h)          # 最大连通分量的大小
        # 结构同质性
        degrees = dict(nx.degree(g))
        degrees_list = list(degrees.values())
        std_degrees = np.std(degrees_list, ddof=0)
        homogeneity = 1 - std_degrees / avg_degrees  # 结构同质性

        # 同配性
        # 计算无向图的度数同配性
        assort_degree = nx.degree_assortativity_coefficient(g)

        return {
            "N": N,
            "M": M,
            "avg_clustering": avg_clustering,
            "avg_degrees": avg_degrees,
            "avg_length": avg_length,
            "efficiency": efficiency,
            "homogeneity": homogeneity,
            "density": density,
            "spectral_radius": spectral_radius,
            "mcc_sizes": mcc_sizes,
            "assortativity_coefficient": assort_degree
        }