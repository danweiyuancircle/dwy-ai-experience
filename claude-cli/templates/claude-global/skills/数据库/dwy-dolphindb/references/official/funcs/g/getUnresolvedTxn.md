---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getUnresolvedTxn.html
fetched_at: 2026-05-19T09:26:43Z
category: funcs
title: getUnresolvedTxn
sha1: 6e62bfbb734444039374eea0f9d1139d60784a5c
---

# getUnresolvedTxn

## 语法

`getUnresolvedTxn()`

## 详情

获取两阶段提交协议中处于决议状态的节点及其事务。只能由管理员在控制节点执行。

## 参数

无

## 返回值

返回一个表，包含以下字段：

- tid：事务 id。
- cid：提交的版本号。
- chunkId：chunk 的唯一标识。
- initiatingNode：事务决议的发起节点。
- firstResolutionAt：事务开始决议的时间。
- lastResolutionAt：若事务发生多次决议，则会显示最后一次决议的时间。
