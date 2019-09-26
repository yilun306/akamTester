#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/7/19 16:52
# @Author  : Miyouzi
# @File    : akamTester.py
# @Software: PyCharm

from pythonping import ping
from ColorPrinter import color_print
from GlobalDNS import GlobalDNS
import sys, os
import numpy as np


working_dir = os.path.dirname(os.path.realpath(__file__))
# working_dir = os.path.dirname(sys.executable)  # 使用 pyinstaller 编译时，打开此项
ip_list_path = os.path.join(working_dir, 'ip_list.npy')


def ping_test(ip):
    result = ping(ip, count=5)
    delay = result.rtt_avg_ms
    msg = ip + '  平均延迟:   ' + str(delay) + ' ms'
    if delay<100:
        color_print(msg, status=2)
    else:
        color_print(msg)
    return delay


try:
    akam = GlobalDNS('upos-hz-mirrorakam.akamaized.net')
    color_print('第一次解析:')
    ip_list = akam.get_ip_list()
    print()
    color_print('第二次解析:')
    akam.renew()
    ip_list = ip_list | akam.get_ip_list()
    print()
    color_print('第三次解析:')
    akam.renew()
    ip_list = ip_list | akam.get_ip_list()
except BaseException as e:
    color_print('进行全球解析时遇到未知错误: '+str(e), status=1)
    if os.path.exists(ip_list_path):
        color_print('将读取本地保存的ip列表', status=1)
        ip_list = np.load(ip_list_path, allow_pickle=True)
        ip_list = ip_list.tolist()
    else:
        color_print('没有本地保存的ip列表！程序终止！', status=1)
        print()
        input('按回车退出')
        sys.exit(0)
else:
    # 保存解析结果
    np.save(ip_list_path, np.array(ip_list))

print()
color_print('共取得 '+str(len(ip_list))+' 个 IP, 开始测试延迟')
print()

ip_info = []
good_ips = []

for ip in ip_list:
    delay = ping_test(ip)
    ip_info.append({'ip': ip, 'delay': delay})
    if delay < 100:
        good_ips.append({'ip': ip, 'delay': delay})
print()

if len(good_ips) > 0:
    color_print('基于当前网络环境, 以下为延迟低于100ms的IP', status=2)
    good_ips.sort(key=lambda x:x['delay'])
    for ip in good_ips:
        color_print(ip['ip'] + '  平均延迟:   ' + str(ip['delay']) + ' ms', status=2)
else:
    ip_info.sort(key=lambda x:x['delay'])
    color_print('本次测试未能找到延迟低于100ms的IP! 以下为延迟最低的 3 个节点', status=1)
    for i in range(0,3):
        color_print(ip_info[i]['ip'] + '  平均延迟:   ' + str(ip_info[i]['delay']) + ' ms')

print()
input('按回车退出')
sys.exit(0)