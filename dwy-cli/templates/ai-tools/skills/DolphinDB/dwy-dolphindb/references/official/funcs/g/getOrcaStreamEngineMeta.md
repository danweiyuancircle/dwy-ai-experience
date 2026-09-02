---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getOrcaStreamEngineMeta.html
fetched_at: 2026-05-19T09:25:20Z
category: funcs
title: getOrcaStreamEngineMeta
sha1: f1fdc8b5a8297393c9ff7aa9594e2e517f976ba7
---

# getOrcaStreamEngineMeta

首发版本：3.00.3

## 语法

`getOrcaStreamEngineMeta(name)`

## 详情

获取指定流图中所有流引擎的元信息。

## 参数

**name** 字符串标量，表示流图的名字。可以传入完整的流图全限定名（如
"catalog\_name.orca\_graph.graph\_name"），也可以仅提供流图名（如 "factors"）；系统会根据当前的 catalog
设置自动补全为对应的全限定名。

## 返回值

返回一个表，包含以下字段：

- taskId：引擎所属的任务 id
- name：引擎名称
- type：引擎类型
- schema：引擎输出表的字段类型
- fqn：`setEngineName`定义的全限定名。

## 例子

```dolphindb
getOrcaStreamEngineMeta("streamGraph1") // name 是流图名称
getOrcaStreamEngineMeta("catalog1.orca_graph.streamGraph1") // name 是全限定名
```
