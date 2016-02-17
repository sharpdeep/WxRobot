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
        self.__dict__.update(message)

@handle_for_type('text')
class TextMessage(WeChatMessage):
    def __init__(self,message):
        self.content = message.pop('Content','')
        super(TextMessage,self).__init__(message)

@handle_for_type('location')
class LocationMessage(WeChatMessage):
    def __init__(self,message):
        super(LocationMessage,self).__init__(message)



@handle_for_type('image')
class ImageMessage(WeChatMessage):
    def __init__(self,message):
        super(ImageMessage,self).__init__(message)


@handle_for_type('audio')
class AudioMessage(WeChatMessage):
    def __init__(self,message):
        super(AudioMessage,self).__init__(message)

@handle_for_type('video')
class VideoMessage(WeChatMessage):
    def __init__(self,message):
        super(VideoMessage,self).__init__(message)

@handle_for_type('sharelocation')
class ShareLocationMessage(WeChatMessage):
    def __init__(self,message):
        super(ShareLocationMessage,self).__init__(message)

@handle_for_type('initmsg')
class InitMessage(WeChatMessage):
    def __init__(self,message):
        self.location = message.pop('location','')
        super(InitMessage,self).__init__(message)

class UnKnownMessage(WeChatMessage):
    def __init__(self,message):
        self.type = 'unkonwn'
        super(UnKnownMessage,self).__init__(message)
