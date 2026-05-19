---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getGroupsByUserId.html
fetched_at: 2026-05-19T09:23:51Z
category: funcs
title: getGroupsByUserId
sha1: 781932c796a6805a9e58c671def8a359fd2bfa10
---

# getGroupsByUserId

## 语法

`getGroupsByUserId(userId)`

## 详情

查询用户所在的组。

注：

该函数只能由管理员在控制节点、数据节点和计算节点运行。

## 参数

**userId** 是表示用户名的字符串。

## 返回值

字符串向量。

## 例子

```dolphindb
getGroupsByUserId("admin")

// output: ["MVP","MYMVP"]
```
