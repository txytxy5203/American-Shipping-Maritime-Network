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




with open('../Data/Port/country_continent.json', 'r', encoding='utf-8') as f:
    country_dict = json.load(f)
txy = "tanxueyou"
print(txy[:2])