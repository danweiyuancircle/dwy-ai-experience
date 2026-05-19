---
source_url: https://docs.dolphindb.cn/zh/funcs/m/month.html
fetched_at: 2026-05-19T09:32:17Z
category: funcs
title: month
sha1: 7c36e53d41fc083501937ce17a376ebf21194630
---

# month

## 语法

`month(X)`

## 详情

返回对应的月份。

## 参数

**X** 可以是时间标量或向量。

## 返回值

MONTH 类型标量或向量。

## 例子

```dolphindb
month();
```

返回：null

```dolphindb
month(`2012.12);
```

返回：2012.12M

```dolphindb
month(2012.12.23);  // 把一个 DATE 类型的数据转换成 MONTH 类型。
```

返回：2012.12M

```dolphindb
month(now());  // 把一个 TIMESTAMP 类型的数据转换成 MONTH 类型。
```

返回：2024.02M
