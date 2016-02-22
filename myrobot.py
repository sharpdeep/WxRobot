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

# msg = dict()

#文本消息
@api.textMsg
@api.sourceFilter('腾讯新闻',beside=True)
def FiltedTxtMsgHandler(message):
    if message.isBatch: #群消息
        print('-> %s(%s):%s'%(message.fromMemberName,message.fromUserName,message.content))
        return
    else:
        print('-> %s:%s'%(message.fromUserName,message.content))
    # msg[message.msgId] = message.content
    reply = robot.turing(message)
    print('[*] 自动回复：%s'%reply.content)
    return reply

#图片消息
@api.imageMsg
def ImgeMsgHandler(message):
    print('-> %s给%s发了一张图片'%(message.fromUserName,message.toUserName))
    print('[*] %s'%message.content)
    robot.open(message.image)

#位置消息
@api.location
def LocationMsgHandler(message):
    print('-> %s给你发了一个位置：[我在%s]'%(message.fromUserName,message.location))

#语音消息
@api.voiceMsg
def VoiceMsgHandler(message):
    print('-> %s给%s发了一段语音'%(message.fromUserName,message.toUserName))
    robot.open(message.voice) #打开语音消息,linux下需要安装mpg123

#小视频消息
@api.videoMsg
def VideoMsgHandler(message):
    print('-> %s给%s发了一段小视频'%(message.fromUserName,message.toUserName))
    robot.open(message.video) #打开视频消息,linux需要安装vlc

#名片消息
@api.recommend
def recommendMsgHandler(message):
    print('-> %s给%s发了一张名片'%(message.fromUserName,message.toUserName))
    print(message.recommend)

#撤回消息
@api.revoke
def revokeMsgHandler(message):
    print('-> %s向%s撤回了一条消息(%s)'%(message.fromUserName,message.toUserName,message.msgId))
    # return '%s撤回了一条消息%s'%(message.fromMemberName,msg[message.revokeMsg])

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

@robot.command('->','send text msg:send [name] [msg]')
def sendTextMsg(name,text):
    print(api.getUserId(name))
    api.sendTextMsg(name,text)


if __name__ == '__main__':
    robot.start()
