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



# # ---------- 主循环 ----------
# for year in years:
#     file_path = f'../Data/{year}/US/US{year}.graphml'
#     if not os.path.exists(file_path):
#         print(f'⚠️ 文件不存在: {file_path}')
#         continue
#     Multi_G = nx.read_graphml(file_path)
#     G = nx.Graph(Multi_G)  # 无向简单图，保留权重
#
#     res = calc_metrics(G)
#     res['year'] = year
#     records.append(res)