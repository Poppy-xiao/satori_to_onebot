使用Chronocat的satori协议和星乃之间交互的代码v0.1

事件的处理还没完成，只搭建了框架，现在能够把消息转发完成了（不太完美）

使用方法：
1.修改config文件夹下的config.py，将hoshino，satori和token填写成自己的
2.执行 python3 run.py

可选：
conf中可以调整日志的等级和是否生成日志文件


TODO:
1.各个事件的处理
2.satori协议完整的支持
3.根据Chronocat的开发情况加入新的功能支持