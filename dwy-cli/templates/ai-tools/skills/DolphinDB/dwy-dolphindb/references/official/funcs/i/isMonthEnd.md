---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isMonthEnd.html
fetched_at: 2026-05-19T09:28:37Z
category: funcs
title: isMonthEnd
sha1: b139946d65b60a3edcb6c245a86b862e58bd7bfb
---

# isMonthEnd

## 语法

`isMonthEnd(X)`

## 详情

判断 *X* 是否为月末最后一天。

## 参数

**X** 可以是 DATE, DATEHOUR, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

布尔型标量或向量。

## 例子

```dolphindb
isMonthEnd(2012.05.31);
// output: true

isMonthEnd([2012.05.30,2012.05.31]);
// output: [false,true]
```

相关函数：[isMonthStart](isMonthStart.html)
