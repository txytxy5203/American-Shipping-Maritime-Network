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