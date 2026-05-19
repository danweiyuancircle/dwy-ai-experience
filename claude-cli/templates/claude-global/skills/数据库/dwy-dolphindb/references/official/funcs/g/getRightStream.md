---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getRightStream.html
fetched_at: 2026-05-19T09:25:43Z
category: funcs
title: getRightStream
sha1: 864c85d6b06466c740c88758ff452ee14e93d907
---

# getRightStream

## 语法

`getRightStream(joinEngine)`

## 详情

返回连接引擎右表的表结构对象。向该对象注入的数据，会注入到 *joinEngine* 中。

通过该函数，可以将一个引擎的计算结果直接注入到连接引擎中，实现引擎间的级联。

使用案例请参考 [getLeftStream](getLeftStream.html)。

## 参数

**joinEngine** 创建连接引擎返回的对象。目前 DolphinDB 支持的连接引擎有：

- createAsofJoinEngine
- createEquiJoinEngine
- createLookupJoinEngine
- createWindowJoinEngine
- createLeftSemiJoinEngine

## 返回值

一个表。
