---
source_url: https://docs.dolphindb.cn/zh/progr/sql/crossjoin.html
fetched_at: 2026-05-19T09:03:54Z
category: progr
title: cross join
sha1: 52a310a52255fd34df5bea648b2daa36511900c5
---

# cross join

## 语法

```dolphindb
cj(leftTable, rightTable)
```

## 参数

**leftTable** 和 **rightTable** 是连接的表。

在DolphinDB中，该语句的使用兼容 SQL 的语法：

```dolphindb
select column_name(s) from leftTable cross join rightTable
```

## 详情

交叉连接函数返回两张表的笛卡尔积的结果集。如果左表有n行，右表有m行，那么笛卡尔积结果集含有n\*m行。

## 例子

```dolphindb
a = table(2010 2011 2012 as year)
b = table(`IBM`C`AAPL as Ticker);
a;
```

| year |
| --- |
| 2010 |
| 2011 |
| 2012 |

```dolphindb
b;
```

| Ticker |
| --- |
| IBM |
| C |
| AAPL |

```dolphindb
cj(a,b);
```

| year | Ticker |
| --- | --- |
| 2010 | IBM |
| 2010 | C |
| 2010 | AAPL |
| 2011 | IBM |
| 2011 | C |
| 2011 | AAPL |
| 2012 | IBM |
| 2012 | C |
| 2012 | AAPL |

```dolphindb
select * from cj(a,b) where year>2010;
// 等价于 select * from a cross join b where year>2010
```

| year | Ticker |
| --- | --- |
| 2011 | IBM |
| 2011 | C |
| 2011 | AAPL |
| 2012 | IBM |
| 2012 | C |
| 2012 | AAPL |

相反, [join](../operators/join.html)
只是简单地合并两张表的列。

```dolphindb
join(a,b);
```

| year | Ticker |
| --- | --- |
| 2010 | IBM |
| 2011 | C |
| 2012 | AAPL |
