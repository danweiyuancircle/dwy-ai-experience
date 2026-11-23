---
source_url: https://docs.dolphindb.cn/zh/progr/progr_intro.html
fetched_at: 2026-05-19T08:56:05Z
category: progr
title: 编程语言
sha1: e1e209a9328cfbffa2433b0dc6673dfe2b52dd10
---

# 编程语言

本章节包含以下内容：

- DolphinDB 脚本编程语言。包含了 DolphinDB 编程所需要了解的概念和方法，例如数据类型与数据形式、不同类型的对象、运算符及运算规则、具有
  DolphinDB 特色的编程语句、函数化编程等。DolphinDB 脚本语言大小写敏感，所有标识符（如变量、函数名、类名）及保留字（关键字）严格区分大小写。
- SQL 语句。DolphinDB 充分地兼容 ANSI-92 SQL 语言标准和多个主流 SQL 方言。了解 SQL 关键字在 DolphinDB
  中的具体使用方法能够帮助 SQL 使用者更流畅地体验 DolphinDB。

在 DolphinDB 编程语言中，默认情况下每一行表示一条完整语句，行尾即语句结束。但在某些语法结构中，DolphinDB
支持跨多行书写同一条语句，以提高可读性，尤其适用于较长的 SQL 查询或链式函数调用。

1. **SQL 语句**

   DolphinDB 的 SQL 查询支持按照 SQL
   标准在多个关键字之间换行：

   ```dolphindb
   select sym, qty, price
   from trades
   where date between 2024.01.01 and 2024.12.31
   context by sym
   ```
2. **链式函数调用**

   支持将多次函数调用写在不同的行上：

   ```dolphindb
   data
   .cumsum()
   .max()
   ```
3. **括号内表达式**

   圆括号、方括号、花括号内的表达式可以分成多个物理行，不必使用反斜杠：

   ```dolphindb
   sum = add(
     100,
     200
   )

   lags = ["A1",
   "A2","A3","A4",
   "A5","A6","A7",
   "A8","A9","A10"] 

   myMap = {
       "a": 1,
       "b": 2,
       "c": 3
   }
   ```
4. **行尾为未完成的表达式**

   当一行以运算符或逗号结尾，语句被视为尚未结束，会自动向下一行延续：

   ```dolphindb
   a = 1 +
       2
   ```

   注意：如果一行语义已完整，下一行开始的是一个运算符，会解析为两条语句，导致语法错误。例如：

   ```dolphindb
   a = 1
   + 2  // 错误：此时 + 2 被视为一条新的无效语句
   ```
