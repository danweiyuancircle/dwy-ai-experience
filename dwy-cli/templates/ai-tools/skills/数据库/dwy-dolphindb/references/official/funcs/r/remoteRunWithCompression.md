---
source_url: https://docs.dolphindb.cn/zh/funcs/r/remoteRunWithCompression.html
fetched_at: 2026-05-19T09:35:40Z
category: funcs
title: remoteRunWithCompression
sha1: fee32fc5eebbd69d3ca57f9d529a1c585591550f
---

# remoteRunWithCompression

## 语法

`remoteRunWithCompression(conn, script, args)`

## 详情

和 [remoteRun](remoteRun.html) 功能和用法基本一致，唯一不同的是
`remoteRunWithCompression` 在传输时对脚本中大于 1024 行的表数据进行了压缩。

## 参数

**conn** 是远程数据库的连接句柄。

**script** 是要执行的脚本或函数名。

**args** 可选参数，如果 *script* 是函数名，*args* 是函数的参数。

## 返回值

*script* 的执行结果。
