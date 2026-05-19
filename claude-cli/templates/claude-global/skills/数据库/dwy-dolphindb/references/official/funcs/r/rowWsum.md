---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rowWsum.html
fetched_at: 2026-05-19T09:37:37Z
category: funcs
title: rowWsum
sha1: 9207c32a1ffa382b6cd5bd9f3959babf7f29baed
---

# rowWsum

## 语法

`rowWsum(X, Y)`

row 系列函数通用参数说明和计算规则请参考：[rowFunctions](../themes/rowFunctions.html)

## 详情

逐行计算 *X* 和 *Y* 的内积。

## 返回值

返回一个长度与输入参数行数相同的向量。

## 例子

```dolphindb
m1=matrix(2 -1 4, 8 3 2, 9 0 1)
m2=matrix(8 11 10, 8 17 4, 14 6 4)
rowWsum(m1, m2)
// output
[206, 40, 52]

m3=matrix(8 NULL 10, 8 NULL 4, 14 NULL NULL)
rowWsum(m1, m3)
// output
[206, , 48]

a= -10 12.3 4 -8
b= 17.9 9 7.5 -4
c= 5.5 6.4 -7 8
x=array(DOUBLE[],0, 10).append!([a, b, c])
y=array(DOUBLE[],0, 10).append!([b, a, c])

rowWsum(x, y)
// output
[0.63, -6.3 , 184.21]
```

相关函数：[wsum](../w/wsum.html)
