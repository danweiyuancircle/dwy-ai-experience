---
source_url: https://docs.dolphindb.cn/zh/funcs/l/logout.html
fetched_at: 2026-05-19T09:30:27Z
category: funcs
title: logout
sha1: a393e7170c368c2721b1a07569d7c53ab8286d7d
---

# logout

## 语法

`logout([userId], [sessionOnly=true])`

## 详情

该函数可以在控制节点/数据节点/计算节点上执行。

如果没有指定 *userId*，用户自己退出登录。

如果 *sessionOnly* 为true，用户只退出登录当前会话。

如果 *sessionOnly* 为false，用户会退出登录当前会话、所有的数据节点/计算节点以及控制节点。

管理员可以使其他用户退出登录。如果管理员使用户退出登录，用户会退出登录当前会话、所有的数据节点/计算节点以及控制节点。

## 参数

**userId** 是表示用户名的字符串。注：包含短横线（-）的用户名必须用双引号来包裹，不能用反引号`。

**sessionOnly** 是表示是否退出登录当前会话的布尔值。

## 返回值

无。

## 例子

```dolphindb
logout();

logout(`TomFord);

logout(, false);
```
