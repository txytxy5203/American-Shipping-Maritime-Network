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

alpha_list = np.linspace(0, 0.3, 31)
time = "2017"
DiG,_ = Main.get_certain_networks_by_years(time)

result = Robustness.simulate_cascade(DiG, alpha_list,
                                     Robustness.node_attack_betweenness, Robustness.LWCC)

(pathlib.Path(f'Output/Robustness/Cascade/{time}.json')
         .write_text(json.dumps(result, indent=2)))
