---
source_url: https://docs.dolphindb.cn/zh/funcs/r/replace.html
fetched_at: 2026-05-19T09:36:00Z
category: funcs
title: replace
sha1: 044b1bcad6a85f7efcdc84a9171bb7c708877b59
---

# replace

## 语法

`replace(X, oldValue, newValue)`

## 详情

返回将 *oldValue* 替换成 *newValue*
后的向量或矩阵。`replace!` 是 `replace` 的原地改变版本。

## 参数

**X** 可以是向量、矩阵。

**oldValue** 标量，与 *X/newValue* 具有相同数据类别，表示将被替换的值。

**newValue** 标量，与 *X/oldValue* 具有相同数据类别，表示新的值。

## 返回值

与 *X* 类型相同的向量或矩阵。

## 例子

```dolphindb
x=1 1 3;
x=x.replace(1,2);
x
// output
[2,2,3];

m=1..4$2:2;
m
```

| #0 | #1 |
| --- | --- |
| 1 | 3 |
| 2 | 4 |

```dolphindb
m=m.replace(2,1);
m
```

| #0 | #1 |
| --- | --- |
| 1 | 3 |
| 1 | 4 |

```dolphindb
m.replace!(1,6);
```

| #0 | #1 |
| --- | --- |
| 6 | 3 |
| 6 | 4 |
