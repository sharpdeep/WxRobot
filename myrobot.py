#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: sharpdeep
@file:myrobot.py
@time: 2016-02-15 14:49
"""

import sys
from WxRobot.wxrobot import WxRobot
from WxRobot.webwxapi import WebWxAPI

api = WebWxAPI()
robot = WxRobot(api)

@api.textMsg
@api.sourceFilter('腾讯新闻',beside=True)
def FiltedTxtMsgHandler(message):
    print('%s给%s发送了一个消息'%(message.fromUserName,message.toUserName))
    print('-> %s:%s'%(message.fromUserName,message.content))


@api.location
def LocationMsgHandler(message):
    print('%s给你发了一个位置：[我在%s]'%(message.fromUserName,message.location))

@robot.onPhoneExit
def onPhoneExit():
    print('[*] 你在手机上登出了微信，再见')
    exit(0)

interactCount = 0

@robot.onPhoneInteract
def onPhoneInteract():
    global interactCount
    interactCount += 1
    print('[*] 你在手机上玩了%d次微信被我发现了'%interactCount)

@robot.onMsgReceive
def onMsgReceive():
    pass


@robot.onSyncError
def onSyncError():
    print('[*] 查找同步线路失败')
    exit(0)

# windows下编码问题修复
# http://blog.csdn.net/heyuxuanzee/article/details/8442718


class UnicodeStreamFilter:

    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding

    def write(self, s):
        s.encode(self.encode_to,self.errors).decode(self.encode_to)
        self.target.write(s)

    def flush(self):
        self.target.flush()

if sys.stdout.encoding == 'cp936':
    sys.stdout = UnicodeStreamFilter(sys.stdout)

if __name__ == '__main__':
    robot.start()
