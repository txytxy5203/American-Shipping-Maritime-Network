import numpy as np
import networkx as nx

class DirectedWeighted:
    """
    专门用于计算有向加权网络的相关参数
    """

    @classmethod
    def calculate_average_degree(cls, g: nx.DiGraph):
        """
        计算有向加权网络的平均度  这里的 度 = 出度 + 入度
        :param g:
        :param weight:  权重的key
        :return:
        """
        return 2 * g.number_of_edges() / g.number_of_nodes()
    @classmethod
    def calculate_degree_standard_deviation(cls, g: nx.DiGraph):
        """
        计算有向图中入度、出度、总度（入度+出度）的标准差
        :param g: 有向图（nx.DiGraph）
        :return: 入度标准差、出度标准差、总度标准差  三个值
        """
        # 1. 获取所有节点的入度、出度
        in_degrees = [degree for node, degree in g.in_degree()]  # 入度列表
        out_degrees = [degree for node, degree in g.out_degree()]  # 出度列表
        total_degrees = [in_d + out_d for in_d, out_d in zip(in_degrees, out_degrees)]  # 总度列表（入度+出度）

        # 2. 计算标准差
        # 总体标准差  设置 ddof=0
        in_degree_std = np.std(in_degrees, ddof=0)  # 入度标准差
        out_degree_std = np.std(out_degrees, ddof=0)  # 出度标准差
        total_degree_std = np.std(total_degrees, ddof=0)  # 总度标准差

        # 3. 返回结果（保留4位小数，便于阅读）
        return in_degree_std,out_degree_std,total_degree_std


    @classmethod
    def calculate_average_strength(cls, g:nx.DiGraph, weight='total_TEU'):
        """
        计算有向加权网络的平均加权度
        :param g:
        :param weight:
        :return:
        """
        weighted_degrees = []

        node_weighted_degree = sum(data[weight] for node,data in g.nodes(data=True))
        weighted_degrees.append(node_weighted_degree)

        # 3. 计算加权平均度
        avg_weighted_degree = sum(weighted_degrees) / g.number_of_nodes()
        return avg_weighted_degree
