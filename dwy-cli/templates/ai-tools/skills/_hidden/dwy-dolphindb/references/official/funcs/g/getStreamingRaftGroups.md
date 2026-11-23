---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getStreamingRaftGroups.html
fetched_at: 2026-05-19T09:26:07Z
category: funcs
title: getStreamingRaftGroups
sha1: 2a162ba61ab67a9d5e55dcb3a136bd4b78bc62f2
---

# getStreamingRaftGroups

## 语法

`getStreamingRaftGroups()`

## 详情

获取当前节点所在的流数据 Raft 组的信息。

## 参数

无

## 返回值

一个表，第一列表示 Raft 组的 id，第二列表示 Raft 组包含的数据节点/计算节点信息。

## 例子

```dolphindb
getStreamingRaftGroups();
```

| id | sites |
| --- | --- |
| 12 | 192.168.1.135:18102:NODE1,192.168.1.135:18103:NODE2,192.168.1.135:18104:NODE3 |
| 11 | 192.168.1.135:18102:NODE1,192.168.1.135:18103:NODE2,192.168.1.135:18105:NODE4 |

使用以下脚本可以获取当前集群所有流数据 Raft 组的信息。

```dolphindb
select id,sites from pnodeRun(getStreamingRaftGroups) where isDuplicated([id,sites],FIRST)=false;
```
