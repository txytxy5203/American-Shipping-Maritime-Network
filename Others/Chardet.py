import chardet

# 检测文件编码
with open('D:/Data/Panjiva0820/ciq_Control_log.ldf', 'rb') as file:
    raw_data = file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    print(encoding)