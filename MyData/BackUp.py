# ---------- 工具函数 ----------
def rich_club_phi(G, k):
    """无权无向 rich-club coefficient @ degree k"""
    rich = [n for n, d in G.weighted_degree() if d >= k]
    H = G.subgraph(rich)
    nk = len(rich)
    if nk < 2:
        return np.nan
    return 2 * H.number_of_edges() / (nk * (nk - 1))
def weighted_k_core(G, k, weight='volumeTEU', degree_type='total'):
    """
    计算加权有向图的k-核（支持加权度、加权入度、加权出度）

    参数:
        G: 有向图 (nx.DiGraph)
        k: k-核的阶数
        weight: 边的权重属性名称（默认'weight'）
        degree_type: 加权度类型
            'total'：加权度（总权重和）
            'in'：加权入度（入边权重和）
            'out'：加权出度（出边权重和）

    返回:
        子图 (nx.DiGraph)：满足条件的k-核
    """
    # 复制原图避免修改输入
    H = G.copy()
    n = H.number_of_nodes()
    if n == 0:
        return H

    # 1. 初始化节点的加权度
    def get_weighted_degree(node):
        if degree_type == 'total':
            deg = sum(data.get(weight, 1.0) for _,_, data in H.edges(node, data=True))
            return deg
        elif degree_type == 'in':
            return sum(data.get(weight, 1.0) for _, _, data in H.in_edges(node, data=True))
        elif degree_type == 'out':
            return sum(data.get(weight, 1.0) for _, _, data in H.out_edges(node, data=True))
        else:
            raise ValueError("degree_type必须是'total'、'in'或'out'")

    # 计算初始加权度
    weighted_degrees = {node: get_weighted_degree(node) for node in H.nodes()}

    # 2. 迭代剥离加权度 < k 的节点
    # 使用队列存储待处理节点（加权度 < k）
    queue = deque([node for node, deg in weighted_degrees.items() if deg < k])

    while queue:
        u = queue.popleft()
        if u not in H.nodes():  # 已被移除
            continue

        # 记录与u相连的节点（用于后续更新加权度）
        neighbors = list(H.neighbors(u))  # 获取u的所有邻居

        # 移除节点u
        H.remove_node(u)

        # 3. 更新邻居的加权度，并检查是否需要加入队列
        for v in neighbors:
            if v not in H.nodes():
                continue
            # 重新计算v的加权度
            new_deg = get_weighted_degree(v)
            old_deg = weighted_degrees[v]
            weighted_degrees[v] = new_deg
            # 若v的加权度从≥k变为<k，加入队列
            if old_deg >= k and new_deg < k:
                queue.append(v)
    return H


#region未处理的函数
def draw_nodes_edges_picture():
    '''
    绘制网络nodes，edges数量演化图
    :return:
    '''
    # 1. 读取数据
    df = pd.read_csv('network_evolution_14metrics.csv')

    # 2. 设置出版级样式
    sns.set_style('white')  # 无网格
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11
    plt.rcParams['legend.fontsize'] = 10

    # 3. 绘制
    fig, ax1 = plt.subplots(figsize=(6.5, 3.8))

    # 左轴：nodes
    ax1.plot(df['year'], df['nodes'], marker='o', color='#1f77b4', lw=2.5, label='Nodes')
    ax1.set_ylabel('Nodes', color='black')
    ax1.tick_params(axis='y')

    # 右轴：edges（量级大）
    ax2 = ax1.twinx()
    ax2.plot(df['year'], df['edges'], marker='s', color='#ff7f0e', lw=2.5, label='Edges')
    ax2.set_ylabel('Edges', color='black')
    ax2.tick_params(axis='y')

    # 4. 横坐标整年刻度
    ax1.set_xlabel('Year')
    ax1.set_xticks(df['year'])
    ax1.set_xticklabels(df['year'])

    # 5. 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')

    # 6. 保存
    plt.tight_layout()
    plt.savefig('Figure/nodes_edges.png', dpi=300, bbox_inches='tight')
    plt.show()
def get_numbers_of_connect_countries_to_US(G, year):
    # 统计与美国直接相连的非美国国家数
    connected_countries = {
        G.nodes[n]['Country']
        for n in G.nodes
        if G.nodes[n].get('Country') != 'United States'
    }
    print(year)
    print(f'与美国连接的国家（去重）个数 = {len(connected_countries)}')
def the_degree_of_connection_of_all_countries_to_the_US():
    '''
    得到 Figure/US_top10_TEU_bilateral.csv  Figure/US_top10_Times_bilateral.csv  每年和美国联系程度的top10
    :return:
    '''
    years = range(2017, 2022)
    teu_rows, trips_rows = [], []

    for year in years:
        G = nx.read_graphml(f'../Data/{year}/US/US{year}.graphml')

        country_stats = {}
        for u, v, d in G.edges(data=True):
            c_u = G.nodes[u].get('Country', 'Unknown')
            c_v = G.nodes[v].get('Country', 'Unknown')
            if 'United States' in [c_u, c_v] and c_u != c_v:
                teu = float(d.get('volumeTEU', 1.0))
                trips = 1.0
                partner = c_u if c_v == 'United States' else c_v
                country_stats.setdefault(partner, {'TEU': 0, 'Trips': 0})
                country_stats[partner]['TEU'] += teu
                country_stats[partner]['Trips'] += trips

        # 每年两张榜单
        for metric, label in [('TEU', 'TEU'), ('Trips', 'Trips')]:
            top = (
                pd.Series({k: v[label] for k, v in country_stats.items()})
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
                .rename(columns={'index': 'country', 0: metric})
                .assign(year=year)
            )
            (teu_rows if label == 'TEU' else trips_rows).append(top)

    # 导出
    pd.concat(teu_rows).to_csv('Figure/US_top10_TEU_bilateral.csv', index=False)
    pd.concat(trips_rows).to_csv('Figure/US_top10_Times_bilateral.csv', index=False)

    print('✅ 已生成双边统计：')
    print(pd.concat(teu_rows).head())
def draw_degree_of_connection_of_all_countries_to_the_US():
    # 1) 读数据（TEU 或 Times 均可）
    metrics = 'Times'
    df = pd.read_csv(f'Figure/US_top10_{metrics}_bilateral.csv')  # 或 Trips 文件

    # 2) 计算年度排名（1 最高）
    df['rank'] = df.groupby('year')[metrics].rank(method='min', ascending=False)

    # 3) 绘图
    plt.figure(figsize=(7, 4.2))
    # 2. 设置出版级样式
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11
    plt.rcParams['legend.fontsize'] = 10
    sns.set_style('whitegrid')  # 带方框边框
    sns.lineplot(
        data=df,
        x='year',
        y='rank',
        hue='country',
        marker='o',
        linewidth=2.5,
        palette='tab10'
    )

    # 4) 倒序 y 轴（1 在上）
    plt.gca().invert_yaxis()
    plt.xticks(range(2017, 2022))
    plt.yticks(range(1, 11))
    plt.ylim(10.5, 0.5)

    # 5) 坐标轴
    plt.xlabel('Year')
    plt.ylabel('Rank')
    plt.title('Top 10 Countries Ranked by U.S. Connection (2017–2021)', pad=15)

    # 6) 图例放在右下角，不挡折线
    plt.legend(
        title='Country',
        loc='lower right',  # 右下角
        frameon=True,
        fancybox=True,
        shadow=False
    )

    plt.tight_layout()
    plt.savefig(f'Figure/top10_rank_{metrics}.png', dpi=300, bbox_inches='tight')
    plt.show()
def calculate_spectral_radius():
    years = range(2017, 2022)
    records = []

    for year in years:
        path = f'../Data/{year}/US/US{year}.graphml'
        if not os.path.exists(path):
            print(f'⚠️ 文件不存在: {path}')
            continue

        Mul_G = nx.read_graphml(path)
        G = nx.Graph(Mul_G)

        # 1) 无权谱半径
        A = nx.adjacency_matrix(G).astype(float).astype(float)


        rho_unw = max(abs(np.linalg.eigvals(A.toarray())))

        # 2) TEU 加权谱半径（把邻接矩阵元素换成 volumeTEU）
        # A_w = nx.adjacency_matrix(G, weight='volumeTEU').astype(float)
        # rho_w = max(abs(np.linalg.eigvals(A_w.toarray())))

        records.append({'year': year,
                        'unweighted_rho': rho_unw})
        # records.append({'year': year,
        #                 'unweighted_rho': rho_unw,
        #                 'weighted_rho': rho_w})

    # 保存
    df = pd.DataFrame(records)
    df.to_csv('Figure/spectral_radius_year.csv', index=False)
    print(df)
def calculate_structural_homogeneity():
    '''
    结构同质性
    :return:
    '''
    YEARS = range(2017, 2022)

    records = []

    DATA_DIR = 'Data'
    OUTPUT_DIR = 'Figure'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    def calc_structural_homogeneity(values):
        if len(values) <= 1:
            return np.nan
        pd.Series(values, name='col').to_csv('list.csv', index=False)
        avg = np.mean(values)
        std = np.std(values, ddof=0)
        return 1 - std / avg if avg else np.nan
        print("-------------")

    for y in YEARS:
        path = f'../{DATA_DIR}/{y}/US/US{y}.graphml'
        if not os.path.exists(path):
            print(f'⚠️ 文件不存在: {path}')
            continue
        G = nx.Graph(nx.read_graphml(path))

        rec = {
            'year': y,
            'unweighted': calc_structural_homogeneity(
                [G.degree(n) for n in G.nodes]),
        }
        records.append(rec)
    df = pd.DataFrame(records)
    df.to_csv(f'{OUTPUT_DIR}/structural_homogeneity_year.csv', index=False)
    print(df)
def calculate_assortativity():
    '''
    计算同配性
    :return:
    '''
    YEARS = range(2017, 2022)
    DATA_DIR = '../Data'
    OUTPUT_DIR = '../Figure'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    def calc_assortativity(G, weight=None, attr=None):
        """返回三种同配系数"""
        if attr is not None:
            return nx.attribute_assortativity_coefficient(G, attr)
        if weight is not None:
            return nx.degree_pearson_correlation_coefficient(G, weight=weight)
        return nx.degree_assortativity_coefficient(G)

    records = []
    for y in YEARS:
        G = nx.Graph(nx.read_graphml(f'{DATA_DIR}/{y}/US/US{y}.graphml'))
        rec = {
            'year': y,
            'degree_assort': calc_assortativity(G),
            'weighted_TEU': calc_assortativity(G, weight='volumeTEU'),
        }
        records.append(rec)

    df = pd.DataFrame(records)
    df.to_csv(f'{OUTPUT_DIR}/US_assortativity_year.csv', index=False)
    print(df)
def draw_density_avgDegree_picture():
    # 1. 读数据
    df = pd.read_csv('network_evolution_14metrics.csv')

    # 2. 出版级样式
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11

    # 3. 画图
    fig, ax1 = plt.subplots(figsize=(6.5, 3.8))
    ax1.plot(df['year'], df['density'], marker='o', color='#1f77b4', lw=2.5, label='Density')

    ax1.set_ylabel('density', color='black')
    ax1.tick_params(axis='y')


    ax2 = ax1.twinx()
    ax2.plot(df['year'], df['avg_degree'], marker='s', color='#ff7f0e', lw=2.5, label='avg degree')
    ax2.set_ylabel('avg degree', color='black')
    ax2.tick_params(axis='y')

    # 4. 横坐标整年刻度
    ax1.set_xlabel('Year')
    ax1.set_xticks(df['year'])
    ax1.set_xticklabels(df['year'])

    # 5. 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')

    plt.tight_layout()
    # 不加 ./ 也可以   加了就相当于是显式的
    plt.savefig('./Figure/scale_evolution.png', dpi=300, bbox_inches='tight')
    plt.show()
    # 单独画density
    # # 4. 去网格、整年刻度
    # ax1.grid(False)
    # ax1.set_xticks(df['year'])
    # ax1.set_xticklabels(df['year'])
    # ax1.set_xlabel('Year')
    # ax1.set_ylabel('Density')
    # ax1.set_title('Network Density Evolution (2017–2021)', pad=15)
    # ax1.legend(frameon=False, loc='upper right')   # 图例
    # # 5. 保存
    # plt.tight_layout()
    # plt.savefig('density_evolution.png', dpi=300, bbox_inches='tight')
    # plt.show()
def draw_length_efficiency_picture():
    # 1. 读取数据
    df = pd.read_csv('network_evolution_14metrics.csv')

    # 2. 设置出版级样式
    sns.set_style('white')  # 无网格
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11
    plt.rcParams['legend.fontsize'] = 10

    # 3. 绘制
    fig, ax1 = plt.subplots(figsize=(6.5, 3.8))

    # 左轴：nodes
    ax1.plot(df['year'], df['avg_path_length'], marker='o', color='#1f77b4', lw=2.5, label='avg path length')
    ax1.set_ylabel('avg path length', color='black')
    ax1.tick_params(axis='y')

    # 右轴：edges（量级大）
    ax2 = ax1.twinx()
    ax2.plot(df['year'], df['global_efficiency'], marker='s', color='#ff7f0e', lw=2.5, label='global efficiency')
    ax2.set_ylabel('global efficiency', color='black')
    ax2.tick_params(axis='y')

    # 4. 横坐标整年刻度
    ax1.set_xlabel('Year')
    ax1.set_xticks(df['year'])
    ax1.set_xticklabels(df['year'])

    # 5. 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')
    # 在绘图后、保存前插入


    # 6. 保存
    plt.savefig('path_efficiency_evolution.png', dpi=300, bbox_inches='tight')
    plt.show()
#endregion


#regionNetwork Structure
def draw_degree_distribution():
    """
    画度分布的图
    :return:
    """
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    # 读取数据并构建网络
    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后（数据不全）
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            time = f"{year} {season}"
            G = nx.Graph(nx.read_graphml(file_path))

            # ----------------------
            # 1. 计算度分布数据
            # ----------------------
            degrees = dict(G.degree())  # {节点: 度}
            degree_counts = defaultdict(int)
            for d in degrees.values():
                degree_counts[d] += 1

            degrees_sorted = sorted(degree_counts.keys())  # 排序的度数
            counts = [degree_counts[d] for d in degrees_sorted]  # 对应节点数

            # 计算频率（节点数/总节点数）
            total_nodes = G.number_of_nodes()
            frequencies = [count / total_nodes for count in counts]

            # ----------------------
            # 2. 双对数散点图 + 直线拟合
            # ----------------------
            plt.figure(figsize=(10, 6))

            # 绘制双对数散点图
            plt.loglog(
                degrees_sorted,
                frequencies,
                marker='o',
                linestyle='',
                color='#d62728',
                markersize=6,
                alpha=0.8,
                label='Ports'
            )

            # ----------------------
            # 核心：线性回归拟合幂律直线
            # ----------------------
            # 对度数和频率取对数（避免log(0)，过滤掉频率为0的点）
            log_degrees = np.log10(degrees_sorted)  # 底数为10的对数（也可用np.log自然对数）
            log_frequencies = np.log10(frequencies)

            # 线性回归（y = a*x + b，其中y=log(frequency), x=log(degree)）
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_degrees, log_frequencies)

            # 生成拟合直线的预测值（用于绘图）
            fit_line = 10 **(intercept + slope * log_degrees)  # 转换回原尺度（10^y）

            # 绘制拟合直线
            plt.loglog(
                degrees_sorted,
                fit_line,
                linestyle='--',
                color='black',
                linewidth=2,
                label=f'Fit: log(f) = {slope:.2f}*log(k) + {intercept:.2f}\nR² = {r_value**2:.4f}'
            )

            # ----------------------
            # 美化与标注
            # ----------------------
            plt.xlabel('Degree', fontsize=12, fontweight='bold')
            plt.ylabel('Frequency', fontsize=12, fontweight='bold')
            plt.title(f'{time} degree distribution', fontsize=14, fontweight='bold', pad=15)
            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)
            # plt.grid(True, which="both", linestyle='--', alpha=0.5)
            plt.legend(fontsize=10, loc='upper right')  # 显示拟合公式和R²

            plt.tight_layout()
            plt.savefig(f'Figure/Season/DegreeDistribution/{time} degree distribution.png', dpi=300)
            # plt.show()

            # 输出拟合结果
            print(f"幂律拟合结果：")
            print(f"斜率（-γ）：{slope:.4f} → 幂指数 γ = { -slope:.4f}")
            print(f"截距：{intercept:.4f}")
            print(f"决定系数 R²：{r_value**2:.4f}（越接近1，拟合越好）")
def degree_distribution():
    """
    画网络的度分布
    :return:
    """
    for DiG, G, time in get_network():
        # 1. 初始化数据结构
        degree_counts = defaultdict(int)
        degree_to_ports = defaultdict(list)  # 度值 → 港口列表
        port_to_degree = {}  # 新增：港口 → 度值（快速查询每个港口的度）

        # 2. 遍历节点，统计度值、港口对应关系
        for port, degree in G.degree():
            degree_counts[degree] += 1
            degree_to_ports[degree].append(port)
            port_to_degree[port] = degree  # 记录每个港口的度值

        # 3. 计算排序的度值、频率，并建立“度值→频率”映射
        degrees_sorted = sorted(degree_counts.keys())
        counts = [degree_counts[d] for d in degrees_sorted]
        total_nodes = G.number_of_nodes()
        frequencies = [count / total_nodes for count in counts]

        # 关键：建立“度值→频率”的字典（一个度值对应一个频率）
        degree_to_frequency = dict(zip(degrees_sorted, frequencies))

        # 4. 构建最终数据：港口 → [度值, 频率]（每个港口唯一对应一组数据）
        data = {}
        for port in G.nodes():  # 遍历所有港口，确保不遗漏
            degree = port_to_degree[port]  # 获取该港口的度值
            frequency = degree_to_frequency[degree]  # 通过度值获取对应频率
            data[port] = [(degree, frequency)]  # 每个港口对应唯一的[(度值, 频率)]

        # TODO 最后只能人工打上标签
        df = pd.DataFrame(data)
        Draw.draw_scatter_list(
            df,
            "Undirected/DegreeDistribution/",
            "Degree",
            "Frequency",
            f"DegreeDistribution {time}",
            "loglog",
            "ports"
        )
def draw_in_degree_distribution():
    """
    入度分布  出度分布
    :return:
    """
    degree_type = 'out'  # 出度 or 入度
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    # 读取数据并构建网络
    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后（数据不全）
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            time = f"{year} {season}"
            G = nx.read_graphml(file_path)

            # ----------------------
            # 1. 计算度分布数据
            # ----------------------
            if degree_type == 'in':
                degrees = dict(G.in_degree())  # {节点: 度}
            elif degree_type == 'out':
                degrees = dict(G.out_degree())
            else:
                print("degree_type写错了")

            # 关键修改：过滤掉度数为0的节点
            non_zero_degrees = {node: d for node, d in degrees.items() if d > 0}

            degree_counts = defaultdict(int)
            for d in non_zero_degrees.values():
                degree_counts[d] += 1

            # 排序并过滤掉度数为0的项（即使有也排除）
            degrees_sorted = [d for d in sorted(degree_counts.keys()) if d > 0]
            counts = [degree_counts[d] for d in degrees_sorted]  # 对应节点数

            # 计算频率（节点数/总节点数）
            total_non_zero_nodes = len(non_zero_degrees)
            frequencies = [count / total_non_zero_nodes for count in counts]

            # ----------------------
            # 2. 双对数散点图 + 直线拟合
            # ----------------------
            plt.figure(figsize=(10, 6))

            # 绘制双对数散点图
            plt.loglog(
                degrees_sorted,
                frequencies,
                marker='o',
                linestyle='',
                color='#d62728',
                markersize=6,
                alpha=0.8,
                label='Ports'
            )

            # ----------------------
            # 核心：线性回归拟合幂律直线
            # ----------------------
            # 对度数和频率取对数（避免log(0)，过滤掉频率为0的点）
            log_degrees = np.log10(degrees_sorted)  # 底数为10的对数（也可用np.log自然对数）
            log_frequencies = np.log10(frequencies)

            # 线性回归（y = a*x + b，其中y=log(frequency), x=log(degree)）
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_degrees, log_frequencies)

            # 生成拟合直线的预测值（用于绘图）
            fit_line = 10 **(intercept + slope * log_degrees)  # 转换回原尺度（10^y）

            # 绘制拟合直线
            plt.loglog(
                degrees_sorted,
                fit_line,
                linestyle='--',
                color='black',
                linewidth=2,
                label=f'Fit: log(f) = {slope:.2f}*log(k) + {intercept:.2f}\nR² = {r_value**2:.4f}'
            )

            # ----------------------
            # 美化与标注
            # ----------------------
            plt.xlabel('Degree', fontsize=12, fontweight='bold')
            plt.ylabel('Frequency', fontsize=12, fontweight='bold')
            plt.title(f'{time} {degree_type} degree distribution', fontsize=14, fontweight='bold', pad=15)
            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend(fontsize=10, loc='upper right')  # 显示拟合公式和R²

            plt.tight_layout()
            plt.savefig(f'Figure/Season/DegreeDistribution/{degree_type} degree/{time} {degree_type} degree distribution.png', dpi=300)
            # plt.show()

            # 输出拟合结果
            print(f"幂律拟合结果：")
            print(f"斜率（-γ）：{slope:.4f} → 幂指数 γ = { -slope:.4f}")
            print(f"截距：{intercept:.4f}")
            print(f"决定系数 R²：{r_value**2:.4f}（越接近1，拟合越好）")
def draw_US_Maritime_Network():
    """
    画世界地图
    :return:
    """
    # ----------------------
    # 1. 数据加载与处理
    # ----------------------
    # 读取图数据
    DiG = nx.read_graphml(f'../Data/2021/US/Season/Spring/US2021_Spring_Digraph.graphml')

    # 读取港口坐标数据
    Port_Data = ConstructNetwork.Read_Port_Data()

    # 假设缩写规则：NA=北美洲, SA=南美洲, EU=欧洲, AS=亚洲, AF=非洲, OC=大洋洲, UN=未知
    continent_color_mapping = {
        'NA': '#1f77b4',    # 深蓝色（北美洲）
        'SA': '#ff7f0e',    # 橙色（南美洲）
        'EU': '#2ca02c',    # 绿色（欧洲）
        'AS': '#d62728',    # 红色（亚洲）
        'AF': '#9467bd',    # 紫色（非洲）
        'OC': '#8c564b',    # 棕色（大洋洲）
        'UN': '#7f7f7f'     # 灰色（未知大洲）
    }

    # 筛选有效节点（有坐标+total_TEU>1000），并提取TEU值用于可视化
    port_info = {}  # 存储：{节点: (经度, 纬度, total_TEU)}
    for node in DiG.nodes():
        # 检查坐标是否有效
        if node not in Port_Data or not isinstance(Port_Data[node], dict):
            continue
        if "longitude" not in Port_Data[node] or "latitude" not in Port_Data[node]:
            continue
        # 检查total_TEU是否有效且大于1000
        try:
            total_teu = float(DiG.nodes[node].get('total_TEU', 0))
            if total_teu <= 1000:
                continue
        except (ValueError, TypeError):
            continue

        # 4. 提取双字母大洲缩写（假设存储在节点属性的'continent'键中，根据实际数据调整）
        continent_code = DiG.nodes[node].get('continent', 'UN')  # 替换为实际键名
        # 统一缩写格式（大写，避免'nA'/'na'等不一致）
        continent_code = continent_code.strip().upper()
        # 若缩写不在映射中，归为'UN'（未知）
        if continent_code not in continent_color_mapping:
            continent_code = 'UN'
        # 存储有效信息
        lon = float(Port_Data[node]["longitude"])
        lat = float(Port_Data[node]["latitude"])
        port_info[node] = (lon, lat, total_teu, continent_code)
    # node 信息
    nodes = list(port_info.keys())
    lons = [port_info[node][0] for node in nodes]
    lats = [port_info[node][1] for node in nodes]
    teus = [port_info[node][2] for node in nodes]

    # 筛选有效边（仅保留两端节点都在port_info中的边，避免无坐标节点）
    edges = []
    edge_teus = []  # 边的货运量（用于线条粗细）
    for u, v, data in DiG.edges(data=True):
        if u in port_info and v in port_info:  # 确保边的两端节点都有坐标
            try:
                # 假设边的货运量存在于'volumeTEU'属性
                edge_teu = float(data.get('volumeTEU', 0))
                if edge_teu > 10000:  # 过滤无货运量的边
                    edges.append((u, v))
                    edge_teus.append(edge_teu)
            except (ValueError, TypeError):
                continue

    # ----------------------
    # 2. 地图与网络可视化设置
    # ----------------------
    # 美国中心经纬度：西经98.5°（-98.5），北纬39.8°
    center_lon = -98.5
    center_lat = 39.8

    # 创建画布
    fig, ax = plt.subplots(figsize=(14, 10))


    # 定义地图（聚焦港口集中区域，如美洲：调整经纬度范围）
    # 若全球分布，可保留 llcrnrlon=-180, urcrnrlon=180, llcrnrlat=-90, urcrnrlat=90
    world_map = Basemap(
        resolution='i',  # 中分辨率（比'l'更清晰，加载速度适中）
        projection='cyl',
        lon_0=center_lon,  # 以港口中心为地图中心
        lat_0=center_lat,
        llcrnrlon=min(lons) - 10,  # 左边界：最西港口-10度
        urcrnrlon=max(lons) + 10,  # 右边界：最东港口+10度
        llcrnrlat=min(lats) - 30,  # 下边界：最南港口-30度
        urcrnrlat=max(lats) + 10,  # 上边界：最北港口+10度
        ax=ax
    )

    # 绘制地图要素（更细腻的配色）
    world_map.drawmapboundary(fill_color='#A8DADC')  # 海洋：浅蓝色
    world_map.fillcontinents(color='#F1FAEE', lake_color='#A8DADC', alpha=0.8)  # 陆地：浅灰色
    world_map.drawcoastlines(linewidth=0.8, color='#1D3557')  # 海岸线：深蓝色
    world_map.drawcountries(linewidth=0.6, color='#457B9D')  # 国家边界：中蓝色
    world_map.drawmeridians(np.arange(-180, 180, 20), labels=[0, 0, 0, 1], linewidth=0.3, color='#999')  # 经度线
    world_map.drawparallels(np.arange(-90, 90, 20), labels=[1, 0, 0, 0], linewidth=0.3, color='#999')  # 纬度线

    # ----------------------
    # 3. 绘制海运网络（边+节点）
    # ----------------------
    # 绘制边（航线）：用贝塞尔曲线实现弧形，线条粗细与货运量正相关
    if edges:
        max_edge_teu = max(edge_teus)
        edge_widths = [0.5 + 2.5 * (teu / max_edge_teu) for teu in edge_teus]

        for i, (u, v) in enumerate(edges):
            # 获取两端节点经纬度和地图坐标
            u_lon, u_lat, _, _ = port_info[u]
            v_lon, v_lat, _, _ = port_info[v]
            x1, y1 = world_map(u_lon, u_lat)
            x2, y2 = world_map(v_lon, v_lat)

            # 计算两点距离（控制弯曲程度）
            dx = x2 - x1
            dy = y2 - y1
            distance = np.sqrt(dx ** 2 + dy ** 2)
            mid_x = (x1 + x2) / 2  # 中点x
            mid_y = (y1 + y2) / 2  # 中点y

            # 【关键】判断弯曲方向：50%随机+50%按经度差（避免全随机导致混乱）
            # 规则1：若u在v西边（u_lon < v_lon），50%概率向上，50%向下
            # 规则2：若u在v东边（u_lon > v_lon），反向概率，增加对称性
            if u_lon < v_lon:
                bend_up = random.choice([True, False])  # 随机
            else:
                bend_up = random.choice([False, True])  # 反向随机

            # 根据方向设置控制点y坐标（向上则+距离比例，向下则-）
            bend_strength = 0.15  # 弯曲强度（越大越弯）
            if bend_up:
                ctrl_y = mid_y + distance * bend_strength  # 向上弯
            else:
                ctrl_y = mid_y - distance * bend_strength  # 向下弯
            ctrl_x = mid_x  # 控制点x始终为中点（左右不偏移，保持对称）

            # 创建贝塞尔曲线路径
            verts = [(x1, y1), (ctrl_x, ctrl_y), (x2, y2)]
            codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
            path = Path(verts, codes)

            # 绘制曲线
            curve = patches.PathPatch(
                path,
                facecolor='none',
                edgecolor='#E63946',
                linewidth=edge_widths[i],
                alpha=0.6
            )
            ax.add_patch(curve)

    # ----------------------
    # 4. 按大洲着色绘制节点
    # ----------------------
    if port_info:
        for node in port_info:
            lon, lat, teu, continent_code = port_info[node]
            x, y = world_map(lon, lat)

            # 节点大小与TEU成正比（归一化到5-20）
            max_teu = max(p[2] for p in port_info.values())
            node_size = 5 + 15 * (teu / max_teu)

            # 按大洲获取颜色
            node_color = continent_color_mapping[continent_code]

            # 绘制节点
            world_map.plot(
                x, y, 'o',
                markersize=node_size,
                color=node_color,
                markeredgecolor='white',
                markeredgewidth=0.8,
                alpha=0.9
            )

    # ----------------------
    # 5. 图例与标注（解释大洲缩写）
    # ----------------------
    # 大洲缩写对应的全称（用于图例说明）
    continent_fullname = {
        'NA': 'North America',
        'SA': 'South America',
        'EU': 'Europe',
        'AS': 'Asia',
        'AF': 'Africa',
        'OC': 'Oceania',
        'UN': 'Unknown'
    }

    # 生成图例（包含大洲颜色+缩写+全称）
    legend_elements = [
        Line2D(
            [0], [0], marker='o', color='w',
            markerfacecolor=color, markersize=10,
            label=f'{code} ({continent_fullname[code]})'
        ) for code, color in continent_color_mapping.items()
    ]
    # 新增航线图例
    legend_elements.append(
        Line2D([0], [0], color='#E63946', lw=3, label='Shipping Routes ( > 10000 TEU)')
    )

    ax.legend(
        handles=legend_elements,
        loc='lower left',
        fontsize=9,
        title='Continents',
        title_fontsize=11
    )

    ax.set_title('2021 Spring Maritime Network', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig('Figure/Season/2021 Spring Maritime Network.png', dpi=300)
    plt.show()
def all_in_one(g, year, season) -> dict:
    """
    统一计算相应的基础指标
    :param g: 是一个无向无多边的简单图
    :param year:  图的年份
    :return: 基础信息的表格
    """

    # 先算能够直接计算的
    N = g.number_of_nodes()
    M = g.number_of_edges()
    density = nx.density(g)
    avg_clustering = nx.average_clustering(g)                               # 平均聚类系数
    max_connected_component = max(nx.connected_components(g), key=len)      # 最大连通分量
    mcc_sizes = len(max_connected_component)                                # 最大连通分量的大小
    avg_degrees = 2 * M / N                                                 # 平均度

    # 无权谱半径
    A = nx.adjacency_matrix(g)
    spectral_radius = max(abs(np.linalg.eigvals(A.toarray())))              # 无权谱半径


    # 平均路径长度 and 全局效率
    if nx.is_connected(g):
        avg_length = nx.average_shortest_path_length(g)
        efficiency = nx.global_efficiency(g)
    else:
        h = g.subgraph(max_connected_component)                             # 最大连通分量的那个子图
        avg_length = nx.average_shortest_path_length(h)
        efficiency = nx.global_efficiency(h)


    # 结构同质性
    degrees = dict(nx.degree(g))
    degrees_list = list(degrees.values())
    std_degrees = np.std(degrees_list, ddof=0)
    homogeneity = 1 - std_degrees / avg_degrees                             # 结构同质性

    # 同配性
    # 计算无向图的度数同配性
    assort_degree = degree_assortativity_coefficient(g)


    strength_TEU = {n : 0.0 for n in g.nodes}                   # 存放每个节点的TEU强度
    # 遍历图（主循环）
    for u, v, d in g.edges(data=True):
        w = float(d.get('volumeTEU', 1.0))
        strength_TEU[u] += w
        strength_TEU[v] += w

    total_TEU = sum(strength_TEU.values())
    if total_TEU != 0:
        p = np.array(list(strength_TEU.values())) / total_TEU
        entropy = -np.sum(p * np.log2(p + 1e-12))
    else:
        entropy = np.nan

    return {
        "time": f"{year}{season}",
        "N": N,
        "M": M,
        "avg_clustering": avg_clustering,
        "avg_degrees": avg_degrees,
        "avg_length": avg_length,
        "efficiency": efficiency,
        "homogeneity": homogeneity,
        "entropy": entropy,
        "density": density,
        "spectral_radius": spectral_radius,
        "mcc_sizes": mcc_sizes,
        "assortativity_coefficient": assort_degree
    }
def write_all_in_one():
    """
    把 all_in_one 函数的结果写入csv文件
    :return:
    """
    structure_metrics = []
    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            DiGraph = nx.read_graphml(file_path)
            G = nx.Graph(DiGraph)

            # G_null = G.copy()
            # nx.double_edge_swap(G_null, nswap=20000, max_tries=100000)
            # G_null.remove_edges_from(nx.selfloop_edges(G_null))

            result_year = all_in_one(G, year, season)
            structure_metrics.append(result_year)
            print(f"{year} is already down!")

    # 保存成csv
    df = pd.DataFrame(structure_metrics)
    df.to_csv(f'Figure/Season/all_in_one_Digraph.csv', index=False)
def write_nm_zero_model_all_in_one():
    """
    nm零模型  只有n和m一样  度序列不一样
    :return:
    """
    # ----------------------
    # 1. 定义路径和时间段（根据你的数据结构修改）
    # ----------------------
    years = range(2017, 2022)  # 你的数据年份
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']  # 季节（时间段）

    # 存储所有时间段的最终指标（每个时间段一行）
    all_results = []

    # ----------------------
    # 2. 循环处理每个时间段
    # ----------------------
    for year in years:
        for season in seasons:

            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue

            # 读取包含类别TEU的图文件（根据你的实际文件选择MulGraph/DiGraph，这里假设是MulGraph）
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            time = f"{year}{season}"
            G = nx.Graph(nx.read_graphml(file_path))


            N = G.number_of_nodes()
            M = G.number_of_edges()
            print(f"\n处理时间段：{year}_{season}，节点数={N}，边数={M}")

            # 生成10次ER随机图并计算指标
            num_trials = 10
            all_metrics = []
            for i in range(num_trials):
                G_ER = nx.gnm_random_graph(
                    n=N,
                    m=M,
                    seed=random.randint(1, 1000)
                )
                # 计算该时间段的指标（假设all_in_one返回包含'time'的字典）
                # 注意：all_in_one的参数应匹配当前时间段（year和season）
                metrics = all_in_one(G_ER, year, season)
                all_metrics.append(metrics)
                print(f"  完成第{i + 1}/{num_trials}次ER计算")

            # ----------------------
            # 3. 计算该时间段的指标平均值（含非平均字段）
            # ----------------------
            # 非平均字段（如'time'）
            non_averaged_keys = ['time']
            non_averaged = {
                key: all_metrics[0][key]
                for key in non_averaged_keys
                if key in all_metrics[0]
            }

            # 需平均的字段
            averaged_keys = [k for k in all_metrics[0].keys() if k not in non_averaged_keys]
            averaged = {}
            for key in averaged_keys:
                values = [m[key] for m in all_metrics if not np.isnan(m[key])]
                averaged[key] = np.mean(values) if values else np.nan

            # 合并为该时间段的结果
            final_metrics = {**averaged, **non_averaged}
            all_results.append(final_metrics)
            print(f"  完成{year}_{season}的指标计算")

    # ----------------------
    # 4. 保存为CSV文件
    # ----------------------
    if all_results:
        # 转为DataFrame，确保第一列为'time'
        df = pd.DataFrame(all_results)
        # 调整列顺序：将'time'放在第一列
        if 'time' in df.columns:
            cols = ['time'] + [col for col in df.columns if col != 'time']
            df = df[cols]

        # 保存CSV

        df.to_csv('Figure/Season/all_in_one_nm_zero_model.csv', index=False, encoding='utf-8')
        print(f"\n所有时间段的指标已保存")
    else:
        print("\n未计算到任何有效指标，无法生成CSV")
def draw_edges_nodes_time_series():
    """
    根据 all in one Digraph 的数据画出 edges和nodes变化图
    :return:
    """
    # 1. 读取数据
    df = pd.read_csv('Figure/Season/all_in_one_Digraph.csv')
    # 4. 创建画布和坐标轴
    fig, ax1 = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 2. 创建右侧Y轴（与左侧Y轴共享X轴，实现双轴对齐）
    ax2 = ax1.twinx()  # 关键：生成与ax1共享X轴的第二个Y轴

    # -------------------------- 4. 绘制双折线（分别绑定左右Y轴） --------------------------
    # -------------------------- 左侧Y轴：Nodes（假设N列是Nodes数量） --------------------------
    ax1.plot(
        df['time'],  # X轴：时间
        df['N'],     # Y轴：Nodes数量（绑定左侧ax1）
        label='Nodes',  # 图例名称
        color='red',  # 颜色（可选：用十六进制色更精准，这里是深蓝色）
        marker='o',       # 数据点标记（圆形）
        linestyle='-',    # 线条样式（实线）
        linewidth=2.5,    # 线条宽度（加粗更清晰）
        markersize=7      # 数据点大小
    )

    # -------------------------- 右侧Y轴：Edges（假设M列是Edges数量） --------------------------
    ax2.plot(
        df['time'],  # X轴：时间（与左侧共享，无需重复设置）
        df['M'],     # Y轴：Edges数量（绑定右侧ax2）
        label='Edges',  # 图例名称
        color='blue',  # 颜色（深红色，与左侧区分明显）
        marker='s',       # 数据点标记（方形，与圆形区分）
        linestyle='--',   # 线条样式（虚线，与实线区分）
        linewidth=2.5,    # 线条宽度（与左侧一致，保持美观）
        markersize=7      # 数据点大小（与左侧一致）
    )

    # -------------------------- 5. 美化双轴标签与标题 --------------------------
    # -------------------------- 左侧Y轴（ax1）设置 --------------------------
    ax1.set_xlabel('Time', fontsize=12, fontweight='bold')  # X轴标签（加粗）
    ax1.set_ylabel('Number of Nodes',  # 左侧Y轴标签（明确对应Nodes）
                   color='red',    # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax1.tick_params(axis='y',  # 左侧Y轴刻度设置
                    colors='red',  # 刻度颜色与线条一致
                    labelsize=10)      # 刻度文字大小

    # -------------------------- 右侧Y轴（ax2）设置 --------------------------
    ax2.set_ylabel('Number of Edges',  # 右侧Y轴标签（明确对应Edges）
                   color='blue',    # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax2.tick_params(axis='y',  # 右侧Y轴刻度设置
                    colors='blue',  # 刻度颜色与线条一致
                    labelsize=10)      # 刻度文字大小

    # -------------------------- 标题与X轴刻度 --------------------------
    ax1.set_title(
        'Changes in the Number of Edges and Nodes in the Network Over Time',
        fontsize=14,
        fontweight='bold',
        pad=20  # 标题与图表的间距（避免拥挤）
    )
    ax1.tick_params(axis='x', rotation=45)  # X轴时间标签旋转45度，避免文字重叠

    # -------------------------- 6. 合并双轴图例（关键：避免图例重复） --------------------------
    # 提取左右轴的图例，合并为一个（放在图表右侧，不遮挡数据）
    lines1, labels1 = ax1.get_legend_handles_labels()  # 左侧轴图例
    lines2, labels2 = ax2.get_legend_handles_labels()  # 右侧轴图例
    ax1.legend(
        lines1 + lines2,  # 合并图例线条
        labels1 + labels2,  # 合并图例文字
        fontsize=11,
        loc='lower left',  # 图例位置（右上，不遮挡数据）
        frameon=True,       # 显示图例边框
        fancybox=True,      # 边框圆角
        shadow=True         # 边框阴影（更立体）
    )

    # -------------------------- 7. 调整布局与保存 --------------------------
    # 自动调整布局（避免标签、图例被截断）
    plt.tight_layout()

    # 保存图片（dpi=300为高清，bbox_inches='tight'避免裁剪边缘）
    plt.savefig(
        'Figure/Season/edges_nodes_time_series.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'  # 背景色为白色（避免保存后背景透明）
    )

    # 显示图表（运行时弹出窗口）
    plt.show()
def draw_avg_length_efficiency_time_series():
    """
    画平均度和效率的变化趋势图
    :return:
    """
    # 1. 读取数据
    df = pd.read_csv('Figure/Season/all_in_one_Digraph.csv')
    # 4. 创建画布和坐标轴
    fig, ax1 = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 2. 创建右侧Y轴（与左侧Y轴共享X轴，实现双轴对齐）
    ax2 = ax1.twinx()  # 关键：生成与ax1共享X轴的第二个Y轴

    # -------------------------- 4. 绘制双折线（分别绑定左右Y轴） --------------------------
    # -------------------------- 左侧Y轴：Nodes（假设N列是Nodes数量） --------------------------
    ax1.plot(
        df['time'],  # X轴：时间
        df['avg_length'],     # Y轴：Nodes数量（绑定左侧ax1）
        label='average path length',  # 图例名称
        color='red',  # 颜色（可选：用十六进制色更精准，这里是深蓝色）
        marker='o',       # 数据点标记（圆形）
        linestyle='-',    # 线条样式（实线）
        linewidth=2.5,    # 线条宽度（加粗更清晰）
        markersize=7      # 数据点大小
    )

    # -------------------------- 右侧Y轴：Edges（假设M列是Edges数量） --------------------------
    ax2.plot(
        df['time'],  # X轴：时间（与左侧共享，无需重复设置）
        df['efficiency'],     # Y轴：Edges数量（绑定右侧ax2）
        label='efficiency',  # 图例名称
        color='blue',  # 颜色（深红色，与左侧区分明显）
        marker='s',       # 数据点标记（方形，与圆形区分）
        linestyle='--',   # 线条样式（虚线，与实线区分）
        linewidth=2.5,    # 线条宽度（与左侧一致，保持美观）
        markersize=7      # 数据点大小（与左侧一致）
    )

    # -------------------------- 5. 美化双轴标签与标题 --------------------------
    # -------------------------- 左侧Y轴（ax1）设置 --------------------------
    ax1.set_xlabel('Time', fontsize=12, fontweight='bold')  # X轴标签（加粗）
    ax1.set_ylabel('avg_length',
                   color='red',    # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax1.tick_params(axis='y',  # 左侧Y轴刻度设置
                    colors='red',  # 刻度颜色与线条一致
                    labelsize=10)      # 刻度文字大小

    # -------------------------- 右侧Y轴（ax2）设置 --------------------------
    ax2.set_ylabel('efficiency',  # 右侧Y轴标签（明确对应Edges）
                   color='blue',    # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax2.tick_params(axis='y',  # 右侧Y轴刻度设置
                    colors='blue',  # 刻度颜色与线条一致
                    labelsize=10)      # 刻度文字大小

    # -------------------------- 标题与X轴刻度 --------------------------
    ax1.set_title(
        'Changes in the average length and efficiency in the Network Over Time',
        fontsize=14,
        fontweight='bold',
        pad=20  # 标题与图表的间距（避免拥挤）
    )
    ax1.tick_params(axis='x', rotation=45)  # X轴时间标签旋转45度，避免文字重叠

    # -------------------------- 6. 合并双轴图例（关键：避免图例重复） --------------------------
    # 提取左右轴的图例，合并为一个（放在图表右侧，不遮挡数据）
    lines1, labels1 = ax1.get_legend_handles_labels()  # 左侧轴图例
    lines2, labels2 = ax2.get_legend_handles_labels()  # 右侧轴图例
    ax1.legend(
        lines1 + lines2,  # 合并图例线条
        labels1 + labels2,  # 合并图例文字
        fontsize=11,
        loc='upper right',  # 图例位置（右上，不遮挡数据）
        frameon=True,       # 显示图例边框
        fancybox=True,      # 边框圆角
        shadow=True         # 边框阴影（更立体）
    )

    # -------------------------- 7. 调整布局与保存 --------------------------
    # 自动调整布局（避免标签、图例被截断）
    plt.tight_layout()
    # 保存图片（dpi=300为高清，bbox_inches='tight'避免裁剪边缘）
    plt.savefig(
        'Figure/Season/avg_length_efficiency_time_series.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'  # 背景色为白色（避免保存后背景透明）
    )
    # 显示图表（运行时弹出窗口）
    plt.show()
def draw_avg_degree_and_avg_strength_time_series():
    # 存储结果：键为时间（如"2017 Spring"），值为(平均度, 平均加权度)
    result = {}
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

    # 读取数据并计算指标
    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue

            time = f"{year} {season}"
            DiG = nx.read_graphml(file_path)  # 保留有向图
            n = DiG.number_of_nodes()
            m = DiG.number_of_edges()

            avg_degree = 2 * m / n

            # 2. 计算平均强度（total_TEU的平均值）
            total_strength = 0.0
            for node_id, node_attrs in DiG.nodes(data=True):  # 正确解析节点属性
                # 安全获取属性，处理缺失值
                teu = node_attrs.get('total_TEU', 0.0)
                try:
                    total_strength += float(teu)
                except ValueError:
                    # 处理属性值无法转换为float的情况（如非数值字符串）
                    print(f"⚠️ {time} 节点 {node_id} 的 total_TEU 格式错误，跳过")
                    continue
            avg_strength = total_strength / n
            print(f"{time} - 平均总度数: {avg_degree:.2f}, 平均TEU强度: {avg_strength:.2f}")

            # 存储结果
            result[time] = (avg_degree, avg_strength)

    time_list = list(result.keys())
    # 绘制趋势图
    # 4. 创建画布和坐标轴
    fig, ax1 = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 2. 创建右侧Y轴（与左侧Y轴共享X轴，实现双轴对齐）
    ax2 = ax1.twinx()  # 关键：生成与ax1共享X轴的第二个Y轴

    # 平均度曲线
    ax1.plot(
        time_list,
        [value[0] for key,value in result.items()],
        marker='o',
        linestyle='-',
        color='#1f77b4',
        label='Average Degree'
    )

    # 平均加权度曲线
    ax2.plot(
        time_list,
        [value[1] for key,value in result.items()],
        marker='s',
        linestyle='-',
        color='#ff7f0e',
        label='Average Weighted Degree'
    )

    # 美化图表
    ax1.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Degree',  # 左侧Y轴标签（明确对应Nodes）
                   color='#1f77b4',  # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax1.tick_params(axis='y',  # 左侧Y轴刻度设置
                    labelsize=10)  # 刻度文字大小
    # -------------------------- 右侧Y轴（ax2）设置 --------------------------
    ax2.set_ylabel('Number of Edges',  # 右侧Y轴标签（明确对应Edges）
                   color='#ff7f0e',  # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax2.tick_params(axis='y',  # 右侧Y轴刻度设置
                    labelsize=10)  # 刻度文字大小
    # -------------------------- 标题与X轴刻度 --------------------------
    ax1.set_title(
        'Changes in the average degree and average strength in the Network Over Time',
        fontsize=14,
        fontweight='bold',
        pad=20  # 标题与图表的间距（避免拥挤）
    )
    ax1.tick_params(axis='x', rotation=45)  # X轴时间标签旋转45度，避免文字重叠

    # -------------------------- 6. 合并双轴图例（关键：避免图例重复） --------------------------
    # 提取左右轴的图例，合并为一个（放在图表右侧，不遮挡数据）
    lines1, labels1 = ax1.get_legend_handles_labels()  # 左侧轴图例
    lines2, labels2 = ax2.get_legend_handles_labels()  # 右侧轴图例
    ax1.legend(
        lines1 + lines2,  # 合并图例线条
        labels1 + labels2,  # 合并图例文字
        fontsize=11,
        loc='upper left',  # 图例位置（右上，不遮挡数据）
        frameon=True,  # 显示图例边框
        fancybox=True,  # 边框圆角
        shadow=True  # 边框阴影（更立体）
    )

    # -------------------------- 7. 调整布局与保存 --------------------------
    # 自动调整布局（避免标签、图例被截断）
    plt.tight_layout()

    # 保存图片（dpi=300为高清，bbox_inches='tight'避免裁剪边缘）
    plt.savefig(
        'Figure/Season/avg_degree_and_avg_strength_time_series.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'  # 背景色为白色（避免保存后背景透明）
    )

    # 显示图表（运行时弹出窗口）
    plt.show()
def draw_degree_strength_std_time_series():
    """
    度值与强度的  标准差
    :return:
    """
    # 存储结果：键为时间，值为(平均度, 度的标准差, 平均强度, 强度的标准差)
    result = {}
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

    # 存储原始遍历顺序的时间列表
    time_list = []

    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue

            time = f"{year} {season}"
            DiG = nx.read_graphml(file_path)  # 保留有向图
            nodes = list(DiG.nodes())
            n = len(nodes)
            if n < 2:  # 至少2个节点才能计算标准差
                print(f'⚠️ {time} 节点数不足（{n}个），无法计算统计量')
                continue
            m = DiG.number_of_edges()

            degrees = []
            for node in nodes:
                in_deg = DiG.in_degree(node)
                out_deg = DiG.out_degree(node)
                degrees.append(in_deg + out_deg)

            deg_std = np.std(degrees, ddof=0)  # 度的样本标准差

            strengths = []
            for node_id, node_attrs in DiG.nodes(data=True):
                teu = node_attrs.get('total_TEU', 0.0)
                try:
                    strengths.append(float(teu))
                except ValueError:
                    print(f"⚠️ {time} 节点 {node_id} 的 total_TEU 格式错误，按0处理")
                    strengths.append(0.0)

            if len(strengths) < 2:
                print(f'⚠️ {time} 有效强度数据不足，无法计算标准差')
                continue

            strength_std = np.std(strengths, ddof=0)  # 强度的总体标准差 ddof=0

            result[time] = (deg_std, strength_std)
            time_list.append(time)

    # 提取数据（按原始时间顺序）
    deg_std_list = [result[t][0] for t in time_list]
    strength_std_list = [result[t][1] for t in time_list]

    # 绘制双轴图表（左侧：度相关，右侧：强度相关）
    fig, ax1 = plt.subplots(figsize=(14, 7))
    ax2 = ax1.twinx()

    # 度的标准差曲线
    ax1.plot(
        time_list,
        deg_std_list,
        marker='o',
        linestyle='-',
        color='#1f77b4',
        linewidth=2.5,
        markersize=7,
        label='Degree Std Dev'
    )

    # 强度的标准差曲线
    ax2.plot(
        time_list,
        strength_std_list,
        marker='s',
        linestyle='--',
        color='#ff7f0e',
        linewidth=2.5,
        markersize=7,
        label='Strength Std Dev'
    )

    # 美化图表
    ax1.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Degree Metrics',
                   color='#1f77b4',
                   fontsize=12,
                   fontweight='bold')
    ax1.tick_params(axis='y', labelsize=10)

    ax2.set_ylabel('TEU Strength Metrics',
                   color='#ff7f0e',
                   fontsize=12,
                   fontweight='bold')
    ax2.tick_params(axis='y', labelsize=10)

    ax1.set_title(
        'Degree and Strength Std Dev Over Time',
        fontsize=14,
        fontweight='bold',
        pad=20
    )
    ax1.tick_params(axis='x', rotation=45)  # X轴标签旋转对齐

    # 合并所有图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        fontsize=10,
        loc='upper left',
        frameon=True,
        fancybox=True
    )

    plt.tight_layout()

    # 保存图片
    plt.savefig(
        'Figure/Season/degree_strength_std_time_series.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'
    )

    plt.show()
def draw_total_teu():
    """
    画出总的TEU变化图
    :return:
    """
    years = range(2017, 2022)  # 一年一个单位
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    records = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':  # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)
            total_teu = sum(float(d.get('volumeTEU', 0)) for _, _, d in G.edges(data=True))
            records.append({'time': f"{year}_{season}", 'total_TEU': total_teu})

    df = pd.DataFrame(records)

    # 4. 创建画布和坐标轴
    fig, ax = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 5. 绘制折线图
    ax.plot(df['time'], df['total_TEU'],
            label='TEU',
            color='blue',
            marker='o',  # 数据点标记
            linestyle='-',  # 线条样式
            linewidth=2,  # 线条宽度
            markersize=6)  # 标记大小
    # 6. 设置坐标轴标签和标题
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('TEU', fontsize=12)
    ax.set_title('Changes in the TEU in the network over time', fontsize=14, pad=20)
    # 7. 设置坐标轴刻度
    ax.tick_params(axis='x', rotation=45)  # x轴标签旋转45度，避免重叠
    ax.tick_params(axis='both', which='major', labelsize=10)
    # 9. 添加图例
    ax.legend(fontsize=10, loc='best')  # loc='best' 自动选择最佳位置
    # 10. 调整布局，避免标签被截断
    plt.tight_layout()
    # 11. 保存图片（可选）
    plt.savefig('Figure/Season/teu_time_series.png', dpi=300, bbox_inches='tight')
    # 12. 显示图表
    plt.show()
def draw_total_teu_and_us_cn_teu():
    """
    美国的总体teu 和 与中国交易的teu 变化趋势图
    :return:
    """
    # 中美贸易变化图
    years = range(2017, 2022)  # 一年一个单位
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    us_cn_records = []
    total_records = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':  # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)
            us_cn_teu = 0
            total_teu = 0
            for u, v, data in G.edges(data=True):
                u_country = G.nodes[u].get('Country', 'Unknown')
                v_country = G.nodes[v].get('Country', 'Unknown')
                # 总量teu
                total_teu += data['volumeTEU']
                # 中美teu
                if (u_country == 'United States' and v_country == 'China' or
                        u_country == 'China' and v_country == 'United States'):
                    us_cn_teu += data['volumeTEU']

            total_records.append({
                'time': f"{year}_{season}",
                'total_teu': total_teu}
            )
            us_cn_records.append({
                'time': f"{year}_{season}",
                'us_cn_teu': us_cn_teu
            })
    df_us_cn = pd.DataFrame(us_cn_records)
    df = pd.DataFrame(total_records)
    # 4. 创建画布和坐标轴
    fig, ax = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 5. 绘制折线图
    ax.plot(df_us_cn['time'], df_us_cn['us_cn_teu'],
            label='us and cn teu',
            color='blue',
            marker='o',  # 数据点标记
            linestyle='-',  # 线条样式
            linewidth=2,  # 线条宽度
            markersize=6)  # 标记大小
    ax.plot(df['time'], df['total_teu'],
            label='total teu',
            color='red',
            marker='o',  # 数据点标记
            linestyle='-',  # 线条样式
            linewidth=2,  # 线条宽度
            markersize=6)  # 标记大小
    # 6. 设置坐标轴标签和标题
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('TEU', fontsize=12)
    ax.set_title('Changes in the TEU', fontsize=14, pad=20)
    # 7. 设置坐标轴刻度
    ax.tick_params(axis='x', rotation=45)  # x轴标签旋转45度，避免重叠
    ax.tick_params(axis='both', which='major', labelsize=10)
    # 9. 添加图例
    ax.legend(fontsize=10, loc='best')  # loc='best' 自动选择最佳位置
    # 10. 调整布局，避免标签被截断
    plt.tight_layout()
    # 11. 保存图片（可选）
    plt.savefig('Figure/Season/total_teu_and_us_cn_teu_time_series.png', dpi=300, bbox_inches='tight')
    # 12. 显示图表
    plt.show()
def write_country_teu():
    years = range(2017, 2022)  # 一年一个单位
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    records = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':  # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)

            country_teu = {}
            for u, v, data in G.edges(data=True):
                u_country = G.nodes[u].get('Country', 'Unknown')
                v_country = G.nodes[v].get('Country', 'Unknown')

                # 只处理涉及美国的边
                if u_country == 'United States' and v_country != 'United States':
                    target_country = v_country
                elif v_country == 'United States' and u_country != 'United States':
                    target_country = u_country
                else:
                    # 跳过不涉及美国的边或美国与美国之间的边
                    print("均不是美国")
                    continue

                # 确保volumeTEU是数值类型
                try:
                    teu = float(data.get('volumeTEU', 0))
                except (ValueError, TypeError):
                    print("数值有问题")
                    teu = 0  # 处理无效数值的情况

                # 关键修正：检查字典中是否已有该国家，没有则初始化
                if target_country in country_teu:
                    country_teu[target_country] += teu
                else:
                    country_teu[target_country] = teu
            # 将结果添加到记录中
            records.append({
                'time': f"{year}_{season}",
                'country_teu': country_teu
            })
            print(f"✅ 已处理: {year}_{season}")
    for record in records:
        print(record)
    # 1. 处理每条记录，将国家-TEU字典拆分为键值对
    expanded_records = []
    for record in records:
        # 以time为基础创建新字典
        expanded = {'time': record['time']}
        # 加入每个国家的TEU数据
        for country, teu in record['country_teu'].items():
            expanded[country] = teu
        expanded_records.append(expanded)

    # 2. 转换为DataFrame（缺失的国家数据会自动填充为NaN）
    df = pd.DataFrame(expanded_records)

    # 3. 将NaN填充为0（表示该季节与该国无贸易数据）
    df = df.fillna(0)

    # 4. 调整列顺序：确保time在第一列
    columns = ['time'] + [col for col in df.columns if col != 'time']
    df = df[columns]

    # 5. 显示结果
    print("转换后的DataFrame：")
    print(df.head())

    # 6. 保存为CSV（可选）
    df.to_csv('InputData/country_teu.csv', index=False)
def draw_top5_countries_trading_with_the_US():
    """
    与美国交易TEU最多的top5国家除了中国
    :return:
    """
    df = pd.read_csv('InputData/country_teu.csv')
    record = {}
    # 定义函数：获取每行最大的n个值（最多5个）及其列名
    def get_top5(row):
        # 排除第一列（time列），处理剩余数值列
        value_columns = row.index[1:]  # 获取除time外的列名
        values = row[value_columns]  # 获取对应的值

        # 按值降序排序，取前5个（不足5个则取全部）
        sorted_values = values.sort_values(ascending=False).head(5)

        # 提取列名和值，用NaN填充不足5个的位置
        top_names = list(sorted_values.index) + [np.nan] * (5 - len(sorted_values))
        top_values = list(sorted_values.values) + [np.nan] * (5 - len(sorted_values))

        top = {key: value for key, value in zip(top_names, top_values)}

        record[row['time']] = top


    # 应用函数到每一行
    df.apply(get_top5, axis=1)

    # -------------------------- 1. 国家样式配置 --------------------------
    country_styles = {
        'China': {'color': '#E74C3C', 'marker': 'o', 'linestyle': '-'},  # 红色+圆形+实线
        'South Korea': {'color': '#3498DB', 'marker': 's', 'linestyle': '--'},  # 蓝色+方形+虚线
        'Japan': {'color': '#F39C12', 'marker': '^', 'linestyle': '-.'},  # 橙色+三角形+点线
        'Germany': {'color': '#2ECC71', 'marker': 'D', 'linestyle': ':'},  # 绿色+菱形+点线
        'Belgium': {'color': '#9B59B6', 'marker': 'p', 'linestyle': '-'},  # 紫色+五边形+实线
        'Vietnam': {'color': '#1ABC9C', 'marker': '*', 'linestyle': '--'},  # 青色+星形+虚线
        'Canada': {'color': '#F1C40F', 'marker': 'h', 'linestyle': '-.'},  # 黄色+六边形+点线
        'Singapore': {'color': '#34495E', 'marker': 'X', 'linestyle': '-'}  # 深灰色+X形标记+实线
    }
    fig, ax = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    for country, attr in country_styles.items():
        if country == 'China':
            continue
        time_line = []
        value_line = []
        for year in years:
            for season in seasons:
                if (year == 2021 and
                        (season == 'Summer' or season == 'Autumn' or season == 'Winter')):
                    continue
                time = f'{year}_{season}'
                if country in record[time]:
                    time_line.append(time)
                    value_line.append(record[time][country])
                # 5. 绘制折线图
                # 绘制edges折线
        ax.plot(time_line, value_line,
                label=country,
                color=country_styles[country]['color'],
                marker=country_styles[country]['marker'],  # 数据点标记
                linestyle=country_styles[country]['linestyle'],  # 线条样式
                linewidth=2,    # 线条宽度
                markersize=6)   # 标记大小
    # 6. 设置坐标轴标签和标题
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('TEU', fontsize=12)
    ax.set_title('Chart of TEU changes for the top five countries trading with the United States', fontsize=14, pad=20)
    # 7. 设置坐标轴刻度
    ax.tick_params(axis='x', rotation=45)  # x轴标签旋转45度，避免重叠
    ax.tick_params(axis='both', which='major', labelsize=10)
    # 9. 添加图例
    ax.legend(fontsize=10, loc='best')  # loc='best' 自动选择最佳位置
    # 10. 调整布局，避免标签被截断
    plt.tight_layout()
    plt.savefig('Figure/Season/Chart of TEU changes for the top five countries trading with the United States.png', dpi=300, bbox_inches='tight')
    plt.show()
def calculate_US_top10_node_pairs_by_TEU_year():
    """
    计算出每一个时间段的的TEU最大的edges （nodes之间的TEU 包含了两个方向）
    :return:
    """
    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    top_edges = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)


            # 按节点对累加 TEU
            flows = {}
            for u, v, d in G.edges(data=True):
                pair = tuple(sorted([u, v]))  # 无向，排序去重
                flows[pair] = flows.get(pair, 0) + float(d.get('volumeTEU', 0))

            # 转成 DataFrame
            data = [{'time': f"{year}_{season}", 'from': pair[0], 'to': pair[1], 'total_TEU': teu}
                    for pair, teu in flows.items()]

            # 当年 Top
            top = pd.DataFrame(data).sort_values('total_TEU', ascending=False).head(30)
            top_edges.append(top)
    df = pd.concat(top_edges, ignore_index=True)
    df.to_csv(f'InputData/US_top_edges_by_TEU.csv', index=False)
def draw_top10_TEU_edges_map():
    def draw_year(time):
        """
        绘图函数（只建一次地图，复用）
        :param time:
        :return:
        """
        fig, ax = plt.subplots(figsize=(10, 7))
        world_map = Basemap(resolution='l', projection='cyl', lon_0=-100, ax=ax)
        world_map.drawmapboundary(fill_color='#D0CFD4')
        world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
        world_map.drawcoastlines()

        # ---------- 画港口 ----------
        ports = year_to_ports.get(time, set())
        if ports:
            lon = [shift_lon(port_coords[p][0]) for p in ports]
            lat = [port_coords[p][1] for p in ports]
            x, y = world_map(lon, lat)
            # 按 TEU 总和决定大小
            sizes = [year_to_node_size[time].get(p, base_sz) for p in ports]

            # 拆成两套索引
            us_idx = [i for i, p in enumerate(ports) if p.startswith('US')]
            fore_idx = [i for i, p in enumerate(ports) if not p.startswith('US')]
            # 美国港口
            if us_idx:
                world_map.scatter([x[i] for i in us_idx],
                                  [y[i] for i in us_idx],
                                  s=[sizes[i] for i in us_idx],
                                  marker='o', color='#FF6A00',  # 亮橙
                                  edgecolor='white', linewidth=0.5,
                                  zorder=10, label='US Port')
                # 外国港口
                if fore_idx:
                    world_map.scatter([x[i] for i in fore_idx],
                                      [y[i] for i in fore_idx],
                                      s=[sizes[i] for i in fore_idx],
                                      marker='o', color='#00BFFF',  # 深天蓝
                                      edgecolor='white', linewidth=0.5,
                                      zorder=10, label='Foreign Port')

        # ---------- 画边（带 TEU→透明度映射） ----------
        edges = year_to_edges.get(time, [])
        widths = year_to_edge_width[time]  # 线宽 Series
        teus = edges['total_TEU']  # 原始 TEU
        # 透明度映射：TEU 最小→0.35，最大→1.0
        alphas = 0.5 + 0.5 * (teus - teus.min()) / (
                    teus.max() - teus.min()) if teus.max() != teus.min() else np.full_like(teus, 0.8, dtype=float)
        for index, row in edges.iterrows():
            lon1, lat1 = shift_lon(port_coords[row['from']][0]), port_coords[row['from']][1]
            lon2, lat2 = shift_lon(port_coords[row['to']][0]), port_coords[row['to']][1]
            x1, y1 = world_map(lon1, lat1)
            x2, y2 = world_map(lon2, lat2)
            w = widths[index]  # 取出该行对应的线宽
            alpha = alphas[index]

            # 从列表中随机选择一个元素
            random_list = [-20, 20]     # 贝塞尔曲线的弯曲程度
            delta = random.choice(random_list)
            (cx1, cy1), (cx2, cy2) = auto_control_points(x1, y1, x2, y2, delta)

            # 3. 生成曲线点
            bx, by = bezier([x1, y1], [cx1, cy1], [cx2, cy2], [x2, y2], num=100)
            world_map.plot(bx, by, linewidth=w, color='blue', zorder=5, alpha=alpha)

        ax.set_title(f'Top 30 TEU Links – {time}')
        ax.legend()
        fig.savefig(f'Figure/Season/TopTeuEdges/US_top30_edges_worldmap_{time}.svg',
                    dpi=300, bbox_inches='tight')
        # plt.show()
        plt.close(fig)  # 防止内存泄漏
    def auto_control_points(x1, y1, x2, y2, delta=30):
        """
        给定起点、终点，返回自动生成的一组三次贝塞尔控制点
        delta : 偏移像素，>0 向上弯，<0 向下弯
        """
        t = 1 / 3
        # 1/3 处
        p1x = x1 + t * (x2 - x1)
        p1y = y1 + t * (y2 - y1)
        # 2/3 处
        p2x = x1 + 2 * t * (x2 - x1)
        p2y = y1 + 2 * t * (y2 - y1)
        # 垂直偏移
        dx, dy = x2 - x1, y2 - y1
        lenAB = np.hypot(dx, dy)
        nx, ny = -dy / lenAB, dx / lenAB
        c1x = p1x + delta * nx
        c1y = p1y + delta * ny
        c2x = p2x + delta * nx
        c2y = p2y + delta * ny
        return (c1x, c1y), (c2x, c2y)
    def shift_lon(lon):
        """把经度压到 [-180,180]，解决跨中央经线问题"""
        return lon - 360 if lon > 70 else lon
    def bezier(p0, p1, p2, p3, num=100):
        """
        三阶贝塞尔插值
        :param p0:
        :param p1:
        :param p2:
        :param p3:
        :param num:
        :return:
        """
        t = np.linspace(0, 1, num)
        b = lambda i, t: comb(3, i) * (t ** i) * ((1 - t) ** (3 - i))
        pts = (np.outer(b(0, t), p0) + np.outer(b(1, t), p1) +
               np.outer(b(2, t), p2) + np.outer(b(3, t), p3))
        return pts[:, 0], pts[:, 1]
        # 1. 读 Top10 边


    top30_edges = pd.read_csv('InputData/US_top_edges_by_TEU.csv')
    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(info["longitude"]), float(info["latitude"]))
        for node, info in Port_Data.items()
        if "longitude" in info and "latitude" in info
    }

    # 按年份分组，提前建好 {year: set_of_ports} 和 {year: edges}
    year_to_ports = {}
    year_to_edges = {}

    # 预先算好每年「边」和「节点」的 TEU 比例
    year_to_edge_width = {}  # {year: Series(index=原始行号, 值=线宽)}
    year_to_node_size = {}  # {year: Series(index=港口名, 值=点大小)}

    base_lw = 0.5  # 最细线宽
    max_lw = 3  # 最粗线宽
    base_sz = 20  # 最小点
    max_sz = 200  # 最大点

    for season, group in top30_edges.groupby('time'):  # 按照time分成若干份DataFrame
        # 港口和连接
        ports = set(group['from']).union(set(group['to']))
        year_to_ports[season] = {p for p in ports if p in port_coords}
        year_to_edges[season] = group[
            (group['from'].isin(port_coords)) & (group['to'].isin(port_coords))
            ]

        # 节点和连接的大小
        # 1. 边宽：按 TEU 占比线性映射
        teu = group['total_TEU']
        share = (teu - teu.min()) / (teu.max() - teu.min()) if teu.max() != teu.min() else 0
        year_to_edge_width[season] = base_lw + share * (max_lw - base_lw)

        # 2. 节点大小：把每条边的 TEU 累加到两端港口
        node_teus = {}
        for _, row in group.iterrows():
            for node in (row['from'], row['to']):
                node_teus[node] = node_teus.get(node, 0) + row['total_TEU']
        # 同样归一化
        if node_teus:
            max_t = max(node_teus.values())
            min_t = min(node_teus.values())
            for n in node_teus:
                sh = (node_teus[n] - min_t) / (max_t - min_t) if max_t != min_t else 0
                node_teus[n] = base_sz + sh * (max_sz - base_sz)
        year_to_node_size[season] = node_teus

    # 主循环（支持多年）
    for year in range(2017, 2022):
        for season in ['Spring','Summer','Autumn','Winter']:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            draw_year(f"{year}_{season}")
def write_adjlist_attr(G, path, attr='volumeTEU', encoding='utf-8'):
    """
    将 DiGraph 导出成邻接表
    """
    path = pathlib.Path(path)
    with path.open('w', encoding=encoding) as f:
        f.write('source,target,weight\n')                       # 1. 属性声明
        for u, v, d in G.edges(data=True):
            f.write(f'{u},{v},{d.get(attr, 0)}\n')              # 2. 源 目标 值
def write_US_TEU_change_value():
    """
    保存美国2017和2021的港口TEU变化量
    :return:
    """
    DiGraph_2017 = nx.read_graphml('../Data/2017/US/US2017_Digraph.graphml')
    DiGraph_2021 = nx.read_graphml('../Data/2021/US/US2021_Digraph.graphml')

    US_TEU_change_value = {}        # 美国的节点TEU变化的量
    for node, attr in DiGraph_2017.nodes(data=True):
        if attr.get("Country", None) == "United States":
            if DiGraph_2021.has_node(node):
                # 2017年 2021年 都有的
                US_TEU_change_value[node] = DiGraph_2021.nodes[node]["total_TEU"] - DiGraph_2017.nodes[node]["total_TEU"]
            else:
                # 2017年有的  2021年没有的
                US_TEU_change_value[node] = - DiGraph_2017.nodes[node]["total_TEU"]
    for node, attr in DiGraph_2021.nodes(data=True):
        if attr.get("Country", None) == "United States" and not DiGraph_2017.has_node(node):
            # 2017年没有的  2021年有的
            US_TEU_change_value[node] = DiGraph_2021.nodes[node]["total_TEU"]
    pathlib.Path('Figure/Year/US_TEU_change_value.json').write_text(json.dumps(US_TEU_change_value, indent=2))
def draw_US_TEU_change_value():
    """
    画出美国2017和2021的港口TEU变化量
    :return:
    """
    delta_file = 'Figure/Year/US_TEU_change_value.json'
    US_TEU_change_value = json.loads(pathlib.Path(delta_file).read_text())

    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(d["longitude"]), float(d["latitude"]))
        for node, d in Port_Data.items()
        if "longitude" in d and "latitude" in d
    }

    # 1. 画布（你的原代码）
    fig, ax = plt.subplots(figsize=(10, 7))
    world_map = Basemap(resolution='l', projection='cyl', lon_0=-100, ax=ax)
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()

    # 2. 只画美国港口（颜色+大小）
    vals = np.array(list(US_TEU_change_value.values()))
    sizes = minmax_scale(np.abs(vals),feature_range=(50, 800))  # 节点面积范围
    colors = ['#FF4E50' if v > 0 else '#1B1B1B' for v in vals]

    #region只画top10
    # N = 10  # 可调        只画变化量前十的港口
    # top_nodes = nlargest(N, US_TEU_change_value.items(), key=lambda item: abs(item[1]))
    # for node, delta in top_nodes:
    #     if node not in port_coords:  # 跳过无坐标的孤立节点
    #         continue
    #     lon, lat = port_coords[node]
    #     x, y = world_map(lon, lat)
    #     idx = list(US_TEU_change_value.keys()).index(node)  # 原索引不变
    #     world_map.scatter(x, y, s=sizes[idx],
    #                       c=colors[idx],
    #                       edgecolors='white', linewidths=0.5, zorder=10)
    #endregion

    # 只画 ΔTEU > 0 或则 < 0 的所有美国港口
    for node, delta in US_TEU_change_value.items():
        if delta < 0:  # 负增长或零变化，跳过
            continue
        if node not in port_coords:  # 无坐标，跳过
            continue
        lon, lat = port_coords[node]
        x, y = world_map(lon, lat)
        idx = list(US_TEU_change_value.keys()).index(node)
        world_map.scatter(x, y, s=sizes[idx],
                          c=colors[idx],  # 正增长颜色（红）
                          edgecolors='white', linewidths=0.5, zorder=10)
    # 3. 图例 & 保存
    ax.scatter([], [], c='#FF4E50', s=200, label='TEU increase')
    ax.scatter([], [], c='#1B1B1B', s=200, label='TEU decrease')



    ax.legend(loc='lower left')
    plt.title('US Port TEU Change 2017→2021', fontsize=14, pad=10)
    fig.savefig('Figure/US_TEU_change_map_1.png', dpi=300, bbox_inches='tight')
    plt.show()
def write_US_BC_change_value():
    # 读取图数据
    DiGraph_2017 = nx.read_graphml('../Data/2017/US/US2017_Digraph.graphml')
    DiGraph_2021 = nx.read_graphml('../Data/2021/US/US2021_Digraph.graphml')

    # 计算介数中心性
    betweenness_2017 = nx.betweenness_centrality(DiGraph_2017)
    betweenness_2021 = nx.betweenness_centrality(DiGraph_2021)

    # 计算介数中心性的变化
    betweenness_change = {}
    for node in set(betweenness_2017.keys()) | set(betweenness_2021.keys()):
        if node in betweenness_2017 and node in betweenness_2021:
            betweenness_change[node] = betweenness_2021[node] - betweenness_2017[node]
        elif node in betweenness_2017:
            betweenness_change[node] = -betweenness_2017[node]
        else:
            betweenness_change[node] = betweenness_2021[node]

    # 找出变化最大的几个节点
    N = 10  # 你可以根据需要修改这个数字
    top_nodes = sorted(betweenness_change.items(), key=lambda item: abs(item[1]), reverse=True)[:N]

    # 保存结果
    pathlib.Path('Figure/Year/US_BC_change_value.json').write_text(json.dumps(dict(top_nodes), indent=2))
def draw_US_BC_change_value():

    # 2. 读港口坐标
    Port_Data = ConstructNetwork.Read_Port_Data()
    port_coords = {
        node: (float(d["longitude"]), float(d["latitude"]))
        for node, d in Port_Data.items()
        if "longitude" in d and "latitude" in d
    }
    delta_file = 'Figure/Year/US_BC_change_value.json'
    US_Betweenness_change_value = json.loads(pathlib.Path(delta_file).read_text())
    # 画布
    fig, ax = plt.subplots(figsize=(10, 7))
    world_map = Basemap(resolution='l', projection='cyl', lon_0=-100, ax=ax)
    world_map.drawmapboundary(fill_color='#D0CFD4')
    world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
    world_map.drawcoastlines()


    # 只画美国港口（颜色+大小）
    vals = np.array(list(US_Betweenness_change_value.values()))
    sizes = minmax_scale(np.abs(vals),feature_range=(50, 800))  # 节点面积范围
    colors = ['#FF4E50' if v > 0 else '#1B1B1B' for v in vals]

    N = 10  # 可调        只画变化量前十的港口
    top_nodes = nlargest(N, US_Betweenness_change_value.items(), key=lambda item: abs(item[1]))
    for node, delta in top_nodes:
        if node not in port_coords:  # 跳过无坐标的孤立节点
            continue
        lon, lat = port_coords[node]
        x, y = world_map(lon, lat)
        idx = list(US_Betweenness_change_value.keys()).index(node)  # 原索引不变
        world_map.scatter(x, y, s=sizes[idx],
                          c=colors[idx],
                          edgecolors='white', linewidths=0.5, zorder=10)
        # 在循环里
        dx = 6
        dy = 4
        x_text, y_text = world_map(lon + dx, lat - dy)
        ax.text(x_text, y_text, node, color='white', fontsize=8, ha='center', va='center',
                path_effects=[patheffects.withStroke(linewidth=2, foreground='black')])

    # 图例 & 保存
    ax.scatter([], [], c='#FF4E50', s=200, label='Betweenness increase')
    ax.scatter([], [], c='#1B1B1B', s=200, label='Betweenness decrease')
    ax.legend(loc='lower left')
    plt.title('Port Betweenness Change 2017→2021', fontsize=14, pad=10)
    fig.savefig('Figure/Betweenness_change_map.png', dpi=300, bbox_inches='tight')
    plt.show()
def draw_US_top5_port_TEU_change():
    """
    美国TEU top5港口的TEU随时间变化的趋势图
    """

    # 初始化存储每个港口每年的TEU值
    top_teu_nodes_teu_over_years = {}

    # 定义年份范围
    years = range(2017, 2022)

    # 遍历每个年份
    for year in years:
        file_path = f'../Data/{year}/US/US{year}_Digraph.graphml'
        if not os.path.exists(file_path):
            print(f'⚠️ 文件不存在: {file_path}')
            continue

        # 读取图
        DiGraph = nx.read_graphml(file_path)

        # 获取图中所有美国节点的TEU值
        teu_values = {node: data['total_TEU'] for node, data in DiGraph.nodes(data=True) if
                      data.get("Country") == "United States"}

        # 找出TEU最大的5个节点
        top_teu_nodes = heapq.nlargest(5, teu_values, key=teu_values.get)

        # 更新字典，记录每个节点每年的TEU
        for node in top_teu_nodes:
            if node not in top_teu_nodes_teu_over_years:
                top_teu_nodes_teu_over_years[node] = []
            top_teu_nodes_teu_over_years[node].append(teu_values[node])

    # 绘制Top 5 港口的TEU变化图
    fig = plt.figure(figsize=(12, 8))
    markers = ['o', 's', '^', 'D', 'x']  # 不同的形状
    colors = ['b', 'g', 'r', 'c', 'm']  # 不同的颜色

    # 准备绘图数据
    for i, node in enumerate(top_teu_nodes):
        teu_values = top_teu_nodes_teu_over_years[node]
        plt.plot(years, teu_values, marker=markers[i % len(markers)], color=colors[i % len(colors)], label=node)

    plt.title('Top 5 US Ports TEU Over Years')
    plt.xlabel('Year')
    plt.ylabel('Total TEU')
    plt.legend()
    plt.box(True)  # 去除边框
    plt.xticks(years)  # 设置横坐标刻度

    fig.savefig('Figure/US_top5_port_TEU_change.png', dpi=300, bbox_inches='tight')
    plt.show()
#endregion

#region Node Centrality
def physical_network_layer():
    """
    考虑无向无权的拓扑网络  计算dc bc cc
    :return:
    """
    dc_record = {}
    bc_record = {}
    cc_record = {}
    core_number_record = {}
    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            time = f"{year}_{season}"
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            DiGraph = nx.read_graphml(file_path)
            G = nx.Graph(DiGraph)

            dc_dict = nx.degree_centrality(G)
            bc_dict = nx.betweenness_centrality(G)
            cc_dict = nx.closeness_centrality(G)
            dc_record[time] = dc_dict
            bc_record[time] = bc_dict
            cc_record[time] = cc_dict
            core_number_record[time] = nx.core_number(G)

    pathlib.Path('InputData/ports_degree_centrality.json').write_text(json.dumps(dc_record, indent=2))
    pathlib.Path('InputData/ports_betweenness_centrality.json').write_text(json.dumps(bc_record, indent=2))
    pathlib.Path('InputData/ports_closeness_centrality.json').write_text(json.dumps(cc_record, indent=2))
    pathlib.Path('InputData/ports_core_number_centrality.json').write_text(json.dumps(core_number_record, indent=2))
def freight_traffic_network_layer():
    """
    考虑一个DiGraph网络  权重为TEU
    :return:
    """
    weighted_dc_record = {}
    weighted_bc_record = {}
    weighted_pagerank_record = {}

    years = range(2017, 2022)
    seasons = ['Spring','Summer','Autumn','Winter']
    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            time = f"{year}_{season}"
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            DiGraph = nx.read_graphml(file_path)

            N = DiGraph.number_of_nodes()
            weighted_degree = dict(DiGraph.degree(weight='volumeTEU'))
            weighted_in_degree = dict(DiGraph.in_degree(weight='volumeTEU'))
            weighted_out_degree = dict(DiGraph.out_degree(weight='volumeTEU'))

            dc = {node: d / (N - 1) for node, d in weighted_degree.items()}
            in_dc = {node: d / (N - 1) for node, d in weighted_in_degree.items()}
            out_dc = {node: d / (N - 1) for node, d in weighted_out_degree.items()}

            # weighted node centrality
            node_dc = {}
            for node in DiGraph.nodes():
                node_dc[node] = {
                    'dc': dc[node],
                    'in_dc': in_dc[node],
                    'out_dc': out_dc[node]
                }
            weighted_dc_record[time] = node_dc

            # weighted betweenness centrality
            weighted_bc_record[time] = nx.betweenness_centrality(DiGraph, weight='volumeTEU')

            # weighted pagerank scores
            weighted_pagerank_record[time] = nx.pagerank(
                DiGraph,
                alpha=0.85,
                weight='volumeTEU',
                tol=1e-6
            )

            # # weighted eigen centrality  加权特征向量中心性 暂时计算不了  迭代不出来解
            # weighted_ec_record = nx.eigenvector_centrality(DiGraph, weight='volumeTEU', max_iter=100000, tol= 1e-5)

    pathlib.Path('InputData/ports_weighted_degree_centrality.json').write_text(json.dumps(weighted_dc_record, indent=2))
    pathlib.Path('InputData/ports_weighted_betweenness_centrality.json').write_text(json.dumps(weighted_bc_record, indent=2))
    pathlib.Path('InputData/ports_weighted_pagerank_scores.json').write_text(json.dumps(weighted_pagerank_record, indent=2))

    # pathlib.Path('InputData/ports_weighted_eigenvector_centrality.json').write_text(json.dumps(weighted_ec_record, indent=2))

def write_weighted_dc_sorted_ports_by_time():
    """
    按照weighted dc排名的港口图
    :return:
    """
    dc_type = 'out_dc'      # 'dc' 'in_dc' 'out_dc'
    file_path = 'InputData/ports_weighted_degree_centrality.json'
    degree_centrality = json.loads(pathlib.Path(file_path).read_text())
    # 1. 对每个时间段的港口按dc降序排序，提取港口名称列表
    sorted_ports_by_time = {}
    for time, data in degree_centrality.items():
        # 按dc降序排序，取港口名称（如['USLSA', 'USLGB', 'CNSHA']）
        sorted_ports = [port for port, metrics in sorted(data.items(), key=lambda x: x[1][dc_type], reverse=True)]
        sorted_ports_by_time[time] = sorted_ports
    # 2. 确定最大排名数（即所有时间段中港口数量最多的那个，保证行数足够）
    max_rank = max(len(ports) for ports in sorted_ports_by_time.values())
    # 3. 构建数据：行=排名（1,2,3...），列=时间段，值=港口名称
    rank_data = {}
    for time, ports in sorted_ports_by_time.items():
        # 为每个时间段填充港口名称，不足max_rank的用空值补充
        rank_data[time] = ports + [None] * (max_rank - len(ports))
    # 4. 转为DataFrame，行索引设为排名（1开始）
    df = pd.DataFrame(rank_data, index=range(1, max_rank + 1))
    # 5. 保存为CSV（index_label='排名'，明确行含义）
    df.to_csv(f'Figure/Season/weighted_{dc_type}_sorted_ports_by_time.csv', index_label='排名')
def write_weighted_bc_sorted_ports_by_time():
    """
    生成根据 加权bc值的大小 的港口排序
    :return:
    """
    file_path = 'InputData/ports_weighted_pagerank_scores.json'
    degree_centrality = json.loads(pathlib.Path(file_path).read_text())
    # 1. 对每个时间段的港口按dc降序排序，提取港口名称列表
    sorted_ports_by_time = {}
    for time, data in degree_centrality.items():
        # 按dc降序排序，取港口名称
        sorted_ports = [port for port, metrics in sorted(data.items(), key=lambda x: x[1], reverse=True)]
        sorted_ports_by_time[time] = sorted_ports
    # 2. 确定最大排名数（即所有时间段中港口数量最多的那个，保证行数足够）
    max_rank = max(len(ports) for ports in sorted_ports_by_time.values())
    # 3. 构建数据：行=排名（1,2,3...），列=时间段，值=港口名称
    rank_data = {}
    for time, ports in sorted_ports_by_time.items():
        # 为每个时间段填充港口名称，不足max_rank的用空值补充
        rank_data[time] = ports + [None] * (max_rank - len(ports))
    # 4. 转为DataFrame，行索引设为排名（1开始）
    df = pd.DataFrame(rank_data, index=range(1, max_rank + 1))
    # 5. 保存为CSV（index_label='排名'，明确行含义）
    df.to_csv(f'Figure/Season/weighted_pagerank_scores_sorted_ports_by_time.csv', index_label='排名')
def draw_USLSA_USLGB_USNWK_weighted_degree_centrality_trend_chart():
    """
    美国这三个港口的加权中心性变化趋势图
    :return:
    """
    dc_type = 'in_dc'
    file_path = 'InputData/ports_weighted_degree_centrality.json'
    degree_centrality = json.loads(pathlib.Path(file_path).read_text())
    # 2. 提取目标港口的dc数据（按时间排序）
    target_ports = ['USLSA', 'USLGB', 'USNWK']          # 美国的top3港口
    # target_ports = ['USWAS', 'USSAV', 'USHOU', 'USNFK']

    # 收集数据：{港口: {时间: dc值}}
    port_data = {port: {} for port in target_ports}
    for time, ports in degree_centrality.items():
        for port in target_ports:
            if port in ports:  # 确保港口在该时间段存在
                port_data[port][time] = ports[port][dc_type]

    # 3. 转为DataFrame并按时间排序（关键：保证x轴时间顺序正确）
    df = pd.DataFrame(index=list(degree_centrality.keys()))

    # 填充每个港口的dc值
    for port in target_ports:
        df[port] = [port_data[port].get(time, None) for time in list(degree_centrality.keys())]

    # 4. 绘制折线图
    plt.figure(figsize=(12, 6))

    # 为每个港口绘制折线
    markers = ['o', 's', '^', 'D']  # 不同标记区分港口
    for i, port in enumerate(target_ports):
        plt.plot(
            df.index, df[port],
            marker=markers[i],  # 标记样式
            label=port,         # 图例标签
            linewidth=2,        # 线宽
            markersize=6        # 标记大小
        )

    # 美化图表
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('weighted degree centrality', fontsize=12)
    plt.title(f'USWAS,USSAV,USHOU,USNFK weighted {dc_type} trend chart', fontsize=14)
    plt.legend(fontsize=10)  # 显示图例
    plt.xticks(rotation=45)  # 时间标签旋转45度，避免重叠
    plt.tight_layout()       # 自动调整布局

    # 5. 保存图片（可选）
    # plt.savefig(f'Figure/Season/USLSA,USLGB,USNWK{dc_type}变化趋势.png', dpi=300, bbox_inches='tight')
    # 显示图表
    plt.show()


    # # 占据了美国多少的TEU
    # record = {}
    # years = range(2017, 2022)
    # seasons = ['Spring','Summer','Autumn','Winter']
    # for year in years:
    #     for season in seasons:
    #         if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
    #             continue
    #         time = f"{year}_{season}"
    #         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
    #         if not os.path.exists(file_path):
    #             print(f'⚠️ 文件不存在: {file_path}')
    #             continue
    #         DiGraph = nx.read_graphml(file_path)
    #
    #         total_teu = sum(float(d.get('volumeTEU', 0)) for _, _, d in DiGraph.edges(data=True))
    #         target_teu = sum(float(DiGraph.nodes[p].get('total_TEU', 0)) for p in target_ports)
    #         record[time] = target_teu / total_teu
    # print(record)
def draw_ports_teu_trend(teu_type:str):
    """

    :param teu_type: "in_TEU" or "out_TEU" or "total_TEU"
    :return:
    """
    target_ports = ['USLSA', 'USLGB', 'USNWK']



    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

    # 提取每个港口的TEU数据（按港口单独存储，便于后续绘图）
    port_teu = {port: {} for port in target_ports}  # {港口: {时间: TEU值}}
    time_list = []

    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后（数据不全）
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'

            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')

            time = f"{year}_{season}"
            time_list.append(time)
            # 读取图数据并提取各港口的TEU
            DiGraph = nx.read_graphml(file_path)
            for port in target_ports:
                # 处理港口不存在或属性缺失的情况
                if port not in DiGraph.nodes:
                    print(f'⚠️ 港口{port}在{time}的数据中不存在')
                    port_teu[port][time] = None
                    continue
                teu_str = DiGraph.nodes[port].get(teu_type, '0')
                try:
                    teu = float(teu_str)
                    port_teu[port][time] = teu
                except ValueError:
                    print(f'⚠️ 港口{port}在{time}的TEU值无效: {teu_str}')
                    port_teu[port][time] = None


    df = pd.DataFrame(port_teu, index=time_list)

    # 绘制TEU变化趋势图
    plt.figure(figsize=(14, 7))

    # 自定义样式（配色+标记）
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # 蓝、橙、绿
    markers = ['o', 's', '^']  # 圆形、正方形、三角形

    for i, port in enumerate(target_ports):
        plt.plot(
            df.index, df[port],
            label=port,
            color=colors[i],
            marker=markers[i],
            linewidth=2,
            markersize=7,
            linestyle='-',
            alpha=0.8
        )

    # 美化图表
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('TEU', fontsize=12)
    plt.title(f'USLSA,USLGB,USNWK {teu_type} trend chart', fontsize=14)
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right', fontsize=10)  # 旋转标签避免重叠
    plt.tight_layout()  # 自动调整布局

    # 保存图片
    plt.savefig(f'Figure/Season/USLSA_USLGB_USNWK_{teu_type}_trend.png', dpi=300, bbox_inches='tight')
    plt.show()
def draw_port_inout_trend(port: str):
    """
    绘制单个港口的 in_TEU（进口）和 out_TEU（出口）在同一张图中
    :param port: 目标港口（'USLSA', 'USLGB', 'USNWK'）
    """
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

    # 存储当前港口的进口、出口TEU数据：{TEU类型: {时间: TEU值}}
    teu_data = {'in_TEU': {}, 'out_TEU': {}}
    time_list = []

    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后（数据不全）
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'

            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue

            time = f"{year}_{season}"
            time_list.append(time)
            # 读取图数据
            DiGraph = nx.read_graphml(file_path)

            # 处理港口不存在的情况（进口、出口统一标记为None）
            if port not in DiGraph.nodes:
                print(f'⚠️ 港口{port}在{time}的数据中不存在')
                teu_data['in_TEU'][time] = None
                teu_data['out_TEU'][time] = None
                continue

            # 提取进口TEU（in_TEU）
            in_teu_str = DiGraph.nodes[port].get('in_TEU', '0')
            try:
                teu_data['in_TEU'][time] = float(in_teu_str)
            except ValueError:
                print(f'⚠️ 港口{port}在{time}的in_TEU值无效: {in_teu_str}')
                teu_data['in_TEU'][time] = None

            # 提取出口TEU（out_TEU）
            out_teu_str = DiGraph.nodes[port].get('out_TEU', '0')
            try:
                teu_data['out_TEU'][time] = float(out_teu_str)
            except ValueError:
                print(f'⚠️ 港口{port}在{time}的out_TEU值无效: {out_teu_str}')
                teu_data['out_TEU'][time] = None

    # 转换为DataFrame（时间为索引，进口/出口为列）
    df = pd.DataFrame(teu_data, index=time_list)

    # 绘制同图趋势（进口+出口）
    plt.figure(figsize=(12, 6))

    # 自定义样式：进口用蓝色圆形，出口用橙色正方形，区分度高
    styles = {
        'in_TEU': {'color': '#1f77b4', 'marker': 'o', 'label': 'Import TEU (in_TEU)'},
        'out_TEU': {'color': '#ff7f0e', 'marker': 's', 'label': 'Export TEU (out_TEU)'}
    }

    # 分别绘制进口、出口趋势线
    for teu_type, style in styles.items():
        plt.plot(
            df.index, df[teu_type],
            color=style['color'],
            marker=style['marker'],
            linewidth=2,
            markersize=7,
            linestyle='-',
            alpha=0.8,
            label=style['label']
        )

    # 图表美化（清晰易读）
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('TEU', fontsize=12)
    plt.title(f'{port} Import and Export TEU Trend', fontsize=14, pad=15)
    plt.legend(fontsize=10, loc='upper left')  # 图例放在左上角，避免遮挡线条
    # plt.grid(axis='y', alpha=0.3)  # 仅Y轴网格，辅助读值
    plt.xticks(rotation=45, ha='right', fontsize=10)  # 时间标签旋转，避免重叠
    plt.tight_layout()  # 自动调整布局，防止标签截断

    # 保存图片（按港口命名，便于区分）
    plt.savefig(f'Figure/Season/{port}_in_out_TEU_trend.png', dpi=300, bbox_inches='tight')
    plt.show()
def CNYTN_CNSHN_CNNBO_out_dc_and_in_dc_trend_chart():
    """
    这三个中国港口的 out_dc / in_dc  之比趋势图
    :return:
    """
    # 假设你已计算中国3港的平均in_dc和out_dc（16个季度的平均值，减少波动）
    target_ports = ['CNSHA', 'CNYTN', 'CNNBO']
    file_path = 'InputData/ports_weighted_degree_centrality.json'
    degree_centrality = json.loads(pathlib.Path(file_path).read_text())

    # 3. 提取每个港口在各时间段的 out_dc/in_dc 比值
    # 存储结构：{港口: {时间: 比值}}
    ratio_data = {port: {} for port in target_ports}
    all_times = list(degree_centrality.keys())

    for time in all_times:
        ports_data = degree_centrality[time]  # 该时间段的所有港口数据
        for port in target_ports:
            if port in ports_data:  # 确保港口在该时间段存在
                metrics = ports_data[port]
                in_dc = metrics.get('in_dc', 0.0)
                out_dc = metrics.get('out_dc', 0.0)

                # 避免除以0（若in_dc为0，比值设为None或一个大值）
                if in_dc == 0:
                    ratio = None  # 或根据需求设为np.inf
                else:
                    ratio = out_dc / in_dc  # 计算出口/进口比值

                ratio_data[port][time] = ratio

    # 4. 转为DataFrame（便于绘图）
    df = pd.DataFrame(ratio_data)

    # 5. 绘制折线图
    plt.figure(figsize=(14, 7))

    # 为每个港口绘制比值趋势
    markers = ['o', 's', '^']  # 不同标记区分港口
    colors =  ['#E74C3C', '#3498DB', '#9B59B6']

    for i, port in enumerate(target_ports):
        plt.plot(
            df.index, df[port],
            marker=markers[i],
            color=colors[i],
            label=port,
            linewidth=2,
            markersize=6
        )

    # 美化图表
    plt.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='=1')  # 参考线：1表示双向均衡
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('out_dc/in_dc', fontsize=12)
    plt.title(' out_dc/in_dc trend chart', fontsize=14)
    plt.legend(fontsize=10)
    plt.xticks(rotation=45)  # 时间标签旋转，避免重叠
    plt.tight_layout()

    # 保存图片
    plt.savefig('Figure/Season/CNYTN_CNSHN_CNNBO_out_dc_and_in_dc trend chart.png', dpi=300, bbox_inches='tight')

    # 显示图表
    plt.show()
def write_all_countries_teu():
    """
    保存所有国家的csv  包括美国
    :return:
    """
    years = range(2017, 2022)  # 一年一个单位
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    records = []

    for year in years:
        for season in seasons:
            if year == 2021 and season == 'Summer':  # 因为2021年的数据只到8月份
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            G = nx.read_graphml(file_path)
            total_teu = sum(float(d.get('volumeTEU', 0)) for _, _, d in G.edges(data=True))
            records.append({'time': f"{year}_{season}", 'total_TEU': total_teu})

    df_total = pd.DataFrame(records)

    df_foreign = pd.read_csv('InputData/country_teu.csv')

    df2_filtered = df_foreign[df_foreign.columns[1:]]
    # 将df2添加到df1的右侧（按列合并）
    combined_df = pd.concat([df_total, df2_filtered], axis=1)
    combined_df.to_csv('InputData/all_country_teu.csv', index=False)
def draw_country_teu_correlation_heatmap():
    """
    画top国家的TEU相关系数图
    :return:
    """
    df = pd.read_csv('InputData/all_country_teu.csv')
    # 定义需要保留的国家列名（与你的DataFrame列名一致）
    target_countries = ['total_TEU',
        'South Korea', 'Japan', 'Germany',
        'Belgium', 'Vietnam', 'Canada', 'Singapore', 'China'
    ]
    # 只保留目标国家的列
    df_filtered = df[target_countries]
    print(df_filtered)

    # 2. 计算相关系数矩阵
    # ----------------------
    # 计算皮尔逊相关系数（线性相关），返回矩阵
    corr_matrix = df_filtered.corr()

    # ----------------------
    # 3. 绘制热力图
    # ----------------------
    plt.figure(figsize=(10, 8))  # 设置图大小

    # 绘制热力图
    sns.heatmap(
        corr_matrix,
        annot=True,  # 显示相关系数数值
        cmap='RdYlBu_r',  # 配色方案（红=正相关，蓝=负相关）
        vmin=-1, vmax=1,  # 颜色范围（-1到1）
        center=0,  # 中间值为0
        square=True,  # 单元格为正方形
        linewidths=0.5,  # 单元格边框宽度
        fmt='.2f'  # 数值保留2位小数
    )

    # 设置标题和字体
    plt.title('Correlation Heatmap of TEU Flows Between Countries', fontsize=14, pad=20)
    plt.tight_layout()  # 调整布局

    # 保存图片
    plt.savefig('Figure/Season/country_teu_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()
def draw_weighted_dc_and_weighted_bc():
    """
    加权dc和加权bc之间的关系
    :return:
    """
    # ----------------------
    # 关键：设置支持中文的字体
    # ----------------------
    # 只保留 Windows 系统常见的中文字体
    plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
    port_data = ConstructNetwork.Read_Port_Data()
    years = range(2017,2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后（数据不全）
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            # 读取数据
            try:
                time_period = f"{year}_{season}"

                # 读取度中心性和介数中心性数据
                dc_path = pathlib.Path('InputData/ports_weighted_degree_centrality.json')
                bc_path = pathlib.Path('InputData/ports_betweenness_centrality.json')

                dc = json.loads(dc_path.read_text())
                bc = json.loads(bc_path.read_text())


                # 检查时间段是否存在
                if time_period not in dc or time_period not in bc:
                    raise ValueError(f"Time period {time_period} not found in data")

                # 提取该时间段的港口数据
                dc_data = dc[time_period]
                bc_data = bc[time_period]

                # 获取共同港口
                common_ports = set(dc_data.keys()) & set(bc_data.keys())
                if not common_ports:
                    raise ValueError(f"No common ports found in {time_period}")

                # 设置绘图风格
                plt.style.use('seaborn-v0_8-notebook')
                plt.figure(figsize=(12, 8))

                # 存储所有数据点用于后续范围调整
                all_dc = []
                all_bc = []

                # 绘制每个港口的散点（提高透明度：alpha从0.7→0.9）
                for port in common_ports:
                    try:
                        # 提取度中心性(dc)和介数中心性(bc)值
                        dc_val = dc_data[port]['dc']  # 度中心性值（横坐标）
                        bc_val = bc_data[port]  # 介数中心性值（纵坐标）

                        # 绘制散点：提高透明度（alpha=0.9），增强节点可见性
                        plt.scatter(
                            dc_val, bc_val,
                            s=60,
                            alpha=0.9,  # 透明度提高（0→完全透明，1→完全不透明）
                            color='steelblue',
                            edgecolors='k',
                            linewidth=0.8  # 略微加粗边框，与高透明度匹配
                        )

                        # 记录所有值用于调整坐标轴范围
                        all_dc.append(dc_val)
                        all_bc.append(bc_val)

                        # 横坐标>1000 或 纵坐标>0.075 时添加标签
                        if dc_val > 1000 or bc_val > 0.075:
                            # 计算标签偏移量（根据数据范围动态调整，确保偏移明显）
                            x_offset = (max(all_dc) - min(all_dc)) * 0.01 if all_dc else 50
                            y_offset = (max(all_bc) - min(all_bc)) * 0.01 if all_bc else 0.005

                            # 确定标签位置（增大偏移距离）
                            if dc_val > 1000:
                                # 横坐标大的点，标签向左偏移
                                text_x = dc_val - x_offset
                                ha = 'right'
                            else:
                                # 横坐标小的点，标签向右偏移
                                text_x = dc_val + x_offset
                                ha = 'left'

                            if bc_val > 0.075:
                                # 纵坐标大的点，标签向下偏移
                                text_y = bc_val - y_offset
                                va = 'top'
                            else:
                                # 纵坐标小的点，标签向上偏移
                                text_y = bc_val + y_offset
                                va = 'bottom'

                            # 添加标签（带偏移）
                            plt.text(
                                text_x, text_y,  # 偏移后的位置
                                port_data[port]["chinese_name"],    # 使用中文港口名称的标签
                                fontsize=9,
                                ha=ha,
                                va=va,
                                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.3')  # 标签背景略加深
                            )

                    except KeyError as e:
                        print(f"Warning: Port {port} missing field {e}, skipped")
                    except Exception as e:
                        print(f"Error processing port {port}: {e}, skipped")

                # 设置标题和坐标轴标签（英文）
                plt.title(f'Distribution of Weighted Degree Centrality and Betweenness Centrality ({time_period})',
                          fontsize=14, pad=20)
                plt.xlabel('Weighted Degree Centrality', fontsize=12, labelpad=10)
                plt.ylabel('Betweenness Centrality', fontsize=12, labelpad=10)

                # 添加网格线
                plt.grid(True, linestyle='--', alpha=0.5)

                # 调整坐标轴范围（留一定余量）
                x_margin = (max(all_dc) - min(all_dc)) * 0.1 if all_dc else 100
                y_margin = (max(all_bc) - min(all_bc)) * 0.1 if all_bc else 0.01
                plt.xlim(min(all_dc) - x_margin, max(all_dc) + x_margin)
                plt.ylim(min(all_bc) - y_margin, max(all_bc) + y_margin)

                # 调整布局
                plt.tight_layout()
                plt.savefig(f'Figure/Season/Centrality/Distribution of Weighted Degree Centrality and Betweenness Centrality {time_period}', dpi=300)
                # 显示图像
                # plt.show()

            except FileNotFoundError as e:
                print(f"Error: File not found - {e}")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in files")
            except Exception as e:
                print(f"An error occurred: {e}")
def draw_avg_std_weighted_dc_and_weighted_bc_time_series():
    # 读取度中心性和介数中心性数据
    dc_path = pathlib.Path('InputData/ports_weighted_degree_centrality.json')
    bc_path = pathlib.Path('InputData/ports_betweenness_centrality.json')
    dc = json.loads(dc_path.read_text())
    bc = json.loads(bc_path.read_text())
    result = {}
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

    # 读取数据并计算指标
    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            MulG = nx.read_graphml(file_path)

            time = f"{year}_{season}"

            dc_list = [value['dc'] for node,value in dc[time].items()]
            bc_list = [value for node,value in bc[time].items()]
            avg_dc = sum(dc_list) / len(dc_list)
            avg_bc = sum(bc_list) / len(bc_list)

            std_dc = np.std(dc_list, ddof=0)
            std_bc = np.std(bc_list, ddof=0)
            # 存储结果
            # result[time] = (avg_dc, avg_bc)     # 平均值的变化
            result[time] = (std_dc, std_bc)       # 标准差的变化


    time_list = list(result.keys())
    # 绘制趋势图
    # 4. 创建画布和坐标轴
    fig, ax1 = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 2. 创建右侧Y轴（与左侧Y轴共享X轴，实现双轴对齐）
    ax2 = ax1.twinx()  # 关键：生成与ax1共享X轴的第二个Y轴

    # 平均度曲线
    ax1.plot(
        time_list,
        [value[0] for key,value in result.items()],
        marker='o',
        linestyle='-',
        color='#1f77b4',
        label='Weighted Degree Centrality Std'
    )

    # 平均加权度曲线
    ax2.plot(
        time_list,
        [value[1] for key,value in result.items()],
        marker='s',
        linestyle='-',
        color='#ff7f0e',
        label='Weighted Betweenness Centrality Std'
    )

    # 美化图表
    ax1.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax1.set_ylabel('weighted degree centrality\'s std',  # 左侧Y轴标签（明确对应Nodes）
                   color='#1f77b4',  # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax1.tick_params(axis='y',  # 左侧Y轴刻度设置
                    labelsize=10)  # 刻度文字大小
    # -------------------------- 右侧Y轴（ax2）设置 --------------------------
    ax2.set_ylabel('weighted betweenness centrality\'s std',  # 右侧Y轴标签（明确对应Edges）
                   color='#ff7f0e',  # 标签颜色与线条颜色一致
                   fontsize=12,
                   fontweight='bold')
    ax2.tick_params(axis='y',  # 右侧Y轴刻度设置
                    labelsize=10)  # 刻度文字大小
    # -------------------------- 标题与X轴刻度 --------------------------
    ax1.set_title(
        'Changes in the std weighted degree centrality and std weighted betweenness over time',
        fontsize=14,
        fontweight='bold',
        pad=20  # 标题与图表的间距（避免拥挤）
    )
    ax1.tick_params(axis='x', rotation=45)  # X轴时间标签旋转45度，避免文字重叠

    # -------------------------- 6. 合并双轴图例（关键：避免图例重复） --------------------------
    # 提取左右轴的图例，合并为一个（放在图表右侧，不遮挡数据）
    lines1, labels1 = ax1.get_legend_handles_labels()  # 左侧轴图例
    lines2, labels2 = ax2.get_legend_handles_labels()  # 右侧轴图例
    ax1.legend(
        lines1 + lines2,  # 合并图例线条
        labels1 + labels2,  # 合并图例文字
        fontsize=11,
        loc='upper left',  # 图例位置（右上，不遮挡数据）
        frameon=True,  # 显示图例边框
        fancybox=True,  # 边框圆角
        shadow=True  # 边框阴影（更立体）
    )

    # -------------------------- 7. 调整布局与保存 --------------------------
    # 自动调整布局（避免标签、图例被截断）
    plt.tight_layout()

    # 保存图片（dpi=300为高清，bbox_inches='tight'避免裁剪边缘）
    plt.savefig(
        'Figure/Season/std_weighted_degree_centrality_and_std_weighted_betweenness_time_series.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'  # 背景色为白色（避免保存后背景透明）
    )

    # 显示图表（运行时弹出窗口）
    plt.show()
#region非美国港口中心性变化趋势图
# # port_target = ['BEANT', 'NLROT', 'CNSHA', 'SGSGP', 'KRBUS',
# #                'BSFRT', 'DEHAM', 'HKHKG', 'DEBHN', 'MXATM', 'CNYTN']
# port_target = ['BEANT', 'NLROT', 'CNSHA', 'SGSGP', 'KRBUS']
# value = {port: [] for port in port_target}
# port_data = ConstructNetwork.Read_Port_Data()
# file_path = 'InputData/ports_core_number_centrality.json'
# degree_centrality = json.loads(pathlib.Path(file_path).read_text())
# time = list(degree_centrality.keys())
# for _, data in degree_centrality.items():
#     sorted_asc = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
#     foreign_ports = {port:value for port,value in sorted_asc.items() if port_data[port]['country_english'] != "United States"}
#     print(foreign_ports)
#     for port in port_target:
#         value[port].append(foreign_ports[port])
# # 绘制折线图
# plt.figure(figsize=(10, 6))
# for node in port_target:
#     plt.plot(time, value[node], marker='o', label=node)  # 每个港口一条线，带标记点
#
# plt.xlabel("Time", fontsize=12)
# plt.ylabel("degree centrality", fontsize=12)
# plt.title("", fontsize=14)
# plt.legend()  # 显示港口标签
# plt.show()
#endregion
#endregion

def write_US_Top3_category():
    """
    USTop3港口的商品种类json
    使用的时候要记得自己改一下名字啥的
    :return:
    """
    target_ports = ['USLSA', 'USLGB', 'USNWK']  # 确保与数据中的港口名一致

    commodity_categories = [
        'animal_plant', 'grease', 'minerals', 'rubber_plastics',
        'pulpwood', 'textile', 'metal', 'machinery',
        'precision_instrument', 'special_other'
    ]
    years = range(2017, 2022)
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    records = {}

    for year in years:
        for season in seasons:
            # 跳过2021年夏季及以后（数据不全）
            if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
                continue

            # 读取包含类别TEU的图文件（根据你的实际文件选择MulGraph/DiGraph，这里假设是MulGraph）
            file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
            if not os.path.exists(file_path):
                print(f'⚠️ 文件不存在: {file_path}')
                continue
            time = f"{year}_{season}"
            DiG = nx.read_graphml(file_path)
            category = {}
            for port in target_ports:
                category_dict = {key : 0 for key in commodity_categories}

                # # 关键修复1：统计“港口作为起点（出口）+ 终点（进口）”的所有边
                # # 1. 港口作为起点的出边（出口：port → 其他节点）
                # for u, v, data in DiG.out_edges(port, data=True):
                #     for key in commodity_categories:
                #         teu = float(data.get(key, 0))  # 无字段则取0，转数值避免类型错
                #         category_dict[key] += teu

                # 2. 港口作为终点的入边（进口：其他节点 → port）
                for u, v, data in DiG.in_edges(port, data=True):
                    for key in commodity_categories:
                        teu = float(data.get(key, 0))
                        category_dict[key] += teu
                # 保存当前港口的类别TEU
                category[port] = category_dict

            # 保存当前时间的所有港口数据
            records[time] = category
    pathlib.Path('Figure/Season/USTop3/Category/US_Top3_in_category.json').write_text(json.dumps(records, indent=2))
def draw_US_Top3_category_pie_chart():
    """
    画美国Top3港口的商品种类饼状图
    return:
    """
    file_path = "Figure/Season/USTop3/Category/US_Top3_in_category.json"
    record = json.loads(pathlib.Path(file_path).read_text())

    target_ports = ['USLSA', 'USLGB', 'USNWK']  # 确保与数据中的港口名一致
    seasons = ["2017_Spring", "2020_Spring", "2021_Spring"]

    category_color_mapping = {
        'animal_plant': '#1f77b4',    # 深海蓝（SCI图表常用基准色）
        'grease': '#ff7f0e',          # 暖橙（低饱和，不刺眼）
        'minerals': '#2ca02c',        # 森林绿（沉稳自然）
        'rubber_plastics': '#d62728', # 砖红（低饱和红色，专业感）
        'pulpwood': '#9467bd',        # 薰衣草紫（柔和不突兀）
        'textile': '#8c564b',         # 棕褐（复古专业）
        'metal': '#e377c2',           # 淡粉紫（低饱和，区分度高）
        'machinery': '#7f7f7f',       # 中灰（中性专业）
        'precision_instrument': '#bcbd22', # 橄榄黄（低饱和，不抢眼）
        'special_other': '#17becf'    # 浅青蓝（最后一类，柔和收尾）
    }


    for season in seasons:
        for port in target_ports:
            # 输入数据
            data = record[season][port]
            sorted_data = dict(sorted(data.items(), key=lambda k: k[1], reverse=True))

            # 提取标签和数值
            labels = list(sorted_data.keys())
            values = list(sorted_data.values())

            colors = [category_color_mapping[cate] for cate in labels]  # 按类别取专属颜色

            # 设置画布
            plt.figure(figsize=(6, 6))  # 正方形画布，避免饼图变形

            # 绘制饼状图
            wedges, texts, autotexts = plt.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',  # 显示百分比（保留1位小数）
                startangle=90,      # 从90度位置开始绘制（顶部为起点）
                colors=colors,
                textprops={'fontsize': 12}  # 标签文字大小
            )

            # 美化百分比文本（白色加粗，更清晰）
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            # 添加标题
            plt.title(f'{port} {season} Import Category Distribution', fontsize=14, pad=10)

            # 确保饼图是正圆形
            plt.axis('equal')

            # 显示并保存
            plt.tight_layout()
            plt.savefig(f"Figure/Season/USTop3/Category/{port} {season} Import Category Distribution", dpi=300)
            plt.show()




#region 计算加权core number   算法太慢了，算不了，要优化
# total_record = {}
# in_record = {}
# out_record = {}
#
# years = range(2017, 2022)
# seasons = ['Spring','Summer','Autumn','Winter']
# for year in years:
#     for season in seasons:
#         if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
#             continue
#         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
#         time = f"{year}_{season}"
#         if not os.path.exists(file_path):
#             print(f'⚠️ 文件不存在: {file_path}')
#             continue
#         DiGraph = nx.read_graphml(file_path)
#
#         print(f"{year}{season} loaded")
#
#         # 加权k-core
#         k = 1
#         core_number_dict = {}
#         max_weight = max(dict(nx.degree(DiGraph, weight='volumeTEU')).values())
#
#         while k < max_weight + 2:
#             k_core_total = weighted_k_core(DiGraph, k=k, degree_type='total')
#             for node in k_core_total:
#                 core_number_dict[node] = k
#             k += 1
#         total_record[time] = core_number_dict
#         print(core_number_dict)
#
# pathlib.Path('InputData/ports_weighted_core_number_centrality.json').write_text(json.dumps(total_record, indent=2))
#endregion
#region给DiGraph添加商品种类信息
# category_mapping = {
#         'animal_plant': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
#         'grease': [15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
#         'minerals': [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38],
#         'rubber_plastics': [39, 40, 41, 42, 43],
#         'pulpwood': [44, 45, 46, 47, 48, 49],
#         'textile': [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67],
#         'metal': [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83],
#         'machinery': [84, 85, 86, 87, 88, 89],
#         'precision_instrument': [90, 91, 92, 94, 95, 96],
#         'special_other': [68, 69, 70, 93, 97, 98, 99]
#     }
# 创建反向映射：数字 -> 类别（提高查询效率）
# number_to_category = {}
# for category, numbers in category_mapping.items():
#     for num in numbers:
#         number_to_category[num] = category
#         number_to_category[str(num)] = category  # 额外添加字符串键，避免KeyError
#
#
# years = range(2017, 2022)
# seasons = ['Spring','Summer','Autumn','Winter']
# for year in years:
#     for season in seasons:
#         if year == 2021 and season == 'Summer':                 # 因为2021年的数据只到8月份
#             continue
#         # 读取MulGraph和DiGraph
#         mul_file = f'../Data/{year}/US/Season/{season}/US{year}_{season}.graphml'
#         dig_file = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
#
#         # 检查文件是否存在（合并检查，减少重复代码）
#         if not (os.path.exists(mul_file) and os.path.exists(dig_file)):
#             print(f'⚠️ 文件缺失：{mul_file} 或 {dig_file}')
#             continue
#
#         MulGraph = nx.read_graphml(mul_file)
#         DiGraph = nx.read_graphml(dig_file)
#
#
#         count = 0
#         # 先在DiGraph中创建相应的category
#         for u,v,d in DiGraph.edges(data=True):
#             for category_name in category_mapping.keys():
#                 d[category_name] = 0
#
#         for f,t,data in MulGraph.edges(data=True):
#             if not DiGraph.has_edge(f, t):
#                 print("DiGraph中没有这条边")
#                 count += 1
#                 continue
#                 # 处理HSCode：确保能映射到类别（捕获异常，避免程序中断）
#             try:
#                 hscode = data['HSCode']
#                 # 若HSCode不在映射中，设为unknown（可选，根据需求调整）
#                 cate = number_to_category.get(hscode, 'unknown')
#             except KeyError:
#                 print(f'⚠️ MulGraph边 ({f}, {t}) 无HSCode属性，跳过----{hscode}')
#                 count += 1
#                 continue
#
#             # 处理volumeTEU：确保是数值类型（避免字符串累加报错）
#             try:
#                 teu = float(data['volumeTEU'])
#             except (KeyError, ValueError):
#                 print(f'⚠️ MulGraph边 ({f}, {t}) 的volumeTEU无效，跳过')
#                 count += 1
#                 continue
#
#             # 累加TEU到对应类别（若为unknown，可选择不累加或单独处理）
#             if cate != 'unknown':
#                 DiGraph[f][t][cate] += teu
#             else:
#                 print(f'⚠️ HSCode {hscode} 无对应类别，跳过')
#                 count += 1
#         print(count / MulGraph.number_of_edges())
#         nx.write_graphml(DiGraph, dig_file)
#         print(f'✅ 成功更新并保存：{dig_file}')
#endregion
#region查看港口的商品种类TEU变化趋势图
# file_path = "Figure/Season/US_Top3_category.json"
# record = json.loads(pathlib.Path(file_path).read_text())
# data_list = []
# for time, port_dict in record.items():
#     for port, cate_teu in port_dict.items():
#         for category, teu in cate_teu.items():
#             data_list.append({
#                 "Time": time,
#                 "Port": port,
#                 "Category": category,
#                 "TEU": teu
#             })
#
# # 转为DataFrame并按时间排序（确保趋势图顺序正确）
# df = pd.DataFrame(data_list)
#
# # 商品类别配色+标记（10种类别，区分度高）
# category_colors = plt.cm.Set3(np.linspace(0, 1, 10))  # 柔和多彩的配色
# category_markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']  # 10种不同标记
#
# for port in target_ports:
#     # 筛选当前港口的数据
#     port_df = df[df["Port"] == port].copy()
#
#     # 创建单独的画布
#     plt.figure(figsize=(14, 8))
#
#     # 遍历每个商品类别，绘制趋势线
#     for idx, category in enumerate(port_df["Category"].unique()):
#         cate_df = port_df[port_df["Category"] == category]
#         plt.plot(
#             cate_df["Time"],  # X轴：时间（年_季节）
#             cate_df["TEU"],  # Y轴：TEU数值
#             label=category,
#             color=category_colors[idx],
#             marker=category_markers[idx],
#             linewidth=2.5,  # 线条粗细（清晰可见）
#             markersize=8,  # 标记大小（突出数据点）
#             alpha=0.8  # 透明度（避免重叠时刺眼）
#         )
#
#     # 图表美化（英文适配，专业清晰）
#     plt.title(f'Commodity TEU Trend for {port}', fontsize=16, pad=20)
#     plt.xlabel('Time (Year_Season)', fontsize=14)
#     plt.ylabel('TEU (Twenty-foot Equivalent Unit)', fontsize=14)
#     plt.grid(axis='y', alpha=0.3)  # 仅Y轴网格（辅助读值，不干扰线条）
#     plt.xticks(rotation=45, ha='right', fontsize=12)  # 时间标签旋转（避免重叠）
#     plt.yticks(fontsize=12)
#
#     # 图例（放在右侧，不遮挡趋势线）
#     plt.legend(
#         title='Commodity Categories',
#         title_fontsize=12,
#         fontsize=11,
#         bbox_to_anchor=(1.05, 1),
#         loc='upper left'
#     )
#
#     # 自动调整布局（防止标签/图例被截断）
#     plt.tight_layout()
#
#     # 保存图片（按港口命名，便于区分）
#     # plt.savefig(f'{port}_commodity_trend.png', dpi=300, bbox_inches='tight')
#     plt.show()
#endregion
#region哪些节点
# years = range(2017, 2022)
# seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
# target_ports = ['USLSA', 'USLGB', 'USNWK']  # 确保与数据中的港口名一致
# records = {}
#
# for year in years:
#     for season in seasons:
#         # 跳过2021年夏季及以后（数据不全）
#         if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
#             continue
#         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
#         if not os.path.exists(file_path):
#             print(f'⚠️ 文件不存在: {file_path}')
#             continue
#         time = f"{year}_{season}"
#         DiG = nx.read_graphml(file_path)
#
#         # 获取该港口的所有入边（u → target_port，u是起点，target_port是终点）
#         in_edges = DiG.in_edges(target_ports[0], data=True)  # 返回 (u, v, data)，其中 v=target_port
#         print(f"{target_ports[0]}有多少入边: {len(in_edges)}")
#
#         from_ports = {}
#         for u, v, data in in_edges:
#             teu = data.get('volumeTEU', '未知')
#             from_ports[u] = teu
#
#         sorted_dict = dict(sorted(from_ports.items(), key=lambda k: k[1], reverse=True))
#         records[time] = sorted_dict
# pathlib.Path('Figure/Season/USTop3/Category/ports_to_USTop3.json').write_text(json.dumps(records, indent=2))
# for k,v in records.items():
#     print('------------')
#     print(k)
#     print(list(v)[:5])
#region标准世界地图模板
# DiG = nx.read_graphml(f'../Data/2021/US/Season/Spring/US2021_Spring_Digraph.graphml')
# # 2. 读港口坐标
# Port_Data = ConstructNetwork.Read_Port_Data()
# port_coords = {
#     node: (float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]))
#     for node in DiG.nodes()
#     if "longitude" in Port_Data[node]
#        and "latitude" in Port_Data[node]
#        and DiG.nodes[node].get('total_TEU') >  1000
# }
# # 画布
# fig, ax = plt.subplots(figsize=(12, 8))
# world_map = Basemap(
#     resolution='l',
#     projection='cyl',
#     lon_0=0,
#     ax=ax
# )
# # 2. 绘制地图要素
# world_map.drawmapboundary(fill_color='#D0CFD4')  # 海洋颜色
# world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')  # 陆地和湖泊颜色
# world_map.drawcoastlines(linewidth=0.5, color='#888888')  # 海岸线
# world_map.drawcountries(linewidth=0.5, color='#666666')  # 国家边界（增强地图可读性）
#
#
# # 3. 提取港口经纬度并绘制
# lons = [coord[0] for coord in port_coords.values()]  # 所有港口的经度
# lats = [coord[1] for coord in port_coords.values()]  # 所有港口的纬度
#
# # 绘制港口：用蓝色圆点，大小适中，带黑色边缘（突出显示）
# x, y = world_map(lons, lats)  # 将经纬度转换为地图坐标
# world_map.plot(
#     x, y,
#     'bo',  # 'b'=蓝色, 'o'=圆形标记
#     markersize=4,  # 点大小
#     markeredgecolor='k',  # 边缘黑色
#     markeredgewidth=0.5,
#     alpha=0.7  # 轻微透明，避免重叠时完全遮挡
# )
#
# # 4. 美化图表
# ax.set_title('Global Distribution of Ports', fontsize=14, pad=20)
#
# # 保存高清图片（可选）
# # plt.savefig('global_ports_distribution.png', dpi=300, bbox_inches='tight')
#
# # 显示地图
# plt.show()
#endregion
#region度分布 拟合有截止的度值
# # 读取数据并构建网络
# DiG = nx.read_graphml(f'../Data/2017/US/Season/Spring/US2017_Spring_Digraph.graphml')
# G = nx.Graph(DiG)
#
# # ----------------------
# # 1. 计算完整度分布数据（用于绘图，包含所有度数）
# # ----------------------
# degrees = dict(G.degree())  # {节点: 度}
#
# # 统计所有度数的节点数量（不筛选，用于绘图）
# degree_counts_full = defaultdict(int)
# for d in degrees.values():
#     degree_counts_full[d] += 1
#
# # 完整的度数和频率（绘图用）
# degrees_full = sorted(degree_counts_full.keys())
# counts_full = [degree_counts_full[d] for d in degrees_full]
# total_nodes = G.number_of_nodes()
# frequencies_full = [count / total_nodes for count in counts_full]
#
# # ----------------------
# # 2. 筛选拟合数据（仅度数≤100的点）
# # ----------------------
# # 统计度数≤100的节点数量（用于拟合）
# degree_counts_fit = defaultdict(int)
# for d in degrees.values():
#     if d <= 100:
#         degree_counts_fit[d] += 1
#
# # 拟合用的度数和频率（仅≤100）
# degrees_fit = sorted(degree_counts_fit.keys())
# counts_fit = [degree_counts_fit[d] for d in degrees_fit]
# frequencies_fit = [count / total_nodes for count in counts_fit]
#
# # ----------------------
# # 3. 双对数散点图（显示所有点）+ 拟合直线（仅用≤100的点）
# # ----------------------
# plt.figure(figsize=(10, 6))
#
# # 绘制所有度数的散点（包括>100的点）
# plt.loglog(
#     degrees_full,
#     frequencies_full,
#     marker='o',
#     linestyle='',
#     color='#d62728',
#     markersize=6,
#     alpha=0.8,
#     label='All Degree Distribution'
# )
#
# # ----------------------
# # 核心：仅对度数≤100的点进行拟合
# # ----------------------
# if degrees_fit:  # 确保有可拟合的数据
#     # 对筛选后的度数和频率取对数
#     log_degrees_fit = np.log10(degrees_fit)
#     log_freq_fit = np.log10(frequencies_fit)
#
#     # 线性回归（仅用度数≤100的点）
#     slope, intercept, r_value, p_value, std_err = stats.linregress(log_degrees_fit, log_freq_fit)
#
#     # 生成拟合直线的预测值（基于拟合用的度数）
#     fit_line = 10 **(intercept + slope * log_degrees_fit)
#
#     # 绘制拟合直线（仅覆盖度数≤100的范围）
#     plt.loglog(
#         degrees_fit,
#         fit_line,
#         linestyle='--',
#         color='black',
#         linewidth=2,
#         label=f'Fit (k ≤ 100): log(f) = {slope:.2f}*log(k) + {intercept:.2f}\nR² = {r_value**2:.4f}'
#     )
#
# # ----------------------
# # 美化与标注
# # ----------------------
# plt.xlabel('log(Degree)', fontsize=12, fontweight='bold')
# plt.ylabel('log(Frequency)', fontsize=12, fontweight='bold')
# plt.title('Log-Log Degree Distribution (Fit for k ≤ 100)', fontsize=14, fontweight='bold', pad=15)
# plt.xticks(fontsize=10)
# plt.yticks(fontsize=10)
# plt.grid(True, which="both", linestyle='--', alpha=0.5)
# plt.legend(fontsize=10, loc='upper right')
#
# # 可选：添加一条垂直虚线标记k=100的位置
# plt.axvline(x=100, color='gray', linestyle=':', linewidth=1.5, label='k=100')
#
# plt.tight_layout()
# plt.show()
#
# # 输出拟合结果
# if degrees_fit:
#     print(f"幂律拟合结果（仅针对度数≤100的节点）：")
#     print(f"斜率（-γ）：{slope:.4f} → 幂指数 γ = { -slope:.4f}")
#     print(f"截距：{intercept:.4f}")
#     print(f"决定系数 R²：{r_value**2:.4f}")
# else:
#     print("没有度数≤100的节点，无法进行拟合。")
#endregion
#region根据社团检测的结果画图
# # 1. 读取图数据并进行社团检测
# DiG = nx.read_graphml('../Data/2017/US/Season/Spring/US2017_Spring_Digraph.graphml')
# # 计算有向模块度并划分社团（weight指定边权重属性）
#
#
#
# # 2. 读取港口坐标（保持原过滤条件）
# Port_Data = ConstructNetwork.Read_Port_Data()
# port_coords = {
#     node: (float(Port_Data[node]["longitude"]), float(Port_Data[node]["latitude"]))
#     for node in G.nodes()
#     if "longitude" in Port_Data[node]
#        and "latitude" in Port_Data[node]
#        and G.nodes[node].get('total_TEU', 0) > 1000
# }
#
# # 3. 高饱和度配色方案（鲜艳醒目，对比度强）
# color_palette = [
#     '#E74C3C',  # 鲜红色
#     '#3498DB',  # 深蓝色
#     '#2ECC71',  # 翠绿色
#     '#F39C12',  # 橙色
#     '#9B59B6',  # 深紫色
#     '#1ABC9C',  # 青绿色
#     '#E67E22',  # 深橙色
#     '#8E44AD',  # 暗紫色
#     '#34495E',  # 深蓝色
#     '#D35400'   # 赭红色
# ]
#
# # 如果社团数量超过配色数量，循环使用配色（避免颜色重复过多）
# community_colors = [color_palette[i % len(color_palette)] for i in range(num_communities)]
#
# # 4. 港口-社团映射
# port_community = {}
# for comm_idx, comm in enumerate(comms_list):
#     for port in comm:
#         if port in port_coords:
#             port_community[port] = comm_idx
#
# # 5. 绘制地图（沿用你的模板）
# fig, ax = plt.subplots(figsize=(12, 8))
# world_map = Basemap(
#     resolution='l',
#     projection='cyl',
#     lon_0=0,
#     ax=ax
# )
#
# # 地图要素（保持原风格）
# world_map.drawmapboundary(fill_color='#D0CFD4')
# world_map.fillcontinents(color='#EFEFEF', lake_color='#D0CFD4')
# world_map.drawcoastlines(linewidth=0.5, color='#888888')
# world_map.drawcountries(linewidth=0.5, color='#666666')
#
# # 6. 按社团绘制港口
# for comm_idx in range(num_communities):
#     comm_ports = [port for port, idx in port_community.items() if idx == comm_idx]
#     if not comm_ports:
#         continue
#
#     lons = [port_coords[port][0] for port in comm_ports]
#     lats = [port_coords[port][1] for port in comm_ports]
#     x, y = world_map(lons, lats)
#
#     # 绘制当前社团港口（使用指定配色）
#     world_map.plot(
#         x, y,
#         'o',
#         color=community_colors[comm_idx],
#         markersize=5,
#         markeredgecolor='white',  # 白色边缘更突出
#         markeredgewidth=0.6,
#         alpha=0.9
#     )
#
# # 7. 添加图例
# legend_elements = [
#     plt.Line2D(
#         [0], [0], marker='o', color='w',
#         markerfacecolor=community_colors[i],
#         markersize=8, label=f'Community {i + 1}'
#     )
#     for i in range(num_communities)
# ]
# ax.legend(handles=legend_elements, title='Communities', loc='upper right',
#           frameon=True, framealpha=0.9, edgecolor='#AAAAAA')
#
# # 8. 标题
# ax.set_title('Port Communities Distribution (2017 Spring, US)', fontsize=14, pad=20)
#
# # 保存或显示
# # plt.savefig('port_communities.png', dpi=300, bbox_inches='tight')
# plt.show()
#endregion
#region度分布大度节点加标签
# # 设置度数阈值（可根据需要调整，例如阈值=10）
# DEGREE_THRESHOLD = 100  # 只标记度数>10的节点
# years = range(2017, 2022)
# seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
# # 读取数据并构建网络
# for year in years:
#     for season in seasons:
#         # 跳过2021年夏季及以后（数据不全）
#         if year == 2021 and season in ['Summer', 'Autumn', 'Winter']:
#             continue
#         file_path = f'../Data/{year}/US/Season/{season}/US{year}_{season}_Digraph.graphml'
#         if not os.path.exists(file_path):
#             print(f'⚠️ 文件不存在: {file_path}')
#             continue
#         time = f"{year} {season}"
#         G = nx.Graph(nx.read_graphml(file_path))
#
#         # ----------------------
#         # 1. 计算度分布数据
#         # ----------------------
#         degrees = dict(G.degree())  # {节点: 度}
#         degree_counts = defaultdict(int)
#         for d in degrees.values():
#             degree_counts[d] += 1
#
#         degrees_sorted = sorted(degree_counts.keys())  # 排序的度数
#         counts = [degree_counts[d] for d in degrees_sorted]  # 对应节点数
#
#         # 计算频率（节点数/总节点数）
#         total_nodes = G.number_of_nodes()
#         frequencies = [count / total_nodes for count in counts]
#
#         # 关键：筛选度数>阈值的港口节点，并提取它们的名称
#         high_degree_nodes = [
#             node_id for node_id, d in degrees.items()
#             if d > DEGREE_THRESHOLD
#         ]
#         # 存储 {度数: [港口名称列表]}（同一度数可能对应多个港口）
#         degree_to_names = defaultdict(list)
#         for node_id in high_degree_nodes:
#             d = degrees[node_id]
#             degree_to_names[d].append(node_id)
#
#         # ----------------------
#         # 2. 双对数散点图 + 直线拟合
#         # ----------------------
#         plt.figure(figsize=(10, 6))
#
#         # 绘制双对数散点图
#         plt.loglog(
#             degrees_sorted,
#             frequencies,
#             marker='o',
#             linestyle='',
#             color='#d62728',
#             markersize=6,
#             alpha=0.8,
#             label='Ports'
#         )
#
#         # ----------------------
#         # 为高 degree 点添加港口名称标签
#         # ----------------------
#         for d, freq in zip(degrees_sorted, frequencies):
#             if d > DEGREE_THRESHOLD and d in degree_to_names:
#                 # 获取该度数对应的所有港口名称
#                 port_names = degree_to_names[d]
#                 # 合并名称（若多个港口同度数，用换行分隔）
#                 label_text = '\n'.join(port_names)
#
#                 # 添加标签
#                 plt.annotate(
#                     label_text,  # 显示港口名称（多个则换行）
#                     xy=(d, freq),  # 点坐标
#                     xytext=(10, 5),  # 标签偏移量（右、上）
#                     textcoords='offset points',
#                     fontsize=7,  # 字体稍小，避免拥挤
#                     color='black',
#                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
#                 )
#
#         # ----------------------
#         # 核心：线性回归拟合幂律直线
#         # ----------------------
#         # 对度数和频率取对数（避免log(0)，过滤掉频率为0的点）
#         log_degrees = np.log10(degrees_sorted)  # 底数为10的对数（也可用np.log自然对数）
#         log_frequencies = np.log10(frequencies)
#
#         # 线性回归（y = a*x + b，其中y=log(frequency), x=log(degree)）
#         slope, intercept, r_value, p_value, std_err = stats.linregress(log_degrees, log_frequencies)
#
#         # 生成拟合直线的预测值（用于绘图）
#         fit_line = 10 **(intercept + slope * log_degrees)  # 转换回原尺度（10^y）
#
#         # 绘制拟合直线
#         plt.loglog(
#             degrees_sorted,
#             fit_line,
#             linestyle='--',
#             color='black',
#             linewidth=2,
#             label=f'Fit: log(f) = {slope:.2f}*log(k) + {intercept:.2f}\nR² = {r_value**2:.4f}'
#         )
#
#         # ----------------------
#         # 美化与标注
#         # ----------------------
#         plt.xlabel('Degree', fontsize=12, fontweight='bold')
#         plt.ylabel('Frequency', fontsize=12, fontweight='bold')
#         plt.title(f'{time} degree distribution', fontsize=14, fontweight='bold', pad=15)
#         plt.xticks(fontsize=10)
#         plt.yticks(fontsize=10)
#         plt.legend(fontsize=10, loc='upper right')  # 显示拟合公式和R²
#
#         plt.tight_layout()
#         # plt.savefig(f'Figure/Season/DegreeDistribution/{time} degree distribution.png', dpi=300)
#         plt.show()
#
#         # 输出拟合结果
#         print(f"幂律拟合结果：")
#         print(f"斜率（-γ）：{slope:.4f} → 幂指数 γ = { -slope:.4f}")
#         print(f"截距：{intercept:.4f}")
#         print(f"决定系数 R²：{r_value**2:.4f}（越接近1，拟合越好）")
#endregion



times = ["2017 06", "2018 06", "2019 06", "2020 06", "2021 06"]
data = {}

for time in times:
    _, G = Main.get_certain_networks_by_months(time)
    degree_frequency = Undirected.get_degree_distribution(G)
    data[time] = []

    # 构建最终数据：港口 → [度值, 频率]（每个港口唯一对应一组数据）
    for port in G.nodes():  # 遍历所有港口，确保不遗漏
        degree = G.degree(port)  # 获取该港口的度值
        frequency = degree_frequency[degree]  # 通过度值获取对应频率
        data[time].append((degree, frequency))

df = pd.DataFrame(data)
Draw.draw_scatter_list(
    df,
    "Months/Undirected/DegreeDistribution/",
    "Degree",
    "Frequency",
    f"DegreeDistribution",
    "loglog"
)


def draw_dual_axis_plot(cls,
                        df: DataFrame,
                        save_path: str,
                        title: str,
                        loc: str,
                        linewidth: int = 2,
                        markersize: int = 5,
                        margin_rate: int = 0.7,
                        label_step: int = 4,
                        rotation: int = 15
                        ):
    """
    两个不同尺度的数据画在一起
    :param df:
    :param save_path:
    :param title:
    :param loc: 图例的位置
    :param markersize:
    :param linewidth:
    :param margin_rate:  y轴扩大的范围 这样可以使数据线更集中
    :param label_step: x轴标签间隔
    :param rotation: x轴标签旋转角度
    :return:
    """
    # 数据先保存
    df.to_csv(f'{cls.basic_path}/{save_path}{title}.csv',
              index=False)

    # --- 全局字体设置 ---
    plt.rcParams['font.sans-serif'] = ['Times New Roman']  # 设置默认字体
    plt.rcParams['font.size'] = 16  # 设置默认字体大小
    plt.rcParams['axes.labelsize'] = 30  # 设置轴标签字体大小
    plt.rcParams['xtick.labelsize'] = 16  # 设置X轴刻度标签字体大小
    plt.rcParams['ytick.labelsize'] = 16  # 设置Y轴刻度标签字体大小

    time_col = df.columns[0]
    left_col = df.columns[1]
    right_col = df.columns[2]
    time = df[time_col]

    colors = ['#2878b4', '#373535']
    markers = ['o', 's']

    # 创建画布和坐标轴
    fig, ax1 = plt.subplots(figsize=(12, 6))  # 宽12英寸，高6英寸
    # 创建右侧Y轴（与左侧Y轴共享X轴，实现双轴对齐）
    ax2 = ax1.twinx()  # 关键：生成与ax1共享X轴的第二个Y轴
    # -------------------------- 4. 绘制双折线（分别绑定左右Y轴） --------------------------
    # -------------------------- 左侧Y轴：Nodes（假设N列是Nodes数量） --------------------------
    ax1.plot(
        time,  # X轴：时间
        df[left_col],  # Y轴：绑定左侧ax1
        label=left_col,  # 图例名称
        color=colors[0],  # 颜色（可选：用十六进制色更精准，这里是深蓝色）
        marker=markers[0],  # 数据点标记（圆形）
        linestyle='-',
        linewidth=linewidth,  # 线条宽度（加粗更清晰）
        markersize=markersize  # 数据点大小
    )

    # -------------------------- 右侧Y轴：Edges（假设M列是Edges数量） --------------------------
    ax2.plot(
        time,  # X轴：时间（与左侧共享，无需重复设置）
        df[right_col],  # Y轴：Edges数量（绑定右侧ax2）
        label=right_col,  # 图例名称
        color=colors[1],  # 颜色（深红色，与左侧区分明显）
        marker=markers[1],  # 数据点标记（方形，与圆形区分）
        linestyle='--',  # 线条样式（虚线，与实线区分）
        linewidth=linewidth,  # 线条宽度（与左侧一致，保持美观）
        markersize=markersize  # 数据点大小（与左侧一致）
    )

    # -----------------y轴的范围-------------------------
    # 1. 左侧Y轴（ax1）：适配 left_col 数据，留5%边距
    left_data = df[left_col].dropna()  # 剔除缺失值（避免影响极值计算）
    left_min = left_data.min()
    left_max = left_data.max()
    left_margin = (left_max - left_min) * margin_rate  # 5%边距（可调整为0.1=10%）

    # 特殊处理：若最小值接近0，强制Y轴从0开始（避免负范围）
    if left_min - left_margin < 0:
        ax1.set_ylim(bottom=0, top=left_max + left_margin)
    else:
        ax1.set_ylim(bottom=left_min - left_margin, top=left_max + left_margin)

    # 2. 右侧Y轴（ax2）：适配 right_col 数据，留5%边距
    right_data = df[right_col].dropna()  # 剔除缺失值
    right_min = right_data.min()
    right_max = right_data.max()
    right_margin = (right_max - right_min) * margin_rate  # 边距比例与左侧一致，保持美观

    # 特殊处理：若最小值接近0，强制Y轴从0开始
    if right_min - right_margin < 0:
        ax2.set_ylim(bottom=0, top=right_max + right_margin)
    else:
        ax2.set_ylim(bottom=right_min - right_margin, top=right_max + right_margin)

    # -------------------------- 5. 美化双轴标签与标题 --------------------------
    # -------------------------- 左侧Y轴（ax1）设置 --------------------------
    ax1.set_xlabel(time_col, fontsize=30, fontfamily='Times New Roman')  # X轴标签（加粗）
    ax1.tick_params(axis='x',
                    rotation=rotation,
                    labelsize=16,
                    labelfontfamily='Times New Roman')  # X轴时间标签旋转45度，避免文字重叠

    # regionx轴标签间隔
    # --- 核心修改：手动设置X轴刻度和标签 ---
    # 1. 获取所有原始的X轴标签文本
    all_labels = [item.get_text() for item in ax1.get_xticklabels()]

    # 2. 定义一个步长，比如每隔2个显示一个
    step = label_step

    # 3. 创建新的刻度位置和对应的标签列表
    new_tick_positions = list(range(0, len(all_labels), step))
    new_tick_labels = [all_labels[i] for i in new_tick_positions]

    # 4. 应用新的刻度和标签
    ax1.set_xticks(new_tick_positions)
    ax1.set_xticklabels(new_tick_labels)
    # endregion

    ax1.set_ylabel(left_col,  # 左侧Y轴标签（明确对应Nodes）
                   color='black',  # 标签颜色与线条颜色一致
                   fontsize=30,
                   fontfamily='Times New Roman')
    ax1.tick_params(axis='y',  # 左侧Y轴刻度设置
                    colors='black',  # 刻度颜色与线条一致
                    labelsize=16,
                    labelfontfamily='Times New Roman')  # 刻度文字大小

    # -------------------------- 右侧Y轴（ax2）设置 --------------------------
    ax2.set_ylabel(right_col,  # 右侧Y轴标签（明确对应Edges）
                   color='black',  # 标签颜色与线条颜色一致
                   fontsize=30,
                   fontfamily='Times New Roman')
    ax2.tick_params(axis='y',  # 右侧Y轴刻度设置
                    colors='black',  # 刻度颜色与线条一致
                    labelsize=16,
                    labelfontfamily='Times New Roman')  # 刻度文字大小

    # region图片标题
    # -------------------------- 图片标题 --------------------------
    # ax1.set_title(
    #     title,
    #     fontsize=16,
    #     fontweight='bold',
    #     pad=20  # 标题与图表的间距（避免拥挤）
    # )
    # endregion

    # --- 核心修改：设置图例的字体 ---
    font = {'family': 'Times New Roman',
            'size': 16}  # 'weight' 可选，用于设置粗体
    # -------------------------- 6. 合并双轴图例（关键：避免图例重复） --------------------------
    # 提取左右轴的图例，合并为一个（放在图表右侧，不遮挡数据）
    lines1, labels1 = ax1.get_legend_handles_labels()  # 左侧轴图例
    lines2, labels2 = ax2.get_legend_handles_labels()  # 右侧轴图例
    ax1.legend(
        lines1 + lines2,  # 合并图例线条
        labels1 + labels2,  # 合并图例文字
        prop=font,
        loc=loc,
        frameon=True,  # 显示图例边框
        fancybox=True,  # 边框圆角
        shadow=True  # 边框阴影（更立体）
    )

    # -------------------------- 7. 调整布局与保存 --------------------------
    # 自动调整布局（避免标签、图例被截断）
    plt.tight_layout()

    for for_mat in ["png", "eps"]:  # png and eps
        plt.savefig(f'{cls.basic_path}/{save_path}{title}.{for_mat}',
                    format=for_mat,  # 显式指定格式（可选，但更稳妥）
                    dpi=300,
                    bbox_inches='tight'  # 去除图片周围多余空白
                    )