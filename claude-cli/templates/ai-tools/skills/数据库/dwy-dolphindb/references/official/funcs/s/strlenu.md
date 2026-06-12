---
source_url: https://docs.dolphindb.cn/zh/funcs/s/strlenu.html
fetched_at: 2026-05-19T09:40:45Z
category: funcs
title: strlenu
sha1: 49e85b96fa57a7eeaaa956969fc7ca90045952a2
---

# strlenu

## 语法

`strlenu(X)`

## 详情

用于获取 Unicode 编码的目标字符串的长度。

## 参数

**X** 是一个字符串标量或向量。

## 返回值

INT 类型标量或向量。

## 例子

```dolphindb
strlenu("高性能分布式时序数据库")
// output
11

strlenu(["高性能分布式时序数据库","DolphinDB"])
// output
[11,9]
```
