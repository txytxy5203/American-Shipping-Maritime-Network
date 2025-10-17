import networkx as nx
import matplotlib.pyplot as plt

'''
完成K-shell算法
'''

G = nx.karate_club_graph()

N = G.number_of_nodes()
k_shell_number = 1
k_shell = {}
bigBreak = True
degree = dict(G.weighted_degree())
del_nodes = []

while bigBreak:
    smallBreak = True
    while smallBreak:
        for node in G.nodes():
            if G.weighted_degree(node) <= k_shell_number:  # 注意这里是小于等于
                del_nodes.append(node)
                # G.remove_node(node)
                del degree[node]
                k_shell[node] = k_shell_number
        G.remove_nodes_from(del_nodes)
        del_nodes = []
        degree = dict(G.weighted_degree())


        if all(k_shell_number < value for value in degree.values()):   # 这里注意要是小于
            smallBreak = False

    k_shell_number += 1

    if len(k_shell) == N:
        bigBreak = False

print(k_shell)
# if k_shell_number in degree.values():
#     print(True)
# print(degree.values())
# print(G.nodes())

G = nx.karate_club_graph()
k_shell_subgraph = nx.k_shell(G,k=4)
print(list(k_shell_subgraph))