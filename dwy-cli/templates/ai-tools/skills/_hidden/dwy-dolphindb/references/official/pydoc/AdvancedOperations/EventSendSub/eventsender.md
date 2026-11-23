---
source_url: https://docs.dolphindb.cn/zh/pydoc/AdvancedOperations/EventSendSub/eventsender.html
fetched_at: 2026-05-19T09:52:38Z
category: pydoc
title: 事件发送 EventSender
sha1: afc5461a4de8dab69bec40995c8b8cb6bb9f6475
---

# 事件发送 EventSender

Python API 从 3.0.0.0 版本开始，提供 EventSender 类用于向存储事件信息的异构流表中写入序列化后的事件数据。DolphinDB 服务端的 CEP
引擎通常会订阅这些流表，以便捕获并处理相应的事件。

## 接口说明

### 构造函数

```dolphindb
EventSender(ddbSession, tableName, eventSchema, eventTimeFields=None, commonFields=None)
```

**参数介绍**

- **ddbSession**：必填，一个已经连接到 DolphinDB 服务端的会话。
- **tableName**：必填，字符串，表示待写入的异构流表的名称。
- **eventSchema**：必填，要发送的自定义事件的列表。例如：[EventA, EventB]。其中，
  - 事件定义需继承自 Event 类实现，详情请参考 [自定义事件](event.html)
    章节。
  - API 中事件的定义需要和 DolphinDB 中事件的定义保持一致。
- **eventTimeFields**：选填，字符串或字符串列表，指定各事件的时间字段。*tableName*
  中如果存在时间列，则需要指定该参数，反之则无需指定。默认值为 None，表示不指定时间字段。
  - 如果所有事件的时间字段名相同，则只需指定为一个字符串标量，即这个时间字段的名称。
  - 如果各个事件的时间字段名称不同，则需要指定为一个字符串向量，表示各个事件的时间字段名称。其中各元素的顺序和
    *eventSchema* 参数传入的顺序保持一致。
- **commonFields**：选填，字符串列表，表示事件中具有相同名称的字段。*tableName*
  中如果存在表示相同字段的列，则需要指定该参数；反之则无需指定。默认值为 None，表示不指定相同字段。

### sendEvent

将事件发送至 DolphinDB 服务端。

```dolphindb
sendEvent(event)
```

**参数介绍**

- **event**：必填，自定义事件实例。

## 使用示例

下例将完整演示从 API 端发送事件至 DolphinDB 服务端的完整流程。步骤如下：

1. DolphinDB 服务端首先完成以下内容：
   1. 定义事件和监视器。
   2. 创建 CEP 引擎。
   3. 创建并订阅异构流表到 CEP 引擎。
2. API 端向异构流表中写入事件。

### 定义事件和监视器

在 DolphinDB 服务端，定义两个事件（Event），一个共享内存表和一个监视器（Monitor）。其中，

`EventA` 和 `EventB` 都具有 TIMESTAMP 类型的属性
eventTime，以及 INT 类型的属性 a。此外，`EventB` 还具有 DOUBLE 类型的属性 b。

Monitor 类通过定义两个成员方法和一个 `onload` 方法来管理事件。成员方法分别用于更新
`EventA` 和 `EventB`
到共享内存表中。`onload` 方法利用 `addEventListener`
函数注册了两个侦听器，它们分别在捕获到 `EventA` 或 `EventB`
时，将事件数据写入到预设的共享内存表 result 中。

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

**共享内存表 result**

```dolphindb
share table(100:0, `eventTime`eventType`a`b, [TIMESTAMP, SYMBOL, INT, DOUBLE]) as result
```

**监视器**

```dolphindb
class Monitor {
    def Monitor(){}
    def updateEventA(event) {
        insert into result values(event.eventTime, "A", event.a, NULL)
    }
    def updateEventB(event) {
        insert into result values(event.eventTime, "B", event.a, event.b)
    }
    def onload() {
        addEventListener(updateEventA,"EventA",,"all")
        addEventListener(updateEventB,"EventB",,"all")
    }
}
```

### 创建 CEP 引擎

创建 CEP 引擎时，需要指定一个和订阅的异构流表具有相同结构的 dummyTable。表中字段的顺序如下：

1. 可选，时间类型列。如果需要利用事件时间过滤表数据，或在 CEP 引擎中应用时间字段，则必须指定该列。
2. 必选，STRING/SYMBOL 类型列，表示事件类型。
3. 必选，BLOB 类型列，用于存储事件序列化后的数据。
4. 可选，表示事件中共同属性的字段列。若需基于共有字段过滤输入表，则可以添加1个或多个列。

注意：若指定了时间列，则在创建 CEP 引擎时也需要指定各事件对应的时间字段。

因为 `EventA` 和 `EventB` 中具有共同的时间字段 eventTime 和共同属性
a，本例将演示指定 CEP 引擎时间字段为 eventTime，且使用共同属性的场景。

创建的输入表结构应为 [TIMESTAMP, STRING, BLOB, INT]，创建 CEP 引擎的脚本如下：

```dolphindb
dummy = table(100:0, `eventTime`eventType`blob`a, [TIMESTAMP, STRING, BLOB, INT])
engine = createCEPEngine('cep', <Monitor()>, dummy, [EventA, EventB], 1, "eventTime")
```

### 从异构流表中订阅事件

CEP 引擎通过订阅异构流表的方式接收事件数据。在 DolphinDB 中定义异构流表并发起订阅：

```dolphindb
share streamTable(100:0, `eventTime`eventType`blob`a, [TIMESTAMP, STRING, BLOB, INT]) as input
subscribeTable(,`input, `action, 0, engine, true)
```

### API 端定义事件

参考 [自定义事件](event.html) 中的示例，在 API 端定义一个与 DolphinDB
服务端具有同样结构的 EventA 和 EventB，用于向异构流表中写入事件数据。

```dolphindb
from dolphindb.cep import Event
from dolphindb.typing import Scalar
import dolphindb.settings as keys

class EventA(Event):
    eventTime: Scalar[keys.DT_TIMESTAMP]
    a: Scalar[keys.DT_INT]

class EventB(Event):
    eventTime: Scalar[keys.DT_TIMESTAMP]
    a: Scalar[keys.DT_INT]
    b: Scalar[keys.DT_DOUBLE]
```

### 通过 API 向异构流表中写入数据

定义 `EventSender`，传入定义的 `EventA` 和
`EventB` 作为 *eventSchema*，指定往异构流表 input
中写入事件。在本例中，因为异构流表中包含时间字段列（eventTime）和共同字段列（a），因此 `EventSender`
需要分别指定 *eventTimeFields* 和 *commonFields* 参数为 "eventTime" 和 ["a"]。

```dolphindb
import dolphindb as ddb
from dolphindb.cep import EventSender

s = ddb.Session()
s.connect("localhost", 8848, "admin", "123456")
sender = EventSender(s, "input", [EventA, EventB], "eventTime", ["a"])
```

`EventSender` 定义完成后，分别通过 `sendEvent` 写入
`EventA` 和 `EventB` 的事件实例。

```dolphindb
import numpy as np
sender.sendEvent(EventA(np.datetime64("2024-03-31T12:00:00.123", "ms"), 1))
sender.sendEvent(EventB(np.datetime64("2024-03-31T12:00:00.456", "ms"), 2, 3.3))
```

监视器在侦听到事件后，会将事件数据更新到 result 表中。

### 查看结果

查询 result 表结果如下：

```dolphindb
print(s.run("select * from result"))
// output
                eventTime eventType  a    b
0 2024-03-31 12:00:00.123         A  1  NaN
1 2024-03-31 12:00:00.456         B  2  3.3
```
