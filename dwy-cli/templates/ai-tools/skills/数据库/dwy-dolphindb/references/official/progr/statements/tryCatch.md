---
source_url: https://docs.dolphindb.cn/zh/progr/statements/tryCatch.html
fetched_at: 2026-05-19T09:02:07Z
category: progr
title: try-catch
sha1: a79e0853563ab22f7c2e85574baa9bf3161aee75
---

# try-catch

## 语法

```dolphindb
try

{ ... }

catch(ex)

{ ... }
```

## 详情

首先执行 *try* 语句块。若没有异常发生，跳过 *catch* 语句块，*try* 语句执行结束；否则如果在 *try*
语句块的执行过程中发生了一个异常，错误消息将会存放在变量 *ex* 中，然后再执行 *catch* 语句块。

## 例子

```dolphindb
1/`7
// output
Arguments for div method can not be string.

try {1/`7} catch(ex){print "oops, please make sure they are all numbers"};
// output
oops, please make sure they are all numbers

ex;
// output
"SYSTEM_Operator" : "Arguments for div method can not be string."
```
