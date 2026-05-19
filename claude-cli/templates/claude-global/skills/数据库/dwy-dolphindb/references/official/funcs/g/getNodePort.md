---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getNodePort.html
fetched_at: 2026-05-19T09:25:07Z
category: funcs
title: getNodePort
sha1: 2fcc9ec106ce630c633a7ad9aa9c91836729a8f4
---

# getNodePort

## 语法

`getNodePort()`

## 详情

获取节点使用的端口号。该端口号为配置参数 *localSite* 中定义的 port。

## 参数

无

## 返回值

INT 类型标量。

## 例子

```dolphindb
getNodePort();

// output: 8888
```
