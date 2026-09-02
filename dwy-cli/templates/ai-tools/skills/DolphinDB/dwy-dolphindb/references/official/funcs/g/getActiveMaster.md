---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getActiveMaster.html
fetched_at: 2026-05-19T09:22:34Z
category: funcs
title: getActiveMaster
sha1: 73abacba62fc4883b4d2b1c99e3b6a5d67852bc3
---

# getActiveMaster

## 语法

`getActiveMaster()`

## 详情

对于普通集群，`getActiveMaster` 函数返回控制节点的别名。

对于包含多个控制节点的集群，`getActiveMaster` 函数返回 Leader
控制节点的别名。

注：

该函数只能在控制节点上执行。

## 参数

无

## 返回值

字符串标量。

## 例子

```dolphindb
getActiveMaster();
// output
controller1
```
