import random
import networkx as nx
import matplotlib.pyplot as plt

G = nx.cycle_graph(1000)
N = G.number_of_nodes()
P = [0.00015, 0.001,0.005, 0.01,0.05, 0.1,0.5 ,1]    # 重连的概率
L_ratio = []
C_ratio = []

def draw(G):
    plt.figure()
    nx.draw(G, node_size=2, width=0.1)
    plt.show()
def add_edge():
    # 添加连接
    for i in range(N):
        if i == N - 1:
            G.add_edge(N - 1, 1)
            G.add_edge(N - 1, 2)
            G.add_edge(N - 1, 3)
            G.add_edge(N - 1, 4)
        elif i == N - 2:
            G.add_edge(N - 2, 0)
            G.add_edge(N - 2, 1)
            G.add_edge(N - 2, 2)
            G.add_edge(N - 2, 3)
        elif i == N - 3:
            G.add_edge(N - 3, N - 1)
            G.add_edge(N - 3, 0)
            G.add_edge(N - 3, 1)
            G.add_edge(N - 3, 2)
        elif i == N - 4:
            G.add_edge(N - 4, N - 2)
            G.add_edge(N - 4, N - 1)
            G.add_edge(N - 4, 0)
            G.add_edge(N - 4, 1)
        elif i == N - 5:
            G.add_edge(N - 5, N - 3)
            G.add_edge(N - 5, N - 2)
            G.add_edge(N - 5, N - 1)
            G.add_edge(N - 5, 0)
        else:
            G.add_edge(i, i + 2)
            G.add_edge(i, i + 3)
            G.add_edge(i, i + 4)
            G.add_edge(i, i + 5)
def random_edge():
    # 随机连接
    # 1
    for i in range(N):
        if random.uniform(0, 1) < p:
            j = 0 if i == N - 1 else i + 1  # 正常是i + 1  i为N-1的时候 变成0
            # 重新链接
            G.remove_edge(i, j)  # 删去

            while True:
                random_i = random.randint(0, N - 1)  # randint是左闭右闭!!
                if random_i != i:
                    break
            G.add_edge(i, random_i)  # 添加
    # 2
    for i in range(N):
        if random.uniform(0, 1) < p:
            if i == N - 1:
                j = 1
            elif i == N - 2:
                j = 0
            else:
                j = i + 2

                # 重新链接
            G.remove_edge(i, j)  # 删去
            while True:
                random_i = random.randint(0, N - 1)
                if random_i != i:
                    break
            G.add_edge(i, random_i)  # 添加
    # 3
    for i in range(N):
        if random.uniform(0, 1) < p:
            if i == N - 1:
                j = 2
            elif i == N - 2:
                j = 1
            elif i == N - 3:
                j = 0
            else:
                j = i + 3

                # 重新链接
            G.remove_edge(i, j)  # 删去
            while True:
                random_i = random.randint(0, N - 1)
                if random_i != i:
                    break
            G.add_edge(i, random_i)  # 添加
    # 4
    for i in range(N):
        if random.uniform(0, 1) < p:
            if i == N - 1:
                j = 3
            elif i == N - 2:
                j = 2
            elif i == N - 3:
                j = 1
            elif i == N - 4:
                j = 0
            else:
                j = i + 4

                # 重新链接
            G.remove_edge(i, j)  # 删去
            while True:
                random_i = random.randint(0, N - 1)
                if random_i != i:
                    break
            G.add_edge(i, random_i)  # 添加
    # 5
    for i in range(N):
        if random.uniform(0, 1) < p:
            if i == N - 1:
                j = 4
            elif i == N - 2:
                j = 3
            elif i == N - 3:
                j = 2
            elif i == N - 4:
                j = 1
            elif i == N - 5:
                j = 0
            else:
                j = i + 5

                # 重新链接
            G.remove_edge(i, j)  # 删去
            while True:
                random_i = random.randint(0, N - 1)
                if random_i != i:
                    break
            G.add_edge(i, random_i)  # 添加


add_edge()
L_0 = nx.average_shortest_path_length(G)
C_0 = nx.average_clustering(G)
print("L_0:",L_0)
print("C_0:",C_0)
print(G.number_of_nodes())

# draw(G)

for p in P:
    G = nx.cycle_graph(1000)
    add_edge()
    random_edge()

    L_present = nx.average_shortest_path_length(G)
    C_present = nx.average_clustering(G)
    # print(L_present)
    # print(C_present)
    L_ratio.append(L_present / L_0)
    C_ratio.append(C_present / C_0)
    # draw(G)

plt.scatter(P,L_ratio,marker="v")
plt.scatter(P,C_ratio,marker="o")
plt.xscale("log")
plt.show()