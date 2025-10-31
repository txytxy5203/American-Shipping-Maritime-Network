import re
import csv
import json



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
        data_path = "../Data/2019/FinalGraph/port_hs_rate_info.json"
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
        data_path = "../Data/2019/FinalGraph/port_in_out_info.json"
        # 一次性读取整个JSON文件
        with open(data_path, "r", encoding="utf-8") as file:
            port_in_out_info = json.load(file)
        return port_in_out_info

    @classmethod
    def Read_Port_Data(cls):
        '''
        类方法 直接 cls. 出来用
        :return: Port_Data 标准表
        '''
        data_path = "../Data/2019/Port/Port_Info_Json.json"
        # 一次性读取整个JSON文件
        with open(data_path, "r", encoding="utf-8") as file:
            port_data = json.load(file)
        return port_data