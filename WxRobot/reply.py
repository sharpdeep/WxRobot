#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: sharpdeep
@file:reply.py
@time: 2016-02-17 21:47
"""
REPLY_TYPES = {}

def handle_for_reply_type(type):
	def register(cls):
		cls.type = type
		REPLY_TYPES[type] = cls
		return cls
	return register

class WeChatReply(object):
	def __init__(self):
		pass

@handle_for_reply_type('text')
class TextReply(WeChatReply):
	def __init__(self,reply):
		self.content = reply
		super(TextReply,self).__init__()

@handle_for_reply_type('unknown')
class UnkonwnReply(WeChatReply):
	def __init__(self):
		super(UnkonwnReply,self).__init__()


