"""
脚本文件
"""

import pandas as pd
import numpy as np
import os

from matplotlib import pyplot as plt

from MyData.Main import Main
from MyData.NullModel import NullModel
from MyData.Undirected import Undirected


def process_csv_files(file1_path, file2_path, output_path=None):
    """
    处理两个CSV文件，生成按时间列和指标行组织的新CSV

    参数:
        file1_path: 第一个CSV文件路径
        file2_path: 第二个CSV文件路径
        output_path: 输出CSV文件路径，默认为当前目录下的merged_results.csv
    """
    # 定义需要提取的指标列表
    indicators = [
        'entropy',
        'spectral_radius',
        'density',
        'avg_degrees',
        'homogeneity'
    ]
    try:
        # 读取两个CSV文件
        df1 = pd.read_csv(file1_path)
        df2 = pd.read_csv(file2_path)

        # 获取并统一时间列名称（第一列）
        time_col1 = df1.columns[0]
        time_col2 = df2.columns[0]
        print(f"检测到时间列: {time_col1} (文件1), {time_col2} (文件2)")

        df1 = df1.rename(columns={time_col1: 'Time'})
        df2 = df2.rename(columns={time_col2: 'Time'})

        # 检查指标是否存在
        missing1 = [ind for ind in indicators if ind not in df1.columns]
        missing2 = [ind for ind in indicators if ind not in df2.columns]
        if missing1:
            print(f"警告: 文件1缺少指标: {', '.join(missing1)}")
        if missing2:
            print(f"警告: 文件2缺少指标: {', '.join(missing2)}")

        # 获取所有时间并保持原始顺序（去重，按首次出现顺序）
        all_times = []
        seen = set()
        # 先添加第一个文件的时间（保持原始顺序）
        for time in df1['Time']:
            if time not in seen:
                seen.add(time)
                all_times.append(time)
        # 再添加第二个文件的时间（保持原始顺序，跳过已存在的）
        for time in df2['Time']:
            if time not in seen:
                seen.add(time)
                all_times.append(time)

        # 创建结果数据框
        result_df = pd.DataFrame(index=indicators, columns=all_times)

        # 填充数据（格式：file1_value (file2_value)）
        for time in all_times:
            # 从两个文件中获取该时间点的数据
            row1 = df1[df1['Time'] == time].iloc[0] if time in df1['Time'].values else None
            row2 = df2[df2['Time'] == time].iloc[0] if time in df2['Time'].values else None

            for ind in indicators:
                # 获取两个文件中的值
                val1 = row1[ind] if (row1 is not None and ind in row1) else None
                val2 = row2[ind] if (row2 is not None and ind in row2) else None

                # 格式化输出字符串
                if val1 is not None and val2 is not None:
                    # 保留一位小数，可根据需要调整
                    result_df.at[ind, time] = f"{val1:.2f} ({val2:.2f})"
                elif val1 is not None:
                    result_df.at[ind, time] = f"{val1:.2f} (无数据)"
                elif val2 is not None:
                    result_df.at[ind, time] = f"(无数据) ({val2:.2f})"
                else:
                    result_df.at[ind, time] = "无数据"

        # 处理输出路径
        if output_path is None:
            output_path = os.path.join(os.getcwd(), 'merged_indicators.csv')

        # 保存结果
        result_df.to_csv(output_path)
        print(f"成功生成结果文件: {output_path}")

        return result_df

    except Exception as e:
        print(f"处理出错: {str(e)}")
        return None
def four_to_one_eps():
    """
    将四个小图排列成2×2的大图
    :return:
    """
    time_list = ['2018 06', '2019 06', '2020 06', '2021 06']
    # --- 全局字体设置 ---
    plt.rcParams['font.sans-serif'] = ['Times New Roman']
    plt.rcParams['font.size'] = 30
    plt.rcParams['axes.labelsize'] = 20  # 可以适当调小，因为子图空间有限
    plt.rcParams['xtick.labelsize'] = 20
    plt.rcParams['ytick.labelsize'] = 20
    plt.rcParams['legend.fontsize'] = 16


    # 获取配置信息
    colors = ['#2878b4',
              '#373535']
    markers = ['o',
               's']

    # 1. 创建一个大画布和4个子图
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))  # 2行2列的子图布局
    axes = axes.flatten()  # 将axes数组展平，方便循环索引 (ax1, ax2, ax3, ax4)

    # 2. 循环遍历每个时间段并绘图
    for i, time in enumerate(time_list):
        if i < len(axes):  # 防止time_list过长
            ax = axes[i]  # 获取当前子图

            _,G = Main.get_certain_networks_by_months(time)
            null_model = NullModel.create_degree_distribution_null_model(G)

            knn_dict = Undirected.calculate_knn(G)
            null_model_knn_dict = Undirected.calculate_knn(null_model)

            # 为当前子图绘制数据
            # 原始网络
            x_origin = list(knn_dict.keys())
            y_origin = list(knn_dict.values())
            ax.scatter(
                x_origin, y_origin,
                label=f'Network ({time})',
                color=colors[0 % len(colors)],
                marker=markers[0 % len(markers)],
                s=60, alpha=0.8, linewidth=0.8, edgecolors='k'
            )

            # 空模型
            x_null = list(null_model_knn_dict.keys())
            y_null = list(null_model_knn_dict.values())
            ax.scatter(
                x_null, y_null,
                label=f'Null Model ({time})',
                color=colors[1 % len(colors)],
                marker=markers[1 % len(markers)],
                s=60, alpha=0.8, linewidth=0.8, edgecolors='k'
            )

            ax.set_xscale('log')
            ax.set_yscale('log')
            legend = ax.legend(loc='upper right')
            for label in ax.get_xticklabels():
                label.set_fontweight('bold')
            for label in ax.get_yticklabels():
                label.set_fontweight('bold')
            for text in legend.get_texts():
                text.set_fontweight('bold')

    # 3. 添加整体标题和图例
    # fig.suptitle('KNN Comparison Across Different Time Periods', fontsize=24, y=0.98)

    fig.supxlabel('Degree')
    fig.supylabel('Average Neighbors Node Degree')

    # 4. 调整子图间距，防止标题和标签重叠
    plt.tight_layout()  # rect参数为图例和总标题留出空间

    # 5. 保存图片
    for for_mat in ["png", "eps", "pdf"]:  # png eps pdf
        plt.savefig(f'Output/Months/Undirected/KAndKnn/2018 06-2021 06.{for_mat}',
                    format=for_mat,  # 显式指定格式（可选，但更稳妥）
                    dpi=300,
                    bbox_inches='tight'  # 去除图片周围多余空白
                    )




# 使用示例
if __name__ == "__main__":
    four_to_one_eps()

    #regionProcess_csv_files
    # # 替换为你的文件路径
    # file1 = "Figure/Season/all_in_one_Digraph.csv"  # 第一个CSV文件路径
    # file2 = "Figure/Season/all_in_one_nm_zero_model.csv"  # 第二个CSV文件路径
    # output = "Figure/Season/nm_zero_model_comparison.csv"  # 输出文件路径
    # process_csv_files(file1, file2, output)
    #endregion
