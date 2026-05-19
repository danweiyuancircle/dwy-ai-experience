---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getDFSDatabases.html
fetched_at: 2026-05-19T09:23:33Z
category: funcs
title: getDFSDatabases
sha1: 4e3fd5e509b975c3d5d0ccfd24251121035662c6
---

# getDFSDatabases

## 语法

`getDFSDatabases()`

## 详情

查询当前节点上的分布式数据库。

2.00.9 版本起，

- 当该函数由管理员或拥有 DB\_MANAGE 权限的用户执行时，返回当前节点上所有分布式数据库；
- 否则，仅返回该用户有 DB\_OWNER 权限的数据库。

## 参数

无

## 返回值

字符串向量。

## 例子

```dolphindb
getDFSDatabases()
```
