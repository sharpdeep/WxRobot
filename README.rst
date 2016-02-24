WxRobot |python|
================

面向个人账户的微信机器人框架

已实现功能：
------------

-  **扫描二维码登陆获取联系人**

.. figure:: ./screenshot/1.png
   :alt: 

-  **清理好友(由于接口限制，可能会失败)**

.. figure:: ./screenshot/4.png
   :alt: 

-  **接收文本消息和位置消息**

.. figure:: ./screenshot/2.png
   :alt: 

-  **消息过滤(来源过滤，目标过滤，文本过滤)** 如过滤腾讯新闻文本消息：

   ::

       @api.textMsg
       @api.sourceFilter('腾讯新闻',beside=True)
       def FiltedTxtMsgHandler(message):
           print('%s给%s发送了一个消息'%(message.fromUserName,message.toUserName))
           print('-> %s:%s'%(message.fromUserName,message.content))

-  **手机端互动/退出/消息接收回调接口** 手机客户端互动回调：

   ::

       @robot.onPhoneInteract
       def onPhoneInteract():
           print('[*] 你在手机上玩了微信被我发现了')

.. figure:: ./screenshot/3.png
   :alt: 

Usage
-----

普通用户
~~~~~~~~

1. 下载项目到本地(\ ``git clone``\ 或直接下载)
2. 配置环境： (1). 安装\ ``python3.4``\ 和\ ``pip`` (2).
   安装依赖包:\ ``pip install -r requirement.txt``
3. 运行：进入项目目录，\ ``python myrobot.py``

开发者
~~~~~~

接口用法参照\ ``myrobot.py``

Credit
------

I used

`WeixinBot <https://github.com/Urinx/WeixinBot>`__ by
`Urinx <https://github.com/Urinx>`__

`WeRobot <https://github.com/whtsky/WeRoBot>`__ by
`whtsky <https://github.com/whtsky>`__

`wechat-deleted-friends <https://github.com/0x5e/wechat-deleted-friends>`__
by `0x5e <https://github.com/0x5e>`__

Todo
----

-  [ ] 添加更多类型消息接口
-  [ ] 自动回复
-  [ ] 小黄鸡或图灵机器人自动回复
-  [ ] 主动发送消息
-  [ ] 用微信遥控电脑

反馈
----

有问题或者意见可以到\ `Issues <https://github.com/sharpdeep/WxRobot/issues>`__\ 中提出

.. |python| image:: https://img.shields.io/badge/python-3.4-ff69b4.svg
