import networkx as nx
import matplotlib.pyplot as plt
'''
PageRank算法 用networkx实现
'''
# 创建有向图
G = nx.karate_club_graph()

nx.draw(G, with_labels=True)
plt.show()
pagerank_list = nx.pagerank(G, alpha=0.85, max_iter=1000)
print("pagerank值是：\n", pagerank_list)
# 根据字典的值进行降序排序
sorted_data = sorted(pagerank_list.items(), key=lambda x: x[1], reverse=True)
# sorted_list = [value for key, value in sorted_data]
print(sorted_data)
