import re

# 用python读LDF件
def read_ldf_file(file_path):
    with open(file_path,'r', encoding='utf-8') as file:
        content = file.readlines()  # 读取文件的每一行
    # 返回读取的内容
    return content
def parse_ldf(content):
    ldf_data = {}

    for line in content:
        if line.startwith('NODE'):
            node_info = re.findall(r'NODE\s+(\w+)',line)
        elif line.startswith('SIGNAL'):
            signal_info = re.findall(r'SIGNAL\s+(\w+)',line)
            if signal_info:
                ldf_data['signals'] = ldf_data.get('signals',[]) + signal_info
    return ldf_data
def display_ldf_data(ldf_data):
    print('节点信息:')
    for node in ldf_data.get('nodes',[]):
        print(f"-{node}")
    print('\n信号信息')
    for signal in ldf_data.get('signals',[]):
        print(f"-{signal}")

ldf_content = read_ldf_file('D:/Data/Panjiva0820/ciq_Control_log.ldf')
parsed_data = parse_ldf(ldf_content)
display_ldf_data(parsed_data)