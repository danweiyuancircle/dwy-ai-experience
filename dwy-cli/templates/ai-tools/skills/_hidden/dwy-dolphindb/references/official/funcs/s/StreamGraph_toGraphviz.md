---
source_url: https://docs.dolphindb.cn/zh/funcs/s/StreamGraph_toGraphviz.html
fetched_at: 2026-05-19T09:40:36Z
category: funcs
title: StreamGraph::toGraphviz
sha1: c233fbe623f4dcc14896dd41fe1fd844ec47020c
---

# StreamGraph::toGraphviz

首发版本：3.00.3

## 语法

`StreamGraph::toGraphviz()`

## 详情

以 Graphviz 格式输出流图拓扑结构。

## 返回值

STRING 类型标量。

## 例子

```dolphindb
// g 是流图
g.toGraphviz()

/*
当 g 尚未提交
digraph G {
  "4: demo.orca_table.one_min_indicators" [shape=box];
  "3: engine_3" [shape=ellipse];
  "2: demo.orca_table.one_min_bar" [shape=box];
  "0: demo.orca_table.trade" [shape=box];
  "1: engine_1" [shape=ellipse];
  "3: engine_3" -> "4: demo.orca_table.one_min_indicators";
  "2: demo.orca_table.one_min_bar" -> "3: engine_3";
  "0: demo.orca_table.trade" -> "1: engine_1";
  "1: engine_1" -> "2: demo.orca_table.one_min_bar";
}
*/

/*
当 g 已经提交
digraph G {
  subgraph cluster_graph_2 { subgraph cluster_task_0 { label="task_0" "6: channel_6" [shape=ellipse]; } }
  subgraph cluster_graph_2 { subgraph cluster_task_0 { label="task_0" "3: engine_3" [shape=ellipse]; } }
  subgraph cluster_graph_2 { subgraph cluster_task_0 { label="task_0" "4: demo.orca_table.one_min_indicators" [shape=box]; } }
  subgraph cluster_graph_1 { subgraph cluster_task_2 { label="task_2" "2: demo.orca_table.one_min_bar" [shape=box]; } }
  subgraph cluster_graph_0 { subgraph cluster_task_1 { label="task_1" "0: demo.orca_table.trade" [shape=box]; } }
  subgraph cluster_graph_1 { subgraph cluster_task_2 { label="task_2" "1: engine_1" [shape=ellipse]; } }
  subgraph cluster_graph_1 { subgraph cluster_task_2 { label="task_2" "5: channel_5" [shape=ellipse]; } }
  "6: channel_6" -> "3: engine_3" [label="FORWARD"];
  "3: engine_3" -> "4: demo.orca_table.one_min_indicators" [label="FORWARD"];
  "1: engine_1" -> "2: demo.orca_table.one_min_bar" [label="FORWARD"];
  "0: demo.orca_table.trade" -> "5: channel_5" [label="FORWARD"];
  "5: channel_5" -> "1: engine_1" [label="FORWARD"];
  "2: demo.orca_table.one_min_bar" -> "6: channel_6" [label="FORWARD"];
}
*/
```
