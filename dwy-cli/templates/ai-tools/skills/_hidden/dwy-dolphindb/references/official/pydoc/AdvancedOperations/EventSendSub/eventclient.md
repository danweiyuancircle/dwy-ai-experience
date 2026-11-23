---
source_url: https://docs.dolphindb.cn/zh/pydoc/AdvancedOperations/EventSendSub/eventclient.html
fetched_at: 2026-05-19T09:52:38Z
category: pydoc
title: 事件订阅 EventClient
sha1: 4d921138329b5eb9d017d03456ccfce06bd6803e
---

# 事件订阅 EventClient

Python API 从 3.0.0.0 版本开始，提供 EventClient 类用于订阅异构流表中的事件数据。该异构流表通常接收 DolphinDB 服务端 CEP
引擎处理后并序列化输出的事件数据。

## 接口说明

### 构造函数

```dolphindb
EventClient(eventSchema, eventTimeFields=None, commonFields=None)
```

**参数介绍**

- **eventSchema**：订阅的自定义事件的列表。例如：[EventA, EventB]。其中，
  - 事件定义需继承自 Event 类实现，详情请参考 [自定义事件](event.html)
    章节。
  - API 中事件的定义需要和 DolphinDB 中事件的定义保持一致。
- **eventTimeFields**：字符串或字符串列表，指定各事件的时间字段。订阅的异构流表中如果存在时间列，则需要指定该参数，反之则无需指定。默认值为
  None，表示不指定时间字段。
  - 如果所有事件的时间字段名相同，则只需指定为一个字符串标量，即这个时间字段的名称。
  - 如果各个事件的时间字段名称不同，则需要指定为一个字符串向量，表示各个事件的时间字段名称。其中各元素的顺序和
    *eventSchema* 参数传入的顺序保持一致。
- **commonFields**：字符串列表，表示事件中具有相同名称的字段。订阅的异构流表中如果存在表示相同字段的列，则需要指定该参数；反之则无需指定。默认值为
  None，表示不指定相同字段。

### subscribe

```dolphindb
subscribe(host, port, handler, tableName
          actionName=None, offset=-1, resub=False,
          userName=None, password=None)
```

**连接参数**：*host, port, userName, password*

- **host**：字符串，必填，表示发布端节点的 IP 地址。
- **port**：字符串，必填，表示发布端节点的端口号。
- **userName**：字符串，可选，表示所连接 DolphinDB 的登录用户名。
- **password**：字符串，可选，表示所连接 DolphinDB 的登录用户名对应的密码。

**回调参数**：*handler*

- **handler**：自定义的回调函数，用于处理每次流入的数据。和普通订阅的回调不同，事件订阅中回调传入的参数是
  `EventClient` 中 *eventSchema* 指定的事件类型的实例。

下例定义了一个简单的回调函数：

```dolphindb
def handler(msg):
    print(msg)
```

**订阅参数**：*tableName, actionName, offset, resub*

- **tableName**：表示发布表的名称。
- **actionName**：表示订阅任务的名称。
  - 订阅时，订阅主题由订阅表所在节点的别名、流数据表名称和订阅任务名称组合而成，使用“/”分隔。注意，如果订阅主题已经存在，将会订阅失败。
- **offset**：整数，表示订阅任务开始后的第一条消息所在的位置。消息即为流数据表中的行。
  - 若该参数未指定，或设为 -1，订阅将会从流数据表的当前行开始。
  - 若该参数设为 -2，系统会获取持久化到磁盘上的 offset，并从该位置开始订阅。其中，offset
    与流数据表创建时的第一行对应。如果某些行因为内存限制被删除，在决定订阅开始的位置时，这些行仍然考虑在内。
- **resub**：布尔值，表示订阅中断后，API 是否进行自动重订阅。默认值为 False，表示不会自动重订阅。

### unsubscribe

通过该方法取消订阅。使用方式同普通流订阅，接口如下：

```dolphindb
unsubscribe(host, port, tableName, actionName=None)
```

**参数介绍**

- **host**：字符串，必填，表示发布端节点的 IP 地址。
- **port**：字符串，必填，表示发布端节点的端口号。
- **tableName**：表示发布表的名称。
- **actionName**：表示订阅任务的名称。

### getSubscriptionTopics

通过该方法可以获取当前 `EventClient`
中的所有订阅主题。主题的构成为：`host/port/tableName/actionName` ，每个
EventClient 的主题互不相同。

该接口的使用方式与普通流订阅一致，使用示例如下：

```dolphindb
client.getSubscriptionTopics()
```

## 使用示例

下例将完整演示从 API 端订阅 DolphinDB CEP 引擎输出事件的完整流程。步骤如下：

1. DolphinDB 服务端首先完成以下内容：
   1. 定义事件和监视器。
   2. 定义输出表和序列化器。
   3. 创建 CEP 引擎。
   4. 发送事件到 CEP 引擎的输出队列，输出到一个异构流表。
2. API 端启动事件订阅上步输出的异构流表。

### 定义事件和监视器

在 DolphinDB 服务端，定义两个事件（Event），和一个监视器（Monitor）。其中，

`EventA` 和 `EventB` 都具有 TIMESTAMP 类型的属性
`eventTime`，以及 INT 类型的属性
`a`，除此之外，`EventB` 还具有 DOUBLE 类型的属性
`b`。

Monitor 类通过定义两个成员方法和一个 `onload` 方法来管理事件。成员方法分别在接收到
`EventA` 和 `EventB` 后，通过
`emitEvent` 方法将它们发送到 CEP 引擎指定的输出序列化器。

**事件 EventA**

```dolphindb
class EventA {
    eventTime::TIMESTAMP
    a::INT
    def EventA(a_) {
        eventTime = now()
        a = a_
    }
}
```

**事件 EventB**

```dolphindb
class EventB {
    eventTime::TIMESTAMP
    a::INT
    b::DOUBLE
    def EventB(a_, b_) {
        eventTime = now()
        a = a_
        b = b_
    }
}
```

**监视器 Monitor**

```dolphindb
class Monitor {
  def Monitor(){}
  def updateEventA(event) {
      emitEvent(event)
  }
  def updateEventB(event) {
      emitEvent(event)
  }
  def onload() {
      addEventListener(updateEventA,"EventA",,"all")
      addEventListener(updateEventB,"EventB",,"all")
  }
}
```

### 定义异构流表和序列化器

在 DolphinDB 中定义异构流表用于接收序列化的事件信息，并使用函数 `streamEventSerializer`
定义事件序列化器。

定义序列化器时，需要指定输出表，通常是一个异构流表。表中字段的顺序如下：

1. 可选，时间类型列。如果需要利用事件时间过滤表数据，或在 CEP 引擎中使用时间字段，则必须指定该列。
2. 必选，STRING/SYMBOL 类型列，表示事件。
3. 必选，BLOB 类型列，用于存储事件序列化后的数据。
4. 可选，表示事件中共同属性的字段列。若需基于共有字段过滤表数据，则可以添加1个或多个列。

因为 `EventA` 和 `EventB` 中具有共同的时间字段 eventTime 和共同属性
a，本例将演示指定 CEP 引擎时间字段为 eventTime，且使用共同属性的场景。

创建结构为 [TIMESTAMP, STRING, BLOB, INT] 的输出表和对应的序列化器脚本如下所示：

```dolphindb
share streamTable(100:0, `eventTime`eventType`blob`a, [TIMESTAMP, STRING, BLOB, INT]) as output
serializer = streamEventSerializer(name='serOutput', eventSchema=[EventA, EventB], outputTable=output, eventTimeField = "eventTime", commonField=["a"])
```

### 创建 CEP 引擎并写入事件

使用和输出表具有相同结构的表作为 CEP 引擎的输入表，并指定监视器和事件结构。

```dolphindb
dummy = table(100:0, `eventTime`eventType`blob`a, [TIMESTAMP, STRING, BLOB, INT])
engine = createCEPEngine('cep', <Monitor()>, dummy, [EventA, EventB], 1, "eventTime", outputTable=serializer)
```

调用 `appendEvent` 方法向 CEP 引擎中写入两个事件。DolphinDB 脚本如下：

```dolphindb
appendEvent(engine, EventA(1))
appendEvent(engine, EventB(2, 3.3))
```

### API 端定义事件

参考 [自定义事件](event.html) 中的示例，在 API 端定义与 DolphinDB
服务端具有相同结构的 `EventA` 和 `EventB`。

```dolphindb
from dolphindb.cep import Event
from dolphindb.typing import Scalar
import dolphindb as ddb
import dolphindb.settings as keys

class EventA(Event):
    eventTime: Scalar[keys.DT_TIMESTAMP]
    a: Scalar[keys.DT_INT]

class EventB(Event):
    eventTime: Scalar[keys.DT_TIMESTAMP]
    a: Scalar[keys.DT_INT]
    b: Scalar[keys.DT_DOUBLE]
```

### 通过 API 从异构流表中订阅事件数据

首先定义回调函数 `handler`，它会在接收到 msg（事件数据）后进行打印。

```dolphindb
def handler(msg: Event):
    print(msg)
```

定义 `EventClient`，传入 EventA 和 EventB 作为
*eventSchema*。和普通订阅类似，使用 `subscribe` 接口从 output 表中订阅数据。

```dolphindb
from dolphindb.cep import EventClient
client = EventClient([EventA, EventB], "eventTime", ["a"])
client.subscribe("localhost", 8848, handler, "output", "action", offset=0)

from threading import Event as tEvent
tEvent().wait()
```

订阅结果如下：

```dolphindb
EventA({'eventTime': numpy.datetime64('2024-03-31T11:23:13.730'), 'a': 1})
EventB({'eventTime': numpy.datetime64('2024-03-31T11:23:13.730'), 'a': 2, 'b': 3.3})
```
