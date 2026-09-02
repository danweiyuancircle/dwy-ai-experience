---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getenablenullsafejoin.html
fetched_at: 2026-05-19T09:23:41Z
category: funcs
title: getEnableNullSafeJoin
sha1: dac986e1087b0e4567700f5b4cdff1d6d914cf4f
---

# getEnableNullSafeJoin

首发版本：3.00.3

## 语法

`getEnableNullSafeJoin()`

## 详情

返回在线修改后的 *enableNullSafeJoin* 的配置值。配置详情请参考文档 [DolphinDB-功能配置](../../db_distr_comp/cfg/function_configuration.html)。

## 参数

无

## 返回值

BOOL 类型标量。

## 例子

```dolphindb
// 设置 enableNullSafeJoin 为 true
setDynamicConfig("enableNullSafeJoin", true)
// 查看修改后的配置值
getEnableNullSafeJoin()
// output: true
```
