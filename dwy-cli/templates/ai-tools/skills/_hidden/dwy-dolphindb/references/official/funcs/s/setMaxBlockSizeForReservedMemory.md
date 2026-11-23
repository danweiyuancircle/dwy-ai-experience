---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setMaxBlockSizeForReservedMemory.html
fetched_at: 2026-05-19T09:38:41Z
category: funcs
title: setMaxBlockSizeForReservedMemory
sha1: 95597b99963c88f7a213836e1080084fc2e8c2dd
---

# setMaxBlockSizeForReservedMemory

## 语法

`setMaxBlockSizeForReservedMemory(blockSizeKB)`

## 详情

在线修改系统预留内存可以分配的最大内存块大小。该命令只能由管理员在数据节点/计算节点上执行。

请注意，此命令修改的配置值只对当前节点有效，且在系统重启后将失效。若需要配置值永久生效，请更改配置文件中的
*maxBlockSizeForReservedMemory*。

## 参数

**blockSizeKB** 一个数值型标量（单位为KB），必须大于0。
