import random

import networkx as nx
import numpy as np
from tqdm import tqdm


class Robustness:
    #regionMetrics
    @classmethod
    def LSCC(cls, g:nx.DiGraph, n0:int):
        """
        最大强连通分量（LSCC）大小
        :return:
        """
        if g.number_of_nodes() == 0:
            return 0.0

        # 所有强连通分量
        sccs = nx.strongly_connected_components(g)

        try:
            # 返回最大的连通分量的大小
            lscc = max(sccs, key=len)
            return len(lscc) / n0
        except ValueError:
            print("没有强连通分量")
            return 0.0

    @classmethod
    def LWCC(cls, g:nx.DiGraph, n0:int):
        """
        最大弱连通分量（LWCC）大小
        :return:
        """
        if g.number_of_nodes() == 0:
            return 0.0

        # 所有弱连通分量
        wccs = nx.weakly_connected_components(g)

        try:
            # 返回最大的连通分量的大小
            lwcc = max(wccs, key=len)
            return len(lwcc) / n0
        except ValueError:
            print("没有连通分量")
            return 0.0

    @classmethod
    def Global_Efficiency(cls, g:nx.DiGraph):
        """
        Global Efficiency (无向，全局效率)

        - 忽略方向，反映物理连通性
        - 不连通节点对的贡献为 0
        - 节点攻击后，已删除节点不参与计算
        :param g:
        :return:
        """
        if g.number_of_nodes() <= 1:
            return 0.0

        # 1. 转为无向图（忽略方向）
        undirected_g = g.to_undirected()

        # 2. 使用 NetworkX 内置实现
        return nx.global_efficiency(undirected_g)
    #endregion

    #regionAttackStrategy
    @classmethod
    def node_attack_random(cls, g:nx.DiGraph, frac):
        """
        随机攻击  k个节点
        :param g:
        :param frac:
        :return:
        """
        # 这里使用G来计算N0是没有问题的，因为每个frac的攻击都是从最初始的网络开始攻击的
        N0 = g.number_of_nodes()
        k = int(N0 * frac)
        return {
            "type": "node",
            "targets": np.random.choice(list(g.nodes()), size=k, replace=False)
        }

    @classmethod
    def node_attack_degree(cls, g:nx.DiGraph, frac):
        N0 = g.number_of_nodes()
        k = int(N0 * frac)

        nodes_by_degree = sorted(
            g.degree(weight=None),
            key=lambda x:x[1],
            reverse=True
        )
        return {
            "type": "node",
            "targets": [node for node, _ in nodes_by_degree[:k]]
        }

    @classmethod
    def node_attack_strength(cls, g:nx.DiGraph, frac):

        N0 = g.number_of_nodes()
        k = int(N0 * frac)
        # 依据节点的 'total_TEU' 属性值进行攻击（默认攻击值最大的节点）
        # 1. 得到 'total_TEU' 属性
        nodes_with_teu = [
            (node, g.nodes[node]['total_TEU'])
            for node in g.nodes()
        ]
        # 2. 按 'total_TEU' 属性值降序排序（攻击值最大的节点）
        nodes_with_teu_sorted = sorted(nodes_with_teu, key=lambda x: x[1], reverse=True)

        # 3. 选择前 num_to_remove 个节点
        return {
            "type": "node",
            "targets": [node for node, _ in nodes_with_teu_sorted[:k]]
        }

    @classmethod
    def node_attack_betweenness(cls, g:nx.DiGraph, frac):
        N0 = g.number_of_nodes()
        k = int(N0 * frac)
        bc = nx.betweenness_centrality(g, normalized=True)
        nodes = sorted(bc.items(), key=lambda x: x[1], reverse=True)
        return {
            "type": "node",
            "targets": [n for n, _ in nodes[:k]]
        }

    @classmethod
    def edge_attack_random(cls, g:nx.DiGraph, frac):
        M0 = g.number_of_edges()
        m = int(M0 * frac)
        return {
            "type": "edge",
            "targets": random.sample(list(g.edges()), k=m)
        }

    @classmethod
    def edge_attack_degree(cls, g: nx.DiGraph, frac):
        """edge的度为连接的两个节点的度值之和"""
        M0 = g.number_of_edges()
        m = int(M0 * frac)

        edges_degree = {
            (u,v): g.degree[u] + g.degree[v] for u, v in g.edges()
        }
        edges_degree_sorted = sorted(
            edges_degree.items(),
            key=lambda x: x[1], reverse=True
        )

        return {
            "type": "edge",
            # 一个由 tuple 组成的 list
            "targets": [edge for edge, _ in edges_degree_sorted[:m]]
        }

    @classmethod
    def edge_attack_strength(cls, g: nx.DiGraph, frac):
        """edge的强度就是这条边的流量 哈哈哈"""
        M0 = g.number_of_edges()
        m = int(M0 * frac)

        edges_strength = {
            (u, v): data.get("total_TEU", 0.0) for u, v, data in g.edges(data=True)
        }
        edges_strength_sorted = sorted(
            edges_strength.items(),
            key=lambda x: x[1], reverse=True
        )

        return {
            "type": "edge",
            # 一个由 tuple 组成的 list
            "targets": [edge for edge, _ in edges_strength_sorted[:m]]
        }

    @classmethod
    def edge_attack_betweenness(cls, g:nx.DiGraph, frac):
        M0 = g.number_of_edges()
        m = int(M0 * frac)

        edge_bc = nx.edge_betweenness_centrality(g, normalized=True)
        edge_bc_sorted = sorted(
            edge_bc.items(),
            key=lambda x: x[1], reverse=True
        )
        return {
            "type": "edge",
            "targets": [edge for edge,_ in edge_bc_sorted[:m]]
        }
    #endregion

    @classmethod
    def simulate_attack(cls, g:nx.DiGraph, attack_func:callable,
                        metric_funcs:dict, fraction_removed_list:list):
        """模拟攻击的函数 适用 nodes 和 edges"""

        G0 = g.copy()
        N0 = G0.number_of_nodes()

        """
        returns = {
         "Fraction": [0.1, 0.2, 0.3],
         "Degree":   [0.9, 0.8, 0.7],
         "Strength":  [0.9, 0.8, 0.7]
        }
        """
        results = {
            "Fraction": [],
            **{metric: [] for metric in metric_funcs}
        }

        for frac in tqdm(fraction_removed_list):
            G_current = G0.copy()
            # k = int(frac * N0)

            # 1.对网络执行攻击
            if frac > 0:
                # 得到攻击的返回信息
                plan = attack_func(G_current, frac)
                # node or edge
                if plan["type"] == "node":
                    G_current.remove_nodes_from(plan["targets"])
                elif plan["type"] == "edge":
                    G_current.remove_edges_from(plan["targets"])
                else:
                    raise ValueError("攻击函数的返回type有问题")

            results["Fraction"].append(frac)
            # 2.计算攻击之后网络的指标
            for name, func in metric_funcs.items():
                # 这里用 “异常” 来做 “控制流” 了
                try:
                    value = func(G_current)
                except TypeError:
                    value = func(G_current, N0)
                results[name].append(value)

        return results