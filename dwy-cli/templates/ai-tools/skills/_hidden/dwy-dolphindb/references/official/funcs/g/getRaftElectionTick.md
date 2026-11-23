---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getRaftElectionTick.html
fetched_at: 2026-05-19T09:25:34Z
category: funcs
title: getRaftElectionTick
sha1: 15aad1f192027289e5621df61a8c446de49c4396
---

# getRaftElectionTick

## 语法

`getRaftElectionTick(groupId)`

## 详情

获取 group ID 对应的 raft 组当前有效的 election tick，即通过 `setRaftElectionTick`
设置的 *tickCount* 或配置项 *raftElectionTick* 的设置值。

## 参数

**groupId** 是一个正整数，表示 raft 组的 ID，目前只能是1，表示控制节点组成的 raft 组 ID。

## 返回值

整型标量。

相关函数： [setRaftElectionTick](../s/setRaftElectionTick.html), [getControllerElectionTick](getControllerElectionTick.html)
