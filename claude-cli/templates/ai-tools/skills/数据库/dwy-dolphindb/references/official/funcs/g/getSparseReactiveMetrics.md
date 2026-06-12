---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getSparseReactiveMetrics.html
fetched_at: 2026-05-19T09:25:56Z
category: funcs
title: getSparseReactiveMetrics
sha1: cf6c5e14fa8cdf3a0e208be9a5f43a0aff521f84
---

# getSparseReactiveMetrics

## 语法

`getSparseReactiveMetrics(name)`

## 详情

获取指定稀疏响应式状态引擎当前配置的计算规则。

## 参数

**name** 字符串标量，表示稀疏响应式状态引擎的名字。

## 返回值

返回一个表，结构与 `createSparseReactiveStateEngine` 的 *metrics* 参数相同。

## 例子

```dolphindb
getSparseReactiveMetrics("demoengine")
```

| deviceID | formula | outputMetricKey |
| --- | --- | --- |
| A001 | mavg(value,3) | A001\_1 |
| A002 | mmax(value,3)-mmin(value,3) | A002\_1 |
| A002 | msum(value,3) | A002\_2 |

**相关函数**：[createSparseReactiveStateEngine](../c/createSparseReactiveStateEngine.html), [addSparseReactiveMetrics](../a/addSparseReactiveMetrics.html), [deleteSparseReactiveMetric](../d/deleteSparseReactiveMetric.html)
