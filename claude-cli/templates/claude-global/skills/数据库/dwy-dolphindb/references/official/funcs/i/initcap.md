---
source_url: https://docs.dolphindb.cn/zh/funcs/i/initcap.html
fetched_at: 2026-05-19T09:27:44Z
category: funcs
title: initcap
sha1: 474a20b81109f0d4910993822bbc4b00e2064abf
---

# initcap

## 语法

`initcap(X)`

## 详情

将 *X* 中由分隔符分隔的字符串中的第一个英文字符设置为大写，其余英文字符设置为小写。其中，分隔符是除英文字符和数字外的任意字符，例如：汉字，空格，@
等。

注：

该函数将数字也视为英文字符。

## 参数

**X** STRING 类型的标量/向量，或 SYMBOL 类型的向量。

## 返回值

和 *X* 类型保持一致。

## 例子

```dolphindb
initcap("hello world")
// output
Hello World

initcap("1aBBBBBB")
// output
1abbbbbb

initcap("nihao, hello@you")
// output
Nihao, Hello@You

initcap("你好hello" "hello You")
// output
["你好Hello","Hello You"]
initcap(symbol(["adhE","","1yI"]))
// output
["Adhe",,"1yi"]
```
