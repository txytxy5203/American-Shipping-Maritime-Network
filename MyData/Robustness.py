import networkx as nx
import numpy as np


class Robustness:
    #regionMetrics
    @classmethod
    def LSCC(cls, g:nx.DiGraph):
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
            return len(lscc)
        except ValueError:
            print("没有强连通分量")
            return 0.0

    @classmethod
    def LWCC(cls, g:nx.DiGraph):
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
            return len(lwcc)
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
    def node_attack_random(cls, G, k):
        """
        随机攻击  k个节点
        :param G:
        :param k:
        :return:
        """
        return np.random.choice(list(G.nodes()), size=k, replace=False)

    @classmethod
    def node_attack_degree(cls, G, k):
        nodes_by_degree = sorted(
            G.degree(weight=None),
            key=lambda x:x[1],
            reverse=True
        )
        return [node for node, _ in nodes_by_degree[:k]]

    @classmethod
    def node_attack_strength(cls, G, k):
        # 依据节点的 'total_TEU' 属性值进行攻击（默认攻击值最大的节点）
        # 1. 筛选出具有 'total_TEU' 属性的节点
        nodes_with_teu = [
            (node, G.nodes[node]['total_TEU'])
            for node in G.nodes()
            # if 'total_TEU' in G_current.nodes[node]     # 不想加这个if 因为我的节点应该都有total_TEU属性
        ]
        # 2. 按 'total_TEU' 属性值降序排序（攻击值最大的节点）
        nodes_with_teu_sorted = sorted(nodes_with_teu, key=lambda x: x[1], reverse=True)

        # 3. 选择前 num_to_remove 个节点
        return [node for node, _ in nodes_with_teu_sorted[:k]]

    @classmethod
    def node_attack_betweenness(cls, G, k):
        bc = nx.betweenness_centrality(G)
        nodes = sorted(bc.items(), key=lambda x: x[1], reverse=True)
        return [n for n, _ in nodes[:k]]
    #endregion

    @classmethod
    def simulate_attack(cls, g:nx.DiGraph, attack_func:callable,
                        metric_funcs:dict, fraction_removed_list:list):



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

        for frac in fraction_removed_list:
            G_current = G0.copy()
            k = int(frac * N0)

            if k > 0:
                # 目前只有节点攻击
                nodes_to_remove = attack_func(G_current, k)
                G_current.remove_nodes_from(nodes_to_remove)

            results["Fraction"].append(frac)

            for name, func in metric_funcs.items():
                # 允许指标函数自己决定是否需要 N0
                value = func(G_current)
                results[name].append(value)

        return results