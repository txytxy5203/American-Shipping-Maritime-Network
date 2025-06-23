import nltk
from fontTools.misc.bezierTools import epsilon
# nltk.download('wordnet') # 第一次运行需运行此命令，安装wordnet数据集
from nltk.corpus import wordnet as wn
from math import *
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import networkx as nx



network = {} # 构建层级网络
last_level = 8 # 最深的层设置为8层
levelOfNode = {} # 数据的层级信息，0为哺乳动物（根节点），1为哺乳动物下一结构

# 递归构建network
def get_hyponyms(synset, level):
    if (level == last_level):
        levelOfNode[str(synset)] = level
        return
    if not str(synset) in network:
        network[str(synset)] = [str(s) for s in synset.hyponyms()]
        levelOfNode[str(synset)] = level
    for hyponym in synset.hyponyms():
        get_hyponyms(hyponym, level + 1)

# 构建以哺乳动物为根节点的层次结构数据集
mammal = wn.synset('mammal.n.01')
get_hyponyms(mammal, 0)
levelOfNode[str(mammal)] = 0

# 将终端叶子节点补到network字典中
for a in levelOfNode:
    if not a in network:
        network[a] = []


def norm(x):
    return np.dot(x, x)
def traverse(graph, start, node):
    node_name = node.name().split(".")[0]
    graph.depth[node_name] = node.shortest_path_distance(start)

    for child in node.hyponyms():
        child_name = child.name().split(".")[0]
        graph.add_edge(node_name, child_name)  # 添加边
        traverse(graph, start, child)  # 递归构建

def hyponym_graph(start):
    G = nx.Graph()  # 定义一个图
    G.depth = {}
    traverse(G, start, start)
    return G

def graph_draw(graph):
    plt.figure(figsize=(10, 10))  # 展示整体的网络
    # plt.figure(figsize=(3, 3)) # 展示大象网络
    nx.draw(graph,
            node_size=[10 * graph.degree(n) for n in graph],
            node_color=[graph.depth[n] for n in graph],
            alpha=0.8,
            font_size=4,
            width=0.5,
            with_labels=True)

    def get_keys(d, value):
        return [k for k, v in d.items() if v == value]

    root_name = get_keys(graph.depth, 0)[0]
    plt.savefig("./" + root_name + ".png", dpi=300)


# 全部的
graph = hyponym_graph(mammal)
graph_draw(graph)

## 大象的
# elephant = wn.synset('elephant.n.01')
# graph = hyponym_graph(elephant)
# graph_draw(graph)


def dist1(vec1, vec2):
    diff_vec = vec1 - vec2
    return 1 + 2 * norm(diff_vec) / ((1 - norm(vec1)) * (1 - norm(vec2)))

# 范数计算
def norm(x):
    return np.dot(x, x)

# 距离函数对 \theta 求偏导
def compute_distance_gradients(theta, x, gamma):
    alpha = 1.0 - np.dot(theta, theta)
    norm_x = norm(x)
    beta = 1.0 - norm(x)
    c_ = 4.0 / (alpha * beta * sqrt(gamma ** 2 - 1))
    return c_ * ((norm_x - 2 * np.dot(theta, x) + 1) * theta / alpha  - x)

# 更新公式
def update(emb, grad ,lr):
    c_ = (1 - norm(emb)) ** 2 / 4
    upd = lr * c_ * grad
    emb = emb - upd
    if norm(emb) >= 1:
        emb = emb / sqrt(norm(emb)) - epsilon
    return emb

# embedding 情况绘图
def plotall(ii):
    fig = plt.figure(figsize=(10, 10))
    # 绘制所有节点
    for a in emb:
        plt.plot(emb[a][0], emb[a][1], marker = 'o', color = [levelOfNode[a]/(last_level+1),levelOfNode[a]/(last_level+1),levelOfNode[a]/(last_level+1)])
    for a in network:
        for b in network[a]:
            plt.plot([emb[a][0], emb[b][0]], [emb[a][1], emb[b][1]], color = [levelOfNode[a]/(last_level+1),levelOfNode[a]/(last_level+1),levelOfNode[a]/(last_level+1)])
            circle = plt.Circle((0, 0), 1, color='y', fill=False)
            plt.gcf().gca().add_artist(circle)
    plt.xlim(-1, 1)
    plt.ylim(-1, 1)
    fig.savefig('../Figure/' + str(last_level) + '_' + str(ii) + '.png', dpi = 200)

# 训练过程
emb = {}
for node in levelOfNode:
    emb[node] = np.random.uniform(low = -0.001, high = 0.001, size = (2, ))
vocab = list(emb.keys())
eps = 1e-5     # 更新函数中用的
lr = 0.1       # 学习率
num_negs = 10  # 负样本个数
epoch_number = 2000 # 训练轮数

print("emb:")
print(emb)
print("vocab:")
print(vocab)

# 绘制初始化权重
plotall("init")

# for epoch in range(epoch_number):
#     loss = []
#     random.shuffle(vocab)
#
#     # 下面需要抽取不同的样本：pos2 与 pos1 相关；negs 不与 pos1 相关
#     for pos1 in vocab:
#         if not network[pos1]:  # 叶子节点则不进行训练
#             continue
#         pos2 = random.choice(network[pos1])  # 随机选取与pos1相关的节点pos2
#         dist_pos_ = dist1(emb[pos1], emb[pos2])  # 保留中间变量gamma，加速计算
#         dist_pos = np.arccosh(dist_pos_)  # 计算pos1与pos2之间的距离
#
#         # 下面抽取负样本组（不与pos1相关的样本组）
#         negs = [[pos1, pos1]]
#         dist_negs_ = [1]
#         dist_negs = [0]
#
#         while (len(negs) < num_negs):
#             neg = random.choice(vocab)
#
#             # 保证负样本neg与pos1没有边相连接
#             if not (neg in network[pos1] or pos1 in network[neg] or neg == pos1):
#                 dist_neg_ = dist1(emb[pos1], emb[neg])
#                 dist_neg = np.arccosh(dist_neg_)
#                 negs.append([pos1, neg])
#                 dist_negs_.append(dist_neg_)  # 保存中间变量gamma，加速计算
#                 dist_negs.append(dist_neg)
#
#         # 针对一个样本的损失
#         loss_neg = 0.0
#         for dist_neg in dist_negs:
#             loss_neg += exp(-1 * dist_neg)
#         loss.append(dist_pos + log(loss_neg))
#
#         # 损失函数 对 正样本对 距离 d(u, v) 的导数
#         grad_L_pos = -1
#
#         # 损失函数 对 负样本对 距离 d(u, v') 的导数
#         grad_L_negs = []
#         for dist_neg in dist_negs:
#             grad_L_negs.append(exp(-dist_neg) / loss_neg)
#
#         # 计算正样本对中两个样本的embedding的更新方向
#         grad_pos1 = grad_L_pos * compute_distance_gradients(emb[pos1], emb[pos2], dist_pos_)
#         grad_pos2 = grad_L_pos * compute_distance_gradients(emb[pos2], emb[pos1], dist_pos_)
#
#         # 计算负样本对中所有样本的embedding的更新方向
#         grad_negs_final = []
#         for (grad_L_neg, neg, dist_neg_) in zip(grad_L_negs[1:], negs[1:], dist_negs_[1:]):
#             grad_neg0 = grad_L_neg * compute_distance_gradients(emb[neg[0]], emb[neg[1]], dist_neg_)
#             grad_neg1 = grad_L_neg * compute_distance_gradients(emb[neg[1]], emb[neg[0]], dist_neg_)
#             grad_negs_final.append([grad_neg0, grad_neg1])
#
#         # 更新embeddings
#         emb[pos1] = update(emb[pos1], -grad_pos1, lr)
#         emb[pos2] = update(emb[pos2], -grad_pos2, lr)
#         for (neg, grad_neg) in zip(negs, grad_negs_final):
#             emb[neg[0]] = update(emb[neg[0]], -grad_neg[0], lr)
#             emb[neg[1]] = update(emb[neg[1]], -grad_neg[1], lr)
#
#     # 输出损失
#     if ((epoch) % 10 == 0):
#         print(epoch + 1, "---Loss: ", sum(loss))
#
#     # 绘制二维embeddings
#     if ((epoch) % 100 == 0):
#         plotall(epoch + 1)

