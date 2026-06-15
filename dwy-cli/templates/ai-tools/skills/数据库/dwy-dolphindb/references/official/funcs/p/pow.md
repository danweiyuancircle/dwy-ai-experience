---
source_url: https://docs.dolphindb.cn/zh/funcs/p/pow.html
fetched_at: 2026-05-19T09:34:26Z
category: funcs
title: pow
sha1: cf965f7724d68669398422ec7d725d51172adaa2
---

# pow

## 语法

`pow(X, Y)`

## 详情

返回以 *X* 中的元素为底，以 *Y* 中元素为指数计算得到的值。当 *X* 和 *Y*
为整数时，结果仍然是 DOUBLE 类型。

注：

- DolphinDB `pow` 与 Python 内置 [pow](https://docs.python.org/3/library/functions.html#pow)以及 [numpy.power](https://numpy.org/doc/stable/reference/generated/numpy.power.html) 的核心功能相同，区别在于：
  - Python 内置`pow` 面向 Python 数值对象，并额外支持三参数形式
    `pow(base, exp, mod)` 用于高效模幂运算*。*
  - `numpy.power` 支持更多参数，如
    *out*、*where*、*casting*。
- [scipy.stats.power](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.power.html) 是用于模拟统计检验功效的函数，与
  DolphinDB `pow` 完全不同。

## 参数

**X** 和 **Y** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型标量、向量或矩阵。

## 例子

```dolphindb
x=1 2 3;
pow(x,3);
//output:[1,8,27]

pow(3,x);
//output:[3,9,27]

y=4.5 5.5 6.5;
pow(x,y);
//output:[1,45.254834,1262.665039]

pow(y,x);
//output: [4.5,30.25,274.625]
```

```dolphindb
m=1..10$2:5;
m;
```

返回：

| #0 | #1 | #2 | #3 | #4 |
| --- | --- | --- | --- | --- |
| 1 | 3 | 5 | 7 | 9 |
| 2 | 4 | 6 | 8 | 10 |

```dolphindb
typestr(pow(3,4));
//output: DOUBLE
```
