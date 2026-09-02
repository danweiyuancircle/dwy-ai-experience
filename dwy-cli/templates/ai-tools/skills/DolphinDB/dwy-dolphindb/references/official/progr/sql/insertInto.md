---
source_url: https://docs.dolphindb.cn/zh/progr/sql/insertInto.html
fetched_at: 2026-05-19T09:03:09Z
category: progr
title: insert into
sha1: 944ce51a4cbaf2e4add622c4bbd6f1471dafc492
---

# insert into

用于向表插入数据。

注：

若要向分布式表中插入数据，请先调整配置项
enableInsertStatementForDFSTable。

## 语法

```dolphindb
insert into
 
  table_name1 (colName1 [, colName2, ...])
 
  values (X [, Y, ...]) | select col_name(s) from table_name2
```

其中， colName 指定目标表中的列名，可以有以下三种方式：

- 不加引号的列名 `colName`
- 双引号括起来的列名 `"colName"`
- 前加下划线的双引号列名 `_"colName"`

## 例子

使用 VALUE 子句插入

```dolphindb
t=table(`XOM`GS`FB as ticker, 100 80 120 as volume);
t;
```

| ticker | volume |
| --- | --- |
| XOM | 100 |
| GS | 80 |
| FB | 120 |

```dolphindb
insert into t values(`GOOG, 200);
t;
```

| ticker | volume |
| --- | --- |
| XOM | 100 |
| GS | 80 |
| FB | 120 |
| GOOG | 200 |

```dolphindb
insert into t values(`AMZN`NFLX, 300 250);
t;
```

| ticker | volume |
| --- | --- |
| XOM | 100 |
| GS | 80 |
| FB | 120 |
| GOOG | 200 |
| AMZN | 300 |
| NFLX | 250 |

```dolphindb
insert into t values(('AMD','NVDA'), (60 400));
t;
```

| ticker | volume |
| --- | --- |
| XOM | 100 |
| GS | 80 |
| FB | 120 |
| GOOG | 200 |
| AMZN | 300 |
| NFLX | 250 |
| AMD | 60 |
| NVDA | 400 |

上例还有另一种写法，即按照 SQL 标准写法，直接向表 t 传入多行数据。可得结果一致。

```dolphindb
insert into t values ('AMD', 60), ('NVDA', 400);
t;
```

| ticker | volume |
| --- | --- |
| XOM | 100 |
| GS | 80 |
| FB | 120 |
| GOOG | 200 |
| AMZN | 300 |
| NFLX | 250 |
| AMD | 60 |
| NVDA | 400 |

只往部分列插入新的记录：

```dolphindb
insert into t(ticker, volume) values(`UBER`LYFT, 0 0);
t;
```

| ticker | price | volume |
| --- | --- | --- |
| XOM | 98.5 | 100 |
| GS | 12.3 | 80 |
| FB | 40.6 | 120 |
| GOOG | 100.6 | 200 |
| AMZN | 120 | 300 |
| NFLX | 56.6 | 250 |
| AMD | 78.6 | 60 |
| NVDA | 33.1 | 400 |
| UBER |  | 0 |
| LYFT |  | 0 |

自 3.00.5 版本起，insert into 支持使用 SELECT 子句，将查询得到的结果直接插入到目标表中。

```dolphindb
t1 = table(`XOM`GS`FB as ticker, 100 80 120 as volume)
t1
```

| ticker | volume |
| --- | --- |
| XOM | 100 |
| GS | 80 |
| FB | 120 |

```dolphindb
t2 = table(`GOOG`AMZN`NFLX as ticker, 100 80 120 as volume);
t2
```

| ticker | volume |
| --- | --- |
| GOOG | 110 |
| AMZN | 90 |
| NFLX | 150 |

```dolphindb
insert into t1(ticker,volume) select ticker,volume from t2
t1
```

| ticker | volume |
| --- | --- |
| XOM | 100 |
| GS | 80 |
| FB | 120 |
| GOOG | 110 |
| AMZN | 90 |
| NFLX | 150 |

将表中所有列插入，等价于以下两种写法

```dolphindb
insert into t1 select * from t2
```

```dolphindb
insert into t1 t2
```
