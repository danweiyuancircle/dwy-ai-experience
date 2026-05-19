---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getStreamingLeader.html
fetched_at: 2026-05-19T09:26:06Z
category: funcs
title: getStreamingLeader
sha1: a7a378dada958ce062401abeb2556f461c38774d
---

# getStreamingLeader

## 语法

`getStreamingLeader(groupId)`

## 详情

获取流数据 Raft 组中的 Leader。

## 参数

**groupId** 是一个整数，表示流数据 Raft 组的 ID

## 返回值

字符串标量。

## 例子

```dolphindb
getStreamingLeader(11);
// output: DFS_NODE2
```
