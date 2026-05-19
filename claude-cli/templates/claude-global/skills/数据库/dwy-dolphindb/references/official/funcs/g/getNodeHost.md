---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getNodeHost.html
fetched_at: 2026-05-19T09:25:06Z
category: funcs
title: getNodeHost
sha1: 908889f53381740c0f7b8fc973f67ed3d5a1d6a1
---

# getNodeHost

## 语法

`getNodeHost()`

## 详情

获取本地节点的主机名。该主机名为配置参数 *localSite* 中定义的 host。

## 参数

无

## 返回值

字符串标量。

## 例子

```dolphindb
getNodeHost();

// output: 10.6.0.6
```
