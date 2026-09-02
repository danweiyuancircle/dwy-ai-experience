---
source_url: https://docs.dolphindb.cn/zh/funcs/s/second.html
fetched_at: 2026-05-19T09:38:09Z
category: funcs
title: second
sha1: ad57c81a97ef8fe88e794780f2b765fe196ddb0b
---

# second

## 语法

`second(X)`

## 详情

返回对应的秒数，返回值的类型是 SECOND，一个时间值。

## 参数

**X** 可以是整数/时间类型/字符串类型的标量或向量。

## 返回值

SECOND 类型的标量或向量。

## 例子

```dolphindb
second();
```

返回：null

```dolphindb
second(1)
```

返回：00:00:01

```dolphindb
second("19:36:12");
```

返回：19:36:12

```dolphindb
second(now());
```

返回：16:01:32

```dolphindb
second 2012.12.03 01:22:01;
```

返回：01:22:01

```dolphindb
second(61);
```

返回：00:01:01

```dolphindb
second("09:00:01")
```

返回：09:00:01
