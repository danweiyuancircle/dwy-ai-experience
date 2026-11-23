---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getdynamicconfig.html
fetched_at: 2026-05-19T09:23:40Z
category: funcs
title: getDynamicConfig
sha1: 7cfad6a578ce3cdb6c38f41cee6e3e09492c490f
---

# getDynamicConfig

## 语法

`getDynamicConfig()`

## 详情

获取动态配置项的名称。

## 参数

无

## 返回值

返回一个向量，包含所有可以通过 `setDynamicConfig` 在线修改的配置项名。

## 例子

```dolphindb
getDynamicConfig();
// output: ["TSDBVectorIndexCacheSize","TSDBCacheEngineSize","dfsChunkNodeHeartBeatTimeout","reservedMemSize","recoveryWorkers","OLAPCacheEngineSize","memLimitOfTempResult","maxMemSize","memLimitOfAllTempResults","maxPartitionNumPerQuery","memLimitOfTaskGroupResult","memLimitOfQueryResult","maxConnections","maxBlockSizeForReservedMemory","TSDBBlockCacheSize","logLevel","enableNullSafeJoin","enableMultiThreadMerge"]
```
