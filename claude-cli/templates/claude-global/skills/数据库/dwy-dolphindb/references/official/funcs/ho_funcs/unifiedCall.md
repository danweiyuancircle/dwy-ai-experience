---
source_url: https://docs.dolphindb.cn/zh/funcs/ho_funcs/unifiedCall.html
fetched_at: 2026-05-19T09:45:21Z
category: funcs
title: unifiedCall
sha1: f872607c08f0fb03fc4c58523480207d25a61fcf
---

# unifiedCall

## 语法

`unifiedCall(func, args)`

## 详情

用指定的参数调用一个函数。同 [call](call.html) 类似，可以用在 [each/peach](each.html) 或 [loop](loop.html)/[ploop](ploop.html) 函数中，来调用一批函数。区别在于，*call*
函数的args参数个数不确定，由func传入的函数决定。 而 *unifiedCall*
的args只有一个，通过tuple来给func函数传入多个参数。

## 参数

**func** 是一个函数。

**args** 是一个tuple, tuple的每一个元素作为函数的参数。

## 返回值

取决于 *func* 的返回值。

## 例子

```dolphindb
unifiedCall(sum, [1..10])
```

返回：55

```dolphindb
unifiedCall(add, ([1,2,3,4,5,6,7,8,9,10],2))
```

返回：[3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

```dolphindb
each(unifiedCall, [std, max], [[matrix(1 3 5 7 9, 1 4 7 10 13)], [0..100]]);
```

得到：

| col1 | col2 |
| --- | --- |
| 3.1623 | 100 |
| 4.7434 | 100 |

下面这个例子，自定义一个函数，再通过unifiedCall传入参数，进行调用。

```dolphindb
def f(a,b){return (a+2)*b}
unifiedCall(f, (5,10))
```

返回：70
