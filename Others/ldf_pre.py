import re

# from main import read_ldf_file


# 使用python读取LDF文件
def read_ldf_file(file_path):
    with open(file_path,'r',encoding='latin1') as file:
        content = file.readlines() # 读取文件的每一行
        # 返回读取的内容
    return content

# 解析LDF内容
def parse_ldf(content):
    ldf_data = {} # 创建一个空字典来存储解析后的数据
    for line in content:
        # 解析节点信息
        if line.startswith('NODE') :
            node_info = re.findall(r'NODE\s+(\s+)', line)
            if node_info:
                ldf_data['nodes'] = ldf_data.get('nodes', []) + node_info
        #解析信号信息
        elif line.startswith('SIGNAL'):
            signal_info = re.findall(r'SIGNAL\s+(\s+)', line)
            if signal_info:
                ldf_data['signals'] = ldf_data.get('signals', []) + signal_info
    return ldf_data # 返回解析后的数据

# 存储并打印解析后的数据
def display_ldf_data(ldf_data):
    print("节点信息:")
    for node in ldf_data.get( 'nodes', []):
        print(f"- {node}") # 打印每一个节点信息
    print("n信号信息:")
    for signal in ldf_data.get('signals', []):
        print(f"- {signal}") # 打印每一个信号信息
#主流程
ldf_content = read_ldf_file('D:/Data/Panjiva0820/ciq_Control_log.ldf') # 取LDF文件
parsed_data = parse_ldf(ldf_content) # 解LDF
print(parsed_data)
display_ldf_data(parsed_data) # 打印解析结果