# 使用Chronocat的satori协议和onebotv11协议交互的代码v0.1

事件的处理还没完成，只搭建了框架，现在能够把文字消息转发完成了（应该不太完美）

## 更新：

1.更新了图片的发送支持
2.对多个bot的支持，需要对多个bot转发的时候把config.py的ws_servers数组里增加新的ws地址，就会自动给这几个地址转发
（合并转发还不支持）

## 使用方法：
1. 修改config文件夹下的config.py，将ws_servers，satori和token填写成自己的
2. 执行 python3 run.py

 可选：
conf中可以调整日志的等级和是否生成日志文件


## TODO:
1. 各个事件的处理
2. satori协议完整的支持
3. 根据Chronocat的开发情况加入新的功能支持
