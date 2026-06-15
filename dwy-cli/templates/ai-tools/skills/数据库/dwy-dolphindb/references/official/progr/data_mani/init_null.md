---
source_url: https://docs.dolphindb.cn/zh/progr/data_mani/init_null.html
fetched_at: 2026-05-19T09:02:24Z
category: progr
title: 空值初始化
sha1: 066e9a540da2b83dd390fd06b2d9b872b109b937
---

# 空值初始化

本节介绍 VOID 类型和特定数值类型的空值如何进行初始化。

## VOID 类型空值初始化

VOID 数据类型只能用于标量。不支持直接创建 VOID 类型的向量。

```dolphindb
x=NULL;
typestr x;
// output
VOID

take(NULL, 4);
// output
Not allowed to create void vector
```

不支持向表中添加空值列。

```dolphindb
t = table(rand(10,10) as x)
addColumn(t, `col1, VOID)
Invalid data type: 0
t[`col1]=NULL
Not allowed to create void vector
```

可通过 select NULL 生成表中 VOID 类型的列。

```dolphindb
tmp=select *, NULL from t
typestr(tmp[`NULL])
VOID VECTOR
```

## 特定类型空值初始化

使用00<数据类型符号>对整型，浮点型，以及时间标量进行空值初始化。

初始化一个 NULL 向量，使用 [take](../../funcs/t/take.html) (00<数据类型符号>,
n)，其中 n 为向量中元素数量。

```dolphindb
x=00b;
// b 表示 BOOL 常量
typestr x;
// output
BOOL

bool();
// output
00b
// 如果未提供参数，可以使用如 bool, char, short, int 等类型函数来创建 NULL 标量。

x=00i;
// i 表示 INT 常量

typestr x;
// output
INT

x=00l;
// l 表示 LONG 常量

typestr x;
// output
LONG

x=take(00b, 10);
// 初始化一个含有10个元素的 BOOL 类型空向量。

x;
// output
[,,,,,,,,,]

typestr x;
// output
FAST BOOL VECTOR

x=take(00i, 10)
// 初始化一个含有10个元素的 INT 类型空向量。

x;
// output
[,,,,,,,,,]

x=array(INT, 10, 100, NULL);
// 初始化一个含有10个元素的 INT 类型空向量，初始容量为100。

x;
// output
[,,,,,,,,,]

x=true false NULL true;
x;
// output
[1,0, ,1]

m=matrix(DOUBLE,3,3)*NULL;
m;
```

| #0 | #1 | #2 |
| --- | --- | --- |
|  |  |  |

```dolphindb
shape m;
// output
3:3

typestr m;
// output
DOUBLE MATRIX
```
