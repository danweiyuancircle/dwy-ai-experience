---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropOrcaStreamTable.html
fetched_at: 2026-05-19T09:19:29Z
category: funcs
title: dropOrcaStreamTable
sha1: e8bcec667d7fbd608513504f89df17d95783c99f
---

# dropOrcaStreamTable

首发版本：3.00.4

## 语法

`dropOrcaStreamTable(name)`

## 详情

删除 Orca 流表。

删除时要求已无流图引用该 Orca 流表（可通过 [getOrcaStreamTableMeta](https://docs.dolphindb.cn/zh/funcs/g/getOrcaStreamTableMeta.html) 查看该流表引用情况。）

注意：调用该函数前，必须先启用 Orca 功能，即在配置文件 cluster.cfg 或 controller.cfg 中配置
`enableORCA=true`）。

## 参数

**name** 待删除的流表名称。字符串标量，可以传入完整的流表全限定名（如 trading.orca\_table.trades）；也可以仅提供流表名（如
trades），系统会根据当前的 catalog 设置自动补全为对应的全限定名。

## 返回值

无。

## 例子

```dolphindb
// 创建 Orca 流表
if(!existsCatalog("demo")){
    createCatalog("demo")
}
go
use catalog demo

createOrcaStreamTable("trade", `time`symbol`price`volume, [DATETIME,SYMBOL,DOUBLE,LONG])

// 删除 Orca 流表
dropOrcaStreamTable("demo.orca_table.trade")
// 或 dropOrcaStreamTable("trade")
```
