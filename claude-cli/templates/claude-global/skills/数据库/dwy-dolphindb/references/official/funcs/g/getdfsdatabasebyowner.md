---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getdfsdatabasebyowner.html
fetched_at: 2026-05-19T09:23:34Z
category: funcs
title: getDFSDatabasesByOwner
sha1: de104c5c5697a9558f7d7df32549d77128c850c8
---

# getDFSDatabasesByOwner

## 语法

`getDFSDatabasesByOwner(user)`

## 详情

该函数仅限管理员用户执行，查询当前集群中所有由用户 *user* 创建的数据库。

## 参数

**user** STRING 类型标量，表示用户名。

## 返回值

字符串向量。

## 例子

```dolphindb
getDFSDatabasesByOwner(user="user1")
// output:["dfs://tsdb1","dfs://tsdb2"]
```
