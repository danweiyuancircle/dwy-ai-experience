---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumvar.html
fetched_at: 2026-05-19T09:17:56Z
category: funcs
title: cumvar
sha1: 94e36fc51f6816bd0003ed1a763c2d00094641e1
---

# cumvar

## 语法

`cumvar(X)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累计方差。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
x=[2,3,4];
cumvar(x);
// output
[,0.5,1]

m=matrix(0.15 0.08 0.03 -0.14 -0.09, 0.2 -0.12 -0.16 0.08 0.16);
m;
```

| #0 | #1 |
| --- | --- |
| 0.15 | 0.2 |
| 0.08 | -0.12 |
| 0.03 | -0.16 |
| -0.14 | 0.08 |
| -0.09 | 0.16 |

```dolphindb
cumvar(m);
```

| #0 | #1 |
| --- | --- |
|  |  |
| 0.0024 | 0.0512 |
| 0.0036 | 0.0389 |
| 0.0152 | 0.0288 |
| 0.0143 | 0.0267 |

相关函数：[cummax](cummax.html), [cummin](cummin.html), [cumprod](cumprod.html), [cumPositiveStreak](cumPositiveStreak.html), [cumsum](cumsum.html), [cumavg](cumavg.html), [cumstd](cumstd.html)
