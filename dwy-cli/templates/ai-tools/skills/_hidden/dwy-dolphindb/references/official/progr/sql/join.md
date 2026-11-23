---
source_url: https://docs.dolphindb.cn/zh/progr/sql/join.html
fetched_at: 2026-05-19T09:03:58Z
category: progr
title: join
sha1: a8d39050f21be11b9d41a52f9769b9f5f7c0f934
---

# join

## 语法

```dolphindb
SELECT column_name(s)
FROM table1
JOIN table2
[ON table1.matchingCol1=table2.MatchingCol2]
```

## 参数

**table1/table2** 是待连接的表。

**matchingCol1/matchingCol2** 表示连接列。

## 详情

- 当不指定 ON 连接条件时，执行 CROSS JOIN 连接，返回两个表的笛卡尔积的结果集。
- 当指定 ON 连接条件时，执行 INNER JOIN 连接，返回连接表中满足限制条件的行的结果集。

注：

1. 暂不支持非等值连接，例如：t1 JOIN t2 ON t1.id <op> t2.id，其中
   <op> 为：>, <,>=, <=, <> 。
2. 如果有多个连接列，必须使用 AND 连接。
3. 不能和 UPDATE 关键字一起使用。
4. 在版本 2.00.10 之前，执行 select \* from table1 join table2
   等同于简单地将两张表进行合并，即 join(a,b)。

## 例子

```dolphindb
t1 = table(1 2 3 3 as id, 7.8 4.6 5.1 0.1 as value, 4 3 2 1 as x)
t2 = table(5 3 1 2 as idv,  300 500 800 200 as qty, 4 6 4 5 as xv);
SELECT * FROM t1 JOIN t2 WHERE x>3
//等价于 SELECT * FROM t1 CROSS JOIN t2 WHERE x>3 或 SELECT * FROM cj(t1,t2) WHERE x>3;
```

| id | value | x | idv | qty | xv |
| --- | --- | --- | --- | --- | --- |
| 1 | 7.8 | 4 | 5 | 300 | 4 |
| 1 | 7.8 | 4 | 3 | 500 | 6 |
| 1 | 7.8 | 4 | 1 | 800 | 4 |
| 1 | 7.8 | 4 | 2 | 200 | 5 |

```dolphindb
SELECT * FROM t1 JOIN t2 ON t1.id=t2.idv ;
//等价于 SELECT * FROM t1 INNER JOIN t2 ON t1.id=t2.idv
```

| id | value | x | qty | xv |
| --- | --- | --- | --- | --- |
| 1 | 7.8 | 4 | 800 | 4 |
| 2 | 4.6 | 3 | 200 | 5 |
| 3 | 5.1 | 2 | 500 | 6 |
| 3 | 0.1 | 1 | 500 | 6 |
