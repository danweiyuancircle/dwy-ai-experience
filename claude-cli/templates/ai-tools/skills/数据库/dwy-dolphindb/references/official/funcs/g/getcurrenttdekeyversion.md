---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getcurrenttdekeyversion.html
fetched_at: 2026-05-19T09:23:26Z
category: funcs
title: getCurrentTDEKeyVersion
sha1: 6f8a56b5983783dd9e7d83737cbfbc59e4979850
---

# getCurrentTDEKeyVersion

首发版本：3.00.3

## 语法

`getCurrentTDEKeyVersion()`

## 详情

获取当前应用的 TDE 密钥版本。仅 Linux 系统支持该功能。

## 参数

无

## 返回值

LONG 类型标量。

## 例子

```dolphindb
getCurrentTDEKeyVersion()
// output: long(3,698,850,997)
```
