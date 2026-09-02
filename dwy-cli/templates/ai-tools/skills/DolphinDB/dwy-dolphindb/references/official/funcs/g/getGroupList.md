---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getGroupList.html
fetched_at: 2026-05-19T09:23:49Z
category: funcs
title: getGroupList
sha1: 649e7e559b41157011c6ce025486ffe25d467c60
---

# getGroupList

## 语法

`getGroupList()`

## 详情

查询所有用户组。

注：

该函数只能由管理员在控制节点、数据节点和计算节点运行。

## 参数

无

## 返回值

字符串向量。

## 例子

```dolphindb
getGroupList()

// output: ["MVP","MYMVP"]
```
