---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getSchemaByCatalog.html
fetched_at: 2026-05-19T09:25:47Z
category: funcs
title: getSchemaByCatalog
sha1: 93b100bd8379ceec65d4d7f2c7a302459f6e43b9
---

# getSchemaByCatalog

## 语法

`getSchemaByCatalog(catalog)`

## 详情

检索指定 catalog 中的所有 schema。

## 参数

**catalog** 字符串标量，表示 catalog 的名称。

## 返回值

一个 Table，包含 schema 的名称（schema）和对应路径（dbUrl）。

## 例子

```dolphindb
getSchemaByCatalog("catalog1")
```

返回：

| schema | dbUrl |
| --- | --- |
| schema1 | dfs://db1 |
| schema2 | dfs://db2 |
