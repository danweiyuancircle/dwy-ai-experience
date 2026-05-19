---
source_url: https://docs.dolphindb.cn/zh/funcs/m/merge.html
fetched_at: 2026-05-19T09:31:35Z
category: funcs
title: merge
sha1: 50bf11bfae616b92785f3f7d1c06e58527f4e0c0
---

# merge

## 语法

`merge(left, right, [how='inner'])`

## 详情

联结两个索引序列或两个索引矩阵。

DolphinDB 的 `merge` 函数与 Python Pandas 的 `merge`
函数在核心功能上相似，区别在于：

| 对比维度 | DolphinDB `merge` | Python Pandas `merge` |
| --- | --- | --- |
| 核心功能 | 联结两个索引序列或索引矩阵。基于行标签进行对齐和合并。 | 联结两个 DataFrame。基于一个或多个列（或索引）进行数据库风格的合并。 |
| 主要设计目的 | 处理面板数据，实现时间序列或截面数据的对齐运算。 | 实现关系型数据库的 JOIN 操作（如 inner, left, right, outer join）。 |
| 输入对象 | *left*, *right*：必须均为索引序列或索引矩阵。 | *left*, *right*：DataFrame 或带有名称的 Series。 |
| 关键参数 | 支持 *how*（'inner', 'outer', 'left', 'right', 'asof''（DolphinDB 特有））。 | 支持 *how*, *on*, *left\_on*, *right\_on*, *left\_index*, *right\_index*, *sort*, *suffixes* 等。功能更丰富。 |

## 参数

**left** 与 **right** 均为索引序列，或均为索引矩阵。

**how** 是字符串，表示如何对数据进行联结。可取值为 'inner', 'outer', 'left', 'right' 与 'asof'。默认值为
‘inner’。

## 返回值

一个矩阵。

## 例子

```dolphindb
a = indexedSeries(2012.01.01..2012.01.04, 1..4)
b = indexedSeries([2012.01.01, 2012.01.03, 2012.01.05, 2012.01.06], 5..8)
merge(a, b);
```

|  | series1 | series2 |
| --- | --- | --- |
| 2012.01.01 | 1 | 5 |
| 2012.01.03 | 3 | 6 |

```dolphindb
merge(a, b, 'left');
```

|  | series1 | series2 |
| --- | --- | --- |
| 2012.01.01 | 1 | 5 |
| 2012.01.02 | 2 |  |
| 2012.01.03 | 3 | 6 |
| 2012.01.04 | 4 |  |

```dolphindb
m1 = matrix([1.2, 7.8, 4.6, 5.1, 9.5], [0.15, 1.26, 0.45, 1.02, 0.33]).rename!([2012.01.01, 2015.02.01, 2015.03.01, 2015.04.01, 2015.05.01], `x1`x2).setIndexedMatrix!()
m2 = matrix([1.0, 2.0, 3.0, 4.0], [0.14, 0.26, 0.35, 0.48]).rename!([2015.02.01, 2015.02.16, 2015.05.01, 2015.05.02], `y1`y2).setIndexedMatrix!()
m = merge(m1, m2, 'asof');
```

|  | x1 | x2 | y1 | y2 |
| --- | --- | --- | --- | --- |
| 2012.01.01 | 1.2 | 0.15 |  |  |
| 2015.02.01 | 7.8 | 1.26 | 1 | 0.14 |
| 2015.03.01 | 4.6 | 0.45 | 2 | 0.26 |
| 2015.04.01 | 5.1 | 1.02 | 2 | 0.26 |
| 2015.05.01 | 9.5 | 0.33 | 3 | 0.35 |
