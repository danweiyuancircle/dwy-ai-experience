---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumwsum.html
fetched_at: 2026-05-19T09:18:02Z
category: funcs
title: cumwsum
sha1: cf8d08623acc6a049145f0e26b1a6593a411fce8
---

# cumwsum

## 语法

`cumwsum(X, Y)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 和 *Y* 的累计内积。

## 返回值

DOUBLE 类型，其数据形式同 *X*(*Y*)。

## 例子

```dolphindb
cumwsum(2.2 1.1 3.3, 4 5 6);
// output
[8.8,14.3,34.1]

cumwsum(1 NULL 1, 1 1 1);
// output
[1,1,2]
```

相关函数：[wsum](../w/wsum.html)
