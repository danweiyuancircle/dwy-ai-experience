---
source_url: https://docs.dolphindb.cn/zh/funcs/s/symbol.html
fetched_at: 2026-05-19T09:41:09Z
category: funcs
title: symbol
sha1: b077df0be8a688e528daf0f72f78910b86402c54
---

# symbol

## 语法

`symbol(X)`

## 详情

把输入转换为一个符号向量。

## 参数

**X** 是字符串或符号的向量。

## 返回值

一个 SYMBOL 向量。

## 例子

```dolphindb
x=`XOM`y;
typestr(x);
```

返回：STRING VECTOR

```dolphindb
y=symbol(x);
y;
```

返回：["XOM","y"]

```dolphindb
typestr(y);
```

返回：FAST SYMBOL VECTOR
