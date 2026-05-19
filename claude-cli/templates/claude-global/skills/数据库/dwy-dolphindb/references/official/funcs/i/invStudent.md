---
source_url: https://docs.dolphindb.cn/zh/funcs/i/invStudent.html
fetched_at: 2026-05-19T09:28:07Z
category: funcs
title: invStudent
sha1: b080470c319f2fb8c6c7ad0765d11b49c42991ed
---

# invStudent

## 语法

`invStudent(df, X)`

## 详情

返回 t 分布的累计密度函数的逆函数值。

## 参数

**df** 是正数，表示t分布的自由度。

**X** 是0到1之间的浮点型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
invStudent(1, [0.15, 0.25, 0.35]);
// output: [-1.962611, -1, -0.509525]

invStudent(1, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output: [-3.077684, -0.726543, 0, 0.726543, 3.077684]
```
