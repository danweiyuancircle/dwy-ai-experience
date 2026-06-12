---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getNodeType.html
fetched_at: 2026-05-19T09:25:08Z
category: funcs
title: getNodeType
sha1: 46e41937e68d8d2a267f0968effd1790f5834e5a
---

# getNodeType

## 语法

`getNodeType()`

## 详情

查询节点的类型。0表示数据节点；1表示代理节点；2表示控制器节点；3表示单节点模式；4表示计算节点。

## 参数

无

## 返回值

INT 类型标量。

## 例子

```dolphindb
getNodeType();

// output: 2
```
