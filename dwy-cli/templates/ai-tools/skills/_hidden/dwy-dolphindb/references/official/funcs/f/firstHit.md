---
source_url: https://docs.dolphindb.cn/zh/funcs/f/firstHit.html
fetched_at: 2026-05-19T09:21:44Z
category: funcs
title: firstHit
sha1: 0982654476b7dc4b6d2be8ac15e3a4a4386719a3
---

# firstHit

## 语法

`firstHit(func, X, target)`

## 详情

返回 *X* 中第一个满足 *X*
*func*
*target* （例如 *X*>5) 条件的元素。

若 *X* 中无元素满足条件，则返回空值。

通过 `firstHit` 查找时，NULL 值会被忽略。如需查找第一个非 NULL 值， 可以调用函数 [firstNot](firstNot.html)。

## 参数

**func** 关系运算符 >, >=, <, <=, !=, <>, ==。

**X** 向量或矩阵。

**target** 和 *X* 类型相同的标量，表示比较的对象。

## 返回值

返回值类型与 *X* 类型一致。数据形式为标量或向量。

## 例子

```dolphindb
X = NULL 3.2 4.5 1.2 NULL 7.8 0.6 9.1
firstHit(<, X, 2.5)
```

输出返回：1.2

若无元素满足查找条件，返回空值，如下面这个例子：

```dolphindb
firstHit(>, X, 10.0)
```

输出返回：NULL

相关函数：[ifirstHit](../i/ifirstHit.html)
