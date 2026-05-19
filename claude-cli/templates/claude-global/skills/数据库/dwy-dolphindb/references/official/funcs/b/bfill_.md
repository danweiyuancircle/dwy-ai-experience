---
source_url: https://docs.dolphindb.cn/zh/funcs/b/bfill_.html
fetched_at: 2026-05-19T09:13:43Z
category: funcs
title: bfill!
sha1: 75427993656eaecfdab17942867a31d867aca67e
---

# bfill!

## 语法

`bfill!(obj, [limit])`

## 详情

- 如果*obj*是一个向量，使用 NULL 值后的非空元素来填充 NULL 值。
- 如果*obj*是一个表，对于表中的每一列，使用 NULL 值后的非空元素来填充 NULL 值。

## 参数

**obj** 可以是向量或表。

**limit** 是正整数，表示需要填充的 NULL 值的数量。

## 返回值

返回填充空缺值后的对象，其类型与形式同 *obj*。

## 例子

```dolphindb
x=1 2 3 NULL NULL NULL 4 5 6
x.bfill!()
x;
// output
[1,2,3,4,4,4,4,5,6]

x=1 2 3 NULL NULL NULL 4 5 6
x.bfill!(1)
x;
// output
[1,2,3,,,4,4,5,6]

date=[2012.06.12,,2012.06.13,2012.06.14,2012.06.15]
sym=["IBM","MSFT","IBM","MSFT","MSFT"]
price=[40.56,26.56,,,50.76]
qty=[2200,4500,1200,5600,]
timestamp=[09:34:07,,09:36:42,09:36:51,09:36:59]
t=table(date,timestamp,sym,price,qty)

bfill!(t)
t
```

| date | timestamp | sym | price | qty |
| --- | --- | --- | --- | --- |
| 2012.06.12 | 09:34:07 | IBM | 40.56 | 2200 |
| 2012.06.13 | 09:36:42 | MSFT | 26.56 | 4500 |
| 2012.06.13 | 09:36:42 | IBM | 50.76 | 1200 |
| 2012.06.14 | 09:36:51 | MSFT | 50.76 | 5600 |
| 2012.06.15 | 09:36:59 | MSFT | 50.76 |  |

如果只需要填充表中的某些列，需要使用 [update](../../progr/sql/update.html) 语句和 [bfill](bfill.html) 函数。具体请参考 [bfill](bfill.html) 的例子。
