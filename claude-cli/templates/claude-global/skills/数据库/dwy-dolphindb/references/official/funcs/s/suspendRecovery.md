---
source_url: https://docs.dolphindb.cn/zh/funcs/s/suspendRecovery.html
fetched_at: 2026-05-19T09:41:07Z
category: funcs
title: suspendRecovery
sha1: 4f919a86a5731a466dcd45c8c6405b1022342c3d
---

# suspendRecovery

## 语法

`suspendRecovery()`

## 详情

用于暂停在线恢复节点的进程。恢复进程中，处于 "In-Progress" 状态的数据会继续恢复，"Waiting"
状态的数据会暂停恢复。暂停后，恢复进程的源节点可以继续写入数据。该函数只能由管理员在控制节点上调用。

注：

启用高可用集群时，需要在 raft 组内每个节点执行该命令。

相关命令： [resumeRecovery](../r/resumeRecovery.html)
