# from Algorithm.Basic_Topology import *
from Algorithm.Map import *
from MyData.Read import *


def generate_graph(is_mul: bool):
    if is_mul:
        # # # 读取 GraphML 文件
        BR_Im = nx.read_graphml('../Data/2019/BR2019/BRImport2019.graphml')
        BR_Ex = nx.read_graphml('../Data/2019/BR2019/BRExport2019.graphml')

        G_BR = nx.compose(BR_Im, BR_Ex)
        print("BR is ready")

        G_CL = nx.read_graphml('../Data/2019/CL2019/CLImport2019.graphml')
        print("CL is ready")

        G_CO = nx.read_graphml('../Data/2019/CO2019/COExport2019.graphml')
        print("CO is ready")

        IN_Im = nx.read_graphml('../Data/2019/IN2019/INImport2019.graphml')
        IN_Ex = nx.read_graphml('../Data/2019/IN2019/INExport2019.graphml')
        G_IN = nx.compose(IN_Im, IN_Ex)
        print("IN is ready")

        US_Im = nx.read_graphml('../Data/2019/US/USImport2019.graphml')
        US_Ex = nx.read_graphml('../Data/2019/US/USExport2019.graphml')
        G_US = nx.compose(US_Im, US_Ex)
        print("US is ready")

        G_VE = nx.read_graphml('../Data/2019/VE2019/VEImport2019.graphml')
        print("VE is ready")

        # 合并两个图
        G_combined = nx.compose(G_BR, G_CL)
        G_combined = nx.compose(G_combined, G_CO)
        G_combined = nx.compose(G_combined, G_IN)
        G_combined = nx.compose(G_combined, G_US)
        G_combined = nx.compose(G_combined, G_VE)

        print("N:", G_combined.number_of_nodes())
        print("M:", G_combined.number_of_edges())

        # 使用 GraphML 保存图
        nx.write_graphml(G_combined, '../Data/2019/FinalGraph/MultiDiGraph2019.graphml')
    else:
        # # # 读取 GraphML 文件
        BR_Im = nx.read_graphml('../Data/2019/BR2019/BRImport2019.graphml')
        BR_Ex = nx.read_graphml('../Data/2019/BR2019/BRExport2019.graphml')
        BR_Im_Graph = nx.Graph(BR_Im)
        BR_Ex_Graph = nx.Graph(BR_Ex)
        G_BR = nx.compose(BR_Im_Graph, BR_Ex_Graph)
        print("BR is ready")

        CL_Im = nx.read_graphml('../Data/2019/CL2019/CLImport2019.graphml')
        G_CL = nx.Graph(CL_Im)
        print("CL is ready")

        CO_Ex = nx.read_graphml('../Data/2019/CO2019/COExport2019.graphml')
        G_CO = nx.Graph(CO_Ex)
        print("CO is ready")

        IN_Im = nx.read_graphml('../Data/2019/IN2019/INImport2019.graphml')
        IN_Ex = nx.read_graphml('../Data/2019/IN2019/INExport2019.graphml')
        IN_Im_Graph = nx.Graph(IN_Im)
        IN_Ex_Graph = nx.Graph(IN_Ex)
        G_IN = nx.compose(IN_Im_Graph, IN_Ex_Graph)
        print("IN is ready")

        US_Im = nx.read_graphml('../Data/2019/US/USImport2019.graphml')
        US_Ex = nx.read_graphml('../Data/2019/US/USExport2019.graphml')
        US_Im_Graph = nx.Graph(US_Im)
        US_Ex_Graph = nx.Graph(US_Ex)
        G_US = nx.compose(US_Im_Graph, US_Ex_Graph)
        print("US is ready")

        VE_Im = nx.read_graphml('../Data/2019/VE2019/VEImport2019.graphml')
        G_VE = nx.Graph(VE_Im)
        print("VE is ready")

        # 合并两个图
        G_combined = nx.compose(G_BR, G_CL)
        G_combined = nx.compose(G_combined, G_CO)
        G_combined = nx.compose(G_combined, G_IN)
        G_combined = nx.compose(G_combined, G_US)
        G_combined = nx.compose(G_combined, G_VE)

        print("N:", G_combined.number_of_nodes())
        print("M:", G_combined.number_of_edges())

        # 使用 GraphML 保存图
        nx.write_graphml(G_combined, '../Data/2019/FinalGraph/Graph2019.graphml')

def draw_in_out_rate_map() -> None:
    with open('../Data/2019/FinalGraph/port_in_out_info.json', "r", encoding="utf-8") as file:
        port_in_out_info = json.load(file)

    Port_Data = ConstructNetwork.Read_Port_Data()

    # 得到 tuple 组成的 list  tuple中的元素依次为 longitude、latitude、节点中心性
    coord = [
        (float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]), port_in_out_info[node]['in_rate'],
         node)
        for node in port_in_out_info
        if "latitude" in Port_Data[node].keys() and "longitude" in Port_Data[node].keys() and Port_Data[node][
            "country_english"] == "China"]
    value = [data[2] for data in coord]
    # 使用内置的 coolwarm 颜色映射（从蓝色到红色）
    cmap = plt.cm.coolwarm
    # 创建归一化函数，将值映射到0-1范围
    norm = plt.Normalize(0, 1)

    world_map = Basemap(resolution='l')
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    x, y = world_map([data[0] for data in coord], [data[1] for data in coord])
    scatter = world_map.scatter(x, y, marker='o', c=value, norm=norm, cmap=cmap, s=50, zorder=10)
    # 添加颜色条
    cbar = plt.colorbar(scatter, shrink=0.5, aspect=10)
    # 一次性添加所有标签
    for i, (x_pos, y_pos) in enumerate(zip(x, y)):
        plt.annotate(
            f"{coord[i][3]}({coord[i][2]:.3f})",
            xy=(x_pos, y_pos),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
            zorder=11
        )

    plt.show()

for year in range(2017, 2022):
    g_ex = nx.read_graphml('../Data/' + str(year) + '/US/USExport' + str(year) + '.graphml')
    print(str(year) + "Ex is ready")
    g_im = nx.read_graphml('../Data/' + str(year) + '/US/USImport' + str(year) + '.graphml')
    print(str(year) + "IM is ready")
    g = nx.compose(g_ex, g_im)
    nx.write_graphml(g, '../Data/' + str(year) + '/US' + '/US' + str(year) + '.graphml')
    print(str(year) + "is ready")

# print(g.number_of_edges())
# print(g.number_of_nodes())


# ConstructNetwork.Save_Network_USExport(year=2017)


# draw_world_ports_degree_heat_map(g, degree)

# G_null = G.copy()
# # 进行n_swaps次边交换
# nx.double_edge_swap(G_null, nswap=100000, max_tries=1000000)
# # 确保没有自环
# G_null.remove_edges_from(nx.selfloop_edges(G_null))
# print(G_null.number_of_edges())

# community = nx.community.louvain_communities(G_2019)
# for com in community:
#     print(len(com))


# animal_plant = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
# grease = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
# minerals = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
# rubber_plastics = [39, 40, 41, 42, 43]
# pulpwood = [44, 45, 46, 47, 48, 49]
# textile = [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67]
# metal = [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83]
# machinery = [84, 85, 86, 87, 88, 89]
# precision_instrument = [90, 91, 92, 94, 95, 96]
# special_other = [68, 69, 70, 93, 97, 98, 99]


# 定义分类映射关系：键为类别名称，值为该类别包含的数字列表
# category_mapping = {
#     'animal_plant': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
#     'grease': [15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
#     'minerals': [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38],
#     'rubber_plastics': [39, 40, 41, 42, 43],
#     'pulpwood': [44, 45, 46, 47, 48, 49],
#     'textile': [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67],
#     'metal': [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83],
#     'machinery': [84, 85, 86, 87, 88, 89],
#     'precision_instrument': [90, 91, 92, 94, 95, 96],
#     'special_other': [68, 69, 70, 93, 97, 98, 99]
# }
#
# # 创建反向映射：数字 -> 类别（提高查询效率）
# number_to_category = {}
# for category, numbers in category_mapping.items():
#     for num in numbers:
#         number_to_category[num] = category


#
# # 将所有列表组织成字典，键为类别名称，值为对应的列表
# category_dict = {
#     "animal_plant": animal_plant,
#     "grease": grease,
#     "minerals": minerals,
#     "rubber_plastics": rubber_plastics,
#     "pulpwood": pulpwood,
#     "textile": textile,
#     "metal": metal,
#     "machinery": machinery,
#     "precision_instrument": precision_instrument,
#     "special_other": special_other
# }
#
# # 直接得到 hsCode 到 类别 的映射   方便后续查找
# hs_category_map = dict()
# for name, category in category_dict.items():
#     for value in category:
#         hs_category_map[value] = name


# G = nx.read_graphml('../Data/FinalGraph/MultiDiGraph2019.graphml')
# draw_world_ports_in_out_degree_heat_map(G, "out")

# port_in_out_info = dict()
# for node in MultiDiG_2019.nodes():
#     degree = MultiDiG_2019.degree(node)
#     in_rate = MultiDiG_2019.in_degree(node) / degree
#     out_rate = MultiDiG_2019.out_degree(node) / degree
#
#     in_out_dict = dict()
#     in_out_dict["in_rate"] = in_rate
#     in_out_dict["out_rate"] = out_rate
#     port_in_out_info[node] = in_out_dict
# json_bytes = json.dumps(port_in_out_info).encode('utf-8')
#
# # 将编码后的字符串写入文件
# with open('../Data/FinalGraph/port_in_out_info.json', 'wb') as f:
#     f.write(json_bytes)


# 遍历所有边（包括多重边）
# for u, v, key, data in MultiDiG_2019.edges(data=True, keys=True):
#     data['HSCode'] = str(data['HSCode'])
#     data['HSCode'] = data['HSCode'][:2]
# nx.write_graphml(MultiDiG_2019, '../Data/FinalGraph/MultiDiGraph2019.graphml')

# MultiDiG_2019 = nx.read_graphml('../Data/FinalGraph/MultiDiGraph2019.graphml')

# Port_Data = ConstructNetwork.Read_Port_Data()
# port_hs_rate_info = dict()
# i = 0
# j = 0
#
# for node in MultiDiG_2019:
#     # 出边
#     node_export_category_rate = dict()
#     for neighbor, edge_dict in MultiDiG_2019[node].items():  # G[node] 等价于 G.adj[node]
#         for key, data in edge_dict.items():
#             # print(f"    {node} → {neighbor} (键={key}), 属性: {data}")
#             # dict 嵌套有点多 慢慢看     得到属性的HSCode 再得到是什么类别  再写入 node_import_category_rate
#             # print(type(data['HSCode']))
#             try:
#                 hs_category_ex = int(data['HSCode']) # 一定记得转成 int 类型
#                 if hs_category_map[hs_category_ex] in node_export_category_rate.keys():
#                     node_export_category_rate[hs_category_map[hs_category_ex]] += 1
#                 else:
#                     node_export_category_rate[hs_category_map[hs_category_ex]] = 0
#             except ValueError:
#                 i += 1
#             except KeyError:
#                 print(hs_category_ex)
#
#     # 入边
#     node_import_category_rate = dict()
#     for predecessor, edge_dict in MultiDiG_2019.pred[node].items():
#         for key, data in edge_dict.items():
#             # print(f"    {predecessor} → {node} (键={key}), 属性: {data}")
#             try:
#                 hs_category_in = int(data['HSCode'])  # 一定记得转成 int 类型
#                 if hs_category_map[hs_category_in] in node_import_category_rate.keys():
#                     node_import_category_rate[hs_category_map[hs_category_in]] += 1
#                 else:
#                     node_import_category_rate[hs_category_map[hs_category_in]] = 0
#             except ValueError:
#                 j += 1
#             except KeyError:
#                 print(hs_category_in)
#     # 写入 总的 port_hs_rate_info 字典
#     temp_dict = dict()
#     temp_dict["Import"] = node_import_category_rate
#     temp_dict["Export"] = node_export_category_rate
#     port_hs_rate_info[node] = temp_dict
#
# # 将编码后的字符串写入文件
# json_bytes = json.dumps(port_hs_rate_info).encode('utf-8')
# with open('../Data/FinalGraph/port_hs_rate_info.json', 'wb') as f:
#     f.write(json_bytes)
# print(i / MultiDiG_2019.number_of_edges())
# print(j / MultiDiG_2019.number_of_edges())


def draw_port_hs_category(cate_str: str) -> None:
    '''

    :param cate_str: 要画哪个种类的
    :return:
    '''
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_hs_rate_info = Read.read_port_hs_rate_info()

    # 得到 tuple 组成的 list  tuple中的元素依次为 longitude、latitude......
    # 这里没有找到相应的 key 值  就是 0 之前处理的时候没有处理好
    coord = [(float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]),
              port_hs_rate_info[node]["Import"].get(cate_str, 0), port_hs_rate_info[node]["Export"].get(cate_str, 0), node)
             for node in port_hs_rate_info if
             "latitude" in Port_Data[node].keys() and "longitude" in Port_Data[node].keys()]

    sort_coord = sorted(coord, key=lambda data: data[2], reverse=True)
    print("Import:")
    print(sort_coord)
    sort_coord = sorted(coord, key=lambda data: data[3], reverse=True)
    print("Export:")
    print(sort_coord)

    value_im = [data[2] for data in coord]
    value_ex = [data[3] for data in coord]

    # 计算散点大小 - 使用度值的线性映射，并添加最小尺寸
    min_size = 10
    max_size = 200
    min_value = min(min(value_im), min(value_ex))
    max_value = max(max(value_im), max(value_ex))

    # 线性映射函数：将度值映射到散点大小
    sizes_im = [min_size + (d - min_value) * (max_size - min_size) / (max_value - min_value) for d in value_im]
    sizes_im = [value if value > 40 else 0 for value in sizes_im]
    # # 计算与度值相关的透明度（0.1-1.0）
    # alphas_im = [0.1 + (d - min_value) * (1.0 - 0.3) / (max_value - min_value) for d in value_im]
    # # 过滤掉小于特定值的点
    # alphas_im = [value if value > 0.15 else 0 for value in alphas_im]

    sizes_ex = [min_size + (d - min_value) * (max_size - min_size) / (max_value - min_value) for d in value_ex]
    sizes_ex = [value if value > 40 else 0 for value in sizes_ex]
    # alphas_ex = [0.1 + (d - min_value) * (1.0 - 0.3) / (max_value - min_value) for d in value_ex]
    # # 过滤掉小于特定值的点
    # alphas_ex = [value if value > 0.15 else 0 for value in alphas_ex]


    world_map = Basemap()
    # 绘制地图边界，并设置背景颜色为灰色（海洋颜色）
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    x, y = world_map([data[0] for data in coord], [data[1] for data in coord])
    world_map.scatter(x, y, marker='o', color='b', s=sizes_im, zorder=10)
    world_map.scatter(x, y, marker='o', color='r', s=sizes_ex, zorder=10)
    plt.title(cate_str)
    plt.show()
