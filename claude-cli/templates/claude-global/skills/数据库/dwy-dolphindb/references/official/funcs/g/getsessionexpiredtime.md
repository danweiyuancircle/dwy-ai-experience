---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getsessionexpiredtime.html
fetched_at: 2026-05-19T09:25:50Z
category: funcs
title: getSessionExpiredTime
sha1: 726c1108f846fd9a8917f53686ffc85129771ca8
---

# getSessionExpiredTime

首发版本：3.00.3

## 语法

`getSessionExpiredTime()`

## 详情

在启用严格安全策略（参见配置项*strictSecurityPolicy*）时，通过此函数查看会话的过期时间。

## 参数

无

## 返回值

空值或 DURATION 类型标量。

## 例子

```dolphindb
getSessionExpiredTime() // output: 1H
```
