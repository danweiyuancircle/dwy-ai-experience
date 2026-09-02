---
source_url: https://docs.dolphindb.cn/zh/pydoc/AdvancedOperations/DataTypeCasting/ForceTypeCasting.html
fetched_at: 2026-05-19T09:52:38Z
category: pydoc
title: 强制类型转换
sha1: a1eccaad4346d298c26f38025d5c652d04e45a5e
---

# 强制类型转换

在使用 upload 接口上传 pandas.DataFrame 时，由于 DolphinDB 类型系统与 Python 类型系统不是一一对应的关系，所以无法直接上传部分类型的数据，例如 UUID、IPADDR、SECOND 等类型。

自 1.30.22.1 版本起，Python API 支持强制类型转换。在使用强制类型转换时，需要在待上传的 pandas.DataFrame 上增加属性 \_\_DolphinDB\_Type\_\_，该属性是一个 Python 字典对象，键为列名，值为指定的类型。示例如下：

```dolphindb
import dolphindb as ddb
import pandas as pd
import numpy as np

s = ddb.session()
s.connect("localhost", 8848, "admin", "123456")
df = pd.DataFrame({
    'cint': [1, 2, 3],
    'csymbol': ["aaa", "bbb", "aaa"],
    'cblob': ["a1", "a2", "a3"],
})

s.upload({"df_wrong": df})
print(s.run("schema(df_wrong)")['colDefs'])
```

输出如下：

```dolphindb
      name typeString  typeInt  extra comment
0     cint       LONG        5    NaN        
1  csymbol     STRING       18    NaN        
2    cblob     STRING       18    NaN
```

参考[PROTOCOL\_DDB](PROTOCOL_DDB.html) 可知，如果直接上传 `df`，此时 `cint` 列的 dtype 为 int64，仍会作为 LONG 类型上传；而由于 SYMBOL、BLOB 没有对应的类型，故直接上传的 str 型数据会被视作 STRING 类型。

导入 dolphindb.settings，为待上传的 pandas.DataFrame 添加属性，其字典键为需要指定类型的列名；值为指定的类型，可以是 int 类型或 str 类型（3.0.2.3及以上版本）。示例如下：

```dolphindb
import dolphindb.settings as keys

df.__DolphinDB_Type__ = {
    'cint': keys.DT_INT,
    'csymbol': keys.DT_SYMBOL,
    'cblob': keys.DT_BLOB,
}

s.upload({"df_true": df})
print(s.run("schema(df_true)")['colDefs'])
```

对于 3.0.2.3 及以上版本，以上代码中字典的值可以指定为 str，示例如下：

```dolphindb
import dolphindb.settings as keys

df.__DolphinDB_Type__ = {
    'cint': "INT",
    'csymbol': "SYMBOL",
    'cblob': "BLOB",
}

s.upload({"df_true": df})
print(s.run("schema(df_true)")['colDefs'])
```

输出如下：

```dolphindb
      name typeString  typeInt  extra comment
0     cint        INT        4    NaN        
1  csymbol     SYMBOL       17    NaN        
2    cblob       BLOB       32    NaN
```

再次上传后，由输出结果可知 pandas.DataFrame 的各列都被正确转换为指定的类型。

自 1.30.22.4 版本起，Python API 支持指定数据类型为 Decimal32 / Decimal64 的精度。使用示例如下：

```dolphindb
from decimal import Decimal
df = pd.DataFrame({
    'decimal32': [Decimal("NaN"), Decimal("1.22")],
    'decimal64': [Decimal("1.33355"), Decimal("NaN")],
})
df.__DolphinDB_Type__ = {
    'decimal32': [keys.DT_DECIMAL32, 2],
    'decimal64': [keys.DT_DECIMAL64, 5],
}

s.upload({'df': df})
print(s.run("schema(df)")['colDefs'])
print('-' * 30)
print(s.run("df"))
```

输出如下：

```dolphindb
    name    typeString  typeInt  extra comment
0  decimal32  DECIMAL32(2)       37      2        
1  decimal64  DECIMAL64(5)       38      5        
------------------------------
    decimal32  decimal64
0        NaN    1.33355
1       1.22        NaN
```

自 3.0.2.3 版本起，新增接口 `get_types_from_schema`，可以获取表结构信息。在上传 pandas.DataFrame 时，通过该接口为其添加 **DolphinDB\_Type** 属性。

**接口说明**

```dolphindb
get_types_from_schema(df_schema_info)
```

- df\_schema\_info：DataFrame 类型，必填。包括以下列：

  - 'name'：列名，str 类型，必填列。
  - 'typeInt'：列类型，int 类型，必填列。
  - 'extra'：列的精度，类型需能转换为 int 类型，选填列。

**示例**

下例首先创建表 t，获取它的 schema。然后通过 `get_types_from_schema` 获取表结构信息（一个字典 type\_dict），最后将为 pandas.DataFrame 添加属性 type\_dict。

```dolphindb
from decimal import Decimal

s.run('t = table(1:0, ["col1", "col2"], [INT, DECIMAL32(3)])')
schema_info = s.run("schema(t)")['colDefs']

type_dict = ddb.utils.get_types_from_schema(schema_info)

df = pd.DataFrame({
    'col1': [1],
    'col2': [Decimal("3.141")],
})
df.__DolphinDB_Type__ = type_dict

s.upload({'df': df})
print(s.run("schema(df)")['colDefs'])
```

输出如下：

```dolphindb
{'col1': ['INT', None], 'col2': ['DECIMAL32', 3]}
---------------------------------------------
   name    typeString  typeInt  extra comment
0  col1           INT        4    NaN        
1  col2  DECIMAL32(3)       37    3.0
```

上传后，由输出结果可知 pandas.DataFrame 的各列都被正确转换为指定的类型。
