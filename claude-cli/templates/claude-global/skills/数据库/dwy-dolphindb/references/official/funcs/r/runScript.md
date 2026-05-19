---
source_url: https://docs.dolphindb.cn/zh/funcs/r/runScript.html
fetched_at: 2026-05-19T09:37:46Z
category: funcs
title: runScript
sha1: af1674bdc5e473d44e7ccbb7ff04950717e63b5e
---

# runScript

## 语法

`runScript(script)`

## 详情

本地执行一段脚本。该命令必须要用户登录后才能执行。

## 参数

**script** 是字符串，表示需要执行的脚本。

## 例子

```dolphindb
t = table(1..100 as id,201..300 as val1)
script1 = 'dn = "dfs://test";if(existsDatabase(dn)){dropDatabase(dn)};db = database(dn,VALUE,1..10);pt = db.createPartitionedTable(t,`pt,`id).append!(t)'
script2 = 'select * from loadTable("dfs://test",`pt)'
runScript(script1)
runScript(script2)
```
