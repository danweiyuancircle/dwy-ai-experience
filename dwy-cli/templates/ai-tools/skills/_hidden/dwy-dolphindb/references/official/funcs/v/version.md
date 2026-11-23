---
source_url: https://docs.dolphindb.cn/zh/funcs/v/version.html
fetched_at: 2026-05-19T09:43:43Z
category: funcs
title: version
sha1: 727341868c0c8d8e4c662bbd1f108342d432cc0d
---

# version

## 语法

`version()`

## 详情

返回 DolphinDB 的版本、发布日期，和当前的操作系统版本、特定编译版本（非特定版本不显示）、 CPU
指令集。信息间使用空格隔开。

## 参数

无

## 返回值

STRING 类型标量。

## 例子

```dolphindb
version();
//output: 3.00.0 2024.03.31 LINUX x86_64
```
