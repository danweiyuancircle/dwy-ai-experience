---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getNodeAlias.html
fetched_at: 2026-05-19T09:25:05Z
category: funcs
title: getNodeAlias
sha1: 62c4d3e98ded5ab96f6970d406fd679ec29918f2
---

# getNodeAlias

## 语法

`getNodeAlias()`

## 详情

获取本地节点的别名。该别名为配置参数 *localSite* 中定义的 alias。

## 参数

无

## 返回值

字符串标量。

## 例子

```dolphindb
getNodeAlias();

// output: controller2
```

相关函数：[getControllerAlias](getControllerAlias.html)
