---
source_url: https://docs.dolphindb.cn/zh/funcs/d/decimal128.html
fetched_at: 2026-05-19T09:18:21Z
category: funcs
title: decimal128
sha1: fe1d757452082df14afbb5fdeccac1aafedde7dc
---

# decimal128

## 语法

`decimal128(X, scale)`

## 详情

将输入的数据类型转换为 DECIMAL128 类型。

## 参数

**X** 整型/浮点型/字符串类型标量或向量。

**scale** 整型标量，表示保留的小数位数。

## 返回值

DECIMAL128 类型的标量或向量。

## 例子

```dolphindb
a=decimal128(142, 2)
a
```

返回：142.00

```dolphindb
b=decimal128(1\7, 6)
b
```

返回：0.142857

```dolphindb
a+b
```

返回：142.142857

```dolphindb
a*b
```

返回：20.28569400

```dolphindb
decimal128("3.1415926535", 4)
```

返回：3.1416

一个 DECIMAL 类型向量里的所有元素的类型和 scale 必须相同，例如：

```dolphindb
d1=[1.23$DECIMAL128(4), 3$DECIMAL128(4), 3.14$DECIMAL128(4)];
```

返回：[1.2300,3.0000,3.1400]

```dolphindb
typestr(d1);
```

返回：FAST DECIMAL128 VECTOR

如果元素的 scale 不同，则会创建并输出元组：

```dolphindb
d2=[1.23$DECIMAL128(4), 3$DECIMAL128(4), 3.14$DECIMAL128(3)];
```

返回：(1.2300,3.0000,3.140)

```dolphindb
typestr(d2);
```

返回：ANY VECTOR
