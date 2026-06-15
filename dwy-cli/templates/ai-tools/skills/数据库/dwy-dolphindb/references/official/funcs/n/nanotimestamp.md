---
source_url: https://docs.dolphindb.cn/zh/funcs/n/nanotimestamp.html
fetched_at: 2026-05-19T09:33:08Z
category: funcs
title: nanotimestamp
sha1: 4def6a27f17455b97b2582d7214d66345a03c5a2
---

# nanotimestamp

## 语法

`nanotimestamp(X)`

## 详情

返回由日期和精确到纳秒的时间组成的时间戳。返回值类型是 NANOTIMESTAMP，时间类型变量。如果参数 *X*
不是日期和时间，则返回值是 1970.01.01 00:00:00.000000000 + *X* 纳秒的时间戳。

注：

自 2.00.12 版本起，支持转换 MONTH 类型的数据。

## 参数

**X** 可以是整型标量或向量、时间标量或向量。

## 返回值

NANOTIMESTAMP 类型标量或向量。

## 例子

```dolphindb
nanotimestamp(1);
```

返回：1970.01.01 00:00:00.000000001

```dolphindb
nanotimestamp(1000000000);
```

返回：1970.01.01 00:00:01.000000000

```dolphindb
nanotimestamp(2012.12.03 12:06:09 2012.12.03 13:08:01);
```

返回：[2012.12.03 12:06:09.000000000,2012.12.03 13:08:01.000000000]

```dolphindb
nanotimestamp(2012.12.03 01:22:01.123456789);
```

返回：2012.12.03 01:22:01.123456789

```dolphindb
nanotimestamp('2012.12.03 13:30:10.008007006');
```

返回：2012.12.03 13:30:10.008007006

```dolphindb
nanotimestamp(now());
```

返回：2024.02.22 16:14:28.627000000

```dolphindb
nanotimestamp(2012.01M)
```

返回：2012.01.01T00:00:00.000000000
