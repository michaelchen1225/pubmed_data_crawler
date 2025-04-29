import os

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Use the absolute path for the file
file_current_crawler_path = os.path.join(script_directory, 'current_crawler.txt')

# 讀取當前數目
with open(file_current_crawler_path, 'r') as f:
    count = int(f.read())

count += 1

# 將新數目寫入
with open(file_current_crawler_path, 'w') as f:
    f.write(str(count))

print('當前累加數目為：', count)