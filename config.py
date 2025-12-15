import json
import os

from colorama import init

# 获取当前文件所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建相对路径
relative_path = os.path.join(current_dir)

from global_variable import *

# 读取json文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

# 初始化config.json文件
def init_config():
    try:
        data = []
        data.append({"model":"deepseek-reasoner",
                     "api_key":""})

        # 打开文件，以写入模式创建文件对象
        with open(f'{relative_path}/config.json', 'w', encoding='utf-8') as file:
            # indent=1 每个层级缩进1个空格
            file.write(json.dumps(data, indent=1, ensure_ascii=False))

        print(f"初始化config.json文件成功!")
    except Exception as e:
        print(f"初始化config.json文件失败!")
        pass

def read_config():
    # 读取config.json文件
    path = f'{relative_path}/config.json'

    if os.path.exists(path):
        try:
            original_data = read_json_file(path)

            model[0] = original_data[0].get('model')
            api_key[0] = original_data[0].get('api_key')

            return original_data
        except Exception as e:
            print(f"读取config.json文件失败!")
            pass
    else:
        return None

init()

path = f'{relative_path}/config.json'

if not os.path.exists(path):
    init_config()
else:
    read_config()
