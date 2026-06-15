---
source_url: https://docs.dolphindb.cn/zh/pydoc/AdvancedOperations/EventSendSub/event.html
fetched_at: 2026-05-19T09:52:38Z
category: pydoc
title: 自定义事件
sha1: 413aad3172ac728285b74028dbff0083509f055d
---

# 自定义事件

在客户端自定义事件之前，需要先在 DolphinDB 服务端定义事件。例如：如下 DolphinDB 脚本定义了1个事件类 TestEvent，该类具有3个属性。

```dolphindb
class TestEvent {
    a :: INT
    b :: DECIMAL32(3)
    c :: DOUBLE VECTOR
    def TestEvent(a_, b_, c_) {
        a = a_;
        b = b_;
        c = c_;
    }
}
```

以上定义的事件为 CEP 引擎中要处理的事件。

下例在 Python API 中继承 Event 类，定义一个与 TestEvent
具有同样结构的事件。

```dolphindb
from dolphindb.cep import Event
from dolphindb.typing import Scalar, Vector
import dolphindb.settings as keys
class MyEvent(Event):
    a: Scalar[keys.DT_INT]
    b: Scalar[keys.DT_DECIMAL32, 3]
    c: Vector[keys.DT_DOUBLE]
```

## 属性声明

使用 dolphindb.typing 中新增的 Scalar 和 Vector，可以声明属性的数据形式和数据类型。当前版本（3.0.0.0）仅支持标量和向量（tuple
和数组向量除外）两种数据形式。

**标量**

如果属性是一个标量，有2种声明方式：

- `Scalar[keys.DT_TYPE, (exparam)]`，其中，*DT\_TYPE* 为
  dolphindb.settings 中提供的数据类型常量，例如 `Scalar[keys.DT_INT]`
  ，`Scalar[keys.DT_STRING]`等；*exparam* 为 Decimal
  类型特有参数，用于指定小数位数；例如 `Scalar[keys.DT_DECIMAL32, 3]`。
- `Scalar[DATA_TYPE, (exparam)]`。其中，`DATA_TYPE`
  为数据类型 ID，例如 Scalar[4]，Scalar[37，3]。可在 [DolphinDB 数据类型](https://docs.dolphindb.cn/zh/progr/data_types.html)中查看各类型的 ID。

示例：

```dolphindb
from dolphindb.settings as keys
                    class TestEvent(Event):
                    a: Scalar[keys.DT_INT]        # 或 a: Scalar[4]
```

定义 Decimal 类型的标量，需要指定 *exparam* 参数。

```dolphindb
class TestEvent(Event):
                    a: Scalar[keys.DT_DECIMAL32, 3]    # 或 a: Scalar[37, 3]
```

**向量**

向量的声明方式和标量的方式类似：

- `Vecvtor[keys.DT_TYPE, (exparam)]`
- `Vector[DATA_TYPE, (exparam)]`

示例：

```dolphindb
from dolphindb.settings as keys
                    class TestEvent(Event):
                    a: Vector[keys.DT_INT]      # 或 a: Vector[4]
                    b: Vector[keys.DT_DECIMAL32, 3]  # 或 b: Vector[37, 3]
```

## 构造函数

### 默认构造函数

继承自 Event 类的事件，具备默认构造函数，有两种构造实例的方式：使用位置参数构造和使用关键字构造。

以上文定义的 MyEvent 事件类型为例，分别介绍两种构造实例的方法。

**使用位置参数构造**

```dolphindb
print(MyEvent(1, Decimal("1.234"), [1.1, 2.2]))
// output
MyEvent({'a': 1, 'b': Decimal('1.234'), 'c': [1.1, 2.2]})
```

**使用关键字参数构造**

```dolphindb
print(MyEvent(a=1, b=Decimal("1.234"), c=[1.1, 2.2]))
// output
MyEvent({'a': 1, 'b': Decimal('1.234'), 'c': [1.1, 2.2]})
```

**混合使用位置参数和关键字参数构造**

```dolphindb
print(MyEvent(1, Decimal("1.234"), c=[1.1, 2.2]))
// output
MyEvent({'a': 1, 'b': Decimal('1.234'), 'c': [1.1, 2.2]})
```

### 自定义构造函数

也可以通过重载构造函数的方式自定义构造函数行为，例如：

```dolphindb
class MyEvent(Event):
    ...
    def __init__(self):
        self.a = 1
        self.b = Decimal("1.234")
        self.c = [1.1, 2.2]

print(MyEvent())
// output
MyEvent({'a': 1, 'b': Decimal('1.234'), 'c': [1.1, 2.2]})
```

## **事件名称**

上例中定义的 MyEvent 事件类，其默认事件名称和类的名称相同，即 MyEvent。如果需要指定其它事件名称，可以在定义时指定
`_event_name` 属性，如下所示：

```dolphindb
class MyEvent(Event):
    _event_name = "TestName"
    ...
```

使用该方式重新定义了事件名称后，输出的事件名称为修改后的名称。

```dolphindb
print(MyEvent(1, Decimal("1.234"), [1.1, 2.2]))
// output
TestName({'a': 1, 'b': Decimal('1.234'), 'c': [1.1, 2.2]})
```
