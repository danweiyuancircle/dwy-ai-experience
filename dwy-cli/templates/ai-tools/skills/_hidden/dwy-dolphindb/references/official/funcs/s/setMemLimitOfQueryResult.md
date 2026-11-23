---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setMemLimitOfQueryResult.html
fetched_at: 2026-05-19T09:38:47Z
category: funcs
title: setMemLimitOfQueryResult
sha1: 9a571f87106353262d1d5f77dcf1f782d04ab8f0
---

# setMemLimitOfQueryResult

## 语法

`setMemLimitOfQueryResult(memLimit)`

## 详情

在线修改单次查询结果占用的最大内存上限。该命令只能由管理员在数据节点/计算节点执行。

相关函数： [getMemLimitOfQueryResult](../g/getMemLimitOfQueryResult.html)

## 参数

**memLimit** 数值类型标量，表示内存上限，单位为 GB。该值必须小于 80% \* maxMemSize。
