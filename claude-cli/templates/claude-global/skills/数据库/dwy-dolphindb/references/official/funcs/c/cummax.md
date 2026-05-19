---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cummax.html
fetched_at: 2026-05-19T09:17:34Z
category: funcs
title: cummax
sha1: 043932792226ffd019a681bc6334d7b552899f9c
---

# cummax

## 语法

`cummax(X)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累计最大值。

## 返回值

返回一个与输入 *X* 相同数据类型和形式的对象。

## 例子

```dolphindb
x = [7,4,5,8,9]
cummax(x);
// output
[7,7,7,8,9]

m = matrix(6 5 7 8 1, 3 9 4 2 10);
m;
```

| #0 | #1 |
| --- | --- |
| 6 | 3 |
| 5 | 9 |
| 7 | 4 |
| 8 | 2 |
| 1 | 10 |

```dolphindb
cummax(m);
```

| #0 | #1 |
| --- | --- |
| 6 | 3 |
| 6 | 9 |
| 7 | 9 |
| 8 | 9 |
| 8 | 10 |

相关函数：[cummin](cummin.html), [max](../m/max.html)
