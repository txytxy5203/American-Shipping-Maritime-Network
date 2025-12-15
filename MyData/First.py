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





fraction_removed_list = np.linspace(0, 0.05, 50)
attack_strategies = {
    "random": node_attack_random,
    "strength": node_attack_strength,
    "betweenness": node_attack_betweenness
}

metric_funcs = {
    "LSCC": Robustness.LSCC,
    "LWCC": Robustness.LWCC,
    "Efficiency": Robustness.Global_Efficiency
}

attack_results = {}

for name, attack_func in attack_strategies.items():
    attack_results[name] = Robustness.simulate_attack(
        DiG,
        attack_func,
        metric_funcs,
        fraction_removed_list
    )