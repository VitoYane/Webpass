import asyncio
from base64 import b64decode 
from queue import Queue
import re, difflib
from os.path import join, splitext
from os import walk
from loguru import logger
from threading import Thread
from chardet import detect 
import aiofiles
from datetime import datetime, timedelta
from os import linesep

async def wirte_demo():
    # 异步方式执行with操作,修改为 async with
    async with aiofiles.open("test.txt","a",encoding="utf-8") as fp:
        await fp.write("hello world!\n")
        print("数据写入成功")

async def aread_file(filePath, ret_list = True):
    async with aiofiles.open(filePath,"ab+") as f:
        await f.seek(0, 0); 
        content = await f.read()
        code = detect(content)['encoding']
        code = code or 'latin1'
        ret = content.decode(code, 'ignore')
        if ret_list: ret = ret.split(linesep)
        return ret

async def read2_demo():
    async with aiofiles.open("target1.txt","r",encoding="utf-8") as fp:
        async for line in fp:
            print(line.strip())
            

def change_dir_txt_code(root_dir, code):
    for root, dirs, files in walk(root_dir):

        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for f in files:
            if splitext(f)[1] in ['.txt']:
                change_code(join(root, f), code)

        # 遍历所有的文件夹
        for d in dirs:
            change_dir_txt_code(join(root, d))

def strJudgeCode(str):
    return detect(str)

def readFile(path):
    try:
        f = open(path, 'rb')
        filecontent = f.read()
    finally:
        if f:f.close()
    return filecontent


def change_code(path, code):
    file_con = readFile(path)
    result = strJudgeCode(file_con)
    if result['encoding'] not in [None, 'ascii']:
        content_uni = file_con.decode(result['encoding'])
        content_to = content_uni.encode(code)
        write_file(path, content_to, 'wb', encoding=code)
        if result['encoding'] != 'ascii': logger.info(f"完成格式处理:{result['encoding']} -> {code} : {path}")




def restart_myself():
    from os import execl
    from sys import executable, argv
    execl(executable, executable, *argv)

def kill_myself(include_parants = False):
    from os import getpid ,kill, getppid
    kill(getpid(), 0)
    if include_parants: kill(getppid(), 0)


def if_unique(lst):
    return len(lst) == len(set(lst))

def get_unique(lst):
    return list(set(lst))


def more_than_minutes(old_time, _minutes = 30, new_time = None):
    '''两个datetime时间差大于多少分钟, new_time不写默认为当前时间'''
    if new_time == None: new_time = datetime.now()
    if not isinstance(old_time, datetime) or not isinstance(new_time, datetime):return False
    if (max(new_time, old_time) - min(new_time, old_time)) >= timedelta(minutes=_minutes):
        return True
    else:
        return False

def get_url(_str):
    ret = {}
    for url_info in findallA(r'((?:http(?:s)?)+://)+((?:\d+\.\d+\.\d+\.\d+)|(?:[^/\s:]+(?:\.[^/\s:]+)+))(:\d+)?([^\s]+)?', _str, 4):
        if not url_info: continue
        schema, ip, port, path = url_info
        ret[f'{schema}{ip}{port}'] = {
            'status':'init',
            'title':'',
            'content':'',
            'key':'',
            'last_time': None,
            'user_pass': None,
        }
    return ret

def goA(func, *args, **kwds):
    mthread=Thread(target=func, args=args, kwargs=kwds)
    mthread.daemon = kwds.pop('nowait', False)
    mthread.start()

def goB(func, *args, **kwds):
    mthread=Thread(target=func, args=args, kwargs=kwds)
    # mthread.setDaemon(True)
    mthread.start()

def list_any_one_in_str(_list, _str):
    return any(base642str(_one) in _str for _one in _list)

def str_in_list_any_one( _str, _list):
    return any(base642str(_str) in _one for _one in _list)

def list_all_in_str(_list, _str):
    return all(base642str(_one) in _str for _one in _list)


#判断相似度的方法，用到了difflib库
def get_equal_rate(str1, str2, n = 4):
   return round(difflib.SequenceMatcher(None, str1, str2).quick_ratio(), n)

def get_err_msg(times = 1, pl = False ,_interval = ' -> '):
    '''pl=true 打印局部变量环境'''
    from sys import _getframe, exc_info
    call_str = ''; lcs = ''; _frame = _getframe(); n = -1
    while _frame and n <= times:
        No = _frame.f_lineno
        cname = _frame.f_code.co_name
        if call_str == '':call_str = '|'
        else:
            if lcs == '':
                for k, v in _frame.f_locals.items():
                    lcs = f'{lcs}\t{repr(k):20.20s}: {repr(v):100.100s}\n'
                lcs = f'\n{lcs}'
                No = exc_info()[2].tb_lineno if exc_info()[2] != None else None
            call_str = f'{cname}({No}){_interval}{call_str}'
        _frame = _frame.f_back; n += 1
    return f"\n{call_str[:-len(_interval)]}: {exc_info()[1]} {exc_info()[0]}\n{lcs}\n{'-' * 79}\n\n" if pl else f"{call_str[:-len(_interval) - 1]}{_interval}{exc_info()[0]} : {exc_info()[1]}"

def get_call_link(times = 1, _interval = ' >> '):
    '''获取调用链，0是当前，1是上一个...'''
    from sys import _getframe
    call_str = ''
    _frame = _getframe(); n = -1;
    while _frame and n <= times:
        No = _frame.f_lineno
        cname = _frame.f_code.co_name
        call_str = ' ' if call_str == '' else f'{cname}({No}){_interval}{call_str}'
        _frame = _frame.f_back
        n += 1
    return call_str

def deal_result(r):
    print(f"回调输出：{r.result() = }")



def findallA(patn, src_str, ret_len = 1, mode = re.I|re.M):
    '''
    使用re模块统一输出结果为[(1,2,3),(1,2,3)...], 
    能搜到多个结果统一使用句式：for r in findall('f(\d+)', a, 5): x,y,z = r; ...
    如果只想要第一个结果：x,*y =  findall('f(\d+)', a, 1)    # 这种句式是x代表第一个找到的结果，x在ret_len=1时为字符串，ret_len>1时为元组

    如果每个结果中，只有有1个提取字段，配置ret_len = 1,用下面两种方式解析
    x,*y =  findall('f(\d+)', a, 1)    # 这种句式是x代表第一个找到的结果，x在ret_len=1时为字符串，ret_len>1时为元组
    print(f"x => |{x}| {type(x)}")

    for r in findall('f(\d+)', a, 1):print(r);break

    注意需要 判断 if not r: continue 用来解决没找到的问题
    '''
    p = re.compile(patn, mode)
    single_list = p.findall(src_str)
    s = lambda n: tuple([''] * abs(n))
    for r in single_list:
        if isinstance(r, tuple) and len(r) == ret_len:
            yield r
        elif isinstance(r, tuple) and len(r) < ret_len:
            yield r.__add__(s(ret_len-len(r)))
        elif isinstance(r, tuple) and len(r) > ret_len:
            yield r[:ret_len]
        elif isinstance(r, str):
            if ret_len == 1 and len(r) > 0:yield r
            else:yield (r,).__add__(s(ret_len - 1))
    yield None
    
def read_fileA(filePath, ret_type = 'list'):
    '''无错读文件，返回可选list,str '''
    from chardet import detect
    with open(filePath, 'ab+') as f:
        f.seek(0, 0); content = f.read()
        code = detect(content)['encoding']
        code = code or 'latin1'
        ret = content.decode(code, 'ignore')
        if ret_type == 'list':
            f.seek(0, 0)
            ret = list(map(lambda x: x.decode(code, 'ignore').strip(), f.readlines()))
        return ret

def write_file(file_name, write_data, mode = 'a+', encoding='utf-8', one_line = False, write_title = False):
    '''
    写文件，可以写字符串，元组，列表，字典等结构, 
    one_line仅对列表，集合、元组有效,
    write_title 仅对字符串有效，写标题行
    '''
    from collections import deque
    from loguru import logger
    from chardet import detect
    try:
        if write_title: mode = 'rb+'; encoding = None
        if 'b' in mode: encoding = None
        with open(file_name, mode, encoding = encoding) as fo:
            if sum(map(lambda t: isinstance(write_data, t), [str, int, float, complex])):
                if write_title:
                    content = fo.read(); co = detect(content)['encoding']
                    write_data_en = f'{write_data}\n'.encode(co or 'utf-8', 'ignore')
                    fo.seek(0,0); fo.write(write_data_en + content)
                else:
                    fo.writelines(f'{write_data}\n')
            elif sum(map(lambda t: isinstance(write_data, t), [list, tuple, deque])):
                if one_line:
                    fo.writelines(f'{write_data}\n')
                else:
                    for x in write_data:
                        fo.writelines(f'{x}\n')
            elif sum(map(lambda t: isinstance(write_data, t), [dict])):
                if one_line:
                    fo.writelines(f'{write_data}\n')
                else:
                    fo.writelines('{\n')
                    for k, v in write_data.items():
                        fo.writelines(f'\t{repr(k)} : {repr(v)},\n')
                    fo.writelines('}\n')
            else:
                logger.warning(f'未考虑的类型写入: {write_data} --> type = {type(write_data)}')
                fo.writelines(f"{str(write_data)}\n")
        return True
    except KeyboardInterrupt as e:
        logger.warning('KeyboardInterrupt')
        exit()
    except Exception as e:
        logger.exception(f'{type(e)} => {e}')
        return False

def base642str(_str):
    try:
        return b64decode(_str).decode("utf-8")
    except Exception:
        return _str

from colorama import Fore, Back, Style

def cprint(*args, **kwds):
    front = kwds.pop('f', Fore.GREEN)
    back = kwds.pop('b', Back.RESET)
    end = kwds.pop('end', '\n')
    if raw := kwds.pop('raw', False):
        msg = ', '.join(list(map(repr,args)))
    else:
        msg = ', '.join(list(map(str,args)))
    print(f"{front}{back}{msg}{Style.RESET_ALL}", end=end, flush=1)
    

import nest_asyncio
nest_asyncio.apply()    # 主要解决循环体的嵌套事件, 没有这个语句会报错: This event loop is already running

from sys import version_info

class async_do():
    def __init__(self, sema = 100):                     # 构造函数, 类实例化的时候被调用
        self.sema = asyncio.Semaphore(sema)             # 设置信号量
        self.taskQu = Queue()
        if version_info.major >= 3 and version_info.minor >= 9:
            self.loop = asyncio.new_event_loop()        # 高版本用这两句的不会出现get_event_loop中警告 DeprecationWarning: There is no current event loop
            asyncio.set_event_loop(self.loop)           # 建议3.9以前使用get_event_loop(), 3.9以及之后
        else:
            self.loop = asyncio.get_event_loop()        # get_event_loop 获取循环体兼容性较好, 但是高版本会有一个警告
        
        
    def __call__(self, proc, callback, *args, **kwds):  # 调用函数, 类的实例化可以直接当函数用, 用的时候执行这个过程
        self.add(proc, callback, *args, **kwds)
        
    def add(self, proc, callback = None, *args, **kwds):               # 增加任务
        t = self.loop.create_task(proc(self.sema, *args, **kwds))
        if callback: t.add_done_callback(callback)
        self.taskQu.put(t)
        
    def submit(self, proc, callback, *args, **kwds):            # 提交任务, 等同于增加任务
        self.add(proc, callback, *args, **kwds)
        
    def map(self, proc, callback, arg_list: list = None):       # 映射任务
        '''arg_list 可以是元组组成的列表, 也可以是字典列表'''
        if arg_list is None: return 
        in_type_list = lambda data, type_list: any(isinstance(data, t) for t in type_list)

        for arg in arg_list:
            if in_type_list(arg, [list, tuple, set]): self.add(proc, callback, *arg)
            elif in_type_list(arg, [dict]): self.add(proc, callback, **arg)
            else: self.add(proc, callback, arg)

    def _go(self, func, *args, **kwds):                         # 多线程调用
        mthread=Thread(target=func, args=args, kwargs=kwds)
        mthread.daemon = kwds.pop('nowait', False)
        mthread.start()
    
    
    def wait(self):                                             # 等待任务队列执行完
        if t := [self.taskQu.get_nowait() for _ in range(self.taskQu.qsize())]:
            self.loop.run_until_complete(asyncio.wait(t))

    async def async_wait(self):                                             # 等待任务队列执行完
        if t := [self.taskQu.get_nowait() for _ in range(self.taskQu.qsize())]:
            await asyncio.wait(t)

    def no_wait(self):                                          # 不等待任务队列执行
        self._go(self.wait)
        

# url, pro, title, datetime.now()- timedelta(minutes=5), usernm, passwd
class task():
    def __init__(self, url = None, pro = None, title = None, last_time = None, usernm = None, passwd = None):                   # 构造函数, 类实例化的时候被调用
        self.url = url
        self.pro = pro
        self.title = title
        self.last_time = last_time
        self.usernm = usernm
        self.passwd = passwd
        
class apage():
    def __init__(self, name = 'page', idle = True, browser = None, context = None, page = None, ocr = None):                   # 构造函数, 类实例化的时候被调用
        self.name = name
        self.idle = idle
        self.browser = browser
        self.context = context
        self.page = page
        self.ocr = ocr
        


from collections import defaultdict, deque

def _init():
    '''import的时候会初始化, 因为已经import过的不会再次import 所以过程中不用判断是否存在 _global_data_dict'''
    global _global_data_dict
    _global_data_dict = {}

def set_value(name, value):
    '''设置值'''
    _global_data_dict[name] = value
    return value

def get_value(name, default = None):
    '''获取值'''
    try:
        return _global_data_dict[name]
    except KeyError:
        return default

def in_type_listA(data, type_list):
    return any(isinstance(data, t) for t in type_list)

def update_value(name, *args, **kwds):
    '''
    name 不存在, 将创建一个None
    name 值为字典, value 可以是字典或者元组, 更新
    name 值为列表, value 可以是列表, 也可以是其他值, 加到最后
    name 不是上述类型, 设置为value
    '''
    # 处理 args 和 kwds
    if kwds and args: 
        value = kwds.update(dict(enumerate(args)))
    elif kwds:
        value = kwds
    elif args:
        value = args[0] if len(args) == 1 else list(args)
    else:
        value = None

    # 如果没有name, 就创建一个value类型的空值
    if name not in _global_data_dict: 
        _global_data_dict[name] = type(value)()

    # 如果有name, 且值为dict类型
    if in_type_listA(_global_data_dict[name], [dict]):
        if in_type_listA(value, [dict]):
            _global_data_dict[name].update(value)
        elif in_type_listA(value, [list, set, deque]):
            _global_data_dict[name].update(dict(enumerate(value)))
        elif in_type_listA(value, [tuple]):
            if len(value) == 2:
                key, val = value
                _global_data_dict[name].update({key: val})
            else:
                _global_data_dict[name].update(dict(enumerate(value)))
    # 如果有name, 且值为列表, 集合, 元组类型
    elif in_type_listA(_global_data_dict[name], [list, set, tuple, deque]):
        _global_data_dict[name] = list(_global_data_dict[name])
        if in_type_listA(value, [list, set, tuple, deque]):
            _global_data_dict[name].extend(value)
        else:
            _global_data_dict[name].append(value)

    else:
        set_value(name, value)

def get_all_value():
    return _global_data_dict


if __name__ != '__main__':
    _init()


# class async_do():
#     def __init__(self, sema = 100):                   # 构造函数, 类实例化的时候被调用
#         self.sema = asyncio.Semaphore(sema)
#         self.taskQu = Queue()
#         self.loop = asyncio.get_event_loop()
        
#     def __call__(self, proc, callback, *args, **kwds):      # 调用函数, 类的实例化可以直接当函数用, 用的时候执行这个过程
#         self.add(proc, callback, *args, **kwds)
        
#     def add(self, proc, callback, *args, **kwds):
#         t = self.loop.create_task(proc(self.sema, *args, **kwds))
#         t.add_done_callback(callback)
#         self.taskQu.put(t)
        
#     def submit(self, proc, callback, *args, **kwds):
#         self.add(proc, callback, *args, **kwds)
        
#     def map(self, proc, callback, arg_list: list = None):
#         '''arg_list 可以是元组组成的列表, 也可以是字典列表'''
#         if arg_list is None: return 
#         in_type_list = lambda data, type_list: any(isinstance(data, t) for t in type_list)

#         for arg in arg_list:
#             if in_type_list(arg, [list, tuple, set]): self.add(proc, callback, *arg)
#             elif in_type_list(arg, [dict]): self.add(proc, callback, **arg)
#             else: self.add(proc, callback, arg)

#     def wait(self):
#         self.loop.run_until_complete(asyncio.wait(self.taskQu.queue))
