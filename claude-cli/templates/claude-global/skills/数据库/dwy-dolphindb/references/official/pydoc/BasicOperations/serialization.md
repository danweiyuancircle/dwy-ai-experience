---
source_url: https://docs.dolphindb.cn/zh/pydoc/BasicOperations/serialization.html
fetched_at: 2026-05-19T09:52:40Z
category: pydoc
title: 序列化与反序列化
sha1: eff5a9e55cb56db451e88c89082accd45a9ff505
---

# 序列化与反序列化

Python API 从 3.0.2.1 版本新增 io 模块，包含如下函数：

- dump, load
- dumps, loads

## dump

将对象 *obj* 序列化，并写入打开的 *file* 对象。

```dolphindb
def dump(obj, file, *, types=None)
```

**参数**

- obj：待序列化对象。
- file：待写入对象。
- types：可选参数，用于指定序列化对象的类型。在 dolphindb.settings 中定义了形如 "DT\_XXX"
  的枚举值，用于设置数据类型。指定方式如下：

  - *obj* 是字典或能够转换为字典的数据形式：*types* 是长度为 2
    的列表，其第一个元素表示键的类型，第二个元素表示值的类型。例如：[\_STRING, DT\_INT])
  - *obj* 是 DataFrame 或能够转换为表的数据形式：*types*
    是一个字典，其中，键表示列名，值表示对应列的类型。例如：{'col1': DT\_STRING, 'col2': DT\_INT}。
  - 其它情况：

    - *types* 可以是一个整型（枚举值）。例如：DT\_INT，不指定小数位数的 Decimal 类型
      DT\_DECIMAL32
    - 长度为2的整型列表，第一个元素表示数据类型，第二个元素是额外参数，通常为 Decimal
      类型指定小数位数，例如：指定小数位数的 Decimal 类型 [DT\_DECIMAL32, 2]。

**返回值：**无

## load

从打开的文件对象中读取一个序列化的对象。

```dolphindb
def load(file) -> Any
```

**参数**

- file：待读取文件。

**返回值：**反序列化后的结果。

## dumps

将对象 *obj* 序列化为字节串，并返回该字节串。

```dolphindb
def dumps(obj, *, types=None) -> bytes
```

**参数**

- obj：待序列化对象。
- types：可选参数，用于指定序列化对象的类型。在 dolphindb.settings 中定义了形如 "DT\_XXX"
  的枚举值，用于设置数据类型。指定方式如下：

  - *obj* 是字典或能够转换为字典的数据形式：*types* 是长度为 2
    的列表，其第一个元素表示键的类型，第二个元素表示值的类型。例如：[\_STRING, DT\_INT])
  - *obj* 是 DataFrame 或能够转换为表的数据形式：*types*
    是一个字典，其中，键表示列名，值表示对应列的类型。例如：{'col1': DT\_STRING, 'col2': DT\_INT}。
  - 其它情况：

    - *types* 可以是一个整型（枚举值）。例如：DT\_INT，不指定小数位数的 Decimal 类型
      DT\_DECIMAL32
    - 长度为2的整型列表，第一个元素表示数据类型，第二个元素是额外参数，通常为 Decimal
      类型指定小数位数，例如：指定小数位数的 Decimal 类型 [DT\_DECIMAL32, 2]。

**返回值：**bytes，序列化后的二进制字节串。

## loads

从字节串中反序列化一个对象，并返回该对象。

```dolphindb
def loads(data) -> Any
```

**参数**

- data：序列化数据的二进制字节串。

**返回值：**反序列化后的结果。

## 使用示例

引入 dolphindb.io 模块后，可使用序列化接口。

```dolphindb
from dolphindb import io
```

**示例 1**

序列化数据到文件，并读取出来。

```dolphindb
with open("data.bin", "wb") as f:
     io.dump(1, f)

with open("data.bin", "rb") as f:
     re = io.load(f)
     print(re)

# output: 1
```

序列化数据为二进制字节串，并读取出来。

```dolphindb
data = io.dumps(1)
print(data)

# output: b'\x05\x00\x01\x00\x00\x00\x00\x00\x00\x00'

re = io.loads(data)
print(re)
# output: 1
```

**示例 2**

序列化 Decimal 数据为二进制字节串。这里 *types* 仅指定了类型，未指定小数位数。

```dolphindb
from decimal import Decimal
import dolphindb.settings as keys
data = io.dumps(Decimal("1.23"), types=keys.DT_DECIMAL32)
print(data)

# output: b'%\x00\x02\x00\x00\x00{\x00\x00\x00'

re = io.loads(data)
print(re)

# output: Decimal('1.23')
```

通过 *types* 指定类型和精度（scale）。

```dolphindb
data = io.dumps(Decimal("1.23"), types=[keys.DT_DECIMAL32, 4])
print(data)

# output: b'%\x00\x04\x00\x00\x00\x0c0\x00\x00'

re = io.loads(data)
print(re)

# output: Decimal('1.2300')
```

**示例 3**

序列化一个向量为二进制字节串。

```dolphindb
import dolphindb.settings as keys
import numpy as np
data = io.dumps([1, 2, 3], types=keys.DT_INT)
print(data)

# output: b'\x04\x01\x03\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00'

re = io.loads(data)
print(re)

# output: [1, 2, 3]
```

序列化 AnyVector 为二进制字节串。

```dolphindb
data = io.dumps([[1, 2], [3]], types=keys.DT_ANY)
print(data)

# output: b'\x19\x01\x02\x00\x00\x00\x01\x00\x00\x00\x05\x01\x02\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x05\x01\x01\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00'

re = io.loads(data)
print(re)

# output: [array([1, 2], dtype=int64), array([3], dtype=int64)]
```

序列化一个 ArrayVector 为二进制字节串。

```dolphindb
data = io.dumps([[1, 2], [3]], types=keys.DT_INT_ARRAY)
print(data)

# output: b'D\x01\x02\x00\x00\x00\x03\x00\x00\x00\x02\x00\x01\x00\x02\x01\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00'

re = io.loads(data)
print(re)

# output: [array([1, 2]) array([3])]
```

**示例 4**

序列化一个字典为二进制字节串。

```dolphindb
data = io.dumps({'a': 1, 'b': 2}, types=[keys.DT_STRING, keys.DT_INT])
print(data)

# output: b'\x04\x05\x12\x01\x02\x00\x00\x00\x01\x00\x00\x00b\x00a\x00\x04\x01\x02\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00'

re = io.loads(data)
print(re)

# output: {'a': 1, 'b': 2}
```

序列化一个集合为二进制字节串。

```dolphindb
data = io.dumps({1, 2}, types=keys.DT_INT)
print(data)

# output: b'\x04\x04\x04\x01\x02\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00'

re = io.loads(data)
print(re)

# output: {1, 2}
```

**示例 5**

序列化一个表为二进制字节串。

```dolphindb
import pandas as pd
from decimal import Decimal
df = pd.DataFrame({
     'a': ["a", "b", "c"],
     'b': [1, 2, 3],
     'c': [Decimal("1.1"), Decimal("2.12"), None],
 })

print(df)

""" output:
   a  b     c
0  a  1   1.1
1  b  2  2.12
2  c  3  None
"""
data = io.dumps(df, types={'a': keys.DT_STRING, 'b': keys.DT_INT, 'c': [keys.DT_DECIMAL32, 3]})
re = io.loads(data)
print(re)

""" output:
   a  b      c
0  a  1  1.100
1  b  2  2.120
2  c  3   None
"""
```
