---
source_url: https://docs.dolphindb.cn/zh/funcs/i/ipaddr.html
fetched_at: 2026-05-19T09:28:10Z
category: funcs
title: ipaddr
sha1: 048756bc29432faf3daf0094f2f71cabe2a6f35c
---

# ipaddr

## 语法

`ipaddr(X)`

## 详情

把字符串转换成用于表达 IPv4 或 IPv6 地址的 IPADDR 类型数据。

## 参数

**X** 是一个字符串标量或向量。

## 返回值

IPADDR 类型标量或向量。

## 例子

```dolphindb
a=ipaddr("192.168.1.13");
a;
```

返回：192.168.1.13

```dolphindb
typestr(a);
```

返回：IPADDR
