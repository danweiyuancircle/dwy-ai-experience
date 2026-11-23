---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumstdp.html
fetched_at: 2026-05-19T09:17:47Z
category: funcs
title: cumstdp
sha1: 290613f4933a25015bbb96dbff3df530604fe1a3
---

# cumstdp

## 语法

`cumstdp(X)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累计总体标准差。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
x = [1,2,4,NULL,8];
cumstdp(x)
// output 
[0, 0.5, 1.247219128924647, 1.247219128924647, 2.680951323690902]
```

```dolphindb
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
cumstdp(m);
```

| col1 | col2 |
| --- | --- |
| 0 | 0 |
| 0.035 | 0.16 |
| 0.0492 | 0.1611 |
| 0.107 | 0.147 |
| 0.1071 | 0.1462 |
