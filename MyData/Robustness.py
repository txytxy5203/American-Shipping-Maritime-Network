import random

import networkx as nx
import numpy as np
from tqdm import tqdm

class Robustness:
    #regionMetrics
    @classmethod
    def LSCC(cls, g, n0:int):
        """
        最大强连通分量（LSCC）大小  直接返回的比例 和最初的网络相比
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
    def LWCC(cls, g, n0:int):
        """
        最大弱连通分量（LWCC）大小
        :return:
        """
        if g.number_of_nodes() == 0:
            return 0.0

        # 所有弱连通分量  兼容了无向网络
        wccs = nx.weakly_connected_components(g) if g.is_directed() else nx.connected_components(g)

        try:
            # 返回最大的连通分量的大小
            lwcc = max(wccs, key=len)
            return len(lwcc) / n0
        except ValueError:
            print("没有连通分量")
            return 0.0

    @classmethod
    def Global_Efficiency(cls, g):
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

    @classmethod
    def Number_Of_Connected_Components(cls, g, n0:int):
        """连通块的个数 使用的是弱连通块  n0 实际上是没啥用的但是为了保证调用的时候不出问题"""
        size = nx.number_weakly_connected_components(g)
        return size

    #endregion

    #regionAttackStrategy
    @classmethod
    def node_attack_random(cls, g, frac):
        """
        随机攻击  k个节点
        :param g:
        :param frac: 移除的比例
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
    def node_attack_degree(cls, g, frac):
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
    def node_attack_strength(cls, g, frac):

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
    def node_attack_betweenness(cls, g, frac):
        N0 = g.number_of_nodes()
        k = int(N0 * frac)
        bc = nx.betweenness_centrality(g, normalized=True)
        nodes = sorted(bc.items(), key=lambda x: x[1], reverse=True)
        return {
            "type": "node",
            "targets": [n for n, _ in nodes[:k]]
        }

    @classmethod
    def edge_attack_random(cls, g, frac):
        M0 = g.number_of_edges()
        m = int(M0 * frac)
        return {
            "type": "edge",
            "targets": random.sample(list(g.edges()), k=m)
        }

    @classmethod
    def edge_attack_degree(cls, g, frac):
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
    def edge_attack_strength(cls, g, frac):
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
    def edge_attack_betweenness(cls, g, frac):
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
    def simulate_attack(cls, g, attack_func:callable,
                        metric_funcs:dict, fraction_removed_list:list):
        """
        模拟随机、蓄意攻击的函数
        适用 nodes 和 edges
        鲁棒性 和 脆弱性
        """

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

    @classmethod
    def simulate_cascade(cls, g_original, alpha_list,
                         attack_func:callable, metric_func:callable, mode:str):
        """
        经典级联故障模拟函数
        :param g_original:  有向网络
        :param alpha_list: eg: np.linspace(0, 1, 11)
        :param attack_func: 攻击策略 就是这个class中的函数
        :param metric_func: 指标函数
        :param mode:  "node" or "edge
        :return:
        """
        # TODO 有相变是不是因为整个网络被分成了两个块了？

        N0 = g_original.number_of_nodes()

        # 初始选择一个节点 or 边  用的还是这个class中的攻击策略函数  注意参数
        first_remove_item = attack_func(g_original, 0.1)["targets"][0]

        results = {}
        for alpha in tqdm(alpha_list, desc=f"模拟攻击："):

            g_copy = g_original.copy()
            # 初始化容量
            _, Capacity = cls.calculate_load_betweenness_func(alpha, g_copy, mode)

            remove_items = [first_remove_item]  # 先将第一个要移除的节点或者边加入list 触发Cascade
            while len(remove_items) > 0:
                # 移除 节点 or 边
                if mode == "node":
                    g_copy.remove_nodes_from(remove_items)
                elif mode == 'edge':
                    g_copy.remove_edges_from(remove_items)
                else:
                    raise ValueError("mode 有问题")
                remove_items = []

                if g_copy.number_of_nodes() == 0:
                    break

                # 重新计算负载
                current_load,_ = cls.calculate_load_betweenness_func(alpha, g_copy, mode)

                # 检测哪些 节点 or 边 要删除
                for item, val in current_load.items():
                    if val > Capacity[item]:
                        remove_items.append(item)
            metric = metric_func(g_copy, N0)
            results[alpha] = metric
        return results

    #regionload的不同计算方式
    @classmethod
    def calculate_load_betweenness_func(cls, alpha, g_copy, mode:str):
        """
        容量计算函数   后续可以自己修改
        目前使用介数中心性近似计算 ！！！
        :param alpha:
        :param g_copy:
        :param mode:  "node" or "edge"
        :return:  容量 和 负载
        """
        calc_func = nx.betweenness_centrality if mode == "node" else nx.edge_betweenness_centrality
        # 先计算容量

        raw_data = calc_func(g_copy, normalized=False, weight=None)

        # 因为我都是有向图所以不需要再去 乘以2
        load = {key: val for key, val in raw_data.items()}                  # 负载
        capacity = {edge: val * (1 + alpha) for edge, val in load.items()}  # 容量
        return load, capacity
    @classmethod
    def calculate_load_strength_func(cls, alpha, beta, g_copy, mode:str=""):
        """
        一个node 的 load 就是它的总的 teu 流量
        注意要重新根据边的 volumeTEU 计算节点的 total_TEU
        注意 返回的 capacity 的 value 中：第一个是下界 第二个是上界
        :param alpha: alpha 上界
        :param beta:  beta  下界
        :param g_copy:
        :param mode:
        :return:
        """

        # 先重新计算所有节点的流量信息
        for node in g_copy.nodes:
            g_copy.nodes[node]['in_TEU'] = 0
            g_copy.nodes[node]['out_TEU'] = 0
            g_copy.nodes[node]['total_TEU'] = 0
            TEU_in = 0
            TEU_out = 0
            for _, _, attr in g_copy.in_edges(node, data=True):
                TEU_in += attr.get("volumeTEU", 0)
            for _, _, attr in g_copy.out_edges(node, data=True):
                TEU_out += attr.get("volumeTEU", 0)
            g_copy.nodes[node]['in_TEU'] = TEU_in
            g_copy.nodes[node]['out_TEU'] = TEU_out
            g_copy.nodes[node]['total_TEU'] = TEU_in + TEU_out

        load = {node: attr["total_TEU"] for node,attr in g_copy.nodes(data=True)}
        capacity = {node: (teu * beta, teu * alpha) for node, teu in load.items()}
        return load, capacity
    #endregion

    @classmethod
    def redistribute_flow_from(cls, node, g_copy):
        """
        只需要改边  节点的total_TEU信息不要动 在外边更新
        当 node 即将失效时：
        - 其上游节点把原本发往 node 的流量
          按权重比例重新分配到其他下游节点
        - 下游节点不索取流量
          -> k
        i -> node ->j
          -> k
        :param node:
        :param g_copy:
        :return:
        """
        if node not in g_copy:
            return

        # 所有上游节点 i -> node
        predecessors = list(g_copy.predecessors(node))

        for i in predecessors:
            if i not in g_copy:
                continue

            # 1. 原本 i -> node 的流量
            if not g_copy.has_edge(i, node):
                continue

            lost_flow = g_copy[i][node].get("volumeTEU", 0.0)

            if lost_flow <= 0:
                continue


            # 3. 找 i 的其他下游节点
            successors = [
                k for k in g_copy.successors(i)
                if k != node and k in g_copy
            ]

            if len(successors) == 0:
                # 没有其他下游，流量直接损失
                continue

            # 4. 按权重比例分配
            total_weight = 0.0
            for k in successors:
                total_weight += g_copy[i][k].get("volumeTEU", 0.0)

            if total_weight <= 0:
                continue

            for k in successors:
                w_ik = g_copy[i][k].get("volumeTEU", 0.0)
                delta = lost_flow * (w_ik / total_weight)

                # 增加边流量
                g_copy[i][k]["volumeTEU"] += delta

            # 清空要被移除的边 虽然外边也会 remove edge
            g_copy[i][node]["volumeTEU"] = 0.0

        node_successors = [
            j for j in g_copy.successors(node)
            if j != node and j in g_copy
        ]

        # 5. node的下游节点
        for j in node_successors:
            delta = g_copy[node][j].get("volumeTEU", 0.0)

            # 减少边流量
            g_copy[node][j]["volumeTEU"] -= delta


    @classmethod
    def simulate_underload_cascade(cls, g_original, alpha_list, beta_list,
                                   attack_func:callable, metric_func:callable):
        """
        考虑欠载的模型  beta为下界  alpha为上界
        海运网络级联失效模拟
        """
        N0 = g_original.number_of_nodes()

        # 初始选择一个节点
        first_remove_item = attack_func(g_original, 0.5)["targets"][0]
        results = {}

        for alpha in alpha_list:
            print(f"{alpha} 级联开始：")
            for beta in tqdm(beta_list, desc=f"beta 扫描"):
                g_copy = g_original.copy()
                # 初始化容量
                _, Capacity = cls.calculate_load_strength_func(alpha, beta, g_copy)

                remove_items = [first_remove_item]

                while len(remove_items) > 0:
                    # 1. 流量重新分配（针对即将失效的节点）
                    for node in remove_items:
                        cls.redistribute_flow_from(node, g_copy)
                        # 2. 删除节点
                        g_copy.remove_node(node)

                    # ai给的代码是在重新分配后统一删除 但是我觉得应该在重新分配一个节点后就删除该节点
                    # 这涉及到同步还是异步的问题
                    # 2. 删除节点
                    # g_copy.remove_nodes_from(remove_items)

                    if g_copy.number_of_nodes() == 0:
                        break

                    # 3. 重新计算动态负载
                    current_load, _ = cls.calculate_load_strength_func(alpha, beta, g_copy)

                    # 4. 判断新一轮失效
                    remove_items = []
                    for node in current_load:
                        if current_load[node] < Capacity[node][0] \
                                or current_load[node] > Capacity[node][1]:
                            remove_items.append(node)
                metric = metric_func(g_copy, N0)
                results[(alpha, beta)] = metric
        return results


