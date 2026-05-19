---
source_url: https://docs.dolphindb.cn/zh/funcs/d/DStream_setEngineName.html
fetched_at: 2026-05-19T09:20:11Z
category: funcs
title: DStream::setEngineName
sha1: e58c3b751c23656fda3619a066d1c296d83233c9
---

# DStream::setEngineName

首发版本：3.00.3

## 语法

`DStream::setEngineName(name)`

## 详情

为当前流引擎设置名称。如果系统中已存在同名引擎，则会抛出异常。

## 参数

**name** 表示引擎名称。字符串标量，可以传入完整的全限定名（如
"catalog\_name.orca\_engine.engine\_name"）；或引擎名（如 "engine\_name"），系统会根据当前的 catalog
设置自动补全为对应的全限定名。

## 返回值

返回一个 DStream 对象。
