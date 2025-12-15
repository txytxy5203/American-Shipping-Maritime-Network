import networkx as nx

class Robustness:
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