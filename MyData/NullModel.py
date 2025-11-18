import random
import networkx as nx

class NullModel:
    @classmethod
    def create_degree_distribution_null_model(cls, original_g: nx.Graph) -> nx.Graph:
        """
        保持度序列一样的 null model
        :param original_g: 无向无权的图
        :return: null model
        """
        # 2. 提取原始网络的度序列

        null_model = original_g.copy()
        nx.double_edge_swap(null_model,
                            nswap=10 * null_model.number_of_edges(),    # 推荐重连次数是边的10倍
                            max_tries=10000000,
                            seed=random.randint(1, 1000000)
        )

        original_degree_sequence = [d for n, d in original_g.degree()]  # 格式：[节点0的度, 节点1的度, ...]
        null_model_degree_sequence = [d for n, d in null_model.degree()]

        if original_degree_sequence == null_model_degree_sequence:
            return null_model
        else:
            # 抛出异常，说明度序列不匹配，并显示差异
            raise ValueError(
                "零模型与原始网络的度序列不一致！\n"
            )

    @classmethod
    def create_edges_nodes_null_model(cls, original_g: nx.Graph) -> nx.Graph:
        """
        仅仅只是 edges 和 nodes 一样的 null model
        :param original_g:
        :return:
        """
        N = original_g.number_of_nodes()
        M = original_g.number_of_edges()

        # 使用随机图生成 null model
        null_model = nx.gnm_random_graph(
            n=N,
            m=M,
            seed=random.randint(1, 1000)
        )
        return null_model

    # TODO 生成一个权重分布一样的 null model
    # TODO 可以将节点的所有边的权重随机交换 这样就可以得到权重分布一样的null model