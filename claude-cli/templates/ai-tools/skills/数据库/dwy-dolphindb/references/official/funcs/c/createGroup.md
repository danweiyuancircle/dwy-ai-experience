---
source_url: https://docs.dolphindb.cn/zh/funcs/c/createGroup.html
fetched_at: 2026-05-19T09:16:28Z
category: funcs
title: createGroup
sha1: 6a99b757c5e2f8a8e29850e091b70af85c85f8ee
---

# createGroup

## 语法

`createGroup(groupId, [userIds])`

## 详情

创建组。

组中的用户必须是已经创建了的用户。

注：

该函数只能由管理员在控制节点、数据节点和计算节点运行。

## 参数

**groupId** 是表示组名的字符串。只能包含字母、数字、下划线（\_）、或短横线（-），且必须以字母开头，长度不得超过 30 个字符。

**userId** 是表示组成员的字符串标量或向量。

## 返回值

无。

## 例子

创建组 "production"，并且把用户 "JohnSmith" 添加到该组。

```dolphindb
createGroup(`production, `JohnSmith);
```
