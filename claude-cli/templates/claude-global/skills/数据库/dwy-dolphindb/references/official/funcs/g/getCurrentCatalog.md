---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getCurrentCatalog.html
fetched_at: 2026-05-19T09:23:24Z
category: funcs
title: getCurrentCatalog
sha1: 25e1a6db8487b8cae3336b5d21dfba88b3ca2e3f
---

# getCurrentCatalog

## 语法

`getCurrentCatalog()`

## 详情

查看当前 session 位于哪个 catalog 中。返回一个字符串。

## 参数

无

## 返回值

一个字符串。

## 例子

```dolphindb
select * from cat1.db1.table1 // 成功
select * from db1.table1 // 报错

use CATALOG cat1;

select * from db1.table1 // 成功
getCurrentCatalog() // Output:"cat1"
```
