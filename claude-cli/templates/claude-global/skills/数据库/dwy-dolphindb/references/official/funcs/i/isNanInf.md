---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isNanInf.html
fetched_at: 2026-05-19T09:28:40Z
category: funcs
title: isNanInf
sha1: a5f2ccfeb3c7cd3218cbbd2c491ecbf720f35151
---

# isNanInf

## 语法

`isNanInf(X, [includeNull=false])`

## 详情

检测 *X* 中的每一个元素是否为 NaN 或 Inf。若 *includeNull* 设为 true，NULL
值会被视为 Nan 或 Inf，默认为 false。

## 参数

**X** 是 DOUBLE 类型的标量/向量/矩阵。

**includeNull** 是一个布尔值。

## 返回值

返回布尔类型，数据形式同 X。

## 例子

```dolphindb
x = [1.5, float(`nan), 2.3, float(`inf), NULL, 3.7]  
  
// includeNull = false (默认)，不检查 NULL 值  
isNanInf(x)  
// output: [false,true,false,true,false,false]

// includeNull = true，NULL 值将被视为 Nan 或 Inf
isNanInf(x)  
// output: [false,true,false,true,true,false]
```

相关函数：[countNanInf](../c/countNanInf.html)
