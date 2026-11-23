---
source_url: https://docs.dolphindb.cn/zh/funcs/w/writeLog.html
fetched_at: 2026-05-19T09:44:11Z
category: funcs
title: writeLog
sha1: e8cd7436c94e2c61783da5e2bdb568ec025c6c37
---

# writeLog

## 语法

`writeLog(X1, [X2, X3....Xn])`

## 详情

在日志文件中写入日志。该函数必须要用户登录后才能执行。

## 参数

**X1**, **X2**, **X3** ... **Xn** 是要写入日志文件的字符串。每个字符串都是日志文件中的一行。

## 返回值

无。

## 例子

```dolphindb
writeLog("This is a message written into the log file.")
writeLog("line1.","line2.","line3");

// Check the log file.
// output
Sun Aug 06 16:41:05 2017 <INFO> :This is a message written into the log file.
Sun Aug 06 16:50:35 2017 <INFO> :line1.
Sun Aug 06 16:50:35 2017 <INFO> :line2.
Sun Aug 06 16:50:35 2017 <INFO> :line3
```
