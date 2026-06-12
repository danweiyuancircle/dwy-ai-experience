---
source_url: https://docs.dolphindb.cn/zh/funcs/s/StreamGraph_name.html
fetched_at: 2026-05-19T09:40:28Z
category: funcs
title: StreamGraph::name
sha1: 2a2a44c178235cdac7dd7a72f7dd41c484583d81
---

# StreamGraph::name

首发版本：3.00.3

## 语法

`StreamGraph::name()`

## 详情

获取流图的全限定名（Fully Qualified Name, FQN）。

## 返回值

STRING 类型标量。

## 例子

获取 [StreamGraph::submit](StreamGraph_submit.html) 函数文档的例子中所提交流图 g
的全限定名：

```dolphindb
g.name()
// Output: 'demo.orca_graph.indicators'
```
