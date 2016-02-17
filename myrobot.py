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
    print('-> %s:%s'%(message.fromUserName,message.content))
    reply = robot.turing(message)
    print('[*] 自动回复：%s'%reply)
    return reply


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

@robot.command('test','test function')
def test():
    print('[*] test')

@robot.command('->','send text msg:send [name] [msg]')
def sendTextMsg(name,text):
    print(api.getUserId(name))
    api.sendTextMsg(name,text)

@robot.onSyncError
def onSyncError():
    print('[*] 查找同步线路失败')
    exit(0)

if __name__ == '__main__':
    robot.start()
