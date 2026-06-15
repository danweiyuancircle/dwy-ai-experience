---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumsum3.html
fetched_at: 2026-05-19T09:17:52Z
category: funcs
title: cumsum3
sha1: 53c80b6754cb04e5737fa15e5c3949c106fcc04d
---

# cumsum3

## 语法

`cumsum3(X)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累计立方和。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
x=[2,3,4];
cumsum3 x;
// output
[8,35,99]

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
cumsum3(m);
```

| #0 | #1 |
| --- | --- |
| 1 | 64 |
| 9 | 189 |
| 36 | 405 |

相关函数：[sum](../s/sum.html)
