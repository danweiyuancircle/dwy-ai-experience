---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rowCummax.html
fetched_at: 2026-05-19T09:36:54Z
category: funcs
title: rowCummax
sha1: 34f99127cf4aa2cfafbd72660c17738c6c269f1f
---

# rowCummax

## 语法

`rowCummax(X)`

row 系列函数通用参数说明和计算规则请参考：[rowFunctions](../themes/rowFunctions.html)

## 详情

逐行计算 *X* 元素的累积最大值。

## 返回值

返回一个数据类型与 *X* 相同的对象。

## 例子

```dolphindb
m=matrix([4.5 2.6 1.5, 1.5 4.8 5.9, 4.9 2.0 NULL])
rowCummax(m)
```

| col1 | col2 | col3 |
| --- | --- | --- |
| 4.5 | 4.5 | 4.9 |
| 2.6 | 4.8 | 4.8 |
| 1.5 | 5.9 | 5.9 |

```dolphindb
a=array(INT[], 0, 10).append!([1 2 3, 4 5, 6 7 8]);
rowCummax(a)
// output
[[1,2,3],[4,5],[6,7,8]]

tp = [[1.3,2.5,2.3], [4.1,5.3,6.2]]
tp.setColumnarTuple!()
rowCummax(tp)
// output
[[1.3,2.5,2.5],[4.1,5.3,6.2]]
```
