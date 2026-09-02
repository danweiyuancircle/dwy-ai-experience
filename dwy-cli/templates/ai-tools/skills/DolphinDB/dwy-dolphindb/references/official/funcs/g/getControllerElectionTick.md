---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getControllerElectionTick.html
fetched_at: 2026-05-19T09:23:23Z
category: funcs
title: getControllerElectionTick
sha1: 12611f25364c137b26a017d4b029b827166ff312
---

# getControllerElectionTick

## 语法

`getControllerElectionTick()`

## 详情

获取控制节点组成的 raft 组的 election tick，即通过 `setRaftElectionTick` 设置的
*tickCount* 或配置项 *raftElectionTick* 的设置值。

## 参数

无

## 返回值

整型标量。

相关函数： [setRaftElectionTick](../s/setRaftElectionTick.html), [getRaftElectionTick](getRaftElectionTick.html)
