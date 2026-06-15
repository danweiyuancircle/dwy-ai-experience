---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rowimaxlast.html
fetched_at: 2026-05-19T09:37:07Z
category: funcs
title: rowImaxLast
sha1: bb3fb553938c9b3b11c20fbf79ee2970c2ab1954
---

# rowImaxLast

## 语法

`rowImaxLast(args…)`

## 详情

返回每行元素中最大元素的索引。如果有多个相同的最大值，返回右起第一个最大值的索引。

## 参数

row 系列函数通用参数说明和计算规则请参考：[行计算系列（row
系列）](../themes/rowFunctions.html)

## 返回值

结果为一个长度与输入参数行数相同的向量。

## 例子

```dolphindb
m=matrix([4.5 2.6 1.5 3.2, 1.5 4.8 5.9 1.7, 4.9 2.0 NULL 5.5])
rowImaxLast(m)
// output
[2,1,1,2]

trades = table(10:0,`time`sym`p1`p2`p3`p4`p5`vol1`vol2`vol3`vol4`vol5,[TIMESTAMP,SYMBOL,DOUBLE,DOUBLE,DOUBLE,DOUBLE,DOUBLE,INT,INT,INT,INT,INT])
insert into trades values(2022.01.01T09:00:00, `A, 33.2, 33.8, 33.6, 33.3, 33.1, 200, 180, 180, 220, 200)
insert into trades values(2022.01.01T09:00:00, `A, 33.1, 32.8, 33.2, 34.3, 32.3, 150, 280, 190, 100, 220)
insert into trades values(2022.01.01T09:00:00, `A, 31.2, 32.6, 33.6, 35.3, 34.5, 220, 160, 130, 100, 110)
insert into trades values(2022.01.01T09:00:00, `A, 30.2, 32.5, 33.6, 35.3, 34.1, 200, 180, 150, 140, 120)
insert into trades values(2022.01.01T09:00:00, `A, 33.2, 33.8, 33.6, 33.3, 33.1, 180, 160, 160, 180, 200)

select rowAt(matrix(p1, p2, p3, p4, p5), rowImaxLast(vol1, vol2, vol3, vol4, vol5)) as price from trades
// output
price
33.3
32.8
31.2
30.2
33.1
```

相关函数：[rowImax](rowImax.html)
