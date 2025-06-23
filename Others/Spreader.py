import random
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

# Read the data
path_to_data = 'C:/Users/Rong/Downloads/ca-GrQc/ca-GrQc.mtx'
data = pd.read_csv(path_to_data, delim_whitespace=True, skiprows=2, header=None)
data = data.astype(int)
# print(data.dtypes)
# Add edges
G = nx.Graph()
for index, row in data.iterrows():
    G.add_edge(row[0],row[1])



P = 0.03 # 感染概率
infectious_nodes = [2]   # 初始感染节点list

# 为每个初始感染节点设置初始颜色为黑色
for node in infectious_nodes:
    G.nodes[node]['color'] = 'black'

def spread_progress():
    # 传染步数
    for i in range(100):
        length_infect_nodes = len(infectious_nodes)
        count_number = 0

        # 遍历所有已感染的节点
        for infect_node in infectious_nodes:
            count_number += 1
            if count_number > length_infect_nodes:  # 在每个步长时间中 不处理新加入的元素
                break
            # 遍历该感染节点的邻居节点
            for neighbor in G.neighbors(infect_node):
                if neighbor not in infectious_nodes:
                    if random.uniform(0, 1) < P:
                        G.nodes[neighbor]['color'] = 'black'    # 修改节点颜色属性
                        infectious_nodes.append(neighbor)
    print(infectious_nodes)
    print(len(infectious_nodes))

spread_progress()


# print(max(degree.values()))  # max_degree 81
# print(G.number_of_nodes())   # N 4158
# print(G.number_of_edges())   # L 13422

# 绘制图
pos = nx.spring_layout(G)
# 从节点属性中读取颜色  如果没有默认使用 gray
node_colors = [G.nodes[node].get('color', 'gray') for node in G.nodes()]
nx.draw(G, pos, node_color=node_colors, node_size=2, width=0.1)
plt.show()
