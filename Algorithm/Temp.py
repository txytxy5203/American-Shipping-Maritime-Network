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




date_str = "2017-01-01 00:00:00.000"
month_str = int(date_str[5:7])  # 输出："01"
print(month_str)
print(type(month_str))