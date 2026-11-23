---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumcorrTopN.html
fetched_at: 2026-05-19T09:17:22Z
category: funcs
title: cumcorrTopN
sha1: 4d4ca7938495ba69f20af108af1409a15547728d
---

# cumcorrTopN

## 语法

`cumcorrTopN(X, Y, S, top, [ascending=true],
[tiesMethod='latest'])`

部分通用参数说明和窗口计算规则请参考：[cumTopN 系列](../themes/cumTopN.html)

## 详情

在累计窗口内，根据 *ascending* 指定的排序方式将 *X* 和 *Y* 按照
*S* 进行稳定排序后，取前 *top* 个元素，然后计算 *X* 和 *Y* 之间的相关性。

## 返回值

DOUBLE 类型，其数据形式取决于 *X* (*Y*)。

## 例子

```dolphindb
X=1 2 3 10 13 4 3
Y = 1 7 8 9 0 5 8
S = 0.3 0.5 0.1 0.1 0.5 0.2 0.4
cumcorrTopN(X, Y, S, 6)
// output
[,1,0.9244,0.6588,-0.1784,-0.1764,-0.1825]
```
