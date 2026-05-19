---
source_url: https://docs.dolphindb.cn/zh/funcs/d/deleteGroup.html
fetched_at: 2026-05-19T09:18:35Z
category: funcs
title: deleteGroup
sha1: c96838a48a64a55fa7f3fda09a70f48938da8fae
---

# deleteGroup

## 语法

`deleteGroup(groupName)`

## 详情

删除一个群组。这可能会影响群组内所有成员的权限。

注：

该函数只能由管理员在控制节点、数据节点和计算节点运行。

## 参数

**groupName** 是表示群组名称的字符串。

## 返回值

无。

## 例子

```dolphindb
deleteGroup(`Production);
```
