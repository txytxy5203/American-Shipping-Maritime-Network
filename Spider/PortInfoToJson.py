import json


def parse_port_data(file_path):
    ports_dict = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        # 逐行读取文件
        for line in file:
            line = line.strip()
            if not line:  # 跳过空行
                continue

            # 解析单行数据为字典
            try:
                # 移除开头和结尾的花括号
                line = line.strip('{}')
                # 分割键值对
                pairs = line.split(',')

                port_info = {}
                for pair in pairs:
                    # 处理键值对，注意引号和冒号的位置
                    key, value = pair.split(':', 1)
                    key = key.strip().strip("'\"")  # 去除引号和空格
                    value = value.strip().strip("'\"")  # 去除引号和空格
                    port_info[key] = value

                # 使用port_code作为键
                if 'port_code' in port_info:
                    ports_dict[port_info['port_code']] = port_info

            except Exception as e:
                print(f"解析行失败: {line}, 错误: {e}")

    return ports_dict


# 使用示例
file_path = 'C:/Users/Tan/Desktop/文件/爬虫/Port_Info_Table.txt'  # 替换为您的文件路径
ports_data = parse_port_data(file_path)

# 保存为JSON文件
with open('../Data/Port/Port_Info_Json.json.old', 'w', encoding='utf-8') as f:
    json.dump(ports_data, f, ensure_ascii=False, indent=4)

# 打印结果
print(json.dumps(ports_data, ensure_ascii=False, indent=4))