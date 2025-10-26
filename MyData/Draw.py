from typing import Callable

from matplotlib import pyplot as plt
from pandas import DataFrame


class Draw:
    basic_path = 'Output'       # 保存的时候都在 Output中

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
        """
        模式名 -> 处理函数 的映射
        """
        'linear': _scale_linear,
        'logx': _scale_logx,
        'logy': _scale_logy,
        'loglog': _scale_loglog
    }

    @classmethod
    def draw_plot(cls, df:DataFrame, save_path:str, y_label:str, title:str):
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
        plt.legend()  # 显示图例
        # 调整布局并显示
        plt.tight_layout()
        # plt.show()
        plt.savefig(f'{cls.basic_path}/{save_path}{title}.eps',
                    format = 'eps',  # 显式指定格式（可选，但更稳妥）
                    dpi = 300,  # 分辨率（矢量图不依赖dpi，但部分期刊要求300）
                    bbox_inches = 'tight'  # 去除图片周围多余空白
        )
    @classmethod
    def draw_scatter(cls,
                     df:DataFrame,
                     save_path:str,
                     x_label:str,
                     y_label:str,
                     title:str,
                     scale:str = 'linear'):
        """
        画散点的函数
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
        """
        plt.figure(figsize=(10, 6))
        # 顶刊配色和标记
        markers = [
            'o',
            's',
            '^',
            'D',
            'p'
        ]
        # colors = ['#2E86AB',  # 深海蓝（主色1，沉稳）
        #           '#A23B72',  # 深玫红（主色2，醒目不刺眼）
        #           '#F18F01',  # 暖橙（辅助色1，中和冷色）
        #           '#C73E1D',  # 暗红（辅助色2，小范围强调）
        #           '#7209B7',  # 深紫（补充色1，低饱和不突兀）
        #           '#024059'  # 墨蓝（补充色2，适合背景或次要曲线）
        #           ]
        colors = ['blue', 'grey']
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
                alpha=0.8  # 透明度
            )

        if scale not in cls._scale_handlers:
            raise ValueError("没有这种scale模式")
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