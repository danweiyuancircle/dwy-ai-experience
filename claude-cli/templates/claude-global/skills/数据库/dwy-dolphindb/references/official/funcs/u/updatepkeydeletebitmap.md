---
source_url: https://docs.dolphindb.cn/zh/funcs/u/updatepkeydeletebitmap.html
fetched_at: 2026-05-19T09:43:24Z
category: funcs
title: updatePKEYDeleteBitmap
sha1: a529579c754c90230f3d45fefa977e8999685534
---

# updatePKEYDeleteBitmap

## 语法

`updatePKEYDeleteBitmap(chunkId)`

## 详情

更新 PKEY 引擎的 delete bitmap，完成后清空主键的暂存缓冲区。

## 参数

**chunkId** STRING 类型标量或向量，表示 chunk 对应的 ID。

## 返回值

无。

## 例子

```dolphindb
updatePKEYDeleteBitmap(chunkId="1486f935-6f87-479c-b341-34c6a303d4f9")
```
