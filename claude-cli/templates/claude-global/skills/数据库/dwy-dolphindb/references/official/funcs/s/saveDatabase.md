---
source_url: https://docs.dolphindb.cn/zh/funcs/s/saveDatabase.html
fetched_at: 2026-05-19T09:37:51Z
category: funcs
title: saveDatabase
sha1: 63eb4b8d9f2b529eccd1cd0739e664f39dccef84
---

# saveDatabase

## 语法

`saveDatabase(dbHandle)`

## 详情

保存数据库句柄。该命令必须要用户登录后才能执行。这个命令和 [database](../d/database.html) 函数配合使用。

第一次创建数据库之后，我们需要用 `saveDatabase`
命令保存数据库。如果数据库位于一个已经包含了 DolphinDB 表相关文件的目录下，函数 `database`
会重新打开之前创建的数据库，且不需要用 `saveDatabase` 命令保存。

## 参数

**dbHandle** 是 DolphinDB 数据库句柄。

## 例子

```dolphindb
db=database("C:/DolphinDB/")
saveDatabase(db);
```
