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
        degree_sequence = [d for n, d in original_g.degree()]  # 格式：[节点0的度, 节点1的度, ...]

        # 3. 用配置模型生成度序列相同的随机网络
        # 注：配置模型可能生成自环（节点连接自己）和多重边（两节点间多条边），需根据需求处理
        config_G = nx.configuration_model(degree_sequence, seed=1)  # seed固定随机数，保证可重复

        # 4. （可选）转换为简单图（移除自环和多重边，确保与原始网络一样是简单图）
        # 注意：移除后可能导致少数节点的度略微变化（若自环/多重边存在），需根据研究场景选择
        simple_config_G = nx.Graph(config_G)  # 自动合并多重边
        simple_config_G.remove_edges_from(nx.selfloop_edges(simple_config_G))  # 移除自环

        #  计算需补充的边数
        delta = original_g.number_of_edges() - simple_config_G.number_of_edges()
        if delta > 0:
            # print(f"需补充 {delta} 条边以匹配原始边数")

            # 4. 随机补边（仅向非邻接节点对添加）
            nodes = list(simple_config_G.nodes)
            added = 0
            while added < delta:
                # 随机选择两个不同的节点
                u, v = random.sample(nodes, 2)
                # 若节点对无边，则添加
                if not simple_config_G.has_edge(u, v):
                    simple_config_G.add_edge(u, v)
                    added += 1
        return simple_config_G