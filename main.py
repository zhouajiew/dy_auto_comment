import asyncio
import os
import random
import signal
import sys
import threading
import time

import pyperclip

import keyboard

from datetime import datetime

from colorama import Fore
from patchright.async_api import async_playwright

from api import get_ai_response_stream
from config import *
from global_variable import *

# 获取当前文件所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建相对路径
relative_path = os.path.join(current_dir)

def on_key_event(event):
    if event.event_type == 'down':
        if event.name == "f2":
            listen_status[0] = not listen_status[0]

            if listen_status[0] == 1:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(Fore.YELLOW + f'{timestamp} 已开启键盘事件监听' + Fore.RESET)
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(Fore.YELLOW + f'{timestamp} 已关闭键盘事件监听' + Fore.RESET)

        if listen_status[0] == 1:
            if event.name == '2':
                if pause[0] == 0:
                   pause[0] = 1

                   timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                   print(Fore.YELLOW + f'{timestamp} 程序已暂停' + Fore.RESET)
                else:
                   pause[0] = 0

                   timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                   print(Fore.YELLOW + f'{timestamp} 程序已恢复运行' + Fore.RESET)

# 一些事项在此处理
def handle_something():
    start_time = time.time()
    # 本轮程序运行时间
    start_time2 = time.time()

    temp_t1 = time.time()

    while True:
        temp_t2 = time.time()
        if temp_t2 - temp_t1 > 10:
            temp_t1 = temp_t2

            temp_running_time = time.time() - start_time
            temp_running_time2 = time.time() - start_time2

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(Fore.YELLOW + f'{timestamp} 当前程序运行时间:{temp_running_time}s' + Fore.RESET)

            if pause_automatically[0] == 1 and pause[0] == 0:
                if temp_running_time2 > set_pause_running_time[0]:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(Fore.YELLOW + f'{timestamp} 本轮程序运行时间{temp_running_time2}s≥指定值{set_pause_running_time[0]}s，自动暂停程序' + Fore.RESET)

                    pause[0] = 1

                    start_time2 = time.time()

            if close_automatically[0] == 1:
                if temp_running_time > set_close_running_time[0]:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(Fore.YELLOW + f'{timestamp} 程序运行时间{temp_running_time}s≥指定值{set_close_running_time[0]}s，自动关闭程序' + Fore.RESET)

                    time.sleep(5)
                    pid = os.getpid()  # 获取当前进程ID
                    os.kill(pid, signal.SIGTERM)  # 发送终止信号

        time.sleep(0.1)

async def get_doubao_reply(page, page2):
    # 读取剪贴板内容
    temp_link = pyperclip.paste()

    # 获取豆包回复
    input_element = await page2.locator("[class='semi-input-textarea semi-input-textarea-autosize']").all()
    if input_element:
        await page2.type("[class='semi-input-textarea semi-input-textarea-autosize']", temp_link)

        await asyncio.sleep(2, 3)
        '''
        send_button_element = await page2.locator("[data-testid='chat_input_send_button']").all()
        if send_button_element:
            await send_button_element[0].click(force=True)

            await asyncio.sleep(1)
        '''
        # 直接模拟按下回车键即可
        await page2.keyboard.press("Enter")
        # 回复完毕
        try:
            try:
                temp_w = await page2.locator(
                    "[class='message-action-bar-raqbg0 flex flex-row w-full group']").first.wait_for(
                    timeout=30000)
            except Exception as e:
                pause[0] = 1

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(Fore.RED + f'{timestamp} 检测到验证码出现，程序已自动暂停' + Fore.RESET)

            reply_element = await page2.locator(
                "[class='auto-hide-last-sibling-br paragraph-pP9ZLC paragraph-element br-paragraph-space']").all()
            full_reply = ''

            # reply_element还有另一种情况
            # header-iWP5WJ auto-hide-last-sibling-br
            if not reply_element:
                reply_element = await page2.locator(
                    "[class='header-iWP5WJ auto-hide-last-sibling-br']").all()

            # 如果还有其他情况，强制开启新对话
            if not reply_element:
                await asyncio.sleep(random.uniform(3, 5))
                try:
                    await page2.goto("https://www.doubao.com/chat", timeout=10000)
                except Exception as e:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(Fore.RED + f'{timestamp} 跳转超时！' + Fore.RESET)

            if reply_element:
                for r in reply_element:
                    temp_reply = await r.inner_text(timeout=5000)
                    full_reply += temp_reply

                # 分段元素的处理
                ol_element = await page2.locator("[class='auto-hide-last-sibling-br']").all()
                if ol_element:
                    for ol in ol_element:
                        temp_reply = await ol.inner_text(timeout=5000)
                        full_reply += temp_reply

                print(full_reply)

                await asyncio.sleep(random.uniform(3, 5))
                try:
                    await page2.goto("https://www.doubao.com/chat", timeout=10000)
                except Exception as e:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(Fore.RED + f'{timestamp} 跳转超时！' + Fore.RESET)

                error_reply = False

                # 系统内部异常/非公开 pass
                if '系统内部异常' in full_reply or '非公开' in full_reply:
                    error_reply = True

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(Fore.RED + f'{timestamp} 获取到的豆包回复异常，本次将不进行评论！' + Fore.RESET)

                if not error_reply:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(Fore.YELLOW + f'{timestamp} 正在向DeepSeek发送请求' + Fore.RESET)

                    system_prompt = '你是一个善于给视频进行评论的助手，接下来用户将会给你发送一段视频总结，请你根据视频总结作出合适的评论，评论禁止像人机也不要过长！'

                    temp_messages = []
                    temp_messages.append({"role": "system", "content": system_prompt})
                    temp_messages.append({"role": "user", "content": full_reply})

                    get_ai_response_result = get_ai_response_stream(model[0], temp_messages)

                    final_reply = get_ai_response_result['content']

                    # 按'X'键评论
                    await page.keyboard.press("X")

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{timestamp} 正在评论视频...')

                    await asyncio.sleep(random.uniform(3, 5))
                    comment_element = await page.locator("[class='hVeIqFGi']").all()
                    if comment_element:
                        await comment_element[0].click(force=True)
                        await asyncio.sleep(random.uniform(1, 2))

                        await page.type("[class='DraftEditor-editorContainer']", final_reply)

                        await asyncio.sleep(random.uniform(3, 5))

                        send_button_element = await page.locator("[class='WFB7wUOX NUzvFSPe']").all()
                        if send_button_element:
                            await send_button_element[0].click(force=True)

                            await asyncio.sleep(random.uniform(3, 5))
                            # 按'X'键关闭评论区
                            await page.keyboard.press("X")

                            await asyncio.sleep(random.uniform(3, 5))

                    return 'reply succeed'
                else:
                    return 'reply failed'

        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(Fore.RED + f'{timestamp} 评论时出现异常！{e}' + Fore.RESET)

            return 'reply failed'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=f'{relative_path}/user/playwright_data/dy_auto_comment',
            channel="chrome",
            headless=False,
            no_viewport=True,
            # do NOT add custom browser headers or user_agent
        )

        browser2 = await p.chromium.launch_persistent_context(
            user_data_dir=f'{relative_path}/user/playwright_data/doubao',
            channel="chrome",
            headless=False,
            no_viewport=True,
            # do NOT add custom browser headers or user_agent
        )

        page = await browser.new_page()
        page2 = await browser2.new_page()

        try:
            await page.goto("https://www.douyin.com/?recommend=1", timeout=20000)
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(Fore.RED + f'{timestamp} 打开网页超时！' + Fore.RESET)

        try:
            await page2.goto("https://www.doubao.com/chat", timeout=20000)
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(Fore.RED + f'{timestamp} 打开网页超时！' + Fore.RESET)

        login_status = False

        # 未登录状态 -> 出现'登录后免费畅享高清视频'字样
        if await page.locator("[class='mV5mWhEp']").all():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(Fore.YELLOW + f'{timestamp} 当前未登录抖音官网，请先登录，然后重启程序' + Fore.RESET)
        else:
            login_status = True

        temp_count = random.uniform(10, 30)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{timestamp} 本次将观看视频{temp_count}s')

        t1 = time.time()
        t2 = t1

        # 本轮看过的视频数量(点赞)
        video_watched_count = 0
        # 本轮看过的视频数量(评论)
        video_watched_count2 = 9999
        # 随机看多少个视频/直播后进行点赞
        random_make_actions_count = random.randint(min_click_like_count[0], max_click_like_count[0])
        # 随机看多少个视频/直播后进行评论
        random_make_actions_count2 = random.randint(min_comment_count[0], max_comment_count[0])

        while True:
            temp_element = await page.locator("[class='temp_element']").all()
            await asyncio.sleep(1)
            if login_status and pause[0] == 0:
                # 转到下一个视频
                t2 = time.time()
                if t2 - t1 > temp_count:
                    temp_count = random.uniform(10, 30)
                    t1 = t2

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(Fore.YELLOW + f'{timestamp} 正在切换到下一个视频/直播...' + Fore.RESET)

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{timestamp} 本次将观看视频/直播{temp_count}s')

                    go_to_next_element = await page.locator("[class='xgplayer-playswitch-next']").all()
                    if go_to_next_element:
                        await go_to_next_element[0].click(force=True)

                        await asyncio.sleep(random.uniform(3, 5))

                        active_video_element = await page.locator("[data-e2e='feed-active-video']").all()

                        if active_video_element:
                            temp_active_video_element = active_video_element[0]
                            like_count = ''

                            like_count_element = await temp_active_video_element.locator(
                                "[class='KV_gO8oI uwkzJlBF myn2Itp_']").all()
                            if like_count_element:
                                like_count = await like_count_element[0].inner_text(timeout=5000)

                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print(f'{timestamp} 该视频的点赞数量:{like_count}')

                                # 只对万赞以上的视频点赞和评论
                                if '万' in like_count:
                                    # 考虑到同时满足两种情况的时候，只执行自动点赞
                                    meet_condition1 = False

                                    if video_watched_count > random_make_actions_count:
                                        meet_condition1 = True

                                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        print(
                                            Fore.YELLOW + f'{timestamp} 尝试自动点赞中...' + Fore.RESET)

                                        async def click_like():
                                            nonlocal video_watched_count
                                            nonlocal random_make_actions_count

                                            temp_t1 = time.time()

                                            # 随机观看视频[20, 30]秒后，进行点赞和评论
                                            random_watch_video_time = random.uniform(20, 30)

                                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            print(f'{timestamp} 将在{random_watch_video_time}秒后自动点赞')

                                            while True:
                                                temp_t2 = time.time()
                                                if temp_t2 - temp_t1 > random_watch_video_time:
                                                    # 按'Z'键点赞
                                                    await page.keyboard.press("Z")

                                                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                    print(f'{timestamp} 已点赞该视频:)')

                                                    # 重置相关数据
                                                    video_watched_count = 0
                                                    random_make_actions_count = random.randint(min_click_like_count[0], max_click_like_count[0])

                                                    # 点赞后仍需随机停留一段时间
                                                    await asyncio.sleep(random.uniform(3, 5))

                                                    break

                                                temp_element = await page.locator("[class='temp_element']").all()
                                                await asyncio.sleep(1)

                                        await asyncio.create_task(click_like())

                                    if video_watched_count2 > random_make_actions_count2 and not meet_condition1:
                                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        print(
                                            Fore.YELLOW + f'{timestamp} 尝试自动评论视频中...' + Fore.RESET)

                                        async def comment():
                                            nonlocal video_watched_count2
                                            nonlocal random_make_actions_count2

                                            temp_t1 = time.time()

                                            # 随机观看视频[20, 30]秒后，进行点赞和评论
                                            random_watch_video_time = random.uniform(20, 30)

                                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            print(f'{timestamp} 将在{random_watch_video_time}秒后自动评论视频')

                                            while True:
                                                temp_t2 = time.time()
                                                if temp_t2 - temp_t1 > random_watch_video_time:
                                                    right_condition = False
                                                    if click_like_before_comment[0] == 1 and video_watched_count2 < 9999:
                                                        right_condition = True

                                                    if comment_next_and_click_like[0] == 1 and video_watched_count2 >= 9999:
                                                        right_condition = True

                                                    if right_condition:
                                                        # 按'Z'键点赞
                                                        await page.keyboard.press("Z")

                                                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                        print(f'{timestamp} 已点赞该视频:)')

                                                    # 重置相关数据
                                                    video_watched_count2 = 0
                                                    random_make_actions_count2 = random.randint(min_comment_count[0], max_comment_count[0])

                                                    # 按'V'键分享
                                                    await page.keyboard.press("V")
                    
                                                    await asyncio.sleep(random.uniform(1, 2))

                                                    reply_result = await get_doubao_reply(page, page2)

                                                    if reply_result == 'reply failed':
                                                        # 本次评论失败的话，尝试转至下个视频进行评论(需启用该功能)
                                                        if comment_next_if_failed[0] == 1:
                                                            video_watched_count2 = 9999

                                                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                            print(
                                                                Fore.RED + f'{timestamp} 本次评论失败，尝试转至下个视频进行评论' + Fore.RESET)
                                                        else:
                                                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                            print(
                                                                Fore.RED + f'{timestamp} 本次评论失败！' + Fore.RESET)
                                                    else:
                                                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                        print(
                                                            Fore.GREEN + f'{timestamp} 本次评论成功:D' + Fore.RESET)

                                                    await asyncio.sleep(random.uniform(5, 10))

                                                    break

                                                temp_element = await page.locator("[class='temp_element']").all()
                                                await asyncio.sleep(1)

                                        await asyncio.create_task(comment())

                        video_watched_count += 1
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f'{timestamp} 本轮已观看视频/直播{video_watched_count}个，超过{random_make_actions_count}个后自动进行点赞:)')

                        video_watched_count2 += 1
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(
                            f'{timestamp} 本轮已观看视频/直播{video_watched_count2}个，超过{random_make_actions_count2}个后自动进行评论:)')

if __name__ == "__main__":
    # 设置键盘钩子
    keyboard.hook(on_key_event)

    # 线程:处理一些事项
    handle_something_thread = threading.Thread(target=handle_something)
    handle_something_thread.start()

    time.sleep(5)

    asyncio.run(main())
