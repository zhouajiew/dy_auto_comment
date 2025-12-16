import json
import re
import sys
import threading
import time

import requests

from openai import OpenAI

from global_variable import *

# 查询余额
def balances_info():
    url = "https://api.deepseek.com/user/balance"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key[0]}'
    }

    response = None
    try:
        # 有时候会卡在这里，需要设置超时时间
        response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
        info = json.loads(response.text)
        print(f"总的可用余额为:{info.get("balance_infos")[0].get("total_balance")}元")
    except requests.exceptions.Timeout:
        print('查询余额的请求超时!')
    except requests.exceptions.RequestException as e:
        print(f"查询余额的请求发生错误: {e}")

# 提取流式输出的Tokens相关信息(deepseek)
def get_tokens_info(last_chunk_content):
    tokens_list = {}

    try:
        pattern = r'completion_tokens=(\d+),'
        temp_completion_tokens = re.search(pattern, last_chunk_content).group(1)
        tokens_list["completion_tokens"] = temp_completion_tokens

        pattern = r'prompt_cache_hit_tokens=(\d+),'
        temp_prompt_cache_hit_tokens = re.search(pattern, last_chunk_content).group(1)
        tokens_list["prompt_cache_hit_tokens"] = temp_prompt_cache_hit_tokens

        pattern = r'prompt_cache_miss_tokens=(\d+)\)'
        temp_prompt_cache_miss_tokens = re.search(pattern, last_chunk_content).group(1)
        tokens_list["prompt_cache_miss_tokens"] = temp_prompt_cache_miss_tokens

        return tokens_list

    except Exception as e:
        print(f"提取流式输出的Tokens相关信息失败!{e}")
        return None

# 同步获取ai回复，流式输出回复
def get_ai_response_stream(model, messages):
    start_time = time.time()

    '''
    print("请求内容为:\n")
    for m in messages:
        print(m)
    '''

    client = OpenAI(api_key=api_key[0], base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    completion_tokens = 0
    cache_hit_tokens = 0
    cache_miss_tokens = 0
    cost = 0

    reasoning_content = ""
    content = ""

    one_time = False
    one_time2 = False

    all_chunk = []

    for chunk in response:
        all_chunk.append(chunk)
        # R1模型
        if hasattr(chunk.choices[0].delta, "reasoning_content"):
            if chunk.choices[0].delta.reasoning_content:
                if chunk.choices[0].delta.reasoning_content:
                    if not one_time:
                        print("\n思维链:")
                        one_time = True

                    reasoning_content += chunk.choices[0].delta.reasoning_content
                    sys.stdout.write(chunk.choices[0].delta.reasoning_content)
                    sys.stdout.flush()
            else:
                if chunk.choices[0].delta.content:
                    if not one_time2:
                        print("\n\n最终回复:")
                        one_time2 = True

                    content += chunk.choices[0].delta.content
                    sys.stdout.write(chunk.choices[0].delta.content)
                    sys.stdout.flush()
        # chat模型
        else:
            if chunk.choices[0].delta.content:
                if not one_time2:
                    print("\n\n最终回复:")
                    one_time2 = True

            content += chunk.choices[0].delta.content
            sys.stdout.write(chunk.choices[0].delta.content)
            sys.stdout.flush()

    last_chunk_content = str(all_chunk[-1:])

    tokens_list = get_tokens_info(last_chunk_content)

    if tokens_list:
        completion_tokens = int(tokens_list["completion_tokens"])
        cache_hit_tokens = int(tokens_list["prompt_cache_hit_tokens"])
        cache_miss_tokens = int(tokens_list["prompt_cache_miss_tokens"])
        print(f"\n\ncompletion_tokens:{completion_tokens}")
        print(f"prompt_cache_hit_tokens:{cache_hit_tokens}")
        print(f"prompt_cache_miss_tokens:{cache_miss_tokens}\n")

    if model == "deepseek-chat":
        cost = (0.5*cache_hit_tokens + 2*cache_miss_tokens + 8*completion_tokens)/1000000
    if model == "deepseek-reasoner":
        cost = (cache_hit_tokens + 4*cache_miss_tokens + 16*completion_tokens)/1000000

    print(f"本次请求消费{cost}元\n")

    thread = threading.Thread(target=balances_info)
    thread.start()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"本次请求执行时间为{total_time}s\n")

    if reasoning_content != "":
        '''
        full_content = f'思维链:\n{reasoning_content}\n\n最终回复:{content}'

        with open(f"{relative_path}/final_response.txt", "w", encoding='utf-8') as file:
            file.write(full_content)
        '''

        return {
            "reasoning_content":reasoning_content, "content":content, "cost":cost,
            "completion_tokens":completion_tokens,
            "prompt_cache_hit_tokens":cache_hit_tokens,
            "prompt_cache_miss_tokens":cache_miss_tokens
            }
    else:
        '''
        full_content = f'最终回复:{content}'

        with open(f"{relative_path}/final_response.txt", "w", encoding='utf-8') as file:
            file.write(full_content)
        '''

        return {
            "content":content, "cost":cost,
            "completion_tokens": completion_tokens,
            "prompt_cache_hit_tokens": cache_hit_tokens,
            "prompt_cache_miss_tokens": cache_miss_tokens
            }
