from typing import Callable
from matplotlib import pyplot as plt
from pandas import DataFrame


class Draw:
    basic_path = 'Output'       # 保存的时候都在 Output中

    # 通用配色/标记库（各模式可复用）
    _normal_colors = [
        '#2E86AB', '#A23B72', '#F18F01',
        '#C73E1D', '#7209B7', '#024059'
    ]
    _normal_markers = ['o', 's', '^', 'D', 'p']

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
    _mode_configs:dict[str, dict] = {
        # 配置
        'normal': {
            'colors': _normal_colors,
            'markers': _normal_markers,
            'show_legend': True
        },
        'ports': {
            'colors': _ports_colors,
            'markers': _ports_markers,
            'show_legend': False
        }
    }

    @classmethod
    def draw_plot(cls,
                  df:DataFrame,
                  save_path:str,
                  y_label:str,
                  title:str
                  ):
        """
        适用于大家的横坐标一样  比如说时间
        :param df:
        示例
        data = {
                "Time": ["2017", "2018", "2019", "2020"],
                "US": [28.5, 35.2, 22.8, 41.1],
                "CN": [14, 28, 20, 40.1]
        }
        :param save_path: 保存路径 只需要写文件夹即可
        :param y_label: y轴的label
        :param title:   图片的名字
        """

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
        colors = ['#2E86AB',  # 深海蓝（主色1，沉稳）
                  '#A23B72',  # 深玫红（主色2，醒目不刺眼）
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
    def draw_scatter(cls,
                     df:DataFrame,
                     save_path:str,
                     x_label:str,
                     y_label:str,
                     title:str,
                     scale:str = 'linear',
                     mode:str = 'normal'
                     ):
        """
        画散点的函数
        TODO 加一个在散点图上显示标签的功能  比如说大于多少就显示标签

        :param df:
        Example：
        data = {
            "US": [(28.5, 3), (35.2,3), (22.8, 34), (41.1,4)],
            "CN": [(5, 5), (1,3), (22, 3), (40.1,5)]
        }
        :param save_path:
        :param x_label:
        :param y_label:
        :param title:
        :param scale:  横纵坐标的缩放模式
        :param mode: 画图的模式  具体有哪些配置看上边的 _mode_configs
        """

        # 模式的合法性
        if scale not in cls._scale_handlers.keys():
            raise ValueError("没有这种scale模式")
        if mode not in cls._mode_configs.keys():
            raise ValueError("没有这种mode模式")

        # 获取配置信息
        mode_config = cls._mode_configs[mode]
        colors = mode_config['colors']
        markers = mode_config['markers']
        show_legend = mode_config['show_legend']

        plt.figure(figsize=(10, 6))
        # # 顶刊配色和标记
        # markers = [
        #     'o',
        #     's',
        #     '^',
        #     'D',
        #     'p'
        # ]
        # # colors = ['#2E86AB',  # 深海蓝（主色1，沉稳）
        # #           '#A23B72',  # 深玫红（主色2，醒目不刺眼）
        # #           '#F18F01',  # 暖橙（辅助色1，中和冷色）
        # #           '#C73E1D',  # 暗红（辅助色2，小范围强调）
        # #           '#7209B7',  # 深紫（补充色1，低饱和不突兀）
        # #           '#024059'  # 墨蓝（补充色2，适合背景或次要曲线）
        # #           ]
        # # colors = ['blue', 'grey']
        # colors = ['blue']
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
                linewidth=0.8  # 略微加粗边框，与高透明度匹配
            )


        cls._scale_handlers[scale]()   # 执行对应的缩放模式
        # 添加标签和标题
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=14)
        if show_legend:
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
                  title:str):
        """
        两个不同尺度的数据画在一起
        :param df:
        :param save_path:
        :param title:
        :return:
        """

        time_col = df.columns[0]
        left_col = df.columns[1]
        right_col = df.columns[2]
        time = df[time_col]

        colors = ['blue', 'grey']
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
            linestyle='-',  # 线条样式（实线）
            linewidth=2.5,  # 线条宽度（加粗更清晰）
            markersize=7  # 数据点大小
        )

        # -------------------------- 右侧Y轴：Edges（假设M列是Edges数量） --------------------------
        ax2.plot(
            time,  # X轴：时间（与左侧共享，无需重复设置）
            df[right_col],  # Y轴：Edges数量（绑定右侧ax2）
            label=right_col,  # 图例名称
            color=colors[1],  # 颜色（深红色，与左侧区分明显）
            marker=markers[1],  # 数据点标记（方形，与圆形区分）
            linestyle='--',  # 线条样式（虚线，与实线区分）
            linewidth=2.5,  # 线条宽度（与左侧一致，保持美观）
            markersize=7  # 数据点大小（与左侧一致）
        )

        # -------------------------- 5. 美化双轴标签与标题 --------------------------
        # -------------------------- 左侧Y轴（ax1）设置 --------------------------
        ax1.set_xlabel(time_col, fontsize=12, fontweight='bold')  # X轴标签（加粗）
        ax1.tick_params(axis='x', rotation=45)  # X轴时间标签旋转45度，避免文字重叠


        ax1.set_ylabel(left_col,  # 左侧Y轴标签（明确对应Nodes）
                       color=colors[0],  # 标签颜色与线条颜色一致
                       fontsize=12,
                       fontweight='bold')
        ax1.tick_params(axis='y',  # 左侧Y轴刻度设置
                        colors=colors[0],  # 刻度颜色与线条一致
                        labelsize=10)  # 刻度文字大小

        # -------------------------- 右侧Y轴（ax2）设置 --------------------------
        ax2.set_ylabel(right_col,  # 右侧Y轴标签（明确对应Edges）
                       color=colors[1],  # 标签颜色与线条颜色一致
                       fontsize=12,
                       fontweight='bold')
        ax2.tick_params(axis='y',  # 右侧Y轴刻度设置
                        colors=colors[1],  # 刻度颜色与线条一致
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
            loc='upper left',  # 图例位置（右上，不遮挡数据）
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
