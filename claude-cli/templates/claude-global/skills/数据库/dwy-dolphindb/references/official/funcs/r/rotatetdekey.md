---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rotatetdekey.html
fetched_at: 2026-05-19T09:36:39Z
category: funcs
title: rotateTDEKey
sha1: b0eda8d816a2b307e2ccef8c600adeaa29ee3e72
---

# rotateTDEKey

首发版本：3.00.3

## 语法

`rotateTDEKey(masterKeyPath)`

## 详情

启用静态数据加密密钥轮转以更新 TDE 密钥。该函数必须由管理员在控制节点执行。仅 Linux 系统支持该功能。

系统会使用新的 TDE 密钥对所有加密表的表密钥重新加密，并更新表头文件。如函数报错，请检查密钥路径是否正确，以及文件是否符合密钥格式要求。

## 参数

**masterKeyPath** 字符串标量，指定 TDE 密钥文件的路径。

## 返回值

如果设置成功，函数返回 true。

## 例子

```dolphindb
enableTDEKey(path/to/newKey)
```
