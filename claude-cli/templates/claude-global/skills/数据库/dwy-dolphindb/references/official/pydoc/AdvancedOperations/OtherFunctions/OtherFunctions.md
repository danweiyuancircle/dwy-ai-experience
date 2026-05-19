---
source_url: https://docs.dolphindb.cn/zh/pydoc/AdvancedOperations/OtherFunctions/OtherFunctions.html
fetched_at: 2026-05-19T09:52:39Z
category: pydoc
title: 其他功能
sha1: d04c86c5f61954ee75d7db067fec78144a90ee66
---

# 其他功能

## 强制取消任务

session 对象中提供静态方法 `enableJobCancellation()`，用于开启强制取消任务的功能。此功能默认关闭。开启后，通过 “Ctrl+C” 按键等方式终止 API 进程中时，会同时取消所有 session 提交的正在运行的作业。

**注意：** 目前该功能仅在 Linux 系统生效。

## 日志重定向

Python API 自 3.0.2.2 起提供了 Logger 对象用于处理 API 程序运行中产生的日志信息和 Session.run 执行脚本中 print 的输出信息。

### Logger

Logger 仅提供两种日志记录器：default\_logger 和 msg\_logger。

- default\_logger：API 程序运行中的日志信息，例如序列化错误、网络连接错误等。

```dolphindb
import dolphindb as ddb
ddb.logger.default_logger
```

- msg\_logger：通过 Session.run 执行的脚本中的 print 输出信息将返回给 API，由对应的 msg\_logger 控制输出行为。每个 Session 都对应一个 msg\_logger。

```dolphindb
import dolphindb as ddb
s = ddb.Session()
s.msg_logger
```

### 日志等级

通过 min\_level 属性，可以设置输出日志的等级。日志等级从低到高依次为：DEBUG、INFO、WARNING（默认值）、ERROR。

```dolphindb
import dolphindb as ddb
ddb.logger.default_logger.min_level = ddb.logger.Level.ERROR
```

### 标准输出

Logger 对象提供如下接口，用于开启或关闭标准输出模式。API 默认开启标准输出。

**enable\_stdout\_sink**

```dolphindb
def enable_stdout_sink(self) -> None: ...
```

启用标准输出。

**disable\_stdout\_sink**

```dolphindb
def disable_stdout_sink(self) -> None: ...
```

关闭标准输出。

### 文件输出

API 默认不启用文件输出。可通过以下接口开启或关闭文件输出。

**enable\_file\_sink**

```dolphindb
def enable_file_sink(self, path: str) -> None: ...
```

- **path**：输出文件日志的路径。

启用文件日志输出。执行该函数将会被覆盖之前已经指定的路径。

**disable\_file\_sink**

```dolphindb
def disable_file_sink(self) -> None: ...
```

关闭文件日志输出。

### 自定义输出

**Sink**

Logger 对象提供 `Sink` 类。用户可以通过继承该类来实现自定义的输出日志方式。构造 Sink 实例时，需要为其指定名称。

**add\_sink**

```dolphindb
def add_sink(self, sink: Sink) -> None: ...
```

向 Logger 对象中增加自定义 Sink 实例。

**remove\_sink**

```dolphindb
def remove_sink(self, name: str) -> None: ...
```

根据 Sink 实例名称从 Logger 对象中删除对应的 Sink。

**list\_links**

```dolphindb
def list_sinks(self) -> List[Sink]: ...
```

列出当前 Logger 中的所有自定义的 Sink。

### 使用示例

下面以修改 msg\_logger 为例，演示如何通过自定义 Sink 重定向输出。

```dolphindb
import dolphindb as ddb
from dolphindb.logger import Sink

msg_list = []

class mySink(Sink):
    def handle(self, msg):
        msg_list.append(msg.log)

s = ddb.Session()
s.msg_logger.add_sink(mySink("test1"))

s.connect("localhost", 8848, "admin", "123456")
s.run("print(123)")

print("msg: ", msg_list)

""" output:

123
msg: ['123']
"""
```

以上代码逻辑为：

- 首先，继承 `Sink` 类实现子类 `mySink`，并重写其 `handle` 方法，以将接收到的消息保存到 msg\_list 中。
- 接着，向 msg\_logger 添加一个名为 "test1" 的自定义 Sink 实例 `mySink`。
- 最后，执行脚本 `print(123)`。由于未关闭标准输出，控制台将显示两行输出：第一行是默认的标准输出，第二行是 msg\_list 的内容。
