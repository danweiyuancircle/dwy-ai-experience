---
source_url: https://docs.dolphindb.cn/zh/funcs/g/gmtime.html
fetched_at: 2026-05-19T09:27:00Z
category: funcs
title: gmtime
sha1: 8be152e93f3ba404d1919304f33492f70706dcb2
---

# gmtime

## 语法

`gmtime(X)`

## 详情

把本地时间 *X* 转换成零时区时间，即格林尼治时间（GMT）。

## 参数

**X** 可以是 DATETIME, TIMESTAMP, NANOTIMESTAMP 类型的标量或向量。

## 返回值

与输入的数据类型和形式一致。

## 例子

以下例子在美国东部时区执行：

```dolphindb
gmtime(2018.01.22 10:20:26);

// output: 2018.01.22T15:20:26

gmtime(2017.12.16T13:30:10.008);

// output: 2017.12.16T18:30:10.008
```
