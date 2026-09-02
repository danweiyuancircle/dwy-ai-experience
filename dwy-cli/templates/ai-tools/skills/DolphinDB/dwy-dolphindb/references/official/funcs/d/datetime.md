---
source_url: https://docs.dolphindb.cn/zh/funcs/d/datetime.html
fetched_at: 2026-05-19T09:18:12Z
category: funcs
title: datetime
sha1: 41fe057c62155a2f015ab51c1f592bb5b5e99e03
---

# datetime

## 语法

`datetime(X)`

## 详情

返回日期和精确到秒的时间值。如果参数 *X* 中未包含前述时间类型标量或向量，则返回值是 1970.01.01 +
*X* 秒的日期与时间。

注：

DATETIME 类型的可用时间范围是 [1901.12.13T20:45:53, 2038.01.19T03:14:07]。

自 2.00.12 版本起，支持转换 MONTH 类型的数据。

## 参数

**X** 可以是时间标量或向量，或整数。

## 返回值

返回一个 DATETIME 类型的标量或向量。

## 例子

```dolphindb
datetime(1)
```

返回：1970.01.01 00:00:01

```dolphindb
datetime(2009.11.10);
```

返回：2009.11.10 00:00:00

```dolphindb
typestr datetime(2009.11.10);
```

返回：DATETIME

```dolphindb
datetime(now());
```

返回：2024.02.22 15:55:39

```dolphindb
datetime(2012.01M)
```

返回：2012.01.01T00:00:00
