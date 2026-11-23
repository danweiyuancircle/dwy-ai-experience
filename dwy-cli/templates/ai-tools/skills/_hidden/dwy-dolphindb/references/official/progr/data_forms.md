---
source_url: https://docs.dolphindb.cn/zh/progr/data_forms.html
fetched_at: 2026-05-19T09:00:26Z
category: progr
title: 数据形式
sha1: 79fd91c723a7177bdd87848d7fa43cd73ce7f60f
---

# 数据形式

DolphinDB 支持以下数据形式：

| 名称 | ID | 例子 |
| --- | --- | --- |
| 标量 | 0 | 5, 1.3, 2012.11.15, `hello |
| 向量 | 1 | - 常规向量：5 4 8 或 [5, 4, 8] - 元组：(1 2 3, ["I","M","G"], 2.5) - 数组向量：[arrayVector](data_types_forms/arrayVector.html) - 大数组：[bigArray](data_types_forms/BigArray.html) - 列式元组：[columnar   tuple](data_types_forms/columnarTuple.html) |
| 数据对 | 2 | 3:5; 'a':'c'; "Tom":"John"。参考：  - [pair](../funcs/p/pair.html) |
| 矩阵 | 3 | 1..6$2:3 or reshape(1..6, 2:3)。参考：  - 普通矩阵：[matrix](../funcs/m/matrix.html) - 索引矩阵：[setIndexedMatrix!](../funcs/s/setIndexedMatrix_.html) - 索引序列：[indexedSeries](../funcs/i/isIndexedSeries.html), [setIndexedSeries!](../funcs/s/setIndexedSeries_.html) |
| 集合 | 4 | [set](../funcs/s/set.html) |
| 字典 | 5 | - 有序/无序字典：[dict](../funcs/d/dict.html) - 有序/无序同步字典：[syncDict](../funcs/s/syncDict.html) |
| 表 | 6 | - 内存表：   - 常规表：[table](../funcs/t/table.html)   - 索引表：[indexedTable](../funcs/i/indexedTable.html)   - 键值表：[keyedTable](../funcs/k/keyedTable.html), [latestIndexedTable](../funcs/l/latestIndexedTable.html)   - 流数据表：[streamTable](../funcs/s/streamTable.html),[haStreamTable](../funcs/h/haStreamTable.html), [keyedStreamTable](../funcs/k/keyedStreamTable.html), [latestKeyedStreamTable](../funcs/l/latestkeyedstreamtable.html)   - 缓存表：[cachedTable](../funcs/c/cachedTable.html)   - 分区表：[createPartitionedTable](../funcs/c/createPartitionedTable.html)   - 跨进程共享内存表：[createIPCInMemoryTable](../funcs/c/createIPCInMemoryTable.html) - 分布式表：   - 分区表：[createPartitionedTable](../funcs/c/createPartitionedTable.html)   - 维度表：[createTable](../funcs/c/createTable.html) - 多版本并发控制表：[mvccTable](../funcs/m/mvccTable.html), [haMvccTable](../funcs/h/haMvccTable.html) |
| 张量 | 10 | 通过 [tensor](../funcs/t/tensor.html) 函数，创建张量。例如：  1 维张量：`tensor(1..100)`  2 维张量：`tensor(1..10$5:2)`  3 维张量：`tensor((rand(1.0, 6)$3:2, rand(1.0, 6)$3:2))`  …  n 维张量，其中 n 不能大于10。  注意：   - 目前张量仅支持如下类型：BOOL, CHAR, SHORT, INT, LONG, FLOAT, DOUBLE。 |

可以通过 [form](../funcs/f/form.html) 函数来取得一个变量或者常量的数据形式。

```dolphindb
form false;
// output: 0

form `TEST;
// output: 0

form `t1`t2`t3;
// output: 1

form 1 2 3;
// output: 1

x= 1 2 3
if(form(x) == VECTOR){y=1};
y;
// output: 1

form 1..6$2:3;
// output: 3

form(tensor(1..10$5:2))
// output: 10
```
