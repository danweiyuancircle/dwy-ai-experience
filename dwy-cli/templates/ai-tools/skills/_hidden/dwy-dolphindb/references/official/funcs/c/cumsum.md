---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumsum.html
fetched_at: 2026-05-19T09:17:50Z
category: funcs
title: cumsum
sha1: 74d5c2e97a2a5ae1a8f1b45e35b2b097ffe81ded
---

# cumsum

## 语法

`cumsum(X)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累计和。

注：

与 NumPy 的 [numpy.cumsum](https://numpy.com.cn/doc/stable/reference/generated/numpy.cumsum.html) 的功能基本相同，区别在于 DolphinDB 的
`cumsum` 对矩阵默认按列累加（等价于 `numpy.cumsum` 设置
*axis*=0），且只接受一个参数 *X*，不支持 `numpy.cumsum` 中的
*axis*、*dtype* 和 *out* 参数。

## 返回值

LONG/DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
x=[2,3,4];
cumsum(x);
// output
[2,5,9]

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
cumsum(m);
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 3 | 9 |
| 6 | 15 |

相关函数：[sum](../s/sum.html)
