import matplotlib.pyplot as plt
import pandas as pd
import sys

sys.path.append('..')
import Algorithm.Draw
from mpl_toolkits.basemap import Basemap


def Read_and_save_port_region():
    data_path = 'E:/panjivaUSImport.csv'

    df = pd.read_csv(data_path, usecols=['portOfUnladingRegion', 'portOfLading'])
    df.columns = ['portOfLading', 'portOfLadingRegion']
    # print(df.head())

    # 删除包含null值的行
    df.dropna(inplace=True)
    # 删除完全重复的行
    df = df.drop_duplicates()
    # 保存成csv文件
    df.to_csv('../Data/port_Region.csv', index=False, sep=';', encoding='utf-8')
def draw_world_region_map(g):
    world_map = Basemap()
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    for node in g.nodes():
        try:
            # if port_Region[node] == 'South America':
            for neighbor in g.neighbors(node):
                if node in Longitude and neighbor in Longitude and node in Latitude and neighbor in Latitude:
                    x1, y1 = world_map(Longitude[node], Latitude[node])
                    x2, y2 = world_map(Longitude[neighbor], Latitude[neighbor])
                    # world_map.drawgreatcircle(x1, y1, x2, y2, linewidth=0.5, color='blue')
                    world_map.plot([x1, x2], [y1, y2], linewidth=0.1, color='b')
        except KeyError as k:
            pass
    plt.show()

