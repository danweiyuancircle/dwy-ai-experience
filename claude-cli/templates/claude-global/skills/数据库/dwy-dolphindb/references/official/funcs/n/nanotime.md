---
source_url: https://docs.dolphindb.cn/zh/funcs/n/nanotime.html
fetched_at: 2026-05-19T09:33:07Z
category: funcs
title: nanotime
sha1: cfd288a519f3b5bd0414d896965923755d29b690
---

# nanotime

## 语法

`nanotime(X)`

## 详情

返回相应的纳秒。返回值类型是 NANOTIME，时间类型的变量。

## 参数

**X** 可以是整型标量或向量、时间标量或向量。

## 返回值

NANOTIME 类型标量或向量。

## 例子

```dolphindb
nanotime(1000000000);
```

返回：00:00:01.000000000

```dolphindb
nanotime(12:06:09 13:08:01);
```

返回：[12:06:09.000000000,13:08:01.000000000]

```dolphindb
nanotime(2012.12.03 01:22:01.123456789);
```

返回：01:22:01.123456789

```dolphindb
nanotime('13:30:10.008007006');
```

返回：13:30:10.008007006
