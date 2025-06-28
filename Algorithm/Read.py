import re
import csv
import json

# 这几个方法 暂时弃用
# def read_port_name_info():
#     '''
#     这个函数是为了消除 数据中港口名称有问题而产生的影响  相当于是做一个规范化
#     :return: 返回一个dict key为输入的port name  value为正确的port name
#     '''
#     # 读取port Name
#     PortName = {}
#
#     # 逐行读取csv文档
#     with open('../Data/Port/PortInfo.csv', 'r', encoding='utf-8') as file:
#         lines = file.readlines()
#     for line in lines[1:]:
#
#         # 去掉行尾的换行符号
#         line = line.strip()
#         # 切分
#         parts = line.split(";")
#
#         # 切分后第一段是港口  第二段是正确的港口信息
#         Port = parts[0].strip()
#         RightPort = parts[1].strip()
#
#         PortName[Port] = RightPort
#     return PortName
# def read_remove_port_info():
#     '''
#
#     :return: 返回一个list 是已经标记好的错误的port name
#     '''
#     # 初始化一个空列表来存储港口名称
#     ports_list = []
#
#     # 打开文件并读取内容
#     with open('../Data/Port/Error_Port.txt', 'r', encoding='utf-8') as file:
#         # 逐行读取文件
#         for line in file:
#             # 去除每行末尾的换行符并添加到列表中
#             ports_list.append(str(line.strip()))
#     return ports_list
# def read_USHSCode_Origin():
#     '''
#     处理原始数据  Import 和 Export 一样的 改一下路径就行
#     :return: 返回一个 dict  key 为 USImpRecordId   value 为 HSCode
#     '''
#     # 读取 USImpHSCode
#     USImpHSCode = dict()
#
#     # 逐行读取csv文档
#     with open('D:/PortData/USImpHSCode/panjivaUSExpHSCode.csv', 'r', encoding='utf-8') as file:
#         lines = file.readlines()
#     for line in lines:
#         try:
#             # 去掉行尾的换行符号
#             line = line.strip()
#             # 切分
#             parts = line.split(",")
#
#             # 切分后第一段是交易记录ID  第二段是HSCode
#             RecordId = parts[0].strip()
#             HScode = parts[1].strip()
#
#             # 使用正则表达式提取前两个数字
#             match = re.search(r'\d{1,2}', HScode)
#
#             if match:
#                 # 将匹配到的字符串转换为整数
#                 HScode = int(match.group())
#             else:
#                 HScode = None
#
#             USImpHSCode[RecordId] = HScode
#         except IndexError as i:
#             print(RecordId)
#     return USImpHSCode
# def save_USHSCode(dict_data):
#     '''
#     在执行完read_USImpHSCode_Origin()函数后  将HSCode保存成一个csv文件
#     Import 和 Export 一样的 改一下路径就行
#     :param dict_data:
#     :return:
#     '''
#     # 指定要保存的 CSV 文件名
#     filename = 'D:/PortData/USImpHSCode/USExpHSCode.csv'
#
#     # 打开文件并写入内容
#     with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#         # 创建一个 CSV 写入器
#         writer = csv.writer(csvfile)
#
#         # 遍历字典的每个键值对
#         for key, value in dict_data.items():
#             # 将键值对写入 CSV 文件，每个键值对占一行
#             writer.writerow([key, value])

class Read:
    @classmethod
    def read_USImpHSCode(cls):
        '''
        得到USImHSCode
        :return: 返回一个 dict  key 为 USImpRecordId   value 为 HSCode
        '''
        # 读取 USImpHSCode
        USImpHSCode = dict()

        # 逐行读取csv文档
        with open('D:/PortData/USImpHSCode/USImpHSCode.csv', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            # 去掉行尾的换行符号
            line = line.strip()
            # 切分
            parts = line.split(",")

            # 切分后第一段是交易记录ID  第二段是HSCode
            # 注意这里我把 key 转换成了 int 类型   方便与 DataFrame中的row['panjivaRecordId'] 匹配
            RecordId = parts[0].strip()
            HScode = parts[1].strip()

            USImpHSCode[RecordId] = HScode
        print("USImpHSCode读取完毕")
        return USImpHSCode

    @classmethod
    def read_USExpHSCode(cls):
        '''
        得到USExpHSCode
        :return: 返回一个 dict  key 为 USExpRecordId   value 为 HSCode
        '''
        # 读取 USImpHSCode
        USExpHSCode = dict()

        # 逐行读取csv文档
        with open('D:/PortData/USImpHSCode/USExpHSCode.csv', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            # 去掉行尾的换行符号
            line = line.strip()
            # 切分
            parts = line.split(",")

            # 切分后第一段是交易记录ID  第二段是HSCode
            # 注意这里我把 key 转换成了 int 类型   方便与 DataFrame中的row['panjivaRecordId'] 匹配
            RecordId = parts[0].strip()
            HScode = parts[1].strip()

            USExpHSCode[RecordId] = HScode
        print("USExpHSCode读取完毕")
        return USExpHSCode

    @classmethod
    def read_port_hs_rate_info(cls):
        '''
        类方法 直接 cls. 出来用
        :return: port_hs_rate_info Dict
        '''
        data_path = "../Data/FinalGraph/port_hs_rate_info.json"
        # 一次性读取整个JSON文件
        with open(data_path, "r", encoding="utf-8") as file:
            port_hs_rate_info = json.load(file)
        return port_hs_rate_info

    @classmethod
    def read_port_in_out_info(cls):
        '''
        类方法 直接 cls. 出来用
        :return: port_port_in_out_info Dict
        '''
        data_path = "../Data/FinalGraph/port_in_out_info.json"
        # 一次性读取整个JSON文件
        with open(data_path, "r", encoding="utf-8") as file:
            port_in_out_info = json.load(file)
        return port_in_out_info