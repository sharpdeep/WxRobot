#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: sharpdeep
@file:webwxapi.py
@time: 2016-02-13 15:47
"""
import inspect
import time
import re
import json
import random,sys,os
import subprocess
import qrcode
from bs4 import BeautifulSoup
from urllib import request, parse
from http.cookiejar import CookieJar
from WxRobot.message import MESSAGE_TYPES, UnKnownMessage
from WxRobot.reply import WeChatReply,TextReply

QRCODE_PATH = os.path.join(os.getcwd(), 'qrcode.jpg')

class WebWxAPI(object):
    message_types_dict = {
        1: 'text',  # 文本消息
        3: 'image',  # 图片消息
        34: 'voice',  # 语音消息
        42: 'recommend', #名片
        48: 'sharelocation',  # 位置共享
        51: 'initmsg',  # 微信初始化消息
        62: 'video',  # 小视频
        10002: 'revoke', #撤回消息
    }

    message_types = message_types_dict.values()

    def __str__(self):
        description = \
            "=========================\n" + \
            "[#] Web Weixin\n" + \
            "[#] Debug Mode: " + str(self.DEBUG) + "\n" + \
            "[#] Uuid: " + self.uuid + "\n" + \
            "[#] Uin: " + str(self.uin) + "\n" + \
            "[#] Sid: " + self.sid + "\n" + \
            "[#] Skey: " + self.skey + "\n" + \
            "[#] DeviceId: " + self.deviceId + "\n" + \
            "[#] PassTicket: " + self.pass_ticket + "\n" + \
            "========================="
        return description

    def __init__(self):
        self.DEBUG = False
        self.appid = 'wx782c26e4c19acffb'
        self.uuid = ''
        self.base_uri = ''
        self.redirect_uri = ''
        self.uin = ''
        self.sid = ''
        self.skey = ''
        self.pass_ticket = ''
        self.deviceId = 'e' + repr(random.random())[2:17]
        self.BaseRequest = {}
        self.synckey = ''
        self.SyncKey = []
        self.User = []
        self.MemberList = []
        self.ContactList = []
        self.GroupList = []
        self.autoReplyMode = False
        self.syncHost = ''

        self._handlers = dict((k, []) for k in self.message_types)
        self._handlers['location'] = []
        self._handlers['all'] = []

        self._filters = dict()

        opener = request.build_opener(request.HTTPCookieProcessor(CookieJar()))
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'),
                             ('Referer','https://wx2.qq.com/')]
        request.install_opener(opener)

    def getUUID(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid': self.appid,
            'fun': 'new',
            'lang': 'zh_CN',
            '_': int(time.time()),
        }
        data = self._post(url, params, False)
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        result = re.search(regx, data)
        if result:
            code = result.group(1)
            self.uuid = result.group(2)
            return code == '200'
        return False

    def genQRCode(self):
        if sys.platform.find('win') >= 0:
            self._genQRCodeImg()
            self._safe_open(QRCODE_PATH)
        else:
            mat = self._str2QRMat('https://login.weixin.qq.com/l/' + self.uuid)
            self._printQR(mat)

    def waitForLogin(self, tip=1):
        data = self._get('https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (
            tip, self.uuid, int(time.time())))
        result = re.search(r'window.code=(\d+);', data)
        code = result.group(1)

        if code == '201':  # 扫描成功
            return True
        elif code == '200':  # 登陆成功
            result = re.search(r'window.redirect_uri="(\S+?)";', data)
            r_uri = result.group(1) + '&fun=new'
            self.redirect_uri = r_uri
            self.base_uri = r_uri[:r_uri.rfind('/')]
            return True
        elif code == '408':  # 登陆超时
            return False, '登陆超时'
        else:  # 登陆异常
            return False, '登陆异常'

    def login(self):
        data = self._get(self.redirect_uri)
        soup = BeautifulSoup(data, "html.parser")

        self.skey = soup.skey.text
        self.sid = soup.wxsid.text
        self.uin = soup.wxuin.text
        self.pass_ticket = soup.pass_ticket.text

        if '' in (self.skey, self.sid, self.uin, self.pass_ticket):
            return False

        self.BaseRequest = {
            'Uin': int(self.uin),
            'Sid': self.sid,
            'Skey': self.skey,
            'DeviceID': self.deviceId,
        }
        return True

    def webwxinit(self):
        url = self.base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (self.pass_ticket, self.skey, int(time.time()))
        params = {
            'BaseRequest': self.BaseRequest
        }
        dic = self._post(url, params)
        self.SyncKey = dic['SyncKey']
        self.User = dic['User']
        # synckey for synccheck
        self.synckey = '|'.join([str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List']])
        return dic['BaseResponse']['Ret'] == 0

    def webwxstatusnotify(self):
        url = self.base_uri + '/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % (self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Code": 3,
            "FromUserName": self.User['UserName'],
            "ToUserName": self.User['UserName'],
            "ClientMsgId": int(time.time())
        }
        dic = self._post(url, params)

        return dic['BaseResponse']['Ret'] == 0

    def webwxgetcontact(self):
        url = self.base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))
        dic = self._post(url, {})
        self.MemberList = dic['MemberList']

        ContactList = self.MemberList[:]

        for i in range(len(ContactList) - 1, -1, -1):
            Contact = ContactList[i]
            if Contact['VerifyFlag'] & 8 != 0:  # 公众号/服务号
                ContactList.remove(Contact)
            elif Contact['UserName'] in specialUsers:  # 特殊账号
                ContactList.remove(Contact)
            elif Contact['UserName'].find('@@') != -1:  # 群聊
                self.GroupList.append(Contact)
                ContactList.remove(Contact)
            elif Contact['UserName'] == self.User['UserName']:  # 自己
                ContactList.remove(Contact)
        self.ContactList = ContactList

        return True

    def webwxgetbatchcontact(self,groupid):
        if groupid[:2] != '@@':
            return None
        url = self.base_uri + '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (int(time.time()), self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Count": len(self.GroupList),
            "List": [{"UserName": groupid, "EncryChatRoomId": ""}]
        }
        dic = self._post(url, params)
        group = dic['ContactList'][0]
        # 群联系人(todo)
        return group

    def webwxsendtextmsg(self,text,to = 'filehelper'):
        url = self.base_uri + '/webwxsendmsg?pass_ticket=%s' % (self.pass_ticket)
        clientMsgId = str(int(time.time()*1000)) + str(random.random())[:5].replace('.','')
        params = {
            'BaseRequest': self.BaseRequest,
            'Msg': {
                "Type": 1,
                "Content": text,
                "FromUserName": self.User['UserName'],
                "ToUserName": to,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        # headers = {'content-type': 'application/json; charset=UTF-8'}
        # data = json.dumps(params, ensure_ascii=False).encode('utf8')
        # r = requests.post(url, data = data, headers = headers)
        # dic = r.json()
        # return dic['BaseResponse']['Ret'] == 0
        dic = self._post(url,params)
        return dic['BaseResponse']['Ret'] == 0

    def webwxgeticon(self,id):
        url = self.base_uri + '/webwxgeticon?username=%s&skey=%s' % (id, self.skey)
        data = self._get(url,byte_ret=True)
        icon_path = os.path.join(os.getcwd(),'icon_'+id+'.jpg')
        with open(icon_path,'wb') as f:
            f.write(data)
        return icon_path

    def webwxgetheading(self,id):
        url = self.base_uri + '/webwxgetheadimg?username=%s&skey=%s' % (id, self.skey)
        data = self._get(url,byte_ret=True)
        head_path = os.path.join(os.getcwd(),'head_'+id+'.jpg')
        with open(head_path,'wb') as f:
            f.write(data)
        return head_path

    def webwxgetmsgimg(self,msgid):
        url = self.base_uri + '/webwxgetmsgimg?MsgID=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url,byte_ret=True)
        return self._save_file(data,'msgimg_' + msgid + '.jpg')


    def webwxgetmsgvideo(self,msgid):
        url = self.base_uri + '/webwxgetvideo?msgid=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url,byte_ret=True)
        return self._save_file(data,'msgvideo_'+msgid+'.mp4')


    def webwxgetmsgvoice(self,msgid):
        url = self.base_uri + '/webwxgetvoice?msgid=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url,byte_ret=True)
        return self._save_file(data,'msgvoice_'+msgid+'.mp3')


    def testsynccheck(self):
        syncHost = [
            'webpush.weixin.qq.com',
            'webpush1.weixin.qq.com',
            'webpush2.weixin.qq.com',
            'webpush.wechat.com',
            'webpush1.wechat.com',
            'webpush2.wechat.com',
            'webpush1.wechatapp.com',
        ]
        for host in syncHost:
            self.syncHost = host
            [retcode, selector] = self.synccheck()
            if self.DEBUG:
                print('[*] test',host,'->',retcode)
            if retcode == '0': return True
        return False

    def synccheck(self):
        params = {
            'r': int(time.time()),
            'sid': self.sid,
            'uin': self.uin,
            'skey': self.skey,
            'deviceid': self.deviceId,
            'synckey': self.synckey,
            '_': int(time.time()),
        }
        url = 'https://' + self.syncHost + '/cgi-bin/mmwebwx-bin/synccheck?' + parse.urlencode(params)
        data = self._get(url)
        pm = re.search(r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', data)
        retcode = pm.group(1)
        selector = pm.group(2)
        return [retcode, selector]

    def webwxsync(self):
        url = self.base_uri + '/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (self.sid, self.skey, self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            'SyncKey': self.SyncKey,
            'rr': ~int(time.time())
        }
        dic = self._post(url, params)
        if self.DEBUG:
            print(json.dumps(dic, indent=4))

        if dic['BaseResponse']['Ret'] == 0:
            self.SyncKey = dic['SyncKey']
            self.synckey = '|'.join([str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List']])
        return dic

    def sendTextMsg(self,name,text,isfile = False):
        id = self.getUserId(name)
        if id:
            if self.webwxsendtextmsg(text,id):
                return True,None
            else:
                return False,'api调用失败'
        else:
            return False,'用户不存在'




    def listenMsgLoop(self, onExit, onMsgReceive, onPhoneInteract,onIdle,onSyncError):
        # 测试同步线路
        if not self.testsynccheck():
            onSyncError()
        while True:
            [retcode, selector] = self.synccheck()
            if retcode == '1100':
                onExit()
                break
            elif retcode == '0':
                if selector == '2':
                    onMsgReceive()
                    syncRet = self.webwxsync()
                    if syncRet is not None:
                        self.handleMsg(syncRet)
                elif selector == '7':
                    onPhoneInteract()
                elif selector == '0':
                    onIdle()
                    time.sleep(1)

    def handleMsg(self, syncret):
        for msg in syncret['AddMsgList']:
            message = self._process_message(msg)
            handlers = self.get_handler(message.type)
            for handler, args_count in handlers:
                #filte message
                filters = self.get_filter(handler)
                is_match = self._filte(message,*filters)
                if not is_match:
                    continue
                args = [message, ][:args_count]
                reply = handler(*args)
                if reply:
                    self._process_reply(reply,message)


    def getUserRemarkName(self, id):
        name = '未知群' if id[:2] == '@@' else '陌生人'
        if id in specialUsers:
            return specialUsersDict[id]
        for member in self.MemberList:
            if self.User['UserName'] == id:  # 自己
                return '我'
            if member['UserName'] == id:
                name = member['RemarkName'] if member['RemarkName'] else member['NickName']
                return name
        if id[:2] == '@@': #没加入通讯录的群
            newGroup = self.webwxgetbatchcontact(id)
            if not newGroup['RemarkName'] and not newGroup['NickName']:
                return '未命名群'
            self.GroupList.append(newGroup)
            name = newGroup['RemarkName'] if newGroup['RemarkName'] else newGroup['NickName']
            return name
        return name

    def getUserId(self,name):
        for member in self.MemberList:
            if name == member['RemarkName'] or name == member['NickName']:
                return member['UserName']
        return None

    def createChatroom(self,userNames):
        memberList = [{'UserName':username} for username in userNames]

        url = self.base_uri + '/webwxcreatechatroom?pass_ticket=%s&r=%s' % (self.pass_ticket,int(time.time()))
        params = {
            'BaseRequest':self.BaseRequest,
            'MemberCount':len(memberList),
            'MemberList':memberList,
            'Topic':'',
        }

        dic = self._post(url = url, params = params)

        state = True if dic['BaseResponse']['Ret'] == 0 else False
        errMsg = dic['BaseResponse']['ErrMsg']
        chatRoomName = dic['ChatRoomName']
        memberList = dic['MemberList']
        deletedList = []
        blockedList = []
        for member in memberList:
            if member['MemberStatus'] == 4: #被对方删除了
                deletedList.append(member['UserName'])
            elif member['MemberStatus'] == 3: #被加入黑名单
                blockedList.append(member['UserName'])
        return state,errMsg,chatRoomName,deletedList,blockedList

    def addChatroomMember(self,chatRoomName,userNames):
        url = self.base_uri + '/webwxupdatechatroom?fun=addmember&pass_ticket=%s' % (self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            'ChatRoomName': chatRoomName,
            'AddMemberList': ','.join(userNames),
        }

        dic = self._post(url,params)

        state = True if dic['BaseResponse']['Ret'] == 0 else False
        errMsg = dic['BaseResponse']['ErrMsg']
        memberList = dic['MemberList']
        deletedList = []
        blockedList = []
        for member in memberList:
            if member['MemberStatus'] == 4: #被对方删除了
                deletedList.append(member['UserName'])
            elif member['MemberStatus'] == 3: #被加入黑名单
                blockedList.append(member['UserName'])
        return state,errMsg,deletedList,blockedList

    def delChatroomMember(self,chatRoomName,userNames):
        url = self.base_uri +  '/webwxupdatechatroom?fun=delmember&pass_ticket=%s' % (self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            'ChatRoomName': chatRoomName,
            'DelMemberList': ','.join(userNames),
        }
        dic = self._post(url,params)

        return dic['BaseResponse']['Ret'] == 0

    def getBatchMemberRemarkName(self,groupid,memberid):
        name = '陌生人'
        for group in self.GroupList:
            if group['UserName'] == groupid:
                for member in group['MemberList']:
                    if member['UserName'] == memberid:
                        name = member['DisplayName'] if member['DisplayName'] else member['NickName']
                        return name
        new_group = self.webwxgetbatchcontact(groupid)
        if new_group:
            for member in new_group['MemberList']:
                if member['UserName'] == memberid:
                    name = member['DisplayName'] if member['DisplayName'] else member['NickName']
                    return name
        return name

    def _process_message(self, message):
        message['type'] = self.message_types_dict.get(message.pop('MsgType'), None)
        message['FromUserId'] = message.get('FromUserName',None)
        message['FromUserName'] = self.getUserRemarkName(message.pop('FromUserName'))
        message['ToUserId'] = message.get('ToUserName',None)
        message['ToUserName'] = self.getUserRemarkName(message.pop('ToUserName'))
        message['Content'] = message.pop('Content').replace('<br/>', '\n').replace('&lt;', '<').replace('&gt;', '>')

        if message['FromUserId'][:2] == '@@': #群消息
            fromMemberId = message['Content'].split(':')[0]
            message['FromMemberId'] = fromMemberId
            message['FromMemberName'] = self.getBatchMemberRemarkName(message['FromUserId'],fromMemberId)
            message['Content'] = ''.join(message['Content'].split(':')[1:])

        if message['type'] == 'text' and message['Content'].find( #位置消息
                'http://weixin.qq.com/cgi-bin/redirectforward?args=') != -1:
            message['type'] = 'location'
            data = self._get(message['Content'],encoding='gbk')
            location = self._searchContent('title',data,fmat='xml')
            message['location'] = location


        message_type = MESSAGE_TYPES.get(message['type'], UnKnownMessage)
        return message_type(self,message)

    def _process_reply(self,reply,message):
        if isinstance(reply,tuple):
            for r in reply:
                self._process_reply(r,message)
        elif isinstance(reply,str):
            self.sendTextMsg(message.fromUserName,reply)
        elif isinstance(reply,WeChatReply):
            if isinstance(reply,TextReply): #文本回复
                self.sendTextMsg(message.fromUserName,reply.content)
        else:
            raise TypeError('your reply is a %s,reply should be str or WechatReply instance'%type(reply))

    def _str2QRMat(self, str):
        qr = qrcode.QRCode()
        qr.border = 1
        qr.add_data(str)
        mat = qr.get_matrix()
        return mat

    def _genQRCodeImg(self):
        url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
        params = {
            't': 'webwx',
            '_': int(time.time()),
        }

        req = request.Request(url=url, data=parse.urlencode(params).encode('utf-8'))
        response = request.urlopen(req)
        data = response.read()

        with open(QRCODE_PATH,'wb') as f:
            f.write(data)

    def _printQR(self, mat):
        BLACK = '\033[40m  \033[0m'
        WHITE = '\033[47m  \033[0m'
        for row in mat:
            print(''.join([BLACK if item else WHITE for item in row]))

    def _get(self, url,encoding='utf-8',byte_ret = False):
        req = request.Request(url)
        response = request.urlopen(req)
        if byte_ret:
            return response.read()
        data = response.read().decode(encoding)
        return data

    def _post(self, url, params, jsonfmt=True,encoding='utf-8',byte_ret = False):
        if jsonfmt:
            req = request.Request(url=url, data=json.dumps(params,ensure_ascii=False).encode('utf-8'))
            req.add_header('ContentType', 'application/json; charset=UTF-8')
        else:
            req = request.Request(url=url, data=parse.urlencode(params).encode('utf-8'))

        response = request.urlopen(req)
        if byte_ret:
            return response.read()
        data = response.read().decode(encoding)
        return json.loads(data) if jsonfmt else data

    def _filte(self,message,*filters):
        is_match = True
        if len(filters) == 0:
            return is_match

        for filter in filters:
            if not is_match:
                break
            if filter[0] and not message.fromUserName in filter[0]: #filte fromUserName
                is_match = False
            if filter[1] and not message.toUserName in filter[1]: #filte toUserName
                is_match = False
            if filter[2] and not self._filte_content(message,*filter[2]):
                is_match = False
            is_match = not is_match if filter[3] else is_match


        return is_match

    def _filte_content(self,message,*args):
        if len(args) > 1:
            for x in args:
                if self._filte_content(message,x):
                    return True
            return False
        else:
            target_content = args[0]
            if isinstance(target_content,str):
                return target_content == message.content
            elif hasattr(target_content, "match") and callable(target_content.match): #正则匹配
                return target_content.match(message.content)
            else:
                raise TypeError("%s is not a valid target_content" % target_content)

    def allMsg(self,func):
        self.add_handler(func)
        return func

    def textMsg(self, func):
        self.add_handler(func, type='text')
        return func

    def imageMsg(self, func):
        self.add_handler(func, type='image')
        return func

    def videoMsg(self, func):
        self.add_handler(func, type='video')
        return func

    def voiceMsg(self, func):
        self.add_handler(func, type='voice')
        return func

    def sharelocation(self, func):
        self.add_handler(func, type='sharelocation')
        return func

    def location(self, func):
        self.add_handler(func, type='location')
        return func

    def recommend(self,func):
        self.add_handler(func,type='recommend')
        return func

    def revoke(self,func):
        self.add_handler(func,type='revoke')
        return func

    def initMsg(self, func):
        self.add_handler(func, type='initmsg')
        return func

    def textFilter(self,*args,beside = False):
        def wrapper(func):
            self.add_filter(func,content=args,beside=beside)
            return func
        return wrapper

    def sourceFilter(self,*fromUserNames,beside = False):
        def wrapper(func):
            self.add_filter(func,fromUserNames=fromUserNames,beside=beside)
            return func
        return wrapper

    def targetFilter(self,*toUserNames,beside = False):
        def wrapper(func):
            self.add_filter(func,toUserNames=toUserNames,beside=beside)
            return func
        return wrapper

    def filter(self,*args,beside = False):
        args_is_list = False
        if len(args) > 1:
            args_is_list = True
        elif len(args) == 0:
            raise ValueError('filter should have 1 argments at least')
        else:
            target_content = args[0]
            if isinstance(target_content,str):
                def _compareContent(message):
                    compareResult = (target_content == message.content)
                    return compareResult if not beside else  not compareResult
            elif hasattr(target_content, "match") and callable(target_content.match): #正则匹配
                def _compareContent(message):
                    compareResult = target_content.match(message.content)
                    return compareResult if not beside else not compareResult
            else:
                raise TypeError("%s is not a valid target_content" % target_content)

        def wrapper(f):
            if args_is_list:
                for x in args:
                    self.filter(x)(f)
                return f

            @self.textMsg
            def _f(message):
                if _compareContent(message):
                    return f(message)
            return f
        return wrapper


    def add_handler(self, func, type='all'):
        if not callable(func):
            raise ValueError("{} is not callable".format(func))
        self._handlers[type].append((func, len(inspect.getargspec(func).args)))

    def add_filter(self,func,fromUserNames = None,toUserNames = None,content =  None,beside = False):

        fromUserNames = None if isinstance(fromUserNames,tuple) and len(fromUserNames) == 0 else fromUserNames
        toUserNames = None if isinstance(toUserNames,tuple) and len(toUserNames) == 0 else toUserNames
        content = None if isinstance(content,tuple) and len(content) == 0 else content

        if not self._filters.get(func):
            self._filters[func] = []

        self._filters[func].append((fromUserNames,toUserNames,content,beside))

    def get_handler(self, type):
        return self._handlers.get(type, []) + self._handlers['all']

    def get_filter(self,func):
        return self._filters.get(func,[])

    def _searchContent(self, key, content, fmat='attr'):
        if fmat == 'attr':
            pm = re.search(key + '\s?=\s?"([^"<]+)"', content)
            if pm: return pm.group(1)
        elif fmat == 'xml':
            pm = re.search('<{0}>([^<]+)</{0}>'.format(key), content)
            if pm: return pm.group(1)
        return '未知'

    def _save_file(self,data,file_name):
        file_type = file_name[:file_name.find('_')]
        if file_type == 'msgimg':
            path = self._mkdir(os.path.join(os.getcwd(),'images'))
        elif file_type == 'msgvoice':
            path = self._mkdir(os.path.join(os.getcwd(),'voices'))
        elif file_type == 'msgvideo':
            path = self._mkdir(os.path.join(os.getcwd(),'videos'))
        elif file_type == 'icon':
            path = self._mkdir(os.path.join(os.getcwd(),'icons'))
        else:
            path = self._mkdir(os.path.join(os.getcwd(),'tmp'))
        path = os.path.join(path,file_name)
        with open(path,'wb') as f:
            f.write(data)
        return path



    def _mkdir(self,path):
        if not os.path.exists(path):
            self._mkdir(os.path.split(path)[0])
            os.mkdir(path)
        elif not os.path.isdir(path):
            return False
        return path

    def _safe_open(self,file_path):
        try:
            if sys.platform.find('darwin') >= 0:
                subprocess.call(['open',file_path])
            elif sys.platform.find('linux') >= 0:
                subprocess.call(['xdg-open',file_path])
            else:
                os.startfile(file_path)
            return True
        except:
            return False

specialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage',
                'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp',
                'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin', 'weixin',
                'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c',
                'officialaccounts', 'notification_messages', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil',
                'userexperience_alarm', 'notification_messages']

specialUsersDict = {
    'blogapp': '微博阅读',
    'blogappweixin': '微博阅读',
    'brandsessionholder': 'brandsessionholder',
    'facebookapp': 'Facebook',
    'feedsapp': '朋友圈',
    'filehelper': '文件传输助手',
    'floatbottle': '漂流瓶',
    'fmessage': '朋友圈推荐消息',
    'gh_22b87fa7cb3c': 'gh_22b87fa7cb3c',
    'lbsapp': 'lbsapp',
    'masssendapp': '群发助手',
    'medianote': '语音记事本',
    'meishiapp': 'meishiapp',
    'newsapp': '腾讯新闻',
    'notification_messages': 'notification_messages',
    'officialaccounts': 'officialaccounts',
    'qmessage': 'QQ离线助手',
    'qqfriend': 'qqfriend',
    'qqmail': 'QQ邮箱',
    'qqsync': '通讯录同步助手',
    'readerapp': 'readerapp',
    'shakeapp': '摇一摇',
    'tmessage': 'tmessage',
    'userexperience_alarm': '用户体验报警',
    'voip': 'voip',
    'weibo': 'weibo',
    'weixin': '微信',
    'weixinreminder': 'weixinreminder',
    'wxid_novlwrv3lqwv11': 'wxid_novlwrv3lqwv11',
    'wxitil': '微信小管家'
}