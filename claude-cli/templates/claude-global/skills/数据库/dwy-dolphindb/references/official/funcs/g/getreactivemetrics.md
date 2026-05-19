---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getreactivemetrics.html
fetched_at: 2026-05-19T09:25:36Z
category: funcs
title: getReactiveMetrics
sha1: c1e69e24e675a685c644c02bf6ed4ac62fd856ff
---

# getReactiveMetrics

## 语法

`getReactiveMetrics(name)`

### 详情

获取指定名称的 narrowReactiveStateEngine 的计算指标列。

### 参数

**name** 字符串，表示 narrowReactiveStateEngine 的名称。

### 返回值

返回一个表，第一列为 metricName，第二列为 metricCode。

### 例子

```dolphindb
dummy = streamTable(1:0, ["securityID1","securityID2","securityID3","createTime","updateTime","upToDatePrice","qty","value"], [STRING,STRING,STRING,TIMESTAMP,TIMESTAMP,DOUBLE,DOUBLE,INT]) 
outputTable = streamTable(1:0,["securityID1","securityID2","securityID3","createTime","updateTime","metricNames","factorValue"], [STRING,STRING,STRING, TIMESTAMP,TIMESTAMP,STRING,DOUBLE])
factor = [<createTime>, <updateTime>,<cumsum(qty)>]
Narrowtest = createNarrowReactiveStateEngine(name="narrowtest1",metrics=factor,metricNames="factor1",dummyTable=dummy,outputTable=outputTable,keyColumn=["securityID1","securityID2","securityID3"])
getReactiveMetrics("narrowtest1")
```

| metricName | metricCode |
| --- | --- |
| factor1 | cumsum(qty) |

相关函数：[createNarrowReactiveStateEngine](../c/createnarrowreactivestateengine.html)，[addReactiveMetrics](../a/addreactivemetrics.html)
