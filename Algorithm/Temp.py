import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import sys
sys.path.append('../Algorithm')
import re
import json
import powerlaw
from ConstructNetwork import *





# 假设有一个MultiDiGraph对象G
G_multi = nx.MultiDiGraph()
G_multi.add_edge(1, 2)  # 添加多条边
G_multi.add_edge(1, 2)
G_multi.add_edge(2, 1)  # 反向边
G_multi.add_edge(1, 3)  # 反向边

print(nx.degree(G_multi))
degree_frequency_numbers = nx.degree_histogram(G_multi)  # 度的频数
print(degree_frequency_numbers)

N = G_multi.number_of_nodes()
# [0, 675, 789, 676, 428, 258, 205, 153, 140, 99, 92, 65, 45, 57, 38, 48, 25, 44, 20, 18, 28, 16, 12, ...]
# print(len(nx.degree_histogram(G)))  # 82
x_degree = list(range(len(degree_frequency_numbers)))  # 所有的度数 作为下面画图的x坐标

# 删去 度为0的元素
for i in sorted(x_degree, reverse=True):  # 注意这里要反向遍历 不然索引会出问题
    if degree_frequency_numbers[i] == 0:
        del degree_frequency_numbers[i]
        del x_degree[i]

degree_frequency = [x / N for x in degree_frequency_numbers]  # 度的频率

# 初始化幂律拟合对象
fit = powerlaw.Fit(x_degree, xmin=min(x_degree))

# 获取拟合参数
alpha = fit.power_law.alpha
x_min = fit.power_law.xmin

# 绘制原始数据点
plt.scatter(x_degree, degree_frequency, color='blue', label='Ports')

# 绘制拟合得到的幂律分布曲线
pdf = fit.power_law.pdf(x_degree)
plt.plot(x_degree, pdf, color='red', linestyle='--', label=f'Fit $k^{{{-alpha:.3f}}}$')

# 设置对数坐标轴
plt.xscale("log")
plt.yscale("log")

# 设置坐标轴范围
plt.xlim([min(x_degree) * 0.6, max(x_degree) * 1.7])  # 设置x轴范围为数据的最小值到最大值的1.1倍
plt.ylim([min(degree_frequency) * 0.6, max(degree_frequency) * 1.7])  # 设置y轴范围为数据的最小值到最大值的1.1倍

# 添加图例和标题
plt.legend()
plt.title("Degree Distribution")
plt.xlabel("Degree")
plt.ylabel("Degree Frequency")
plt.show()
# # 转换为无向图（忽略多重边和方向）
# G_1 = nx.Graph(G_multi)  # 或使用G_multi.to_undirected(as_view=False)
# G_2 = nx.Graph()
# G_2.add_edge(1, 2)
# G_2.add_edge(1, 3)
#
# g = nx.Graph()
# g.add_edge(0, 1)
# # g.add_edge(0, 2)
# g.add_edge(1, 2)
# g.add_edge(3, 2)
# # g.add_edge(1, 3)
# # g.add_edge(0, 3)

# G_combined = nx.compose(G_1, G_2)
# G_combined = nx.compose(G_combined, G_3)
# # 使用 GraphML 保存图
# # nx.write_graphml(G_combined, '../Data/FinalGraph/test.graphml')
#
# # # 验证结果
# print(G_combined.edges())

