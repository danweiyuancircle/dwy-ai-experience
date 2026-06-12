---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getmemlimitofalltempresults.html
fetched_at: 2026-05-19T09:25:01Z
category: funcs
title: getMemLimitOfAllTempResults
sha1: c54655997d8717410d377e5663c39ebc3347a0b4
---

# getMemLimitOfAllTempResults

## 语法

`getMemLimitOfAllTempResults()`

## 详情

获取分布式查询操作（例如表连接、GROUP BY、CONTEXT BY、PIVOT BY）产生的临时表可以占用的内存上限。

## 参数

无

## 返回值

DOUBLE 类型标量。

## 例子

```dolphindb
getMemLimitOfAllTempResults()
// output: 3.0
```

相关函数：[setMemLimitOfAllTempResults](../s/setmemlimitofalltempresults.html)
