---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumavg.html
fetched_at: 2026-05-19T09:17:16Z
category: funcs
title: cumavg
sha1: 7d9e835cc0564ae42e407594fa6bf7b03f16fb1e
---

# cumavg

## 语法

`cumavg(X)`

参数说明和窗口计算规则请参考: [累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累积平均值。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
x=[2,3,NULL,4];

cumavg(x);
[2,2.5,2.5,3]

m=matrix(1 2 3 NULL 4, 5 6 NULL 7 8);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 5 |
| 2 | 6 |
| 3 |  |
|  | 7 |
| 4 | 8 |

```dolphindb
cumavg(m);
```

| #0 | #1 |
| --- | --- |
| 1 | 5 |
| 1.5 | 5.5 |
| 2 | 5.5 |
| 2 | 6 |
| 2.5 | 6.5 |

相关函数：[avg](../a/avg.html)
