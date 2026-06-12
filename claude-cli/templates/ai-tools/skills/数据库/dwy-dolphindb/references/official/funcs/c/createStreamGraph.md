---
source_url: https://docs.dolphindb.cn/zh/funcs/c/createStreamGraph.html
fetched_at: 2026-05-19T09:17:02Z
category: funcs
title: createStreamGraph
sha1: 1c052ea7204871e1fcc355f23ca9b8ff65d2e729
---

# createStreamGraph

首发版本：3.00.3

## 语法

`createStreamGraph(name)`

## 详情

创建一个声明式流图，支持以下功能：

- 控制流图的生命周期（如初始化、运行、销毁）；
- 配置订阅与私有流表的行为；
- 定义数据源（如持久化流表、高可用流数据表、流计算引擎等）。

## 参数

**name** 字符串标量，表示流图的名字。可以传入完整的流图全限定名（如
"catalog\_name.orca\_graph.graph\_name"），也可以仅提供流图名（如 "factors"）；系统会根据当前的 catalog
设置自动补全为对应的全限定名。

## 返回值

StreamGraph 对象。

## 例子

创建一个名为 indicators 的流图。

```dolphindb
if (!existsCatalog("orca")) {
	createCatalog("orca")
}
go
use catalog orca

g = createStreamGraph("indicators")
```

**相关函数：**[dropStreamGraph](../d/dropStreamGraph.html), [startStreamGraph](../s/startStreamGraph.html), [stopStreamGraph](../s/stopStreamGraph.html), [StreamGraph::dropGraph](../s/StreamGraph_dropGraph.html)
