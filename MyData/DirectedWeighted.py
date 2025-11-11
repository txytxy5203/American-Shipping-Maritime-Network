import json
import pathlib

import numpy as np
import networkx as nx
from Read import Read



class DirectedWeighted:
    """
    专门用于计算有向加权网络的相关参数
    """

    @classmethod
    def calculate_average_degree(cls, g: nx.DiGraph):
        """
        计算有向加权网络的平均度  这里的 度 = 出度 + 入度
        :param g:
        :return: 入度平均值  出度平均值  总度平均值
        """
        # 获取所有节点的入度、出度
        in_degrees = [degree for node, degree in g.in_degree()]  # 入度列表
        out_degrees = [degree for node, degree in g.out_degree()]  # 出度列表
        total_degrees = [in_d + out_d for in_d, out_d in zip(in_degrees, out_degrees)]  # 总度列表（入度+出度）

        # 计算平均值
        in_degree_mean = np.mean(in_degrees)
        out_degree_mean = np.mean(out_degrees)
        total_degree_mean = np.mean(total_degrees)

        return in_degree_mean, out_degree_mean, total_degree_mean

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
        return in_degree_std, out_degree_std, total_degree_std

    @classmethod
    def get_network_weighted_degree(cls, g: nx.DiGraph):
        """
        得到DiGraph的加权度的list
        :param g:
        :return:
        """
        # 1. 获取所有节点的入度、出度
        in_weighted_degrees = [attr['in_TEU'] for node, attr in g.nodes(data=True)]  # 入度列表
        out_weighted_degrees = [attr['out_TEU'] for node, attr in g.nodes(data=True)]  # 出度列表
        total_weighted_degrees = [attr['total_TEU'] for node, attr in g.nodes(data=True)]  # 总度列表（入度+出度）

        return in_weighted_degrees, out_weighted_degrees, total_weighted_degrees
    @classmethod
    def calculate_average_weighted_degree(cls, g:nx.DiGraph):
        """
        计算有向加权网络的平均加权度
        :param g:
        :param weight:
        :return:
        """
        in_weighted_degrees, out_weighted_degrees, total_weighted_degrees = cls.get_network_weighted_degree(g)

        return np.mean(in_weighted_degrees), np.mean(out_weighted_degrees), np.mean(total_weighted_degrees)

    @classmethod
    def calculate_weighted_degree_standard_deviation(cls, g: nx.DiGraph):
        # 1. 获取所有节点的入度、出度

        in_weighted_degrees, out_weighted_degrees, total_weighted_degrees = cls.get_network_weighted_degree(g)

        return np.std(in_weighted_degrees, ddof=0), np.std(out_weighted_degrees, ddof=0), np.std(total_weighted_degrees, ddof=0)

    @classmethod
    def write_ports_centrality(cls):
        """
        把港口的节点中心性写入json文件
        :return:
        """
        weighted_dc_record = {}
        weighted_bc_record = {}
        weighted_pagerank_record = {}

        for DiG, G, time in Read.get_network():

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

        pathlib.Path('Output/DirectedWeighted/PortsWeightedDegree/ports_weighted_degree_centrality.json').write_text(
            json.dumps(weighted_dc_record, indent=2))
        pathlib.Path('Output/DirectedWeighted/PortsDirectedBetweenness/ports_weighted_betweenness_centrality.json').write_text(
            json.dumps(weighted_bc_record, indent=2))
        pathlib.Path('Output/DirectedWeighted/PortsWeightedPageRank/ports_weighted_pagerank_scores.json').write_text(
            json.dumps(weighted_pagerank_record, indent=2))