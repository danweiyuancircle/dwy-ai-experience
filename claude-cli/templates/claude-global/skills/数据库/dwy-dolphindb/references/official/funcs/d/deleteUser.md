---
source_url: https://docs.dolphindb.cn/zh/funcs/d/deleteUser.html
fetched_at: 2026-05-19T09:18:43Z
category: funcs
title: deleteUser
sha1: c825c64c63320a0a11241748e1182d5173c278fa
---

# deleteUser

## 语法

`deleteUser(userId)`

## 详情

删除一个用户。

注：

该函数只能由管理员在控制节点、数据节点和计算节点运行。

## 参数

**userId** 是表示用户名的字符串。

## 返回值

无。

## 例子

```dolphindb
deleteUser(`JohnSmith);
```
