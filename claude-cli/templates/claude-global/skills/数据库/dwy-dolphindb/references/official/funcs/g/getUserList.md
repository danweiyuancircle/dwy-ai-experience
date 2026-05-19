---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getUserList.html
fetched_at: 2026-05-19T09:26:49Z
category: funcs
title: getUserList
sha1: de79d2c022dd7630d9b0f3e726a7da9b8a826636
---

# getUserList

## 语法

`getUserList()`

## 详情

返回包含除管理员之外的所有用户名称的向量。

注：

该函数只能由管理员在控制节点、数据节点和计算节点运行。

## 返回值

字符串向量。

## 例子

```dolphindb
login(`admin, `123456);
getUserList().sort();
// output: ["AA","AAA","BB","BBB","CC","DeionSanders","EliManning","JoeFlacco"]
```
