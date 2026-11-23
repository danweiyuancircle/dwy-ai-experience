---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getAuthenticatedUsers.html
fetched_at: 2026-05-19T09:22:44Z
category: funcs
title: getAuthenticatedUsers
sha1: 9cce80166182c5c69dd65b4b26a6f7575d6fafe7
---

# getAuthenticatedUsers

## 语法

`getAuthenticatedUsers()`

## 详情

获取所有节点已经登录的用户信息。

## 参数

无

## 返回值

返回一个字符串向量，包含所有已登录用户的名称。

## 例子

```dolphindb
getAuthenticatedUsers()
// output
["admin","a1","a3","a2","a4"]
```
