---
source_url: https://docs.dolphindb.cn/zh/funcs/m/minute.html
fetched_at: 2026-05-19T09:31:57Z
category: funcs
title: minute
sha1: 9bc7da607803153bb27d4481ccf71f9cbe49edd1
---

# minute

## 语法

`minute(X)`

## 详情

返回对应的分钟数。

## 参数

**X** 可以是整数标量或向量、时间标量或向量。

## 返回值

MINUTE 类型标量或向量。

## 例子

```dolphindb
minute();
```

返回：null

```dolphindb
minute(1)
```

返回：00:01m

```dolphindb
minute(now());
```

返回：16:02m
