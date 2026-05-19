---
source_url: https://docs.dolphindb.cn/zh/funcs/e/exp.html
fetched_at: 2026-05-19T09:21:26Z
category: funcs
title: exp
sha1: aa7cd478a7e00eb9eb5634dbe2d508604b27d4e2
---

# exp

## 语法

`exp(X)`

## 详情

返回 e 的 *X* 次方。e 是一个常数，为2.71828。

注：

与 `numpy.exp` 及
`scipy.stats.exp` 的功能都基本相同，区别在于 DolphinDB 的 `exp`
函数只接受一个参数 *X*，不支持 `numpy.exp` 中的 *out*、*where*
等参数。

## 参数

**X** 可以是标量、数据对、向量、矩阵或表。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
exp(1 2 3);
// output
[2.718282,7.389056,20.085537]

log(exp(1));
// output
1
```
