import networkx as nx
import matplotlib.pyplot as plt

G = nx.karate_club_graph()
nx.draw(G, with_labels=True)
plt.show()

# 遍历整个图
for n in G:
    print(n)
# 遍历一个节点的邻居
for n in G[16]:
    print(n)
print('---------')

# 边的数据接口
# print(G[1][2]['size'])
# print(G.edges[1, 2]['color'])

print('---------')

# 获取节点 1 的 AtlasView
atlas = G[1]  # 或 G.adj[1]
print(atlas)  # 输出：AtlasView({2: {'weight': 4.7}, 3: {'weight': 3.2}})
# 访问邻居及其边的属性
for neighbor, attrs in atlas.items():
    print(f"Neighbor: {neighbor}, Attributes: {attrs}")

# subgraph_view 过滤节点和边 是一个视图
def filter_node(n1):
    return n1 != 5
view = nx.subgraph_view(G, filter_node=filter_node)
print(view.nodes())

# # 设置 节点 边 属性
# nx.set_node_attributes()
# nx.set_edge_attributes()