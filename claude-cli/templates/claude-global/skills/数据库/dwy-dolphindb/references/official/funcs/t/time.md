---
source_url: https://docs.dolphindb.cn/zh/funcs/t/time.html
fetched_at: 2026-05-19T09:41:40Z
category: funcs
title: time
sha1: a865f7840e2c59236a54ee5f834800a0bf3c70d0
---

# time

## 语法

`time(X)`

## 详情

返回毫秒精度时间。

## 参数

**X** 是一个时间标量/向量。

## 返回值

TIME 类型标量或向量。

## 例子

```dolphindb
time();
```

返回：null

```dolphindb
time(1)
```

返回：00:00:00.001

```dolphindb
time("12:32:56.356");
```

返回：12:32:56.356

```dolphindb
time(now());
```

返回：16:03:36.529
