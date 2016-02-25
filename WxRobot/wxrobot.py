#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'sharpdeep'

import multiprocessing
import sys,os
import functools
import math
import time
import inspect
import ssl
import requests
import subprocess

from WxRobot.webwxapi import WebWxAPI
from WxRobot.reply import *

MAX_GROUP_NUM = 35 #每组人数
INTERFACE_CALL_INTERVAL = 60 #接口调用时间间隔

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

def catchKeyboardInterrupt(fun):
    @functools.wraps(fun)
    def wrapper(*args):
        try:
            return fun(*args)
        except KeyboardInterrupt:
            print('\n[*] 强制退出程序')

    return wrapper

class WxRobot(object):

    def __init__(self,api):
        self.DEBUG = False
        self.api = api
        self.commands = dict()
        self.addCommand('quit',self._logout,'退出微信')
        self.addCommand('help',self._print_help_msg,'显示可用命令')
        self.addCommand('delfriend',self._deleted_friends_detected,'清理好友')

    @catchKeyboardInterrupt
    def start(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        print('[*] WxRobot ... start')
        self._run('[*] 获取uuid ... ', self.api.getUUID)
        print('[*] 生成二维码 ... 成功');
        self.api.genQRCode()
        self._run('[*] 扫描二维码登陆 ... ', self.api.waitForLogin)
        self._run('[*] 在手机上确认登陆 ... ', self.api.waitForLogin, 0)
        self._run('[*] 正在登陆 ... ', self.api.login)
        self._run('[*] 初始化微信 ... ', self.api.webwxinit)
        self._run('[*] 开启状态通知 ... ', self.api.webwxstatusnotify)
        self._run('[*] 获取联系人 ... ', self.api.webwxgetcontact)
        print('[*] 共有%d位联系人' % len(self.api.ContactList))
        if self.api.DEBUG:
            print(self.api)

        self._print_help_msg()

        self.listenLoop = multiprocessing.Process(target=self.api.listenMsgLoop,
                                             args=(self._onPhoneExit, self._onMsgReceive, self._onPhoneInteract,self._onIdle,self._onSyncError))
        self.listenLoop.start()
        while True:
            commandline = input('').lower()
            if len(commandline.strip()) == 0:
                continue
            command = commandline.split()[0]
            args = commandline.split()[1:]
            responses = self.commands.get(command)

            command_exist = False
            if responses is not None:
                optional_response = []
                for response in responses:
                    argCount = response[2]
                    if len(args) >= argCount:
                        optional_response.append((response[2],response[0]))

                if len(optional_response) > 0:
                    optional_response.sort()
                    optional_response[-1][1](*args[:argCount])
                    command_exist = True


            if not command_exist:
                print('[*] 系统识别不了命令')

    def _logout(self):
        self.listenLoop.terminate()
        print('[*] 退出微信')
        exit(0)

    def _print_help_msg(self):
        msg = '=================================================\n'

        for command,responses in self.commands.items():
            for response in responses:
                argCount = response[2]
                msg = msg + command + '\t\t-->\t' + response[1] + '\n'
        msg += '================================================='

        print(msg)

    def _deleted_friends_detected(self):
        print('[*] 开始检测 ... ')

        groupCount = math.ceil(len(self.api.ContactList)/float(MAX_GROUP_NUM))
        chatroomName = ''
        totalDeletedList = []
        totalBlockList = []

        for group in range(0,groupCount):
            userNames = []
            for i in range(0,MAX_GROUP_NUM):
                if group * MAX_GROUP_NUM + i >= len(self.api.ContactList):
                    break
                member = self.api.ContactList[group * MAX_GROUP_NUM + i]
                userNames.append(member['UserName'])

            if chatroomName == '':
                state,errMsg,chatroomName,deletedList,blockedList = self.api.createChatroom(userNames)
                self._echo('[*] 新建群聊[%s] ... '%chatroomName)
                if state:
                    self._echo('成功\n')
                else:
                    self._echo('失败[%s]\n'%errMsg)
                    print('=======退出检测=========')
                    return
            else:
                state,errMsg,deletedList,blockedList = self.api.addChatroomMember(chatroomName,userNames)
                self._echo('[*] 添加第%s组成员 ... '%str(group+1))
                if state:
                    self._echo('成功\n')
                else:
                    self._echo('失败[%s]\n'%errMsg)
                    continue
            deletedCount = len(deletedList)
            blockedCount = len(blockedList)
            if deletedCount > 0:
                totalDeletedList += deletedList
            if blockedCount > 0:
                totalBlockList += blockedList

            self.api.delChatroomMember(chatroomName,userNames)

            if self.DEBUG:
                print('[*] 群聊添加以下成员：')
                for m in userNames:
                    print(self.api.getUserRemarkName(m))
            if group != groupCount - 1:
                time.sleep(INTERFACE_CALL_INTERVAL) #接口调用间隔时间

        print('=======检测结束=========')
        print('由于微信接口限制，本功能将会有30分钟的技能冷却时间')
        print('[*] 检测结果如下：')
        print('总共有%s位联系人将你删除'%(len(totalDeletedList)))
        print('总共有%s位联系人将你拉入黑名单'%(len(totalBlockList)))

        if len(totalDeletedList) > 0:
            print('[*] 以下成员将你删除')
            for m in totalDeletedList:
                print(self.api.getUserRemarkName(m))
        if len(totalBlockList) > 0:
            print('[*] 以下成员将你拉入黑名单')
            for m in totalBlockList:
                print(self.api.getUserRemarkName(m))

    def _run(self, str, func, *params):
        self._echo(str)
        ret = func(*params)
        if isinstance(ret, tuple):
            (status, msg) = ret
        else:
            (status, msg) = (ret, '')

        if status:
            self._echo('成功\n')
        else:
            self._echo(msg)
            print(msg + '\n[退出程序]')
            exit(0)

    def _echo(self, str):
        sys.stdout.write(str)
        sys.stdout.flush()

    def command(self,command,helpMsg = ''):
        def wrapper(func):
            self.addCommand(command,func,helpMsg)
            return func
        return wrapper

    def addCommand(self,command,func,helpMsg):
        args = inspect.getargspec(func).args
        argCount = len(args)
        if 'self' in args:
            argCount -= 1
        if not self.commands.get(command):
            self.commands[command] = []
        self.commands[command].append((func,helpMsg,argCount))
        # self.commands[command] = (func,helpMsg,argCount)

    def _onPhoneExit(self):
        pass

    def _onMsgReceive(self):
        pass

    def _onPhoneInteract(self):
        pass

    def _onIdle(self):
        pass

    def _onSyncError(self):
        pass

    def onMsgReceive(self,func):
        self._onMsgReceive = func
        return func

    def onPhoneExit(self,func):
        self._onPhoneExit = func
        return func

    def onPhoneInteract(self,func):
        self._onPhoneInteract = func
        return func

    def onIdle(self,func):
        self._onIdle = func
        return func

    def onSyncError(self,func):
        self._onSyncError = func
        return func

    def open(self,path):
        pattern = path[-3:]
        if sys.platform.find('win') >= 0:
            os.startfile(path)
            return
        if pattern == 'jpg':
            r = self.api._safe_open(path)
            if not r:
                print('[*] 打开失败')
        elif pattern == 'mp3':
            subprocess.call(['mpg123',path])
        elif pattern == 'mp4':
            subprocess.call(['vlc',path])
        else:
            raise ValueError('the file format is wrong')

    def active_turing(self,turing_key = ''):
        self.turing_key = turing_key

    def active_simsimi(self,simsimi_key = ''):
        self.simsimi_key = simsimi_key

    #http://developer.simsimi.com/
    def simsimi(self,message): #只有免费7天,不推荐
        if message.type != 'text':
           raise ValueError('auto reply request text message')
        text = message.content
        key = self.simsimi_key
        url = url = 'http://sandbox.api.simsimi.com/request.p?key=%s&lc=ch&ft=0.0&text=%s' % (key, text)
        response = requests.get(url)
        data = response.json()
        reply = data['response'] if data['result'] else '你说什么，风太大了听不清！'
        return '[simsimi回复]'+reply

    #http://www.tuling123.com/
    def turing(self,message):
        if message.type != 'text':
           raise ValueError('auto reply request text message')
        text = message.content
        userid = message.fromUserId
        key = self.turing_key
        url = 'http://www.tuling123.com/openapi/api?key=%s&info=%s&userid=%s'%(key,text,userid)
        response = requests.get(url)
        data = response.json()
        code = data['code']
        prefix = '[图灵机器人回复]'
        if code == 100000: #文本回复
            return TextReply(prefix + data['text'])
        elif code == 200000: #链接回复
            return TextReply(prefix + data['text'] + ',点击查看:' + data['url'])
        elif code == 302000: #新闻回复
            pass
        elif code == 308000: #菜谱回复
            pass
        elif code == 40001: #key错误
            pass
        elif code == 40002: #info为空
            pass
        elif code == 40004: #当天请求次数已使用完
            pass
        elif code == 40007: #数据格式异常
            pass
        else:
            return TextReply(prefix + '你说什么，风太大了听不清')
        return TextReply(prefix + data['text'])


