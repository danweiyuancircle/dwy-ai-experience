---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumsum4.html
fetched_at: 2026-05-19T09:17:54Z
category: funcs
title: cumsum4
sha1: 04c27a0d8c6c5ac0650d8328aa1b32add30bde89
---

# cumsum4

## 语法

`cumsum4(X)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累计四次方和。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
x=[2,3,4];
cumsum4 x;
// output
[16,97,353]

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
cumsum4(m);
```

| #0 | #1 |
| --- | --- |
| 1 | 256 |
| 17 | 881 |
| 98 | 2177 |

相关函数：[sum4](../s/sum4.html)
