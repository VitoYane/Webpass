import os, chardet
from fire import Fire
from loguru import logger
def change_dir_txt_code(root_dir, code):
    for root, dirs, files in os.walk(root_dir):

        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for f in files:
            if os.path.splitext(f)[1] in ['.txt']:
                change_code(os.path.join(root, f), code)

        # 遍历所有的文件夹
        for d in dirs:
            change_dir_txt_code(os.path.join(root, d))

def strJudgeCode(str):
    return chardet.detect(str)

def readFile(path):
    try:
        f = open(path, 'rb')
        filecontent = f.read()
    finally:
        if f:f.close()
    return filecontent

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


def get_err_msg(pl = False ,_interval = ' -> '):
    '''pl=true 打印局部变量环境'''
    from sys import _getframe, exc_info
    call_str = ''; lcs = ''; _frame = _getframe()
    while _frame:
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
        _frame = _frame.f_back
    return f"\n{call_str[:-len(_interval)]}: {exc_info()[1]} {exc_info()[0]}\n{lcs}\n{'-' * 79}\n\n" if pl else f"{call_str[:-len(_interval) - 1]}{_interval}{exc_info()[0]} : {exc_info()[1]}"

def change_code(path, code):
    file_con = readFile(path)
    result = strJudgeCode(file_con)
    if result['encoding'] not in [None, 'ascii']:
        content_uni = file_con.decode(result['encoding'])
        content_to = content_uni.encode(code)
        write_file(path, content_to, 'wb', encoding=code)
        if result['encoding'] != 'ascii': logger.info(f"完成格式处理:{result['encoding']} -> {code} : {path}")


def main(root_dir = '.', code='utf-8'):
    change_dir_txt_code(root_dir, code)

if __name__ == '__main__':
    Fire(main)