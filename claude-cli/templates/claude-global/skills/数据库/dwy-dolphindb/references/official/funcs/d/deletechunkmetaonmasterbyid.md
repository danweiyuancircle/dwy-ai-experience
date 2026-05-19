---
source_url: https://docs.dolphindb.cn/zh/funcs/d/deletechunkmetaonmasterbyid.html
fetched_at: 2026-05-19T09:18:33Z
category: funcs
title: deleteChunkMetaOnMasterById
sha1: b1426c9c759febed990a7e1d323a90237e6d73a8
---

# deleteChunkMetaOnMasterById

## 语法

`deleteChunkMetaOnMasterById(chunkPath, chunkId)`

## 详情

根据 chunk 的路径和 ID，删除控制节点上该 chunk 的元数据。当数据节点的数据意外丢失，可以调用此函数删除对应 chunk 的元数据。正常情况下删除
chunk 的元数据，会导致无法查询 chunk 数据，但数据依然残留在数据节点，占用磁盘空间。该函数只能由管理员在控制节点执行。

## 参数

**chunkPath** 一个字符串，表示需要删除的 chunk 的路径。

**chunkId** 一个字符串，表示需要删除的 chunk 的 ID。

## 返回值

无。

## 例子

```dolphindb
deleteChunkMetaOnMasterById(chunkPath="/olap_value/8/40o", chunkId="11d45d2d-a995-7c97-c041-32362f3400d7")
```
