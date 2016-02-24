#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: sharpdeep
@file:message.py
@time: 2016-02-13 15:53
"""

MESSAGE_TYPES = {}

def handle_for_type(type):
    def register(cls):
        MESSAGE_TYPES[type] = cls
        cls.type = type
        return cls
    return register

class WeChatMessage(object):
    def __init__(self,message):
        self.fromUserName = message.pop('FromUserName',None)
        self.toUserName = message.pop('ToUserName',None)
        self.fromUserId = message.pop('FromUserId',None)
        self.toUserId = message.pop('ToUserId',None)
        self.msgId = message.pop('MsgId',0)
        self.createTime = message.pop('CreateTime',0)
        self.content = message.pop('Content','')
        self.__dict__.update(message)
        self.isBatch = False
        if self.fromUserId[:2] == '@@':
            self.isBatch = True
            self.fromMemberId = message.pop('FromMemberId',None)
            self.fromMemberName = message.pop('FromMemberName',None)

@handle_for_type('text')
class TextMessage(WeChatMessage):
    def __init__(self,api,message):
        super(TextMessage,self).__init__(message)

@handle_for_type('location')
class LocationMessage(WeChatMessage):
    def __init__(self,api,message):
        super(LocationMessage,self).__init__(message)


@handle_for_type('image')
class ImageMessage(WeChatMessage):
    def __init__(self,api,message):
        self.image = api.webwxgetmsgimg(message['MsgId'])
        super(ImageMessage,self).__init__(message)


@handle_for_type('voice')
class VoiceMessage(WeChatMessage):
    def __init__(self,api,message):
        self.voice = api.webwxgetmsgvoice(message['MsgId'])
        super(VoiceMessage,self).__init__(message)

@handle_for_type('video')
class VideoMessage(WeChatMessage):
    def __init__(self,api,message):
        self.video = api.webwxgetmsgvideo(message['MsgId'])
        super(VideoMessage,self).__init__(message)

@handle_for_type('sharelocation')
class ShareLocationMessage(WeChatMessage):
    def __init__(self,api,message):
        super(ShareLocationMessage,self).__init__(message)

@handle_for_type('recommend')
class RecommendMessage(WeChatMessage):
    def __init__(self,api,message):
        info = message['RecommendInfo']
        self.recommend =    '=============================\n' + \
                            '昵称  : %s \n'%info['NickName'] + \
                            '微信号: %s \n'%info['Alias'] + \
                            '地区  : %s %s \n'%(info['Province'], info['City']) + \
                            '性别  : %s \n'%['未知','男','女'][info['Sex']] + \
                            '=============================\n'
        super(RecommendMessage,self).__init__(message)

@handle_for_type('revoke')
class RevokeMessage(WeChatMessage):
    def __init__(self,api,message):
        self.revokeMsgId = api._searchContent('msgid',message['Content'],fmat='xml')
        super(RevokeMessage,self).__init__(message)


@handle_for_type('initmsg')
class InitMessage(WeChatMessage):
    def __init__(self,api,message):
        super(InitMessage,self).__init__(message)

class UnKnownMessage(WeChatMessage):
    def __init__(self,api,message):
        self.type = 'unkonwn'
        super(UnKnownMessage,self).__init__(message)
