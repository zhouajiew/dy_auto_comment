import asyncio
import os
import random
import time

import pyperclip

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

async def get_doubao_reply(page, page2):
    # 读取剪贴板内容
    temp_link = pyperclip.paste()

    # 获取豆包回复
    input_element = await page2.locator("[class='editor-wrapper-aTMAEc']").all()
    if input_element:
        await page2.type("[class='editor-wrapper-aTMAEc']", temp_link)

        await asyncio.sleep(2, 3)
        send_button_element = await page2.locator("[class='container-kD9BOs send-btn-wrapper']").all()
        if send_button_element:
            await send_button_element[0].click(force=True)

            await asyncio.sleep(1)
            # 回复完毕
            try:
                temp_w = await page2.locator(
                    "[class='message-action-bar-raqbg0 flex flex-row w-full group']").first.wait_for(
                    timeout=30000)

                reply_element = await page2.locator(
                    "[class='auto-hide-last-sibling-br paragraph-pP9ZLC paragraph-element br-paragraph-space']").all()
                full_reply = ''
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

            except Exception as e:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(Fore.RED + f'{timestamp} 获取豆包回复超时！{e}' + Fore.RESET)

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

        # 本轮看过的视频数量
        video_watched_count = 0
        # 随机看多少个视频/直播后进行点赞+评论
        random_make_actions_count = random.randint(20, 30)

        while True:
            temp_element = await page.locator("[class='temp_element']").all()
            await asyncio.sleep(1)
            if login_status:
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

                        # comment_element = await page.locator("[class='jp8u3iov']").all()

                        active_video_element = await page.locator("[data-e2e='feed-active-video']").all()

                        if active_video_element:
                            temp_active_video_element = active_video_element[0]
                            like_count = ''

                            # KV_gO8oI uwkzJlBF myn2Itp_
                            like_count_element = await temp_active_video_element.locator(
                                "[class='KV_gO8oI uwkzJlBF myn2Itp_']").all()
                            if like_count_element:
                                like_count = await like_count_element[0].inner_text(timeout=5000)

                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print(f'{timestamp} 该视频的点赞数量:{like_count}')

                                # 只对万赞以上的视频点赞和评论
                                if '万' in like_count:
                                    if video_watched_count > random_make_actions_count:
                                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        print(
                                            Fore.YELLOW + f'{timestamp} 尝试自动点赞和评论视频中...' + Fore.RESET)

                                        async def click_like():
                                            nonlocal video_watched_count
                                            nonlocal random_make_actions_count

                                            temp_t1 = time.time()

                                            # 随机观看视频[20, 30]秒后，进行点赞和评论
                                            random_watch_video_time = random.uniform(20, 30)

                                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            print(f'{timestamp} 将在{random_watch_video_time}秒后自动点赞和评论')

                                            while True:
                                                temp_t2 = time.time()
                                                if temp_t2 - temp_t1 > random_watch_video_time:
                                                    # 按'Z'键点赞
                                                    await page.keyboard.press("Z")

                                                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                    print(f'{timestamp} 已点赞该视频:)')

                                                    # 重置相关数据
                                                    video_watched_count = 0
                                                    random_make_actions_count = random.randint(20, 30)

                                                    # 按'V'键分享
                                                    await page.keyboard.press("V")
                    
                                                    await asyncio.sleep(random.uniform(1, 2))
                    
                                                    get_reply_task = asyncio.create_task(get_doubao_reply(page, page2))
                                                    await get_reply_task

                                                    await asyncio.sleep(random.uniform(5, 10))

                                                    break

                                                temp_element = await page.locator("[class='temp_element']").all()
                                                await asyncio.sleep(1)

                                        await asyncio.create_task(click_like())

                        video_watched_count += 1
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f'{timestamp} 本轮已观看视频/直播{video_watched_count}个，超过{random_make_actions_count}个后自动进行点赞以及评论:)')

if __name__ == "__main__":
    asyncio.run(main())
