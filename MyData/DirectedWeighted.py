import networkx as nx

class DirectedWeighted:
    """
    专门用于计算有向加权网络的相关参数
    """

    @classmethod
    def calculate_average_degree(cls, g: nx.DiGraph, weight='volumeTEU'):
        """
        计算有向加权网络的平均度  这里的 度 = 出度 + 入度
        :param g:
        :param weight:  权重的key
        :return:
        """
        return 2 * g.number_of_edges() / g.number_of_nodes()
    @classmethod
    def calculate_average_strength(cls, g:nx.DiGraph, weight='total_TEU'):
        # 2. 计算每个节点的加权度（关联边的权重之和）
        weighted_degrees = []

        node_weighted_degree = sum(data[weight] for node,data in g.nodes(data=True))
        weighted_degrees.append(node_weighted_degree)

        # 3. 计算加权平均度
        avg_weighted_degree = sum(weighted_degrees) / g.number_of_nodes()
        return avg_weighted_degree
