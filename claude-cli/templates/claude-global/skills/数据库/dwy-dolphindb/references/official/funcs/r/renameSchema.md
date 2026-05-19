---
source_url: https://docs.dolphindb.cn/zh/funcs/r/renameSchema.html
fetched_at: 2026-05-19T09:35:53Z
category: funcs
title: renameSchema
sha1: 4c7b9cf2ae00c1276d12b2b4948c7e3e6f2f6ac1
---

# renameSchema

## 语法

`renameSchema(catalog, oldSchema, newSchema)`

## 详情

重命名 schema。

## 参数

**catalog** 字符串标量，表示 catalog 的名称。

**oldSchema** 字符串标量，表示要修改的 schema 的原名称。

**newSchema** 字符串标量，表示要修改的 schema 的新名称。

## 例子

```dolphindb
renameSchema("catalog1", "schema1", "schema2")
```
