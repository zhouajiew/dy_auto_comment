import json
import os
from datetime import datetime

from colorama import init, Fore

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
        data.append({
            "model":"deepseek-reasoner",
            "api_key":""
        })

        data.append({
            "功能": "自动点赞视频",
            "一轮数量最小值": 20,
            "一轮数量最大值": 30
        })

        data.append({
            "功能": "自动评论视频",
            "一轮数量最小值": 20,
            "一轮数量最大值": 30,
            "是否同时点赞视频": 1
        })

        data.append({
            "功能": "自动暂停程序",
            "是否启用该功能": 0,
            "程序运行时间≥": 999999
        })

        data.append({
            "功能": "自动关闭程序",
            "是否启用该功能": 0,
            "程序运行时间≥": 999999
        })

        data.append({
            "功能": "评论失败处理",
            "描述": "评论失败后尝试转至下个符合条件的视频进行评论",
            "是否启用该功能": 0,
            "是否同时点赞视频": 0
        })

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

            if model[0] is None:
                model[0] = "deepseek-reasoner"
            if api_key[0] is None:
                api_key[0] = ""

            temp_idx = -1

            for idx, o in enumerate(original_data):
                if o.get('功能') == '自动点赞视频':
                    temp_idx = idx

            if temp_idx != -1:
                min_click_like_count[0] = original_data[temp_idx].get('一轮数量最小值')
                max_click_like_count[0] = original_data[temp_idx].get('一轮数量最大值')

                if min_click_like_count[0] is None:
                    min_click_like_count[0] = 20
                if max_click_like_count[0] is None:
                    max_click_like_count[0] = 30

            temp_idx = -1

            for idx, o in enumerate(original_data):
                if o.get('功能') == '自动评论视频':
                    temp_idx = idx

            if temp_idx != -1:
                min_comment_count[0] = original_data[temp_idx].get('一轮数量最小值')
                max_comment_count[0] = original_data[temp_idx].get('一轮数量最大值')
                click_like_before_comment[0] = original_data[temp_idx].get('是否同时点赞视频')

                if min_comment_count[0] is None:
                    min_comment_count[0] = 20
                if max_comment_count[0] is None:
                    max_comment_count[0] = 30
                if click_like_before_comment[0] is None:
                    click_like_before_comment[0] = 1

            temp_idx = -1

            for idx, o in enumerate(original_data):
                if o.get('功能') == '自动暂停程序':
                    temp_idx = idx

            if temp_idx != -1:
                pause_automatically[0] = original_data[temp_idx].get('是否启用该功能')
                set_pause_running_time[0] = original_data[temp_idx].get('程序运行时间≥')

                if pause_automatically[0] is None:
                    pause_automatically[0] = 0
                if set_pause_running_time[0] is None:
                    set_pause_running_time[0] = 999999

            temp_idx = -1

            for idx, o in enumerate(original_data):
                if o.get('功能') == '自动关闭程序':
                    temp_idx = idx

            if temp_idx != -1:
                close_automatically[0] = original_data[temp_idx].get('是否启用该功能')
                set_close_running_time[0] = original_data[temp_idx].get('程序运行时间≥')

                if close_automatically[0] is None:
                    close_automatically[0] = 0
                if set_close_running_time[0] is None:
                    set_close_running_time[0] = 999999

            temp_idx = -1

            for idx, o in enumerate(original_data):
                if o.get('功能') == '评论失败处理':
                    temp_idx = idx

            if temp_idx != -1:
                comment_next_if_failed[0] = original_data[temp_idx].get('是否启用该功能')
                comment_next_and_click_like[0] = original_data[temp_idx].get('是否同时点赞视频')

                if comment_next_if_failed[0] is None:
                    comment_next_if_failed[0] = 0
                if comment_next_and_click_like[0] is None:
                    comment_next_and_click_like[0] = 0

            # 更新config.json
            data = []
            data.append({
                "model": model[0],
                "api_key": api_key[0]
            })

            data.append({
                "功能": "自动点赞视频",
                "一轮数量最小值": min_click_like_count[0],
                "一轮数量最大值": max_click_like_count[0]
            })

            data.append({
                "功能": "自动评论视频",
                "一轮数量最小值": min_comment_count[0],
                "一轮数量最大值": max_comment_count[0],
                "是否同时点赞视频": click_like_before_comment[0]
            })

            data.append({
                "功能": "自动暂停程序",
                "是否启用该功能": pause_automatically[0],
                "程序运行时间≥": set_pause_running_time[0]
            })

            data.append({
                "功能": "自动关闭程序",
                "是否启用该功能": close_automatically[0],
                "程序运行时间≥": set_close_running_time[0]
            })

            data.append({
                "功能": "评论失败处理",
                "描述": "评论失败后尝试转至下个符合条件的视频进行评论",
                "是否启用该功能": comment_next_if_failed[0],
                "是否同时点赞视频": comment_next_and_click_like[0]
            })

            # 打开文件，以写入模式创建文件对象
            with open(f'{relative_path}/config.json', 'w', encoding='utf-8') as file:
                # indent=1 每个层级缩进1个空格
                file.write(json.dumps(data, indent=1, ensure_ascii=False))

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(Fore.GREEN + f'{timestamp} config.json文件格式已更新到最新版:D' + Fore.RESET)

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

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(Fore.YELLOW + f'{timestamp} 当前使用的模型:{model[0]}' + Fore.RESET)
print(Fore.YELLOW + f'{timestamp} api_key:{api_key[0]}\n' + Fore.RESET)

print(Fore.YELLOW + f'{timestamp} 自动点赞视频|一轮数量最小值:{min_click_like_count[0]}' + Fore.RESET)
print(Fore.YELLOW + f'{timestamp} 自动点赞视频|一轮数量最大值:{max_click_like_count[0]}\n' + Fore.RESET)

print(Fore.YELLOW + f'{timestamp} 自动评论视频|一轮数量最小值:{min_comment_count[0]}' + Fore.RESET)
print(Fore.YELLOW + f'{timestamp} 自动评论视频|一轮数量最大值:{max_comment_count[0]}' + Fore.RESET)
if click_like_before_comment[0] == 1:
    print(Fore.YELLOW + f'{timestamp} 自动评论视频|是否同时点赞视频:是\n' + Fore.RESET)
else:
    print(Fore.YELLOW + f'{timestamp} 自动评论视频|是否同时点赞视频:否\n' + Fore.RESET)

if pause_automatically[0] == 1:
    print(Fore.YELLOW + f'{timestamp} 自动暂停程序|是否启用该功能:是' + Fore.RESET)
    print(Fore.YELLOW + f'{timestamp} 自动暂停程序|程序运行时间≥:{set_pause_running_time[0]}\n' + Fore.RESET)
else:
    print(Fore.YELLOW + f'{timestamp} 自动暂停程序|是否启用该功能:否\n' + Fore.RESET)

if close_automatically[0] == 1:
    print(Fore.YELLOW + f'{timestamp} 自动关闭程序|是否启用该功能:是' + Fore.RESET)
    print(Fore.YELLOW + f'{timestamp} 自动关闭程序|程序运行时间≥:{set_close_running_time[0]}\n' + Fore.RESET)
else:
    print(Fore.YELLOW + f'{timestamp} 自动关闭程序|是否启用该功能:否\n' + Fore.RESET)

if comment_next_if_failed[0] == 1:
    print(Fore.YELLOW + f'{timestamp} 评论失败处理|是否启用该功能:是' + Fore.RESET)
    if comment_next_and_click_like[0] == 1:
        print(Fore.YELLOW + f'{timestamp} 评论失败处理|是否同时点赞视频:是\n' + Fore.RESET)
    else:
        print(Fore.YELLOW + f'{timestamp} 评论失败处理|是否同时点赞视频:否\n' + Fore.RESET)
else:
    print(Fore.YELLOW + f'{timestamp} 评论失败处理|是否启用该功能:否\n' + Fore.RESET)
