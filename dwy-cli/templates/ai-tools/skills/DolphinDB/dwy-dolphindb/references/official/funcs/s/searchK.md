---
source_url: https://docs.dolphindb.cn/zh/funcs/s/searchK.html
fetched_at: 2026-05-19T09:38:06Z
category: funcs
title: searchK
sha1: d25433d995275411607b9cf1fe632b360729cb43
---

# searchK

## 语法

`searchK(X, k)`

## 详情

返回第 *k* 小的元素，忽略 NULL 值。

## 参数

**X** 是一个向量。

## 返回值

数据类型与 *X* 相同的标量。

## 例子

```dolphindb
searchK(1 7 3 5 3 9 6 1 NULL, 1);
```

输出返回：1

```dolphindb
searchK(1 7 3 5 3 9 6 1 NULL, 2);
```

输出返回：1

```dolphindb
searchK(1 7 3 5 3 9 6 1 NULL, 3);
```

输出返回：3
