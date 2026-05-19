---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isColumnarTuple.html
fetched_at: 2026-05-19T09:28:22Z
category: funcs
title: isColumnarTuple
sha1: c6380a3f1c3c3e07d48edf05b09a6893830cb0d6
---

# isColumnarTuple

## 语法

`isColumnarTuple(X)`

## 详情

判断一个元组是否是 columnar tuple。

## 参数

`X` 是一个元组。

## 返回值

布尔标量。

## 例子

```dolphindb
tp = [[1,2,3], [4,5,6], [7,8]]
isColumnarTuple(tp)
// output: false

tp.setColumnarTuple!()
isColumnarTuple(tp)
// output: true
```

```dolphindb
id = 3 2 1 4
val = [`aa`bb, `aa`cc`dd, `bb, `cc`dd]
t = table(id, val)

isColumnarTuple(t.val)
// output: true

isColumnarTuple(t.id)
// output: false

exec isColumnarTuple(val) from t
// output: true

av = array(INT[], 0, 10).append!([1 1 1 3, 2 4 2 5, 8 9 7 1, 5 4 3])
t = table(id, av)
isColumnarTuple(t.av)
// output: false
```
