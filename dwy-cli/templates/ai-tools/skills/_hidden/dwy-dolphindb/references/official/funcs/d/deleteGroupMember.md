---
source_url: https://docs.dolphindb.cn/zh/funcs/d/deleteGroupMember.html
fetched_at: 2026-05-19T09:18:36Z
category: funcs
title: deleteGroupMember
sha1: 4aad087266e4c07079afc055ff9d043686eb0b68
---

# deleteGroupMember

## 语法

`deleteGroupMember(userIds, groupIds)`

## 详情

删除多个组中的同一个成员，或删除同一个组中的多个成员。

注：

该函数只能由管理员在控制节点、数据节点和计算节点运行。

## 参数

**userIds** 是表示用户名称的字符串标量或向量。

**groupIds** 是表示群组名称的字符串标量或向量。

*userIds* 和 *groupIds* 不能同时为向量。

## 返回值

无。

## 例子

```dolphindb
deleteGroupMember(`AlexEdwards`ElizabethRoberts, `production);
```
