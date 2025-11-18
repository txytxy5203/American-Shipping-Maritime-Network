import json
import pathlib
from collections import defaultdict

import numpy as np
import networkx as nx
import pandas as pd

from MyData.Draw import Draw
from Read import Read



class DirectedWeighted:
    """
    专门用于计算有向加权网络的相关参数
    """

    @classmethod
    def calculate_knn_strength(cls,
                               g: nx.DiGraph,
                               strength_type: str = "out",
                               neighbors_strength_type: str = "out",
                               ) -> dict:
        """
        计算有向加权网络的「强度的平均邻居强度」
        :param g: 有向加权图（nx.DiGraph，边属性需含'weight'）
        :param strength_type: 计算类型：
            - "out"：按节点「出强度」分组，计算「出邻居的平均入强度」（默认）
            - "in"：按节点「入强度」分组，计算「入邻居的平均出强度」
        :param neighbors_strength_type:
            邻居算出强度还是入强度
        :return: {s: knn(s)} 的字典（s=节点强度，knn(s)=该强度组的平均邻居强度）
        """
        # ----------------------
        # 1. 计算所有节点的出强度和入强度（替代原有的度）
        # ----------------------
        # 出强度：节点所有出边的权重之和（s_out(v) = sum(weight(v→u))）
        node_out_strength = dict(nx.out_degree_centrality(g, weight='total_TEU'))
        # 入强度：节点所有入边的权重之和（s_in(v) = sum(weight(u→v))）
        node_in_strength = dict(nx.in_degree_centrality(g, weight='total_TEU'))

        # ----------------------
        # 2. 按目标强度分组，收集对应邻居的强度
        # ----------------------
        strength_groups = defaultdict(list)  # {目标强度s: [邻居强度列表]}

        for node in g.nodes:
            # 2.1 确定当前节点的「目标强度」（按 strength_type 选择出/入强度）
            if strength_type == "out":
                target_strength = node_out_strength[node]  # 按出强度分组
                # 出邻居：当前节点指向的节点（v→u），取邻居的「入强度」（u的入强度包含v→u的权重）
                neighbors = g.successors(node)  # 有向图出邻居（successors）
                if neighbors_strength_type == "out":
                    neighbor_strengths = [node_out_strength[neigh] for neigh in neighbors]
                elif neighbors_strength_type == "in":
                    neighbor_strengths = [node_in_strength[neigh] for neigh in neighbors]
                else:
                    raise ValueError("neighbor_strength_type 只能是 'out' 或 'in'")
            elif strength_type == "in":
                target_strength = node_in_strength[node]  # 按入强度分组
                # 入邻居：指向当前节点的节点（u→v），取邻居的「出强度」（u的出强度包含u→v的权重）
                neighbors = g.predecessors(node)  # 有向图入邻居（predecessors）
                if neighbors_strength_type == "out":
                    neighbor_strengths = [node_out_strength[neigh] for neigh in neighbors]
                elif neighbors_strength_type == "in":
                    neighbor_strengths = [node_in_strength[neigh] for neigh in neighbors]
                else:
                    raise ValueError("neighbor_strength_type 只能是 'out' 或 'in'")
            else:
                raise ValueError("neighbor_strength_type 只能是 'out' 或 'in'")

            # 2.2 将邻居强度加入对应强度组（避免浮点数精度问题，保留3位小数）
            target_strength_rounded = round(target_strength, 3)
            strength_groups[target_strength_rounded].extend(neighbor_strengths)

        # ----------------------
        # 3. 计算每个强度组的平均邻居强度（knn(s)）
        # ----------------------
        knn_strength_dict = {}
        for s, neighbor_strengths in strength_groups.items():
            if neighbor_strengths:  # 跳过无邻居的节点（孤立节点）
                knn_strength_dict[s] = round(np.mean(neighbor_strengths), 3)  # 结果保留3位小数

        return knn_strength_dict

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

    #region讲道理这些东西要放在class里面吗
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
            file_path = f'Output/DirectedWeighted/{type[1]}/{type[2]}'
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
            df.to_csv(f'Output/DirectedWeighted/{type[1]}/weighted_{type[0]}_sorted_ports_by_time.csv',
                      index_label='排名')

    @classmethod
    def write_ports_weighted_betweenness_centrality_rank(cls):
        """
        把介数中心性的排名写入csv文件
        :return:
        """
        file_path = 'Output/DirectedWeighted/PortsDirectedBetweenness/ports_weighted_betweenness_centrality.json'
        degree_centrality = json.loads(pathlib.Path(file_path).read_text())
        # 1. 对每个时间段的港口按dc降序排序，提取港口名称列表
        sorted_ports_by_time = {}
        for time, data in degree_centrality.items():
            # 按dc降序排序，取港口名称
            sorted_ports = [port for port, metrics in sorted(data.items(), key=lambda x: x[1], reverse=True)]
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
        df.to_csv(f'Output/DirectedWeighted/PortsDirectedBetweenness/ports_weighted_bc_sorted_ports_by_time.csv', index_label='排名')

    # TODO PageRank排名还没有写

    @classmethod
    def draw_ports_degree_centrality_change(cls,
                                            target_ports:list,
                                            target_centrality:str,
        ):
        """
        画港口的度中心性变化趋势图
        使用的时候记得自己改名字
        :param target_ports: 例如 ： target_ports = ['VNVUT', 'KRBUS']]
        :param target_centrality: "dc", "in_dc", "out_dc
        :return:
        """
        file_path = f'Output/DirectedWeighted/PortsWeightedDegree/ports_weighted_degree_centrality.json'
        degree_centrality = json.loads(pathlib.Path(file_path).read_text())

        data = {
            "Time": []
        }
        for port in target_ports:
            data[port] = []  # 为每个港口初始化空列表，避免KeyError
        for time, port_info in degree_centrality.items():
            data["Time"].append(time)
            for port in target_ports:
                data[port].append(port_info[port][target_centrality])

        # 3. 空格连接（如 "VNVUT KRBUS"）
        str_joined_space = ' '.join(target_ports)
        df = pd.DataFrame(data)
        Draw.draw_plot(
            df,
            'DirectedWeighted/PortsCentralityChangeByTime/',
            f'{target_centrality}',
            f'{str_joined_space} {target_centrality} change by time'
        )
    #endregion