---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isQuarterStart.html
fetched_at: 2026-05-19T09:28:49Z
category: funcs
title: isQuarterStart
sha1: 3ff623858d1b2fc1eaa4c5bf0f4c00cd1c1917a0
---

# isQuarterStart

## 语法

`isQuarterStart(X)`

## 详情

判断 *X* 是否为季度第一天。

## 参数

**X** 可以是 DATE, DATEHOUR, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

布尔标量或向量。

## 例子

```dolphindb
isQuarterStart(2012.04.01);
// output: true

isQuarterStart([2012.04.01,2012.05.01]);
// output: [true,false]
```

相关函数：[isQuarterEnd](isQuarterEnd.html)
