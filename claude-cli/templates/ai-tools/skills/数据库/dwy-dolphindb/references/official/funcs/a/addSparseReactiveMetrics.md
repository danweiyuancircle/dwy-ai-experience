---
source_url: https://docs.dolphindb.cn/zh/funcs/a/addSparseReactiveMetrics.html
fetched_at: 2026-05-19T09:12:50Z
category: funcs
title: addSparseReactiveMetrics
sha1: 62ba60818e48a0c671a7814663c6142e31573ed2
---

# addSparseReactiveMetrics

## 语法

`addSparseReactiveMetrics(name, metrics)`

## 详情

为指定的 SparseReactiveStateEngine 增加稀疏状态计算规则。

## 参数

**name** 字符串标量，表示需要增加计算规则的 SparseReactiveStateEngine 的名称。

**metrics** 是一个表，表示需要新增的规则。表结构与 `createSparseReactiveStateEngine` 的
*metrics* 参数相同。

## 例子

```dolphindb
newMetrics = table(
    ["A003"] as deviceID,
    ["mavg(value,3)"] as formula,
    ["A003_1"] as outputMetricKey
)
addSparseReactiveMetrics("demoengine", newMetrics)
```

**相关函数**：[createSparseReactiveStateEngine](../c/createSparseReactiveStateEngine.html), [getSparseReactiveMetrics](../g/getSparseReactiveMetrics.html), [deleteSparseReactiveMetric](../d/deleteSparseReactiveMetric.html)
