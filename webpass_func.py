import asyncio
from base64 import b64decode 
from queue import Queue
import re, difflib
from os.path import join

from threading import Thread 


async def do_read(file):
    with open(file, 'rb') as fr:
        content = fr.read()
        await asyncio.sleep(5)
    return content
 
async def do_write(source_file, target_dir):
    with open(source_file,'rb') as fr:
        content = fr.read()
 
    with open(join(target_dir, 'test.writer'), 'wb') as fw:
        fw.write(content)
        await asyncio.sleep(10)
    return



def if_unique(lst):
    return len(lst) == len(set(lst))

def get_unique(lst):
    return list(set(lst))

def get_url(_str):
    ret = []
    for url_info in findallA(r'((?:http(?:s)?)+://)+((?:\d+\.\d+\.\d+\.\d+)|(?:[^/\s:]+(?:\.[^/\s:]+)+))(:\d+)?([^\s]+)?', _str, 4):
        if not url_info: continue
        schema, ip, port, path = url_info
        ret.append((f'{schema}{ip}{port}', f'{ip}{port}'))
    return ret


def goA(func, *args, **kwds):
    mthread=Thread(target=func, args=args, kwargs=kwds)
    mthread.setDaemon(True) # 孤儿线程, 即设为不重要, 不等待结束
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

def get_err_msg(times = 3, pl = False ,_interval = ' -> '):
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

def get_call_link(times = 999, _interval = ' --> '):
    '''获取调用链，0是当前，1是上一个...'''
    from sys import _getframe
    call_str = ''
    _frame = _getframe(); n = -1;
    while _frame and n <= times:
        No = _frame.f_lineno
        cname = _frame.f_code.co_name
        call_str = '|' if call_str == '' else f'{cname}({No}){_interval}{call_str}'
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
    



class async_do():
    def __init__(self, sema = 100):                   # 构造函数, 类实例化的时候被调用
        self.sema = asyncio.Semaphore(sema)
        self.taskQu = Queue()
        self.loop = asyncio.get_event_loop()
        
    def __call__(self, proc, callback, *args, **kwds):      # 调用函数, 类的实例化可以直接当函数用, 用的时候执行这个过程
        self.add(proc, callback, *args, **kwds)
        
    def add(self, proc, callback, *args, **kwds):
        t = self.loop.create_task(proc(self.sema, *args, **kwds))
        t.add_done_callback(callback)
        self.taskQu.put(t)
        
    def submit(self, proc, callback, *args, **kwds):
        self.add(proc, callback, *args, **kwds)
        
    def map(self, proc, callback, arg_list: list = None):
        '''arg_list 可以是元组组成的列表, 也可以是字典列表'''
        if arg_list is None: return 
        in_type_list = lambda data, type_list: sum(map(isinstance, [data], type_list))

        for arg in arg_list:
            if in_type_list(arg, [list, tuple, set]): self.add(proc, callback, *arg)
            elif in_type_list(arg, [dict]): self.add(proc, callback, **arg)
            else: self.add(proc, callback, arg)

    def wait(self):
        self.loop.run_until_complete(asyncio.wait(self.taskQu.queue))
