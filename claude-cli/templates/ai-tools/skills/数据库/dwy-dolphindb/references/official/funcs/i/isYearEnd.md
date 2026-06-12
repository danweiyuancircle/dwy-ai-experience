---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isYearEnd.html
fetched_at: 2026-05-19T09:29:02Z
category: funcs
title: isYearEnd
sha1: a57f7de8657818c4d94fa89688a636d92dc2d07b
---

# isYearEnd

## 语法

`isYearEnd(X)`

## 详情

判断 *X* 是否为年末最后一天。

## 参数

**X** 可以是 DATE, DATEHOUR, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

布尔标量或向量。

## 例子

```dolphindb
isYearEnd(2012.12.31);
// output: true

isYearEnd([2012.12.30,2012.12.31]);
// output: [false,true]
```

相关函数：[isYearStart](isYearStart.html)
