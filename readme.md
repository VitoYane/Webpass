<a name="u428o"></a>
### 场景说明
账号密码是信息安全的第一道屏障, 在攻防中, 弱密码拥有与高危漏洞同样的重视程度, 除了传统协议(ftp, mysql, ssh等) 的弱密码检测外, http(s) 层面的关键系统越来越多, 例如VPN系统、 SDP系统等，如果能快速对http(s)业务系统的弱密码进行探测, 相当于多了一条渗透路径.

但是http(s) 层面有**验证码**、**密码加密**等灵活的防御机制, 且经常配置**错误次数限制**，一个账号短时间错误次数太多, 直接禁止登陆. 这种情况下, 万能的burpsuite也显得有些无力.

Webpass工具通过**驱动浏览器**，模拟真实登录场景，形成通用的弱密码检测系统，可以支持http(s) 协议的web登录弱密码检测，也支持针对不同的网络设备定制不同的字典，从而更容易检测到弱密码；
<a name="aFb2W"></a>
### 有哪些解决的问题
<a name="YzJNE"></a>
#### 密码加密传输
![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411514381-e4f3d1bb-79e2-4c96-91f8-0715111ae8d7.png#averageHue=%23eaeae5&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=uac2e9d81&margin=%5Bobject%20Object%5D&originHeight=719&originWidth=984&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u3f23e51b-1ba1-4715-8de6-4e022d6bb5a&title=)<br />填写表单后, 页面代码对填写内容进行加密, 加密后发送到服务器后台, 如图看起来像base64实际上不是, 那么就因为不知道他怎么加密的, 从而无法直接发包爆破.<br />这种情况可以**驱动浏览器**来进行爆破, 让系统自己的代码进行加密转化, 最为简单直接通用.

```python
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
```

上述代码会打开指定数量的页面, 自动填写配置好的用户名密码, 效果图如下:<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411556504-c896d4df-70b3-4fb2-9367-5df3dc4013fb.png#averageHue=%23ebeef1&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u97d93259&margin=%5Bobject%20Object%5D&originHeight=808&originWidth=1296&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u69867a65-9d86-443b-a107-65033893daf&title=)
<a name="zyZLT"></a>
#### 验证码和Token验证
![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411556439-ec191578-fe05-4c19-90d9-fe87c3cfc3d9.png#averageHue=%2395b1ca&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u0a162bf6&margin=%5Bobject%20Object%5D&originHeight=327&originWidth=442&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=ud38feabe-4b94-4566-a3ec-9b80ee70ba4&title=)<br />验证码是很常见的, 当然单纯的验证码, 发包模式也可以解决. 但是有的时候, 页面会带有隐藏表单, 进行token提交, 服务器会对token进行验证.<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411556616-9ea50d3b-2f24-4b35-9dc2-8cf8672759bb.png#averageHue=%23e4e0d4&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=uedbab56c&margin=%5Bobject%20Object%5D&originHeight=151&originWidth=1068&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u80149fae-dbdc-40ed-b43b-0eb6615732a&title=)<br />对于token验证不符合的请求, 直接丢弃, 这个类似于密码加密传输, 不知道生成算法, 直接发包也扑街.
<a name="xL2lq"></a>
#### 错误次数限制
![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411556540-42d1849f-0080-4efa-84da-f5052451399f.png#averageHue=%23dce1e4&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u6162dc55&margin=%5Bobject%20Object%5D&originHeight=397&originWidth=844&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u55c41635-e23b-4e62-af78-7d449869307&title=)<br />这种情况也很常见, 当然发包的方式也可以解决这个问题, 本程序主要是密码优先, 枚举用户.
```python
username_list = await aread_file(glob.cfg.pass_dict[key]['user_info'][1])
password_list = await aread_file(glob.cfg.pass_dict[key]['pass_info'][1])

user_pass = [[username_list[i], password_list[i]] for i in range(min(len(username_list), len(password_list)))]  # 先写一一对应的

for _pass in password_list:     # 再添加剩余的, 密码枚举用户
    for _user in username_list:
        if [_user, _pass] not in user_pass:
            user_pass.append([_user, _pass])
```

单个目标枚举3次之后, 测试下一个目标, 这个目标切换为等待状态:<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411590492-86adf73e-20f0-42fd-b211-86c4c56574fb.png#averageHue=%2312171c&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u5973759f&margin=%5Bobject%20Object%5D&originHeight=185&originWidth=1321&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u218197fb-497a-4046-a29e-409c02c2fb3&title=)<br />另外, webpass最初想法是爆破一些常见的网络设备, 这样常见网络设备的默认密码自然是最高优先级, 比通用弱密码更优先, 上述代码也有体现. 在配置中, 可以配置每类产品独立的字典:<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411590441-492c1f62-77b0-45b5-add0-7eb0906065a3.png#averageHue=%23262220&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=uf964ce2a&margin=%5Bobject%20Object%5D&originHeight=664&originWidth=964&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=ua13a621f-81b8-469e-a43a-f89796e29dc&title=)<br />代码配置如上图, 字典文件如下图:<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411590423-0aa43a4a-d71e-4035-abbe-55cbdac06031.png#averageHue=%23faf8f6&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u52ca7a3e&margin=%5Bobject%20Object%5D&originHeight=646&originWidth=643&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=ub27c3b93-2346-463a-a775-893c9179fd1&title=)
<a name="c8VIi"></a>
#### 用户名密码表单名灵活多变
![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411590499-caadf607-4d68-4d2e-b6d6-2876950ed3da.png#averageHue=%23fcfaf9&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u0360d0e5&margin=%5Bobject%20Object%5D&originHeight=305&originWidth=618&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u72c61368-5509-43b7-a446-55708b9c280&title=)<br />Web页面的用户名密码表单, 一般习惯是写username, password但是也有很多情况不是这两个名称, 那么在程序填写用户名密码时, 往往也需要配置或者智能识别, 目前考虑的方案是:

1. 列举出所有的input, 类型为password的肯定是password
2. 计算表单name与user关键字的相似度, 超过一定值考虑为username字段
3. 计算表单name与pass关键字的相似度, 超过一定值考虑为password字段
4. 补充一些用户配置字典.

对于未识别的系统, 可以使用通用字典来进行自动化爆破
<a name="FYEvq"></a>
#### 多目标批量
单个web目标的爆破, burpsuite很灵活有效, 但是多个目标, 就比较麻烦了. 新出的国产挑战者Yakit可以支持, 但是在请求次数过多也会程序卡死<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411590787-2d6cb91f-dcd1-4893-95ca-2fe246b83bdb.png#averageHue=%23e7e8e4&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=ub95b8139&margin=%5Bobject%20Object%5D&originHeight=284&originWidth=655&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u16d30c49-e4de-4e55-a898-75e2a3e8989&title=)<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411591076-5b7f6087-00c7-42be-8c1c-ca41ed7ec6c6.png#averageHue=%23fdfbfa&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u861baaff&margin=%5Bobject%20Object%5D&originHeight=598&originWidth=957&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=uf66f37b6-19e1-4a74-bae8-4271164e00a&title=)<br />实测最新版本8k个请求也会让UI卡死, 可能需要继续等待官方修复.<br />自己来写程序实现驱动浏览器进行弱密码爆破, 就能解决这个问题:<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411591288-0991a120-0ce9-4803-a687-994a04e22dd4.png#averageHue=%23133368&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u19e45347&margin=%5Bobject%20Object%5D&originHeight=599&originWidth=1049&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=uc13a5f40-3bd1-41e3-895b-34f8cbec629&title=)<br />可以在文件中一行一个目标, 自动识别系统, 调用指定的字典, 未识别的使用通用字典
<a name="yGdV4"></a>
### 使用方法
```python
INFO: Showing help with the command 'webpass_call.py -- --help'.

NAME
    webpass_call.py - -u: url -f: file -g: 配置模式 -w: 单目标等待时间, 分钟 -j: 只探测识别到的目标

SYNOPSIS
    webpass_call.py <flags>

DESCRIPTION
    -u: url -f: file -g: 配置模式 -w: 单目标等待时间, 分钟 -j: 只探测识别到的目标

FLAGS
    --u=U
        Default: ''
    --f=F
        Default: ''
    --debug=DEBUG
        Default: False
    --gen=GEN
        Default: False
    --wait=WAIT
        Default: 3
    --process=PROCESS
        Default: 8
    --just_discern=JUST_DISCERN
        Default: True
```

```python
python webpass_call.py -u http://1.2.3.4 
python webpass_call.py -f /etc/target.txt python webpass_call.py -u http://1.2.3.4 -f /etc/target.txt
python webpass_call.py -g http://baidu.com
```
<a name="OIdgp"></a>
#### 基本用法
-u <url> : 探测单个或者多个目标弱密码, 含有url的字符串即可, 会自动解析url<br />-f <file> : 探测文件中所有的url, 带有url的文件即可, 会自动解析url<br />上述两个开关可以都配置, 目标相加<br />注意: url需要带入协议类型如http, https等, 如果不带, 可能导致url无法识别.
<a name="ZhFUz"></a>
#### 配置模式
当然, 在实际使用中, 默认密码的情况比较多见, 所以尽量还是经过配置后使用, 而不是直接通用字典.<br />-g <url> : 配置模式, 默认以webkit浏览器打开<br />![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411624671-5c02dfcd-4966-48f6-a314-1ac7e05be812.png#averageHue=%23faf7f7&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u220cb886&margin=%5Bobject%20Object%5D&originHeight=583&originWidth=1674&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=ub352e8f7-63c5-4f2f-a947-b3d46aaf26b&title=)<br />比较方便于生成配置.
<a name="KR6FH"></a>
#### 其他开关
-w <mins> : 配置单目标等待时长, 默认单目标尝试3次后等待3分钟<br />-p <process> : 浏览器最大页面数, 即理解成多少个线程, 实际上是协程的程序<br />-j <True>: 配置True则只爆破已识别的目标, 不进行通用爆破, 是just_discern的首字母<br />-d <True>: 调试开关, 配置为True, 多很多步骤打印, 浏览器也会显示出来
<a name="VUXlp"></a>
#### 配置文件说明
![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411624617-22fefba0-0303-4354-b948-d428c1807892.png#averageHue=%23272321&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u12ca7e8f&margin=%5Bobject%20Object%5D&originHeight=204&originWidth=591&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u396e217c-9b68-428d-9e1a-39515657119&title=)<br />配置文件基本结构如上图, 是一个大字典, 每类产品一个小字典, 字典内部是key:list结构.
> -  keywords：列表类型，识别产品的关键词，各个关键词之间与关系，即登录页html中某些关键词，支持base64编码；留空则直接用“key”作为关键词判断，如果没有找到则归为未识别 
> -  user_info：是包含username 字段名和字典目录的列表，pass_info类似 
> -  button：按钮名称，列表类型，一般用webpass_call.py -g url 获取按钮名称 
> -  CAPTCHA: 长度一般为2，位置0位填充，位置1为截图，如果长度为0，则代表没有验证码 
> -  suc：登录成功后html中内容关键字，支持base64，根据logic计算整体真假 
> -  fail：登录失败后html中内容关键字，支持base64，根据logic计算整体真假 
> 
> 考虑到配置的便捷性，可以使用-g参数激活浏览器自动获取关键字段，便于填写, 如果suc, fail都为空, 则直接根据登陆前后页面相似度进行正确性判断


<a name="u42h1"></a>
#### 安装
STEP1. 官方网站下载Python3.7+环境。

- [python.org](https://python.org)

STEP2. 安装调用库PlayWright，Fire，loguru 等

- pip install playwright ddddocr fire loguru chardet aiofiles
- python -m playwright install 

可能有一些未列举的, 后续提供requirements.txt<br />装完库就可以运行.
<a name="HmOey"></a>
### 代码结构
代码主要使用Python3, 尽量使用Python3.9及以上的版本
<a name="Um6QI"></a>
#### 文件结构

- 0-errlog.txt # 报错信息
- 1-unknown_devices.txt # 未知设备
- 2-success.txt # 成功的目标
- 3-fail.txt # 失败的目标
- 4-check.txt # 需要检查的目标
- webpass_call.py # 主程序
- webpass_config.py # 主配置
- webpass_func.py # 功能库
- webpass_report.py # 上报ES, 未完成
<a name="HMdct"></a>
#### 整体结构
![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411729128-f7871ffa-39e3-4139-8bea-c7eaae64985a.png#averageHue=%23c7c6c6&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u4056f570&margin=%5Bobject%20Object%5D&originHeight=575&originWidth=1098&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u11400b4d-34f0-4b24-b4ef-8d5db0aa980&title=)
<a name="Gddrk"></a>
#### target_dict数据结构
```python
{
    'target_dict':{
        'http://1.2.2.2':{
            'status':'init',
            'title':'',
            'content':'',
            'key':'下一代防火墙',
            'last_time':datetime 对象,
            'user_pass':aQueue,
        }
    }
}
```

<a name="dljCC"></a>
#### status状态

- init
- identify, unknown, timeout
- tasking, wait
- done, success

![](https://cdn.nlark.com/yuque/0/2022/png/21920707/1668411786958-09a176e8-6b98-4f45-ab74-326c035994b2.png#averageHue=%234c4c4c&clientId=u321fd47d-676b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u085f62fb&margin=%5Bobject%20Object%5D&originHeight=378&originWidth=1076&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u4069d1c4-374c-4551-9085-1fa7ecbf96c&title=)
<a name="Wc9X8"></a>
### 后续计划
<a name="R5WN0"></a>
#### 计划

- go开发实现, 便于编译成exe在目标内网执行
- 支持通用爆破
- 减少配置量, 例如通过已有指纹库识别资产, 结合通用爆破调用指定字典
<a name="y0FaM"></a>
#### 已实现

- 文档上述内容, 除了计划之外, 均已实现
