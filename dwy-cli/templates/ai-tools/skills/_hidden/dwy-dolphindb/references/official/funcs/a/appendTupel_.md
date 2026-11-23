---
source_url: https://docs.dolphindb.cn/zh/funcs/a/appendTupel_.html
fetched_at: 2026-05-19T09:13:09Z
category: funcs
title: appendTuple!
sha1: 0929fba156cefb8d317bd5e3597b7bffdb3550ad
---

# appendTuple!

## 语法

`appendTuple!(X, Y, [wholistic=false])`

## 详情

将 *Y* 中的数据追加到 *X* 中。

- 当 *wholistic* 为 true 时，将 *Y* 整体作为一个元素追加到 *X* 中
- 当 *wholistic* 为 false 时，将 *Y* 中的每一个元素依次追加到 *X* 中
- 当 *X* 是列式元组时，*Y* 中元素必须与 *X* 中元素类型一致，且 *wholistic* 只能为
  false

## 参数

**X** 是一个元组。

**Y** 是一个元组。

**wholistic** 是一个 bool 标量，默认值为 false。

## 返回值

数据类型和数据形式与 *obj* 一致。

## 例子

```dolphindb
x = (1,"X")
y = ([2,3],"Y")
x.appendTuple!(y,true)
print(x)
// output
(1,"X",([2,3],"Y"))

x.appendTuple!(y,false)
print(x)
// output
(1,"X",([2,3],"Y"),[2,3],"Y")

x = [[1,2,3],4]
x.setColumnarTuple!()
x.appendTuple!((5,6),false)
print(x)
([1,2,3],4,5,6)
```
