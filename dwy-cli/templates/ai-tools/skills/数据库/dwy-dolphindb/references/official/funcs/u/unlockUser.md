---
source_url: https://docs.dolphindb.cn/zh/funcs/u/unlockUser.html
fetched_at: 2026-05-19T09:43:10Z
category: funcs
title: unlockUser
sha1: bcf48c288d4032ccea182d020ad68d9dfde631aa
---

# unlockUser

首发版本：3.00.3

## 语法

`unlockUser(userId)`

## 详情

解锁用户 *userId*。该函数仅限管理员用户调用，调用时须开启配置项 *enhancedSecurityVerification*。

## 参数

**userId** 是表示用户名的字符串。

## 返回值

无。

## 例子

```dolphindb
unlockUser("user1")
```

相关函数：[lockUser](../l/lockUser.html)
