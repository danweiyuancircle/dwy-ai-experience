---
source_url: https://docs.dolphindb.cn/zh/funcs/l/listTables.html
fetched_at: 2026-05-19T09:29:50Z
category: funcs
title: listTables
sha1: 3af94547888e001deb953694785ca7d13468e400
---

# listTables

## 语法

`listTables(dbUrl)`

## 详情

返回一个表对象，包含两列，分别为数据库中的表名和物理索引名。

注：

只有表级分区具有物理索引。

## 参数

**dbUrl** 是一个字符串，表示分布式数据库的路径。

## 例子

```dolphindb
listTables(dbPath)
```

| tableName | physicalIndex |
| --- | --- |
| pt1 | 1By |
| pt | 1Bw |
