---
source_url: https://docs.dolphindb.cn/zh/progr/sql/top.html
fetched_at: 2026-05-19T09:03:22Z
category: progr
title: top
sha1: ec226d746f55308d8c1fcdea133172f39da1120c
---

# top

top 子句返回指定数量的记录，从表的第一个记录开始，可以在 top 子句中使用一个标量值或一个范围。范围下标从 0 开始而不是 1，并且不包含结束下标值。

## 例子

```dolphindb
sym = `C`MS`MS`MS`IBM`IBM`C`C`C$SYMBOL
price= 49.6 29.46 29.52 30.02 174.97 175.23 50.76 50.32 51.29
qty = 2200 1900 2100 3200 6800 5400 1300 2500 8800
timestamp = [09:34:07,09:36:42,09:36:51,09:36:59,09:32:47,09:35:26,09:34:16,09:34:26,09:38:12]
t1 = table(timestamp, sym, qty, price);

t1;
```

```dolphindb
select top 3 * from t1;
```

| timestamp | sym | qty | price |
| --- | --- | --- | --- |
| 09:34:07 | C | 2200 | 49.6 |
| 09:36:42 | MS | 1900 | 29.46 |
| 09:36:51 | MS | 2100 | 29.52 |

```dolphindb
select top 2:4 * from t1;
```

| timestamp | sym | qty | price |
| --- | --- | --- | --- |
| 09:36:51 | MS | 2100 | 29.52 |
| 09:36:59 | MS | 3200 | 30.02 |

top 子句中的标量值或范围必须是整型常量，不允许使用变量或表达式。

```dolphindb
x=2;
select top x * from t1;

Syntax Error: [line #2] integer constant expected after keyword top
```

```dolphindb
select top (1+2) * from t1;

Syntax Error: [line #1] integer constant expected after keyword top
```

top 子句不能和 pivot by 子句共同使用，但是可以与 group by, context by 子句共同使用。参考 [contextBy](contextBy.html)。
