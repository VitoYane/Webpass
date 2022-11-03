# -*- coding:utf-8 -*-

import sys
import json

# 解析结果格式
result = {
    "report":"",        # 解析报告,用于web页面展示
    "parm": {},         # 参数,可供任务中后面的工具使用
    "priority": 0       # 优先级0-9,值越大,优先级越高。如果解析有重大发现,可以酌情提高优先级。
}


def main():
    with open(input_file, "r") as rf:
        # 在此处添加代码,解析工具执行结果,补充上面"result"中的内容。
        result['report'] = rf.read()
    return result


if __name__ == '__main__':
    # 工具执行结果文件作为输入
    input_file = sys.argv[1]
    # 用于解析结果写入
    output_file = sys.argv[2]
    main()
    with open(output_file, "w") as wf:
        wf.write(json.dumps(result))

 