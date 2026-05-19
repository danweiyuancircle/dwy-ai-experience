---
source_url: https://docs.dolphindb.cn/zh/funcs/l/lockUser.html
fetched_at: 2026-05-19T09:30:17Z
category: funcs
title: lockUser
sha1: 39645f376fa66fe4281500f2fd6b75434c4c1bcd
---

# lockUser

首发版本：3.00.3

## 语法

`lockUser(userId)`

## 详情

锁定用户 *userId*。该函数仅限管理员用户调用，调用时须开启配置项 *enhancedSecurityVerification*。

## 参数

**userId** 是表示用户名的字符串。

## 返回值

无。

## 例子

```dolphindb
lockUser("user1")
```

相关函数：[unlockUser](../u/unlockUser.html)
