---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropSchema.html
fetched_at: 2026-05-19T09:19:31Z
category: funcs
title: dropSchema
sha1: 355394c4155b432e78e0397c723e93ee0db4dcca
---

# dropSchema

## 语法

`dropSchema(catalog, schema)`

## 详情

删掉指定 catalog 中的指定 schema。

## 参数

**catalog** 字符串标量，表示 catalog 的名称。

**schema** 字符串标量，表示要删除的 schema 的名称。

## 返回值

无。

## 例子

```dolphindb
dropSchema("catalog1", "Schema")
```
