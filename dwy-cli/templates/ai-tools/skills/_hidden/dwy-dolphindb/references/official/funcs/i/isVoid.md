---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isVoid.html
fetched_at: 2026-05-19T09:29:00Z
category: funcs
title: isVoid
sha1: 8af59f19fc832b77a75344e9ebff3bf87a04504b
---

# isVoid

## 语法

`isVoid(X)`

## 详情

检查一个对象是否是 VOID 类型。有两种 VOID 类型的对象：一种是 NULL 对象；另一种是 Nothing 对象。参见
[isNothing](isNothing.html)。

## 参数

**X** 可以是系统支持的任意数据形式。

## 参数

布尔类型，数据形式同 *X*。

## 例子

```dolphindb
isVoid(NULL);
// output: true

isVoid(1 NULL 2);
// output: false

// 和 isNull 相比
isNull(1 NULL 2);
// output: [false,true,false]

isVoid(matrix(NULL 2 NULL, NULL 2 1))
// output: false
```
