import pandas as pd
import os
import pyarrow.parquet as pq
import time

# path = 'D:/Data/Revelio_lab/individual/individual_user_skill_internal/individual_user_skill_0000_part_00.parquet'
# df = pd.read_parquet(path,engine='pyarrow')
# df.to_csv('Data/individual_user_skill_0000_part_00.csv')
# print(df)



# 读取同一个文件夹下的多个parquet文件
start_time = time.time()  # 记录开始时间

folder_path = 'D:/Data/Revelio_lab/individual/individual_user_skill_internal/'
parquet_files = [f for f in os.listdir(folder_path) if f.endswith('.parquet')]

# 初始化空的DataFrame用于存储数据
data = pd.DataFrame()

# 逐个读取Parquet文件中的数据并进行处理
for file in parquet_files:
    file_path = os.path.join(folder_path, file)
    data_iterator = pq.ParquetFile(file_path).iter_batches(batch_size=1024)

    for batch in data_iterator:
        # 将RecordBatch转换为Pandas DataFrame
        df_batch = batch.to_pandas()
        print(1)
        # 将处理后的数据追加到DataFrame中
        data = data._append(df_batch, ignore_index=True)

# 删除原始的feature列
data = data.drop('feature', axis=1)

# 保存到csv文件
csv_path = './Data/individual_user_skill_internal.csv'
data.to_csv(csv_path, index=False)

end_time = time.time()  # 记录结束时间
print(f'数据已保存到 {csv_path}')
print(f'总运行时间: {end_time - start_time} 秒')

