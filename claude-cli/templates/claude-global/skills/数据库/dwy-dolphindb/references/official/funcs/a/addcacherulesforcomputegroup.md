---
source_url: https://docs.dolphindb.cn/zh/funcs/a/addcacherulesforcomputegroup.html
fetched_at: 2026-05-19T09:12:33Z
category: funcs
title: addCacheRulesForComputeGroup
sha1: 734fdb7d839828b2c63d9e0af407cd49cde2f6f2
---

# addCacheRulesForComputeGroup

首发版本：3.00.5

## 语法

`addCacheRulesForComputeGroup(name, tableNames)`

## 详情

为计算组增加缓存规则，指定需要在计算组缓存路径中进行缓存的表。

## 参数

**name** 字符串标量，指定需要增加缓存规则的计算组。

**tableNames**
字符串标量或向量，指定需要在计算组缓存路径中进行缓存的表，以库名/表名的形式拼接，例如"dfs://compute\_test/tb1"。暂不支持通配符。

## 返回值

无

## 例子

```dolphindb
addCacheRulesForComputeGroup("cgroup1", "dfs://compute_test/tb1")

addCacheRulesForComputeGroup("cgroup1", ["dfs://compute_test/tb1", "dfs://compute_test/tb2"])
```

**相关函数：**[removeCacheRulesForComputeGroup](../r/removecacherulesforcomputegroup.html)、[getCacheRulesForComputeGroup](../g/getcacherulesforcomputegroup.html)
