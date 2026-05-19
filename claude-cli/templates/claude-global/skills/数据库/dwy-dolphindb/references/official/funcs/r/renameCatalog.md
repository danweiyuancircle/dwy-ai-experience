---
source_url: https://docs.dolphindb.cn/zh/funcs/r/renameCatalog.html
fetched_at: 2026-05-19T09:35:51Z
category: funcs
title: renameCatalog
sha1: e2a13e51c6144ff55a4b374ed1484beb1cbdd224
---

# renameCatalog

## 语法

`renameCatalog(oldCatalog, newCatalog)`

## 详情

重命名 catalog。

## 参数

**oldCatalog** 字符串标量，表示要修改的 catalog 的原名称。

**newCatalog** 字符串标量，表示要修改的 catalog 的新名称。

## 例子

```dolphindb
renameCatalog("catalog1", "catalog2")
```
