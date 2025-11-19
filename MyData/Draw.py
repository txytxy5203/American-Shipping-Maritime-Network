import numpy as np
import pandas as pd
from typing import Callable
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.basemap import Basemap
from pandas import DataFrame

from Read import Read

class Draw:
    basic_path = 'Output'       # 保存的时候都在 Output中

    colors_config = {
        1:[ # 天询师兄的配色 respect
            '#4c91c3',
            '#ff993d',
            '#55b355',
            '#dd5153'
        ]
    }
    markers_config = {
        1:[
            'o',
            's',
            '^',
            'D',
            'p'
        ]
    }



    # 专门针对港口的  一种配色 一种标记
    _ports_colors = ['blue']
    _ports_markers = ['o']

    @staticmethod
    def _scale_linear():
        """线性坐标轴 不做处理"""
        pass

    @staticmethod
    def _scale_logx():
        """x轴缩放"""
        plt.xscale('log')

    @staticmethod
    def _scale_logy():
        """y轴缩放"""
        plt.yscale('log')

    @staticmethod
    def _scale_loglog():
        """x y 轴缩放"""
        plt.xscale('log')
        plt.yscale('log')


    _scale_handlers: dict[str, Callable] = {
        # 模式名 -> 处理函数 的映射
        'linear': _scale_linear,
        'logx': _scale_logx,
        'logy': _scale_logy,
        'loglog': _scale_loglog
    }


    #regionWorldMap
    # 假设缩写规则：NA=北美洲, SA=南美洲, EU=欧洲, AS=亚洲, AF=非洲, OC=大洋洲, UN=未知
    continent_color_mapping = {
        'NA': '#1f77b4',  # 深蓝色（北美洲）
        'SA': '#ff7f0e',  # 橙色（南美洲）
        'EU': '#2ca02c',  # 绿色（欧洲）
        'AS': '#d62728',  # 红色（亚洲）
        'AF': '#9467bd',  # 紫色（非洲）
        'OC': '#8c564b',  # 棕色（大洋洲）
        'UN': '#7f7f7f'  # 灰色（未知大洲）
    }
    #endregion

    @classmethod
    def draw_plot(cls,
                  df:DataFrame,
                  save_path:str,
                  y_label:str,
                  title:str,
                  margin_rate:float=0.2,
                  ):
        """
        适用于大家的横坐标一样  比如说时间
        :param df:
        示例
        data = {
                "time": ["2017", "2018", "2019", "2020"],
                "US": [28.5, 35.2, 22.8, 41.1],
                "CN": [14, 28, 20, 40.1]
        }
        :param save_path: 保存路径 只需要写文件夹即可
        :param y_label: y轴的label
        :param title:   图片的名字
        :param margin_rate:
        """
        # 数据先保存
        df.to_csv(f'{cls.basic_path}/{save_path}{title}.csv',
                  index=False)

        x_col = df.columns[0]  # 第一列列名
        y_cols = df.columns[1:]  # 后面的列名
        x = df[x_col]  # 第一列的数据

        plt.figure(figsize=(10, 6))

        markers = [
            'o',
            's',
            '^',
            'D',
            'p'
        ]
        colors = ['#2878b4',
                  '#373535',
                  '#F18F01',  # 暖橙（辅助色1，中和冷色）
                  '#C73E1D',  # 暗红（辅助色2，小范围强调）
                  '#7209B7',  # 深紫（补充色1，低饱和不突兀）
                  '#024059'  # 墨蓝（补充色2，适合背景或次要曲线）
        ]
        # 绘制折线图
        for i, col in enumerate(y_cols):  # 遍历后面所有的列的数据
            plt.plot(
                x,
                df[col],
                label=col,
                marker=markers[i],
                color=colors[i]
            )


        # ---------------------- 核心修改：自适应范围 + 留边距 ----------------------
        # 计算所有 Y 数据的最小值和最大值
        all_y_data = df[y_cols].values.flatten()  # 合并所有 Y 列数据
        y_min = all_y_data.min()
        y_max = all_y_data.max()
        # 预留的边距（可调整比例）
        margin = (y_max - y_min) * margin_rate
        plt.ylim(bottom=y_min - margin, top=y_max + margin)


        # 添加标签和标题
        plt.xlabel(x_col, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=14)
        plt.xticks(rotation=45)  # 时间标签旋转45度，避免重叠
        plt.legend()  # 显示图例
        # 调整布局并显示
        plt.tight_layout()

        for for_mat in ["png", "eps"]:  # png and eps
            plt.savefig(f'{cls.basic_path}/{save_path}{title}.{for_mat}',
                        format=for_mat,  # 显式指定格式（可选，但更稳妥）
                        dpi=300,
                        bbox_inches='tight'  # 去除图片周围多余空白
            )
    @classmethod
    def draw_scatter_list(cls,
                          df:DataFrame,
                          save_path:str,
                          x_label:str,
                          y_label:str,
                          title:str,
                          scale:str = 'linear',
                          label:bool = False,
                          colors:int = 1,
                          markers:int = 1,
                          ):
        """
        画散点的函数
        TODO 加一个在散点图上显示标签的功能  比如说大于多少就 显示标签
        :param df:
        Example：
        data1 = {
            "US": [(28.5, 3), (35.2,3), (22.8, 34), (41.1,4)],
            "CN": [(5, 5), (1,3), (22, 3), (40.1,5)]
        }
        :param save_path:
        :param x_label:
        :param y_label:
        :param title:
        :param scale:  横纵坐标的缩放模式
        :param label:
        :param colors: 颜色配置
        :param markers: 标记配置
        """
        df.to_csv(f'{cls.basic_path}/{save_path}{title}.csv', index=False)
        # 模式的合法性
        if scale not in cls._scale_handlers.keys():
            raise ValueError("没有这种scale模式")

        # 获取配置信息
        colors = cls.colors_config[colors]
        markers = cls.markers_config[markers]

        plt.figure(figsize=(10, 6))

        for i, col in enumerate(df.columns):
            coordinates = df[col]
            x = [coord[0] for coord in coordinates]
            y = [coord[1] for coord in coordinates]

            plt.scatter(
                x,
                y,
                label=col,  # 图例用国家名（US/CN）
                color=colors[i % len(colors)],
                marker=markers[i % len(markers)],
                s=60,  # 散点大小
                alpha=0.8,  # 透明度
                linewidth=0.8,  # 略微加粗边框，与高透明度匹配
                edgecolors = 'k',
            )

        cls._scale_handlers[scale]()   # 执行对应的缩放模式
        # 添加标签和标题
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=14)
        plt.legend()
        plt.tight_layout()

        for for_mat in ["png", "eps"]:      # png and eps
            plt.savefig(f'{cls.basic_path}/{save_path}{title}.{for_mat}',
                        format=for_mat,  # 显式指定格式（可选，但更稳妥）
                        dpi=300,
                        bbox_inches='tight'  # 去除图片周围多余空白
            )
    @classmethod
    def draw_scatter_ports(cls,
                     df:DataFrame,
                     save_path:str,
                     x_label:str,
                     y_label:str,
                     title:str,
                     scale:str = 'linear',
                     label:bool = False
                     ):
        """
        画散点的函数
        key就是港口  value中的list每一列就是不同的值
        :param df:
        Example：
        data2 = {
            "USLGB": [1, 3],
            "CNSHN": [2, 3]
        }
        :param save_path:
        :param x_label:
        :param y_label:
        :param title:
        :param scale:  横纵坐标的缩放模式
        :param label:
        """

        # 模式的合法性
        if scale not in cls._scale_handlers.keys():
            raise ValueError("没有这种scale模式")


        plt.figure(figsize=(10, 6))

        for i, port in enumerate(df.columns):
            coordinates = df[port]
            x = coordinates[0][0]       # 这个地方要取两次值
            y = coordinates[0][1]

            plt.scatter(
                x,
                y,
                label=port,  # 图例用国家名（US/CN）
                marker='o',
                s=60,  # 散点大小
                alpha=0.8,  # 透明度
                linewidth=0.8,  # 略微加粗边框，与高透明度匹配
                color = 'steelblue',
                edgecolors = 'k',
            )

            # -------------------------- 关键：plt.text() 添加标签 --------------------------
            if label and (x > 7e5 or y > 0.04):
                plt.text(
                    # 注意这里是坐标系中的数值偏移
                    x + 0.5,  # 文本的 x 坐标（在散点 x 基础上右移1，避免重叠）
                    y - 0.003,  # 文本的 y 坐标（在散点 y 基础上上移1）
                    s=port,  # 标签内容（港口名）
                    fontsize=9,  # 字体大小
                    color='black',  # 字体颜色
                    weight='bold',  # 加粗（可选）
                    ha='left',  # 文本水平对齐方式（left/center/right）
                    va='bottom',  # 文本垂直对齐方式（bottom/center/top）
                    bbox=dict(  # 半透明背景框（可选，增强可读性）
                        boxstyle='round,pad=0.2',
                        facecolor='white',
                        alpha=0.7,
                        edgecolor='black'
                )
            )

        cls._scale_handlers[scale]()   # 执行对应的缩放模式
        # 添加标签和标题
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=14)

        plt.legend()
        plt.tight_layout()

        for for_mat in ["png", "eps"]:      # png and eps
            plt.savefig(f'{cls.basic_path}/{save_path}{title}.{for_mat}',
                        format=for_mat,  # 显式指定格式（可选，但更稳妥）
                        dpi=300,
                        bbox_inches='tight'  # 去除图片周围多余空白
            )

    @classmethod
    def draw_dual_axis_plot(cls,
                df:DataFrame,
                save_path:str,
                title:str,
                loc:str,
                linewidth:int=2,
                markersize:int=5,
                margin_rate:int=0.7
        ):
        """
        两个不同尺度的数据画在一起
        :param df:
        :param save_path:
        :param title:
        :param loc: 图例的位置
        :param markersize:
        :param linewidth:
        :param margin_rate:  y轴数值的范围
        :return:
        """
        # 数据先保存
        df.to_csv(f'{cls.basic_path}/{save_path}{title}.csv',
                  index=False)

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
        ax1.set_xlabel(time_col, fontsize=12, fontweight='bold')  # X轴标签（加粗）
        ax1.tick_params(axis='x', rotation=45)  # X轴时间标签旋转45度，避免文字重叠


        ax1.set_ylabel(left_col,  # 左侧Y轴标签（明确对应Nodes）
                       color='black',  # 标签颜色与线条颜色一致
                       fontsize=12,
                       fontweight='bold')
        ax1.tick_params(axis='y',  # 左侧Y轴刻度设置
                        colors='black',  # 刻度颜色与线条一致
                        labelsize=10)  # 刻度文字大小

        # -------------------------- 右侧Y轴（ax2）设置 --------------------------
        ax2.set_ylabel(right_col,  # 右侧Y轴标签（明确对应Edges）
                       color='black',  # 标签颜色与线条颜色一致
                       fontsize=12,
                       fontweight='bold')
        ax2.tick_params(axis='y',  # 右侧Y轴刻度设置
                        colors='black',  # 刻度颜色与线条一致
                        labelsize=10)  # 刻度文字大小

        # -------------------------- 标题与X轴刻度 --------------------------
        ax1.set_title(
            title,
            fontsize=14,
            fontweight='bold',
            pad=20  # 标题与图表的间距（避免拥挤）
        )

        # -------------------------- 6. 合并双轴图例（关键：避免图例重复） --------------------------
        # 提取左右轴的图例，合并为一个（放在图表右侧，不遮挡数据）
        lines1, labels1 = ax1.get_legend_handles_labels()  # 左侧轴图例
        lines2, labels2 = ax2.get_legend_handles_labels()  # 右侧轴图例
        ax1.legend(
            lines1 + lines2,  # 合并图例线条
            labels1 + labels2,  # 合并图例文字
            fontsize=11,
            loc=loc,
            frameon=True,  # 显示图例边框
            fancybox=True,  # 边框圆角
            shadow=True  # 边框阴影（更立体）
        )

        # -------------------------- 7. 调整布局与保存 --------------------------
        # 自动调整布局（避免标签、图例被截断）
        plt.tight_layout()

        for for_mat in ["png", "eps"]:      # png and eps
            plt.savefig(f'{cls.basic_path}/{save_path}{title}.{for_mat}',
                        format=for_mat,  # 显式指定格式（可选，但更稳妥）
                        dpi=300,
                        bbox_inches='tight'  # 去除图片周围多余空白
            )

    @classmethod
    def draw_step(cls,
            df: DataFrame,  # 包含k值和节点数的DataFrame
            save_path:str,  # 保存路径
            x_label: str,  # x轴标签
            y_label: str,  # y轴标签
            title: str,  # 图表标题
            step_where:str ='post'   # 阶梯对齐方式：'pre'/'post'/'mid'
    ):
        """

        :param df:
        示例：
        df = {
            "k":     [1,  2,  4],
            "nodes": [10, 6,  2]
        }
        :param save_path:
        :param x_label:
        :param y_label:
        :param title:
        :param step_where:
        :return:
        """


        # 提取x和y数据（确保k值按顺序排列）
        k_values = df['k'].sort_values().values  # x轴：k值（排序）
        node_counts = df['nodes'].values  # y轴：节点数

        # 绘制阶梯图
        plt.figure(figsize=(8, 5))
        plt.step(
            k_values,
            node_counts,
            where=step_where,  # 阶梯对齐方式
            color='blue',
            linewidth=2,
            # marker='o',  # 标记每个k值对应的点
            markersize=6,
            linestyle='-'  # 阶梯线样式
        )

        # 设置坐标轴和标题
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=14, pad=15)
        plt.grid(alpha=0.3)  # 添加网格线
        plt.xticks(k_values)  # x轴刻度与k值一致
        plt.tight_layout()  # 自动调整布局

        # 保存图片
        for for_mat in ["png", "eps"]:  # png and eps
            plt.savefig(f'{cls.basic_path}/{save_path}{title}.{for_mat}',
                        format=for_mat,  # 显式指定格式（可选，但更稳妥）
                        dpi=300,
                        bbox_inches='tight'  # 去除图片周围多余空白
            )

    @classmethod
    def draw_world_ports_map(cls,
                             df:DataFrame,
                             save_path:str,
                             title:str
                             ):
        """
        TODO 这个画WorldMap的工作之后再处理 有点乱
        画港口的函数  港口的颜色抛给外部处理
        :param df: {
            "Port": ['USLGB'],
            "Continent": ["NA"],
            "TEU": [10000],
            "Colors": ['red']
        }
        :param save_path:
        :param title:
        :return:
        """

        # 读取港口坐标数据
        Port_Data = Read.Read_Port_Data()



        port_info = {}  # key 为港口   value为各种信息组成的tuple
        for idx, port_data in df.iterrows():
            # 检查坐标是否有效
            node = port_data['Port']
            if node not in Port_Data:
                print(f"{node} 不在港口信息表中")
                continue
            if "longitude" not in Port_Data[node] or "latitude" not in Port_Data[node]:
                print(f"{node} 没有经纬度信息")
                continue

            # 存储有效信息
            lon = float(Port_Data[node]["longitude"])
            lat = float(Port_Data[node]["latitude"])
            port_info[node] = (lon, lat,
                               port_data['TEU'],
                               port_data['Continent'],
                               port_data['Colors'])

        # 地图与网络可视化设置
        # 创建画布
        fig, ax = plt.subplots(figsize=(14, 10))
        # 定义地图
        world_map = Basemap(
            resolution='i',  # 中分辨率（比'l'更清晰，加载速度适中）
            projection='cyl',
            # lon_0=center_lon,
            # lat_0=center_lat,
            llcrnrlon=-180,  # 左边界：最西港口-10度
            urcrnrlon=180,  # 右边界：最东港口+10度
            llcrnrlat=-70,  # 下边界：最南港口-30度
            urcrnrlat=70,  # 上边界：最北港口+10度
            ax=ax
        )

        # 绘制地图要素（更细腻的配色）
        world_map.drawmapboundary(fill_color='#A8DADC')  # 海洋：浅蓝色
        world_map.fillcontinents(color='#F1FAEE', lake_color='#A8DADC', alpha=0.8)  # 陆地：浅灰色
        world_map.drawcoastlines(linewidth=0.8, color='#1D3557')  # 海岸线：深蓝色
        world_map.drawcountries(linewidth=0.6, color='#457B9D')  # 国家边界：中蓝色
        world_map.drawmeridians(np.arange(-180, 180, 20), labels=[0, 0, 0, 1], linewidth=0.3, color='#999')  # 经度线
        world_map.drawparallels(np.arange(-90, 90, 20), labels=[1, 0, 0, 0], linewidth=0.3, color='#999')  # 纬度线

        for node, attr in port_info.items():
            lon, lat, teu, continent_code, color = port_info[node]
            x, y = world_map(lon, lat)

            # 节点大小与TEU成正比（归一化到5-20）
            max_teu = max(p[2] for p in port_info.values())
            node_size = 5 + 10 * (teu / max_teu)


            # 绘制节点
            world_map.plot(
                x,
                y,
                'o',
                markersize=node_size,
                color=color,
                markeredgecolor='black',
                markeredgewidth=0.8,
                alpha=0.9
            )
            # # 【新增】给节点添加标签（以港口名为例，可替换为其他内容）
            # # 1. 标签内容：从port_info的attr中获取港口名（根据你的数据结构调整，确保有该字段）
            # label_text = node
            #
            # # 2. 添加标签：x,y是节点坐标，label_text是标签内容
            # ax.text(
            #     x,  # 标签x轴偏移（向右移1.5个单位，避免覆盖节点）
            #     y - 3.5,  # 标签y轴偏移（向上移0.5个单位，避免覆盖节点）
            #     label_text,
            #     fontsize=7,  # 字体大小（根据节点密度调整，避免杂乱）
            #     color='#333333',  # 标签颜色（深灰色，比黑色柔和，可读性强）
            #     ha='left',  # 标签水平对齐方式（左对齐，配合x偏移）
            #     va='center',  # 标签垂直对齐方式（居中）
            #     alpha=0.9,  # 标签透明度（与节点一致）
            #     bbox=dict(
            #         boxstyle='round,pad=0.2',  # 边框样式：round（圆角），pad=0.2（文本与边框的内边距）
            #         facecolor='white',  # 背景色：白色
            #         edgecolor='black',  # 边框色：黑色
            #         linewidth=0.8,  # 边框宽度：0.8（与节点边框宽度一致，视觉统一）
            #         alpha=0.9  # 背景透明度：0.9（与标签、节点透明度一致）
            #     )
            # )

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

        # # 生成图例（包含大洲颜色+缩写+全称）   TODO 图例之后是一个问题  暂时先这么用着
        # legend_elements = [
        #     Line2D(
        #         [0], [0], marker='o', color='w',
        #         markerfacecolor=color, markersize=10,
        #         label=f'{code} ({continent_fullname[code]})'
        #     ) for code, color in cls.continent_color_mapping.items()
        # ]
        # 图例：红色=remove，蓝色=add（替换原大洲图例逻辑）
        legend_elements = [
            # 蓝色节点：add
            Line2D(
                [0], [0], marker='o', color='w',
                markerfacecolor='blue',  # 蓝色（可根据需求调整色号）
                markersize=10,
                label='add (Blue)'  # 标签：状态+颜色
            ),
            # 红色节点：remove
            Line2D(
                [0], [0], marker='o', color='w',
                markerfacecolor='red',  # 红色（可根据需求调整色号）
                markersize=10,
                label='remove (Red)'  # 标签：状态+颜色
            )
        ]

        ax.legend(
            handles=legend_elements,
            loc='lower left',
            fontsize=9,
            title='Continents',
            title_fontsize=11
        )

        ax.set_title(f'{title}', fontsize=16, pad=20)
        plt.tight_layout()
        # 保存图片
        for for_mat in ["png", "eps"]:  # png and eps
            plt.savefig(f'{cls.basic_path}/{save_path}{title}.{for_mat}',
                        format=for_mat,  # 显式指定格式（可选，但更稳妥）
                        dpi=300,
                        bbox_inches='tight'  # 去除图片周围多余空白
            )


