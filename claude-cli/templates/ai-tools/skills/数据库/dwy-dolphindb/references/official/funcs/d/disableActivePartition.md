---
source_url: https://docs.dolphindb.cn/zh/funcs/d/disableActivePartition.html
fetched_at: 2026-05-19T09:19:00Z
category: funcs
title: disableActivePartition
sha1: 8936d97cd676f58b1b4410b485cb42d79e6b793d
---

# disableActivePartition

## 语法

`disableActivePartition(dbHandle)`

## 详情

断开与历史数据库的连接。

## 参数

**dbHandle** 是历史数据库的句柄。

## 返回值

无。

## 例子

```dolphindb
histdb = database("C:\DolphinDBDemo\example\data\dbspace\historical-A\Trades2ndDomain")
activeNodeAlias = getNodeAlias()
activeDate = today()
enableActivePartition(histdb, activeDate, activeNodeAlias);

disableActivePartition(histdb);
```
