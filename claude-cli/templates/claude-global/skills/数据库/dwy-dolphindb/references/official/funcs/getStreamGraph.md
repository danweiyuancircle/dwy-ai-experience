---
source_url: https://docs.dolphindb.cn/zh/funcs/getStreamGraph.html
fetched_at: 2026-05-19T09:26:02Z
category: funcs
title: getStreamGraph
sha1: 2b55af974c32b17bd42f5f3cea7378f7f8da2e50
---

# getStreamGraph

首发版本：3.00.3

## 语法

`getStreamGraph(name)`

## 详情

获取已提交的流图对象。

## 参数

**name** 字符串标量，表示流图的名字。可以传入完整的流图全限定名（如
"catalog\_name.orca\_graph.graph\_name"），也可以仅提供流图名（如 "factors"）；系统会根据当前的 catalog
设置自动补全为对应的全限定名。

## 返回值

流图（StreamGraph）对象。

## 例子

```dolphindb
g = getStreamGraph("demo.orca_graph.indicators")
g;
// output: '<Instance of Class '::StreamGraph'>'
```
