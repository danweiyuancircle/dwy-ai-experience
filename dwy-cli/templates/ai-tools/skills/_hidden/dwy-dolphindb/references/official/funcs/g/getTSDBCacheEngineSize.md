---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getTSDBCacheEngineSize.html
fetched_at: 2026-05-19T09:26:34Z
category: funcs
title: getTSDBCacheEngineSize
sha1: a7de117c78c3d46baa72c50c0a07cd3f5b4ae4f2
---

# getTSDBCacheEngineSize

## 语法

`getTSDBCacheEngineSize()`

## 详情

查询 TSDB 引擎 Cache Engine 允许使用的内存上限（单位为字节）。

## 参数

无

## 返回值

一个 LONG 类型数据。

## 例子

```dolphindb
setTSDBCacheEngineSize(0.5)
getTSDBCacheEngineSize()
// output: 536870912
```

相关函数： [setTSDBCacheEngineSize](../s/setTSDBCacheEngineSize.html)
