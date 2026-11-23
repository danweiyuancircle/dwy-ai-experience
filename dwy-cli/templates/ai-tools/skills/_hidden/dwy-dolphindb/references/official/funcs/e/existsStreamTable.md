---
source_url: https://docs.dolphindb.cn/zh/funcs/e/existsStreamTable.html
fetched_at: 2026-05-19T09:21:23Z
category: funcs
title: existsStreamTable
sha1: 00ffa54365a588ed12c6775d149f9b07c13058bd
---

# existsStreamTable

## 语法

`existsStreamTable(tableName)`

## 详情

查询指定的流数据表是否存在。

## 参数

**tableName** 字符串，表示流数据表名称。可以是普通流表、共享流表、持久化流表或高可用流表。

## 返回值

布尔类型标量。true 表示该流数据表存在；false 表示该数据表不存在。

## 例子

```dolphindb
id=`XOM`GS`AAPL
x=102.1 33.4 73.6
rt=streamTable(id, x);
existsStreamTable(`rt)
```

返回：true

```dolphindb
existsStreamTable(`srt)
```

返回：false

```dolphindb
share rt as srt
existsStreamTable(`srt)
```

返回：true
