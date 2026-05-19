---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumprod.html
fetched_at: 2026-05-19T09:17:42Z
category: funcs
title: cumprod
sha1: 484feca4100ce8a5b9bb0909f8ac8a8a551a2d96
---

# cumprod

## 语法

`cumprod(X)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累计乘积。

注：

与 [numpy.cumprod](https://numpy.net.cn/doc/stable/reference/generated/numpy.cumprod.html) 的功能基本相同，区别在于 DolphinDB 的
`cumprod` 对矩阵默认按列计算累计乘积（等价于 `numpy.cumprod` 设置
*axis*=0），且只接受一个参数 *X*，不支持 `numpy.cumprod` 中的
*axis*、*dtype* 和 *out* 参数。

## 返回值

LONG/DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
cumprod(2 3 4);
// output
[2,6,24]
# 等价于 [2, 2*3, 2*3*4]

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
cumprod(m);
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 20 |
| 6 | 120 |

相关函数：[prod](../p/prod.html)
