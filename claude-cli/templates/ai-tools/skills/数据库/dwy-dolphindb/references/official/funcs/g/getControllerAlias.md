---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getControllerAlias.html
fetched_at: 2026-05-19T09:23:22Z
category: funcs
title: getControllerAlias
sha1: 997c6c7f4cfe6402653d5bb45c471d85d3cc29ab
---

# getControllerAlias

## 语法

`getControllerAlias()`

## 详情

获取控制节点的别名。该别名定义在由配置参数 config 配置的文件中。

## 参数

无

## 返回值

一个字符串。

## 例子

```dolphindb
getControllerAlias();
// output: master
```

相关函数：[getNodeAlias](getNodeAlias.html)
