---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setsessionexpiredtime.html
fetched_at: 2026-05-19T09:39:02Z
category: funcs
title: setSessionExpiredTime
sha1: a37da62bd81ce58f646e45c4f542e22c5220a6fb
---

# setSessionExpiredTime

首发版本：3.00.3

## 语法

`setSessionExpiredTime(expire)`

## 详情

在启用严格安全策略（参见配置项 *strictSecurityPolicy*）时，管理员可通过此函数设置会话过期时间。

## 参数

**expire** 是一个 DURATION 类型的标量，表示会话的有效期限。

## 例子

```dolphindb
setSessionExpiredTime(3600s)  // 设置会话过期时间为1小时
getSessionExpiredTime() // output: 1H
```
