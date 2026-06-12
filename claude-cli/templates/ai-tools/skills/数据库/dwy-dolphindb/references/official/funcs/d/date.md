---
source_url: https://docs.dolphindb.cn/zh/funcs/d/date.html
fetched_at: 2026-05-19T09:18:10Z
category: funcs
title: date
sha1: 747d99c695a099ece9488f8357c486ee82cf0f21
---

# date

## 语法

`date(X)`

## 详情

返回对应的日期。返回值的类型是 DATE，一个时间值。如果参数 *X* 不是日期，则返回值是 1970.01.01 +
*X* 天的日期。

## 参数

**X** 可以是时间标量、向量或整数。

## 例子

```dolphindb
date();
```

返回：null

```dolphindb
date(1)
```

返回：1970.01.02

```dolphindb
date(`2011.10.12);
```

返回：2011.10.12

```dolphindb
date(now());
```

返回：2024.02.22

```dolphindb
date 2012.12.03 01:22:01;
```

返回：2012.12.03

```dolphindb
date(2016.03M);
```

返回：2016.03.01
