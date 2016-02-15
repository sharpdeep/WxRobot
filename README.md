# WxRobot ![python](https://img.shields.io/badge/python-3.4-ff69b4.svg)
面向个人账户的微信机器人框架

##已实现功能：

- **扫描二维码登陆获取联系人**

![](./screenshot/1.png)

- **清理好友(由于接口限制，可能会失败)**

![](./screenshot/4.png)

- **接收文本消息和位置消息**

![](./screenshot/2.png)

- **消息过滤(来源过滤，目标过滤，文本过滤)**
如过滤腾讯新闻文本消息：
```
@api.textMsg
@api.sourceFilter('腾讯新闻',beside=True)
def FiltedTxtMsgHandler(message):
    print('%s给%s发送了一个消息'%(message.fromUserName,message.toUserName))
    print('-> %s:%s'%(message.fromUserName,message.content))
```

- **手机端互动/退出/消息接收回调接口**
手机客户端互动回调：
```
@robot.onPhoneInteract
def onPhoneInteract():
    print('[*] 你在手机上玩了微信被我发现了')
```

![](./screenshot/3.png)


##Usage

###普通用户

1. 下载项目到本地(`git clone`或直接下载)
2. 配置环境：
    (1). 安装`python3.4`和`pip`
    (2). 安装依赖包:`pip install -r requirement.txt`
3. 运行：进入项目目录，`python myrobot.py`


###开发者

接口用法参照`myrobot.py`

##Credit

I used  

[WeixinBot](https://github.com/Urinx/WeixinBot) by [Urinx](https://github.com/Urinx)   

[WeRobot](https://github.com/whtsky/WeRoBot) by [whtsky](https://github.com/whtsky)

[wechat-deleted-friends](https://github.com/0x5e/wechat-deleted-friends) by [0x5e](https://github.com/0x5e)


##Todo
- [ ] 添加更多类型消息接口
- [ ] 自动回复
- [ ] 小黄鸡或图灵机器人自动回复
- [ ] 主动发送消息
- [ ] 用微信遥控电脑

##反馈

有问题或者意见可以到[Issues](https://github.com/sharpdeep/WxRobot/issues)中提出


