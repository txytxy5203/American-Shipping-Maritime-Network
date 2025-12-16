import heapq
import json
import pathlib
import random
import re
from typing import Set
from matplotlib.lines import Line2D
import os
import networkx as nx
import seaborn as sns
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.special import comb
from networkx.algorithms.assortativity import degree_assortativity_coefficient
from tqdm import tqdm

from Algorithm.ConstructNetwork import ConstructNetwork
from sklearn.preprocessing import minmax_scale
from matplotlib import patheffects
from scipy import stats  # 用于线性回归拟合
from heapq import nlargest
from collections import deque
from collections import defaultdict
from matplotlib.path import Path
import matplotlib.patches as patches
import sys
from MyData.Draw import Draw
from MyData.NullModel import NullModel
from MyData.DirectedWeighted import DirectedWeighted
from MyData.Undirected import Undirected
from MyData.Read import Read
from MyData.Main import Main
from MyData.Robustness import Robustness
sys.path.append('../Algorithm')




time = "2017"
target_metric = "Efficiency"
fraction_removed_list = list(np.linspace(0, 0.05, 50))
DiG,_ = Main.get_certain_networks_by_years(time)

attack_strategies = {
    "random": Robustness.node_attack_random,
    "degree": Robustness.node_attack_degree,
    "strength": Robustness.node_attack_strength,
    "betweenness": Robustness.node_attack_betweenness
}
metric_funcs = {
    "LSCC": Robustness.LSCC,
    "LWCC": Robustness.LWCC,
    "Efficiency": Robustness.Global_Efficiency
}

attack_results = {}
for name, attack_func in attack_strategies.items():
    print(f"{name}攻击开始：")
    attack_results[name] = Robustness.simulate_attack(
        DiG,
        attack_func,
        metric_funcs,
        fraction_removed_list
    )
(pathlib.Path('Output/Robustness/Nodes/node_attack.json')
 .write_text(json.dumps(attack_results, indent=2)))

data = {
    "Fraction": attack_results["random"]["Fraction"],
    "random": attack_results["random"][target_metric],
    "degree": attack_results["degree"][target_metric],
    "strength": attack_results["strength"][target_metric],
    "betweenness": attack_results["betweenness"][target_metric]
}
df = pd.DataFrame(data)
Draw.draw_plot(
    df,
    'Robustness/Nodes/',
    target_metric,
    f'{time} {target_metric} nodes attack',
    margin_rate=0.1,
    is_label_step=False,
    colors=3,
    markers=3
)

