---
source_url: https://docs.dolphindb.cn/zh/funcs/y/year.html
fetched_at: 2026-05-19T09:44:21Z
category: funcs
title: year
sha1: a7dcb7acf04474c3ac28924a871ed64ced7c92d9
---

# year

## 语法

`year(X)`

## 详情

根据输入的值得到其对应的年份。

## 参数

**X** 是一个时间标量或向量。

## 返回值

一个 INT 类型的标量或向量。

## 例子

```dolphindb
year(2012.12.03);
```

返回：2012

```dolphindb
year(2012.12.03 2011.11.05);
```

返回：[2012,2011]

```dolphindb
(2012.12.03).year();
```

返回：2012
