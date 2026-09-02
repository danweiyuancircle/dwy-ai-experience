---
source_url: https://docs.dolphindb.cn/zh/funcs/g/generateuserticket.html
fetched_at: 2026-05-19T09:22:26Z
category: funcs
title: generateUserTicket
sha1: e64cddeedde9b6003168ba2742183f6cae7a6fc3
---

# generateUserTicket

首发版本：3.00.3

## 语法

`generateUserTicket(userName, expire)`

## 详情

管理员用户可使用此函数
为指定用户生成动态登录口令，并可设置口令过期时间。用户可使用该口令，通过`authenticateByTicket(ticket)`进行免密登录。

## 参数

**userName** 是一个 STRING 标量，表示要生成登录口令的用户名。

**expire** 是一个 DATETIME 标量，表示登录口令的过期时间。

## 返回值

字符串标量。

## 例子

```dolphindb
login("admin", "123456")
createUser("user1", "123456")
tik = generateUserTicket("user1", 2030.12.31T12:00:00)
authenticateByTicket(tik)
//查看当前用户
getCurrentSessionAndUser() 
// output: (1659657455,"user1","192.168.1.177",57958)
```
